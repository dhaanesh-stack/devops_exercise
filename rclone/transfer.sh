#!/usr/bin/env bash

set -uo pipefail

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="$LOG_DIR/transfer_${TIMESTAMP}.log"

usage() {
    echo "Usage:"
    echo "  $0 copy <source> <destination>"
    echo "  $0 sync <source> <destination> [--dry-run|--execute]"
    exit 2
}

if [[ $# -lt 3 || $# -gt 4 ]]; then
    usage
fi

OPERATION="$1"
SOURCE="$2"
DESTINATION="$3"
MODE="${4:-}"

if [[ "$OPERATION" != "copy" && "$OPERATION" != "sync" ]]; then
    usage
fi

if [[ "$OPERATION" == "copy" && -n "$MODE" ]]; then
    usage
fi

if [[ "$MODE" != "" && "$MODE" != "--dry-run" && "$MODE" != "--execute" ]]; then
    usage
fi

echo "[$(date)] Starting $OPERATION" | tee -a "$LOG_FILE"
echo "Source: $SOURCE" | tee -a "$LOG_FILE"
echo "Destination: $DESTINATION" | tee -a "$LOG_FILE"

RCLONE_ARGS=(
    --config /dev/null
    "$OPERATION"
    "$SOURCE"
    "$DESTINATION"
    --transfers 2
    --checkers 4
    --retries 3
    --low-level-retries 10
    --stats 5s
    --log-level INFO
)

if [[ "$OPERATION" == "sync" ]]; then
    if [[ "$MODE" == "--execute" ]]; then
        echo "WARNING: Executing actual synchronization." | tee -a "$LOG_FILE"
    else
        echo "Safe mode: synchronization dry-run enabled." | tee -a "$LOG_FILE"
        RCLONE_ARGS+=(--dry-run)
    fi
fi

rclone "${RCLONE_ARGS[@]}" 2>&1 | tee -a "$LOG_FILE"

STATUS=${PIPESTATUS[0]}

if [[ $STATUS -eq 0 ]]; then
    echo "[$(date)] Transfer completed successfully" | tee -a "$LOG_FILE"
else
    echo "[$(date)] Transfer failed with exit code $STATUS" | tee -a "$LOG_FILE"
fi

exit "$STATUS"
