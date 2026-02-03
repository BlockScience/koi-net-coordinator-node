# ==============================================================================
# Templated Makefile for a KOI-net Node
#
# To adapt for a new node, change the variables in the "Configuration" section.
# This Makefile assumes it is located inside the node's root directory
# (e.g., koi-net-coordinator-node/Makefile).
# ==============================================================================

# --- Configuration ---
NODE_NAME       := coordinator
MODULE_NAME     := koi_net_coordinator_node
PORT            := 8080
# --- End Configuration ---

# --- Variables (usually do not need to be changed) ---
ROOT_DIR        := ..
LOGS_DIR        := $(ROOT_DIR)/logs
LOG_FILE        := $(LOGS_DIR)/$(NODE_NAME).log
ENV_FILE        := $(ROOT_DIR)/.env
PYTHON_CMD      := uv run --env-file $(ENV_FILE) python -m $(MODULE_NAME)

.PHONY: all install setup-venv build-shared start stop status dev test logs clean health-check

all: install

# Installs the node's dependencies and builds shared libraries
install: setup-venv build-shared
	@echo "Installing $(NODE_NAME) node..."
	@uv pip install -e ".[dev]"

# Sets up the local virtual environment
setup-venv:
	@if [ ! -d ".venv" ]; then \
		echo "Setting up virtual environment for $(NODE_NAME)..."; \
		uv venv --python=python3.12; \
	else \
		echo "Virtual environment for $(NODE_NAME) already exists."; \
	fi

# Builds the shared koi-net library required by this node
build-shared:
	@echo "Building shared koi-net package..."
	@cd $(ROOT_DIR)/koi-net && uv build
	@cd $(ROOT_DIR)/koi-net-shared && uv build

# Starts the node in the background
start:
	@echo "Starting $(NODE_NAME) node in background..."
	@mkdir -p $(LOGS_DIR)
	@$(PYTHON_CMD) 
# 	> $(LOG_FILE) 2>&1 &
	@echo "$(NODE_NAME) started. Log file: $(LOG_FILE)"

# Stops the node by killing the process on its port
stop:
	@echo "Stopping $(NODE_NAME) node..."
	@pid=$$(lsof -ti :$(PORT) 2>/dev/null); \
	if [ -n "$$pid" ]; then \
		echo "  Killing process $$pid on port $(PORT)"; \
		kill -9 $$pid 2>/dev/null || true; \
	else \
		echo "  No process found on port $(PORT)."; \
	fi

# Checks if the node process is running
status:
	@echo "Checking status for $(NODE_NAME) node:"
	@pid=$$(lsof -ti :$(PORT) 2>/dev/null); \
	if [ -n "$$pid" ]; then \
		echo "  $(NODE_NAME): RUNNING (PID: $$pid, Port: $(PORT))"; \
	else \
		echo "  $(NODE_NAME): STOPPED"; \
	fi

# Runs the node in the foreground for development
dev:
	@echo "Running $(NODE_NAME) node in development mode (foreground)..."
	@$(PYTHON_CMD)

# Runs the test suite for this node
test:
	@echo "Running $(NODE_NAME) tests..."
	@uv run --env-file $(ENV_FILE) pytest tests/ -v --tb=short

# Tails the log file for this node
logs:
	@echo "Following logs for $(NODE_NAME) (Ctrl+C to stop)..."
	@tail -f $(LOG_FILE)

# Cleans up generated files specific to this node
clean: stop clean-cache
	@echo "Cleaning up $(NODE_NAME) node artifacts..."
	@find . -type d -name "*[cC][aA][cC][hH][eE]*" -exec rm -rf {} + 2>/dev/null || true
	@rm -f event_queues.json 2>/dev/null || true
	@rm -rf .venv 2>/dev/null || true
	@echo "Cleanup for $(NODE_NAME) complete."

.PHONY: clean-all
clean-all: clean
	@echo "Removing keys and config.yaml (RID will change on next run)..."
	@rm -f *.pem
	@rm -f config.yaml

# Cleans only cache JSON files
clean-cache:
	@echo "Cleaning cache JSON files..."
	@find cache -type f -name "*.json" -exec rm -f {} + 2>/dev/null || true

# Performs a health check on the node's API
health-check:
	@echo "Checking $(NODE_NAME) node health..."
	@curl -s -f http://127.0.0.1:$(PORT)/koi-net/health >/dev/null && echo "  $(NODE_NAME): HEALTHY" || echo "  $(NODE_NAME): UNHEALTHY or STOPPED"
