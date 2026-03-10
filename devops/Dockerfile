# Stage 1: export deps with poetry
FROM python:3.13-slim AS builder

RUN pip install poetry=='2.2.1' && poetry self add poetry-plugin-export

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry export --without dev -f requirements.txt -o requirements.txt


# Stage 2: final image
FROM python:3.13-slim AS final

RUN apt-get update && apt-get install -y --no-install-recommends nmap && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY pyproject.toml .

RUN pip install --no-cache-dir --no-deps -e .

EXPOSE 3000

CMD ["python", "-m", "nmap_service"]
