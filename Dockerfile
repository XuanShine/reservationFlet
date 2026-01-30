# Dockerfile for reservationFlet
FROM python:3.14-slim

# Set Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# 1. Install uv by copying it from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Set the working directory
WORKDIR /app

# 3. Enable bytecode compilation (faster startup)
ENV UV_COMPILE_BYTECODE=1

# 4. Copy configuration files first (to leverage Docker layer caching)
COPY pyproject.toml .

# 5. Install dependencies (no-install-project since source not copied yet)
RUN uv sync --no-install-project

# 6. Copy the rest of the application code
COPY . .

# 7. Final sync to install the project
RUN uv sync

# 8. Place the virtual environment in the PATH
ENV PATH="/app/.venv/bin:$PATH"

# 9. Set working directory to src folder for uvicorn
WORKDIR /app/src

# Expose port
EXPOSE 8303

# Run uvicorn from the src folder
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8303"]