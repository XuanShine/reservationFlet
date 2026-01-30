# Dockerfile for reservationFlet with Nginx + SSL
FROM python:3.14-slim

# Set Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# 1. Install uv, nginx, and openssl
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    nginx \
    openssl \
    supervisor \
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

# 9. Generate self-signed SSL certificate
RUN mkdir -p /etc/nginx/certs && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/certs/server.key \
    -out /etc/nginx/certs/server.crt \
    -subj "/CN=localhost" \
    -addext "subjectAltName=IP:10.0.0.2,IP:127.0.0.1,DNS:localhost"

# 10. Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# 11. Create supervisor config to run both nginx and uvicorn with logs to stdout
RUN echo '[supervisord]\n\
nodaemon=true\n\
logfile=/dev/null\n\
logfile_maxbytes=0\n\
\n\
[program:nginx]\n\
command=/usr/sbin/nginx -g "daemon off;"\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
\n\
[program:uvicorn]\n\
command=/app/.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000 --ws auto --log-level info\n\
directory=/app/src\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/dev/stdout\n\
stdout_logfile_maxbytes=0\n\
stderr_logfile=/dev/stderr\n\
stderr_logfile_maxbytes=0\n\
' > /etc/supervisor/conf.d/supervisord.conf

# Expose ports (443 for HTTPS)
EXPOSE 443

# Run supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
