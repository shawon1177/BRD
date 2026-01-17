# Use Python slim image
FROM python:3.11-slim

# Prevent buffering
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose Daphne port
EXPOSE 8000

# Run Daphne (for Channels/ASGI)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "BRD_dev.asgi:application"]
