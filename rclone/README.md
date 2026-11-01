# Rclone – File Transfer and Backup

## Overview

This exercise explores **rclone**, a command-line tool used to manage and transfer files between local storage and cloud/object storage.

For this exercise, I used **MinIO** as an S3-compatible object storage server and rclone to perform file transfers, synchronization, backups, and verification.

## What I Did

* Installed and explored rclone commands.
* Connected rclone to a local MinIO server.
* Created a bucket for the exercise.
* Uploaded local directories and files to MinIO.
* Tested repeated uploads and incremental changes.
* Explored the difference between `copy`, `move`, and `sync`.
* Used dry-run mode to preview synchronization changes.
* Downloaded files from MinIO to local storage.
* Copied objects between two buckets.
* Deleted individual objects.
* Verified file integrity using `rclone check`.
* Tested large-file transfers with retry, concurrency, and bandwidth-limit options.
* Explored environment-variable-based configuration without a persistent rclone configuration file.
* Created a Bash script to automate transfers and record logs.

## Directory Structure

```text
rclone/
├── README.md
├── .gitignore
├── transfer.sh
└── source/
    ├── documents/
    │   ├── new-file.txt
    │   ├── readme.txt
    │   └── version.txt
    ├── images/
    │   └── image.txt
    └── videos/
        └── video.txt
```

Large files used during testing were temporary and are not included in this repository.

## Requirements

* Linux or WSL2 Ubuntu
* rclone
* Docker
* MinIO server

Check the installed versions:

```bash
rclone version
docker --version
```

## Configure MinIO

Start or use an existing MinIO server. The default S3 API endpoint used in this exercise is:

```text
http://localhost:9000
```

Configure rclone using environment variables:

```bash
export RCLONE_CONFIG_MINIO_TYPE=s3
export RCLONE_CONFIG_MINIO_PROVIDER=Minio
export RCLONE_CONFIG_MINIO_ENDPOINT=http://localhost:9000
export RCLONE_CONFIG_MINIO_REGION=us-east-1
export RCLONE_CONFIG_MINIO_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export RCLONE_CONFIG_MINIO_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export RCLONE_CONFIG_MINIO_FORCE_PATH_STYLE=true
```

Replace the credentials with your own MinIO credentials.

Verify the connection:

```bash
rclone --config /dev/null lsd minio:
```

Create a bucket:

```bash
rclone --config /dev/null mkdir minio:rclone-exercise
```

**Note:** `--config /dev/null` prevents rclone from using a persistent configuration file. The remote configuration is supplied through environment variables.

## Basic Rclone Commands

Upload local files:

```bash
rclone copy ./source minio:rclone-exercise
```

List remote files:

```bash
rclone ls minio:rclone-exercise
```

Download files:

```bash
rclone copy minio:rclone-exercise ./downloaded
```

Synchronize directories:

```bash
rclone sync ./source minio:rclone-exercise
```

Preview synchronization without making changes:

```bash
rclone sync ./source minio:rclone-exercise --dry-run
```

Verify files:

```bash
rclone check ./source minio:rclone-exercise
```

## Using the Transfer Script

The `transfer.sh` script automates rclone operations and stores execution logs in a `logs/` directory.

### Copy

```bash
./transfer.sh copy ./source minio:rclone-exercise
```

### Sync – Dry Run (Default)

```bash
./transfer.sh sync ./source minio:rclone-exercise
```

The script uses dry-run mode by default for synchronization. It previews changes without modifying the destination.

### Sync – Actual Execution

```bash
./transfer.sh sync ./source minio:rclone-exercise --execute
```

### Logs

Execution logs are stored in:

```text
logs/
```

## Important Difference: Copy vs Sync

| Command       | Behaviour                                                                          |
| ------------- | ---------------------------------------------------------------------------------- |
| `rclone copy` | Copies new and changed files without deleting destination-only files.              |
| `rclone move` | Moves files and removes successfully transferred source files.                     |
| `rclone sync` | Makes the destination match the source, including deleting destination-only files. |

**Be careful with `sync`:** it can delete files from the destination. Always use `--dry-run` before executing it.

## Results

The following operations were tested successfully:

* Uploaded a directory containing multiple files to MinIO.
* Repeated the upload and confirmed unchanged files were skipped.
* Modified existing files and added new files, then verified incremental transfer.
* Tested synchronization and destination-side deletion.
* Downloaded remote files and compared them with the source.
* Verified matching files using `rclone check`.
* Copied objects between MinIO buckets using server-side copy.
* Tested individual object deletion.
* Transferred a 1 GiB test file with a configured bandwidth limit and retry options.
* Tested the Bash automation script with copy, sync dry-run, and actual sync operations.

A detailed record of the experiments and observations can be maintained in `results.md`.

## Key Learnings

* Difference between copy, move, and sync operations.
* How rclone connects to S3-compatible storage.
* How environment variables can provide remote configuration.
* How dry-run helps prevent accidental data deletion.
* How to verify transfers using rclone check.
* How to automate transfers using Bash.
* How to configure retries, concurrency, and bandwidth limits.

