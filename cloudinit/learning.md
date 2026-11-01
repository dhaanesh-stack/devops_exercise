# Cloud-Init – Concepts and Learnings

## 1. What Is Cloud-Init?

Cloud-Init is a tool used to initialize and configure cloud instances during their boot process.

It automates tasks that would otherwise require manual server setup, such as:

- Installing packages.
- Creating users.
- Creating files and directories.
- Configuring services.
- Running commands.

For this project, Cloud-Init configures an Ubuntu VM and deploys a Dockerized Python application.

**Important:** Cloud-Init does not install Ubuntu. Ubuntu is already installed in the VM image. Cloud-Init runs after the operating system starts and performs the initial configuration.

## 2. How Does Cloud-Init Work During Boot?

When the VM starts, Ubuntu boots first. Once the operating system is running, Cloud-Init detects the instance, reads its configuration, and performs the required setup.

```text
VM Starts
   |
   v
Ubuntu Boots
   |
   v
Cloud-Init Runs
   |
   v
Server Configuration
   |
   v
Docker Starts
   |
   v
Testpress Application Starts
```

## 3. Cloud-Init Configuration

The `cloudinit.yaml` file defines what needs to be configured on the server.

It contains instructions to:

- Install required packages.
- Create the application user.
- Create application and service files.
- Build and start the Docker container.
- Enable the application service at boot.

Cloud-Init processes these instructions during instance initialization.

## 4. Cloud-Init Datasource

A datasource is the mechanism through which Cloud-Init obtains instance information and configuration.

This project uses `DataSourceNoCloud`.

NoCloud can provide:

- `meta-data`
- `user-data`
- `network-config`

Multipass provides the NoCloud seed information to the VM, even when a custom Cloud-Init YAML file is not supplied.

## 5. User-Data vs Metadata

These two terms are important when working with Cloud-Init.

### User-Data

User-data contains the configuration or instructions that should be applied to the instance.

For example:

- Install Docker.
- Create an application user.
- Write application files.
- Start a service.

In this project, `cloudinit.yaml` is the user-data configuration.

### Metadata

Metadata contains information about the instance itself.

For example:

- Instance ID.
- Hostname.
- Region or availability zone.
- Network-related information.

A simple comparison:

| User-Data | Metadata |
|---|---|
| Contains configuration instructions | Contains instance information |
| Describes what to configure | Describes the instance |
| Example: Install Docker | Example: Instance ID |

## 6. Where Does Cloud-Init Store Its Data?

Cloud-Init maintains its state and cached information under:

```text
/var/lib/cloud/
```

A simplified directory structure:

```text
/var/lib/cloud/
├── data/
│   ├── instance-id
│   ├── previous-datasource
│   └── previous-instance-id
│
├── instance -> instances/<instance-id>
│
├── instances/
│   └── <instance-id>/
│       ├── boot-finished
│       ├── datasource
│       ├── user-data.txt
│       ├── cloud-config.txt
│       ├── scripts/
│       │   └── runcmd
│       └── sem/
│           ├── config_runcmd
│           ├── config_scripts_user
│           └── config_write_files
│
├── scripts/
│   ├── per-boot/
│   ├── per-instance/
│   └── per-once/
│
└── seed/
```

### Important Files and Directories

- `data/instance-id`: Stores the current instance ID.
- `instances/`: Contains data associated with individual instances.
- `instance`: Symlink to the current instance directory.
- `user-data.txt`: Cached user-data received by Cloud-Init.
- `scripts/runcmd`: Generated script containing commands from `runcmd`.
- `sem/`: Contains semaphore files used to track module execution.

## 7. How Does Cloud-Init Know Whether It Is a New Instance?

Cloud-Init uses the instance ID provided by the datasource to identify an instance.

For example, in this Multipass setup:

```text
Instance ID: testpress-cloudinit
```

When the VM boots again, Cloud-Init checks the instance identity and its cached state.

If it is the same instance, modules configured to run once per instance are not normally executed again.

If a new instance is detected, Cloud-Init performs the relevant first-instance initialization.

**Note:** The instance ID format depends on the datasource. The example above is specific to this Multipass setup.

