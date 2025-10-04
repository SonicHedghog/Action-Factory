FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev git curl && \
    rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Upgrade pip
RUN pip install --upgrade pip