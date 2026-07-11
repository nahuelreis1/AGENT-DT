# Stage: builder — install dependencies (uvicorn[standard] needs gcc for C extensions)
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage: runtime — minimal image, non-root, healthcheck
FROM python:3.11-slim AS runtime
WORKDIR /app
RUN useradd -m -u 1001 appuser
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser backend/ ./backend/
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
