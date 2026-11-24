FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN uv pip install --system -r pyproject.toml --no-cache

COPY backend/ ./backend/
COPY scripts/ ./scripts/

RUN mkdir -p /app/log && chmod +x scripts/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
