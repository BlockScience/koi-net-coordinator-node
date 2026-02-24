# koi-net-coordinator-node

## Overview
Coordinator node for local KOI-net bootstrap and network graph state.

## Prerequisites
- Python 3.10+
- `uv`

## Environment
Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Required:
- `PRIV_KEY_PASSWORD`: encrypts/decrypts local private key material.

## Quick Start
```bash
uv sync --refresh --reinstall
set -a; source .env; set +a
uv run python -m koi_net_coordinator_node
```

Expected startup signal: server binds on `127.0.0.1:8080` and begins processing.

## First Contact / Networking
- Coordinator is the bootstrap root.
- `first_contact` remains empty by default in this node.
- Other nodes default to coordinator URL: `http://127.0.0.1:8080/koi-net`.

## Config Generation
- `config.yaml` is generated automatically on first run.
- Use `config.yaml.example` as a reference template; do not commit local `config.yaml`.

## Troubleshooting
- `PRIV_KEY_PASSWORD not set`: load `.env` into shell before running.
- PEM load errors: remove local key file (`priv_key.pem` or `private_key.pem`) and restart.
