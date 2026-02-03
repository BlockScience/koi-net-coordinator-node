import os
# from koi_net_shared.logging import setup_logging

# Setup logging for this service in repo-level ./logs
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
logs_dir = os.path.join(repo_root, "logs")
log_level = os.getenv("LOG_LEVEL", "INFO")
# setup_logging("coordinator", log_level, log_dir=logs_dir)
