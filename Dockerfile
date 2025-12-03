############################
# Stage 1: Builder
############################
FROM python:3.11-slim AS builder

# Workdir
WORKDIR /app

# Don’t generate .pyc and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build deps (if needed for cryptography)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install into /install (for caching)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt


############################
# Stage 2: Runtime
############################
FROM python:3.11-slim AS runtime

# ---- Timezone to UTC ----
ENV TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Install system dependencies: cron + tzdata
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure timezone to UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . /app

# Create volume mount points and set permissions
RUN mkdir -p /data /cron && \
    chmod 755 /data /cron

# Copy cron configuration from app to system cron.d
# Expecting a file at /app/cron/2fa-cron
RUN cp /app/cron/2fa-cron /etc/cron.d/2fa-cron && \
    chmod 0644 /etc/cron.d/2fa-cron && \
    crontab /etc/cron.d/2fa-cron && \
    touch /var/log/cron.log

# Declare volumes
VOLUME ["/data", "/cron"]

# Expose API port
EXPOSE 8080

# Start cron service and API server
CMD ["/bin/sh", "-c", "cron && uvicorn main:app --host 0.0.0.0 --port 8080"]
