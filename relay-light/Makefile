PYTHON   := python3
PID_FILE := /tmp/relay-light.pid
LOG_FILE := /tmp/relay-light.log
SERVICE  := relay-light

.PHONY: install run start stop restart status logs diag power clean \
        service-install service-uninstall service-start service-stop \
        service-restart service-status service-logs

# ── Python ────────────────────────────────────────────────────────────────────

install:
	pip install -r requirements.txt

run:
	$(PYTHON) main.py

# Run in background, log to file
start:
	$(PYTHON) main.py >> $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE)
	@echo "Started (PID $$(cat $(PID_FILE))) — logs at $(LOG_FILE)"

stop:
	@if [ -f $(PID_FILE) ]; then \
		kill $$(cat $(PID_FILE)) && rm $(PID_FILE) && echo "Stopped"; \
	else \
		echo "Not running (no PID file)"; \
	fi

restart: stop start

status:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Running (PID $$(cat $(PID_FILE)))"; \
	else \
		echo "Not running"; \
	fi

logs:
	tail -f $(LOG_FILE)

diag:
	$(PYTHON) diag.py

power:
	$(PYTHON) power.py

clean:
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f $(PID_FILE) $(LOG_FILE)

# ── systemd ───────────────────────────────────────────────────────────────────

service-install:
	bash scripts/install-service.sh

service-uninstall:
	sudo systemctl stop $(SERVICE) || true
	sudo systemctl disable $(SERVICE) || true
	sudo rm -f /etc/systemd/system/$(SERVICE).service
	sudo systemctl daemon-reload
	@echo "Service removed."

service-start:
	sudo systemctl start $(SERVICE)

service-stop:
	sudo systemctl stop $(SERVICE)

service-restart:
	sudo systemctl restart $(SERVICE)

service-status:
	sudo systemctl status $(SERVICE)

service-logs:
	sudo journalctl -u $(SERVICE) -f
