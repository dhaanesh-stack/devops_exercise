# Linux Process Management & systemd – Bonus Topics

## Part 1: Bonus Challenges

### 1. systemd Timers vs Cron

Both are used to schedule tasks.

- **Cron:** Executes commands or scripts at scheduled times.
- **systemd timers:** Trigger systemd services at scheduled times.

systemd timers provide integrated logging, service management, dependencies and resource controls.

**Use case:** Running database backups every day.

### 2. Restart Configuration

systemd provides settings to control application restarts.

```ini
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=30
StartLimitBurst=3
```

- `Restart=on-failure`: Restart when the application fails.
- `RestartSec=5`: Wait 5 seconds before restarting.
- `StartLimitIntervalSec=30`: Count start attempts within 30 seconds.
- `StartLimitBurst=3`: Allow a maximum of 3 starts within that interval.

These settings prevent continuous restart loops.

### 3. Linux Process States and Zombie Processes

Important Linux process states:

| State | Meaning                 |
| ----- | ----------------------- |
| R     | Running or ready to run |
| S     | Sleeping                |
| D     | Uninterruptible sleep   |
| T     | Stopped                 |
| Z     | Zombie                  |

A **zombie process** is a process that has finished execution, but its parent has not collected its exit status using `wait()`.

It does not consume CPU but retains a process-table entry.

### 4. systemd Service Types

systemd supports different service types.

| Type   | Meaning                                                          |
| ------ | ---------------------------------------------------------------- |
| simple | Considers the service started when the process is launched.      |
| exec   | Considers it started after the executable successfully launches. |
| notify | Waits for the application to send a readiness notification.      |

`notify` is useful when an application needs to complete initialization before systemd considers it ready.

### 5. How systemd Uses cgroups

cgroups (Control Groups) are a Linux kernel feature used to group and manage processes.

systemd uses cgroups to:

- Track service processes.
- Limit CPU and memory usage.
- Manage child processes.
- Control resource consumption.

**Example:**

```ini
CPUQuota=20%
MemoryMax=100M
```

These limits apply to the service's cgroup.

### 6. systemd Watchdog

A watchdog detects applications that are running but have become unresponsive.

How it works:

1. The application sends periodic watchdog notifications.
2. systemd expects these notifications within the configured timeout.
3. If notifications stop, systemd considers the service unhealthy.
4. systemd can terminate and restart the service.

**Example configuration:**

```ini
Type=notify
WatchdogSec=30
Restart=on-failure
```

The application must explicitly send watchdog notifications. Normal log messages are not watchdog notifications.

---

## Part 2: Demonstration Questions

### 1. What is the difference between SIGTERM and SIGKILL?

- **SIGTERM (15):** Requests the process to terminate gracefully. The application can handle it and perform cleanup.
- **SIGKILL (9):** Forcefully terminates the process. The application cannot handle or ignore it.

### 2. Why doesn't nohup provide the same reliability as systemd?

`nohup` prevents a process from terminating due to SIGHUP.

It does not provide automatic restarts, boot startup, resource limits or centralized service management.

systemd provides these features.

### 3. What happens when a service crashes repeatedly?

If `Restart=on-failure` is configured, systemd attempts to restart the service.

Restart limits prevent continuous restart attempts. Once the configured limit is reached, systemd marks the service as failed.

### 4. What is the difference between restarting a process and restarting a service?

- **Process restart:** Terminates and starts an individual process.
- **Service restart:** systemd stops and starts the service according to its unit configuration.

A service can contain multiple processes, including child processes.

### 5. What happens to child processes when a systemd service is stopped?

By default, systemd uses:

```ini
KillMode=control-group
```

1. systemd sends SIGTERM to processes in the service's cgroup.
2. Processes get time to shut down gracefully.
3. If they don't exit within the timeout, systemd sends SIGKILL.

This ensures the service's remaining processes are terminated.

### 6. How would you ensure a Celery worker finishes its current task before shutting down?

Use graceful shutdown with SIGTERM.

1. Send SIGTERM to the Celery worker.
2. The worker stops accepting new tasks.
3. It finishes currently executing tasks.
4. It exits gracefully.

Configure an appropriate systemd stop timeout:

```ini
[Service]
KillSignal=SIGTERM
TimeoutStopSec=300
```

This gives the worker up to 300 seconds to shut down before systemd forcefully terminates remaining processes.

Celery task acknowledgement and worker shutdown settings should also be configured to handle interrupted tasks safely.

