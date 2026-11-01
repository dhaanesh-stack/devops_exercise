# Rclone – Command Reference

## 1. Install and Check Rclone

```bash
sudo apt update
sudo apt install rclone -y

rclone version
```

## 2. Run MinIO Using Docker

```bash
docker run -d \
  --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD='YOUR_STRONG_PASSWORD' \
  -v minio-data:/data \
  elestio/minio:latest \
  server /data --console-address ":9001"
```

MinIO endpoints:

```text
S3 API:  http://localhost:9000
Console: http://localhost:9001
```

Container management:

```bash
docker ps
docker logs minio
docker stop minio
docker start minio
docker rm -f minio
```

## 3. Configure Rclone Using Environment Variables

```bash
export RCLONE_CONFIG_MINIO_TYPE=s3
export RCLONE_CONFIG_MINIO_PROVIDER=Minio
export RCLONE_CONFIG_MINIO_ENDPOINT=http://localhost:9000
export RCLONE_CONFIG_MINIO_REGION=us-east-1
export RCLONE_CONFIG_MINIO_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export RCLONE_CONFIG_MINIO_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
export RCLONE_CONFIG_MINIO_FORCE_PATH_STYLE=true
```

List remote buckets:

```bash
rclone --config /dev/null lsd minio:
```

Create an exercise bucket:

```bash
rclone --config /dev/null mkdir minio:rclone-exercise
```

List bucket contents:

```bash
rclone --config /dev/null ls minio:rclone-exercise
```

## 4. Prepare Sample Files

```bash
mkdir -p source/documents
mkdir -p source/images
mkdir -p source/videos

echo "Rclone exercise" > source/documents/readme.txt
echo "Version 1" > source/documents/version.txt
echo "Sample image file" > source/images/image.txt
echo "Sample video file" > source/videos/video.txt
```

Create a 100 MiB test file:

```bash
dd if=/dev/urandom of=source/videos/large-file.bin bs=1M count=100
```

Create a 1 GiB test file:

```bash
fallocate -l 1G source/videos/large-1gb.bin
```

## 5. Copy Files to MinIO

```bash
rclone --config /dev/null copy ./source minio:rclone-exercise
```

Repeat the same copy:

```bash
rclone --config /dev/null copy ./source minio:rclone-exercise
```

Update an existing file:

```bash
echo "Version 2" > source/documents/version.txt
```

Add a new file:

```bash
echo "New document" > source/documents/new-file.txt
```

Copy the updated source:

```bash
rclone --config /dev/null copy ./source minio:rclone-exercise
```

## 6. Move Files

Create a temporary file:

```bash
echo "Move test" > source/move-test.txt
```

Move it to MinIO:

```bash
rclone --config /dev/null move source/move-test.txt minio:rclone-exercise
```

## 7. Synchronize Files

Create a destination-only file:

```bash
touch destination-only.txt

rclone --config /dev/null copyto \
  destination-only.txt \
  minio:rclone-exercise/destination-only.txt
```

Preview synchronization:

```bash
rclone --config /dev/null sync \
  ./source minio:rclone-exercise \
  --dry-run
```

Execute synchronization:

```bash
rclone --config /dev/null sync \
  ./source minio:rclone-exercise
```

Create another destination-only file:

```bash
echo "Extra file" > extra.txt

rclone --config /dev/null copyto \
  extra.txt \
  minio:rclone-exercise/extra.txt
```

Preview its deletion:

```bash
rclone --config /dev/null sync \
  ./source minio:rclone-exercise \
  --dry-run -v
```

Execute the synchronization:

```bash
rclone --config /dev/null sync \
  ./source minio:rclone-exercise
```

## 8. Check and Download Files

Compare local and remote files:

```bash
rclone --config /dev/null check \
  ./source minio:rclone-exercise
```

Download remote files:

```bash
rclone --config /dev/null copy \
  minio:rclone-exercise ./downloaded
```

Compare downloaded files with the source:

```bash
diff -r source downloaded
```

## 9. Bucket-to-Bucket Copy

Create another bucket:

```bash
rclone --config /dev/null mkdir minio:rclone-backup
```

Copy objects between buckets:

```bash
rclone --config /dev/null copy \
  minio:rclone-exercise minio:rclone-backup
```

## 10. Delete Individual Objects

```bash
rclone --config /dev/null deletefile \
  minio:rclone-backup/documents/readme.txt
```

## 11. Configuration Without a Persistent Config File

Set credentials for the S3 backend:

```bash
export RCLONE_S3_ACCESS_KEY_ID="YOUR_ACCESS_KEY"
export RCLONE_S3_SECRET_ACCESS_KEY="YOUR_SECRET_KEY"
```

List buckets using an S3 backend configured through command-line flags:

```bash
rclone --config /dev/null lsd :s3: \
  --s3-provider Minio \
  --s3-endpoint http://localhost:9000 \
  --s3-region us-east-1 \
  --s3-force-path-style
```

List objects:

```bash
rclone --config /dev/null ls :s3:rclone-exercise \
  --s3-provider Minio \
  --s3-endpoint http://localhost:9000 \
  --s3-region us-east-1 \
  --s3-force-path-style
```

## 12. Large File Transfer and Performance Options

Upload a large file with concurrency, bandwidth limit, and retry options:

```bash
rclone --config /dev/null copy source/videos minio:rclone-exercise/videos \
  --transfers 2 \
  --checkers 4 \
  --bwlimit 50M \
  --retries 3 \
  --low-level-retries 10 \
  --stats 5s \
  -P
```

Check transferred video files:

```bash
rclone --config /dev/null check \
  source/videos minio:rclone-exercise/videos
```

## 13. Interrupted Transfer and Restart

Interrupt a transfer after five seconds:

```bash
timeout -s INT 5s \
  rclone --config /dev/null copyto \
  source/videos/large-1gb.bin \
  minio:rclone-exercise/interrupted-test.bin \
  --bwlimit 50M -P
```

Retry the transfer:

```bash
rclone --config /dev/null copyto \
  source/videos/large-1gb.bin \
  minio:rclone-exercise/interrupted-test.bin \
  -P
```

## 14. Run the Automation Script

Make the script executable:

```bash
chmod +x transfer.sh
```

Copy:

```bash
./transfer.sh copy ./source minio:rclone-exercise
```

Sync in dry-run mode:

```bash
./transfer.sh sync ./source minio:rclone-exercise
```

Execute sync:

```bash
./transfer.sh sync ./source minio:rclone-exercise --execute
```

Sync with explicit dry-run:

```bash
./transfer.sh sync ./source minio:rclone-exercise --dry-run
```

## 15. Inspect Execution Logs

```bash
ls -lh logs/
```

Read a log:

```bash
cat logs/<log-file-name>
```

Read the last few lines:

```bash
tail -n 20 logs/<log-file-name>
```

