# Use official Python slim image
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for Postgres, building packages, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose port 8000 for Django/Daphne
EXPOSE 8000

# Set default command to run Daphne ASGI server
 CMD ["sh", "-c", "gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 & daphne -b 0.0.0.0 -p 8001 BRD_dev.asgi:application"]
