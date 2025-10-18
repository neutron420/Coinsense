FROM python:3.12-slim-bookworm as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY ./app ./app
COPY ./trained_models ./models
RUN mkdir -p logs data

RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app /app
USER app

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]