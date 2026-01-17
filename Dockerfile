FROM python:3.11-slim


ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .


EXPOSE 8000

# Run Daphne (for ASGI + Channels + WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "BRD_dev.asgi:application"]