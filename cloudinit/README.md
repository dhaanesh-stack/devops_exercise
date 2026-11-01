# Automated Server Provisioning with Cloud-Init

## Overview

This project demonstrates automated server provisioning using **Cloud-Init** on an Ubuntu 24.04 virtual machine.

The goal is to prepare a server automatically on its first boot without manually installing packages, creating users, configuring services, or deploying the application.

Cloud-Init handles the initial server configuration, while Docker runs a simple Python HTTP application.

## What This Project Does

On the first boot, Cloud-Init automatically:

- Updates the package index.
- Installs Docker, Git, cURL, and FFmpeg.
- Creates a dedicated `testpress` user and adds it to the Docker group.
- Creates the application files under `/opt/testpress/`.
- Builds a Docker image for the Python application.
- Creates and starts the application container.
- Configures a systemd service to manage the container.
- Enables the service to start automatically after a server reboot.

## Project Structure

```text
cloudinit/
├── README.md
├── cloudinit.yaml
├── commands.md
└── learnings.md
```

| File | Description |
|---|---|
| `cloudinit.yaml` | Cloud-Init configuration used to provision the server. |
| `commands.md` | Commands to validate, launch, inspect, and test the VM. |
| `learnings.md` | Explanations of Cloud-Init concepts and bonus topics. |

## Technologies Used

- Ubuntu 24.04
- Cloud-Init
- Multipass
- Docker
- Python
- systemd

## Application Details

The project deploys a simple Python HTTP server inside a Docker container.

- **Container name:** `testpress-app`
- **Application port:** `8080`
- **Endpoint:** `http://localhost:8080`
- **Expected response:** `Hello from Testpress!`

## Application Recovery

A systemd service manages the Docker container.

It provides two recovery mechanisms:

1. **Application crash recovery:** If the application process exits unexpectedly, systemd attempts to restart the container.
2. **Server reboot recovery:** The systemd service is enabled at boot, so the application starts automatically after the VM restarts.

## Documentation

Refer to the following files for implementation details:

- [Commands](commands.md) – Setup, provisioning, verification, and recovery tests.
- [Learnings](learnings.md) – Cloud-Init architecture, execution lifecycle, datasources, metadata, and other concepts.

