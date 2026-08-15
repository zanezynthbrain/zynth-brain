FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so Docker caches this layer between deploys
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source
COPY backend/ .

# Founder-readable knowledge and capability sources consumed by the Second Brain.
# The backend is intentionally flattened into /app; these retain their versioned
# repository-relative paths so the map can expose truthful source references.
COPY .claude/ ./.claude/
COPY docs/ ./docs/
COPY research/ ./research/

# Obsidian-synced vault (repo root) → readable by the knowledge loader
COPY vault/ ./vault/

# Bot + embedded APScheduler run in one process
CMD ["python", "telegram_bot.py"]
