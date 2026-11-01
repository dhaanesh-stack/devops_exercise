# Rclone – Results and Observations

## 1. Environment Setup

* Installed rclone on WSL2 Ubuntu.
* Ran MinIO using Docker as a local S3-compatible storage service.
* Used local directories and MinIO buckets to simulate different storage locations.

## 2. File Operations

Explored `copy`, `move`, and `sync`.

* **Copy:** Transfers new and modified files. Skips unchanged files and preserves destination-only files.
* **Move:** Transfers files and removes successfully transferred files from the source.
* **Sync:** Makes the destination match the source, including deleting destination-only files.

**Key learning:** Always use `--dry-run` before executing `sync` to avoid accidental data deletion.

## 3. S3 Storage Operations

Successfully performed the following operations using MinIO:

* Created buckets and listed objects.
* Uploaded and downloaded files.
* Copied objects between buckets.
* Deleted individual objects.
* Compared local and remote files.

### Server-Side Copy

Copied objects between two buckets on the same MinIO server.

Rclone reported six server-side copies. The objects were copied within MinIO without downloading them to the local machine.

## 4. Configuration-Free Execution

Explored two ways to configure rclone without an `rclone.conf` file:

* **Command-line flags:** Passed S3 provider, endpoint, and region directly.
* **Environment variables:** Configured a named remote using `RCLONE_CONFIG_*` variables.

Both approaches worked with `--config /dev/null`.

**Production recommendation:** Use environment variables injected securely through a secrets manager. This avoids hardcoding credentials in scripts or source code.

## 5. Large File Transfer

Uploaded a 1 GiB test file with these settings:

* Transfers: 2
* Checkers: 4
* Bandwidth limit: 50 MiB/s
* Retries: 3
* Low-level retries: 10

**Observed result:**

* File size: 1 GiB
* Transfer time: Approximately 34 seconds
* Average speed: 36.6 MiB/s

## 6. File Integrity

Used `rclone check` to compare local and remote files.

**Result:** 0 differences found, with 6 matching files.

Also downloaded the remote files and compared them with the original directory. No differences were found.

## 7. Bash Automation

Created `transfer.sh` to automate file transfers.

The script supports:

* Copy and sync operations.
* Source and destination arguments.
* Dry-run by default for sync.
* Explicit `--execute` for actual synchronization.
* Execution logs.
* Error handling and appropriate exit codes.

## Conclusion

This exercise helped me understand file transfers, synchronization, S3-compatible storage, configuration-free execution, large-file transfers, integrity checks, and Bash automation using rclone.

