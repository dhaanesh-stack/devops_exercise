
import os
import time
import signal
import logging
import sys

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# Application configuration
worker_name = os.getenv("WORKER_NAME", "testpress-worker")
heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "5"))
crash_after = int(os.getenv("CRASH_AFTER", "0"))
allocate_mb = int(os.getenv("ALLOCATE_MB", "0"))

# Graceful shutdown flag
running = True


def shutdown(signum, frame):
    global running
    logger.info("Received signal %s. Shutting down...", signum)
    running = False


# Handle termination signals
signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)


# Optional memory allocation test
memory = None

if allocate_mb > 0:
    logger.info("Allocating %s MB of memory", allocate_mb)

    memory = bytearray(allocate_mb * 1024 * 1024)

    # Touch each memory page to force physical allocation
    for i in range(0, len(memory), 4096):
        memory[i] = 1

    logger.info("Memory allocation completed")


# Start worker
logger.info("%s started. PID: %s", worker_name, os.getpid())

count = 0

while running:
    count += 1

    logger.info("Heartbeat #%s | PID: %s", count, os.getpid())

    # Simulate application crash
    if crash_after > 0 and count >= crash_after:
        logger.error("Simulating application crash!")
        sys.exit(1)

    time.sleep(heartbeat_interval)

logger.info("%s stopped gracefully.", worker_name)

