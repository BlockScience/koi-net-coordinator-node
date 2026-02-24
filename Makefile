.PHONY: sync run start clean

sync:
	uv sync --refresh --reinstall

run:
	UV_ENV_FILE=.env uv run python -m koi_net_coordinator_node

start: sync run

clean:
	rm -rf .venv
	rm -rf __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov coverage.xml
	rm -rf dist build *.egg-info */*.egg-info */*/*.egg-info
	rm -rf .tox .nox
	rm -rf .ipynb_checkpoints */.ipynb_checkpoints */*/.ipynb_checkpoints
	rm -rf .DS_Store */.DS_Store */*/.DS_Store
	rm -rf .rid_cache
	rm -rf *.ndjson *.ndjson.*
