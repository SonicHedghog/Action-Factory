#!/usr/bin/env bash
echo "POSTGRES_PASSWORD=$(openssl rand -base64 16)" > .devcontainer/.env