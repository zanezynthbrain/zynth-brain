FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so Docker caches this layer between deploys
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY backend/ .

# Bot + embedded APScheduler run in one process
CMD ["python", "telegram_bot.py"]
