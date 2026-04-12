PYTHON  := python3
PID_FILE := /tmp/relay-light.pid

.PHONY: install run stop restart diag status clean

install:
	pip install -r requirements.txt

run:
	$(PYTHON) main.py

# Run in background and save PID
start:
	$(PYTHON) main.py & echo $$! > $(PID_FILE)
	@echo "Started (PID $$(cat $(PID_FILE)))"

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

diag:
	$(PYTHON) diag.py

clean:
	find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f $(PID_FILE)
