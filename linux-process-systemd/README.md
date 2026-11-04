# Linux Process Management & systemd

A hands-on DevOps exercise to understand Linux process management and systemd using a Python background worker.

The project covers process signals, background execution, service management, automatic restarts, logging, resource limits and failure handling.

## Project Structure

- `app.py` – Python background worker.
- `demo_process.py` – Process and signal experiments.
- `testpress-worker.service` – systemd service configuration.
- `worker.env` – Application environment variables.
- `experiments.md` – Experiment results and explanations.
- `bonus.md` – Bonus concepts and demonstration questions.
- `evidence/` – Screenshots of completed experiments.

## Setup

```bash
sudo cp app.py worker.env /opt/testpress-worker/
sudo cp testpress-worker.service /etc/systemd/system/

sudo chown -R testpress-worker:testpress-worker /opt/testpress-worker
sudo chmod 750 /opt/testpress-worker
sudo chmod 640 /opt/testpress-worker/app.py
sudo chmod 600 /opt/testpress-worker/worker.env

sudo systemctl daemon-reload
sudo systemctl enable testpress-worker
```
