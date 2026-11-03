
import os
import time
import signal
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

running = True


def shutdown(signum, frame):
    global running
    logger.info("Received signal %s. Shutting down...", signum)
    running = False


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

worker_name = os.getenv("WORKER_NAME", "testpress-worker")
crash_after = int(os.getenv("CRASH_AFTER", "0"))

logger.info("%s started. PID: %s", worker_name, os.getpid())

count = 0

while running:
    count += 1
    logger.info("Heartbeat #%s | PID: %s", count, os.getpid())

    if crash_after and count >= crash_after:
        logger.error("Simulating application crash!")
        sys.exit(1)

    time.sleep(5)

logger.info("%s stopped gracefully.", worker_name)