## 8. What Are Cloud-Init Stages?

Cloud-Init organizes its work into four main stages.

| Stage | Purpose |
|---|---|
| Local | Detects the datasource and performs early configuration. |
| Network | Configures networking and retrieves configuration when required. |
| Config | Processes configuration modules such as users and files. |
| Final | Runs final-stage tasks such as package installation and user scripts. |

Different Cloud-Init modules have different execution frequencies. Some run once per instance, while others can run on every boot.

For example, `runcmd` is processed during configuration and its generated script is executed during the final stage.

## 9. Cloud-Init vs Dockerfile

Both Cloud-Init and Dockerfiles automate setup, but they operate at different levels.

| Cloud-Init | Dockerfile |
|---|---|
| Configures the virtual machine | Builds a container image |
| Installs host packages | Installs container dependencies |
| Creates host users | Defines the container runtime environment |
| Configures systemd services | Defines image startup commands |
| Runs during instance initialization | Runs when building the image |

In this project:

- Cloud-Init prepares the Ubuntu server.
- Dockerfile defines the Python application image.
- Docker runs the application container.
- systemd manages the container lifecycle.

## 10. Why Use systemd to Manage the Container?

Docker can run containers independently, but this project uses systemd to demonstrate service management at the operating-system level.

The service configuration includes:

```ini
[Service]
Type=simple
ExecStart=/usr/bin/docker start -a testpress-app
ExecStop=/usr/bin/docker stop -t 10 testpress-app
Restart=always
RestartSec=5
```

### What These Settings Mean

- `Type=simple`: systemd treats the started process as the main service process.
- `ExecStart`: Starts the existing container and attaches to its main process.
- `ExecStop`: Stops the container gracefully.
- `Restart=always`: Restarts the service when its process exits.
- `RestartSec=5`: Waits five seconds before attempting a restart.

When the container's main process exits, the attached Docker command exits too. systemd detects this and restarts the service.

The Docker container is created with `--restart=no`, so systemd is responsible for its lifecycle in this setup.

## 11. Application Recovery vs Server Reboot Recovery

These are two different scenarios.

### Application Crash

If the application process crashes:

1. The attached Docker process exits.
2. systemd detects the service failure.
3. systemd waits five seconds.
4. systemd starts the container again.

### Server Reboot

If the VM reboots:

1. Ubuntu starts.
2. systemd starts enabled services.
3. Docker starts.
4. `testpress.service` starts the existing container.
5. The application becomes available again.

The `systemctl enable` command configures the service to start automatically during boot.

## 12. Why Doesn't Cloud-Init Run Everything Again After Reboot?

Cloud-Init maintains state using instance information and semaphore files.

For example:

```text
/var/lib/cloud/instance/sem/
```

These files help Cloud-Init track whether particular modules have already executed.

Since a normal reboot does not create a new instance, modules configured to run once per instance are not repeated.

This prevents operations such as rebuilding the Docker image and recreating the container on every reboot.

## 13. Useful Cloud-Init Debugging Commands

Check overall status:

```bash
cloud-init status --long
```

Validate the system configuration schema:

```bash
sudo cloud-init schema --system
```

Check detected datasource:

```bash
cat /var/lib/cloud/instance/datasource
```

Check instance ID:

```bash
cat /var/lib/cloud/data/instance-id
```

Inspect cached user-data:

```bash
sudo cat /var/lib/cloud/instance/user-data.txt
```

Inspect generated `runcmd` script:

```bash
sudo cat /var/lib/cloud/instance/scripts/runcmd
```

Inspect module execution markers:

```bash
sudo ls -la /var/lib/cloud/instance/sem/
```

View Cloud-Init logs:

```bash
sudo less /var/log/cloud-init.log
sudo less /var/log/cloud-init-output.log
```

---

## Summary

Through this project, I learned how Cloud-Init automates the initial configuration of a Linux server.

I also explored how datasources provide instance information, how Cloud-Init tracks execution state, how Docker packages an application, and how systemd manages application recovery and startup after a reboot.

The main takeaway is that **server provisioning, application packaging, and service management are separate responsibilities that work together to automate deployment.**
