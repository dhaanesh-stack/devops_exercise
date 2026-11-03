import os
import time




print(f"Demo process started. PID: {os.getpid()}", flush=True)

while True:
    print("Heartbeat...", flush=True)
    time.sleep(5)

print("Process stopped gracefully.", flush=True)
