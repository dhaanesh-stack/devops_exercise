# Cloud-Init Provisioning – Commands

## 1. Prerequisites

Install Multipass on the host machine.

Verify the installation:

```bash
multipass version
```

## 2. Validate the YAML File

Before launching the VM, validate the YAML syntax.

On macOS:

```bash
ruby -e "require 'yaml'; YAML.load_file('cloudinit.yaml'); puts 'YAML is valid'"
```

On Ubuntu:

```bash
python3 -c "import yaml; yaml.safe_load(open('cloudinit.yaml')); print('YAML is valid')"
```

## 3. Launch the Ubuntu VM

Launch an Ubuntu 24.04 VM with the Cloud-Init configuration:

```bash
multipass launch 24.04 \
  --name testpress-cloudinit \
  --cpus 2 \
  --memory 2G \
  --disk 10G \
  --cloud-init cloudinit.yaml
```

This creates a VM with:

- 2 virtual CPUs
- 2 GB RAM
- 10 GB disk
- Cloud-Init configuration applied during the first boot

## 4. Check VM Status

```bash
multipass info testpress-cloudinit
```

Check the Cloud-Init provisioning status:

```bash
multipass exec testpress-cloudinit -- cloud-init status --wait
```

Expected result:

```text
status: done
```

## 5. Verify Cloud-Init Configuration

Validate the configuration recognized by Cloud-Init:

```bash
multipass exec testpress-cloudinit -- sudo cloud-init schema --system
```

This checks the configuration schema. It does not guarantee that every provisioning command executed successfully, so verify the actual resources separately.

## 6. Verify Installed Packages

```bash
multipass exec testpress-cloudinit -- bash -c '
for p in docker.io git curl ffmpeg; do
  dpkg -s "$p" >/dev/null 2>&1 && echo "$p: INSTALLED" || echo "$p: MISSING"
done'
```

## 7. Verify User and Application Files

Check the application user:

```bash
multipass exec testpress-cloudinit -- id testpress
```

Check the application directory:

```bash
multipass exec testpress-cloudinit -- ls -l /opt/testpress/
```

Expected files:

```text
app.env
app.py
Dockerfile
```

## 8. Verify Docker Container

Check running containers:

```bash
multipass exec testpress-cloudinit -- sudo docker ps
```

Check container health:

```bash
multipass exec testpress-cloudinit -- sudo docker inspect \
  --format='{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' \
  testpress-app
```

Expected result after the health check has completed:

```text
running healthy
```

## 9. Test the Application

Run:

```bash
multipass exec testpress-cloudinit -- curl http://localhost:8080
```

Expected response:

```text
Hello from Testpress!
```

## 10. Verify systemd Service

Check whether the service is enabled at boot:

```bash
multipass exec testpress-cloudinit -- sudo systemctl is-enabled testpress.service
```

Expected:

```text
enabled
```

Check whether it is currently running:

```bash
multipass exec testpress-cloudinit -- sudo systemctl is-active testpress.service
```

Expected:

```text
active
```

View detailed service status:

```bash
multipass exec testpress-cloudinit -- sudo systemctl status testpress.service
```

## 11. Test Application Crash Recovery

Simulate an application container crash:

```bash
multipass exec testpress-cloudinit -- sudo docker kill testpress-app
```

Check the service status:

```bash
multipass exec testpress-cloudinit -- sudo systemctl status testpress.service
```

Check whether the application responds again:

```bash
multipass exec testpress-cloudinit -- curl http://localhost:8080
```

Expected response after systemd restarts the application:

```text
Hello from Testpress!
```

The service uses `Restart=always` and `RestartSec=5`, so systemd attempts to restart the service when its main process exits.

## 12. Test Recovery After VM Reboot

Restart the VM:

```bash
multipass restart testpress-cloudinit
```

Check VM status:

```bash
multipass info testpress-cloudinit
```

Wait for Cloud-Init status:

```bash
multipass exec testpress-cloudinit -- cloud-init status --wait
```

Check the systemd service:

```bash
multipass exec testpress-cloudinit -- sudo systemctl status testpress.service
```

Test the application:

```bash
multipass exec testpress-cloudinit -- curl http://localhost:8080
```

Expected response:

```text
Hello from Testpress!
```

The application starts because the systemd service is enabled at boot. Cloud-Init does not rebuild the Docker image or recreate the container during a normal reboot.

## 13. Useful Debugging Commands

View Cloud-Init logs:

```bash
multipass exec testpress-cloudinit -- sudo less /var/log/cloud-init.log
```

View Cloud-Init output:

```bash
multipass exec testpress-cloudinit -- sudo less /var/log/cloud-init-output.log
```

View systemd service logs:

```bash
multipass exec testpress-cloudinit -- sudo journalctl -u testpress.service
```

View Docker container logs:

```bash
multipass exec testpress-cloudinit -- sudo docker logs testpress-app
```

Check Cloud-Init status:

```bash
multipass exec testpress-cloudinit -- cloud-init status --long
```

## 14. Clean Up

When the testing is complete, delete the VM:

```bash
multipass delete testpress-cloudinit
multipass purge
```

**Note:** These commands permanently remove the VM and its data. Run them only when you no longer need the VM.

