FROM python:3.12.1-slim-bullseye AS builder

COPY uv.lock pyproject.toml ./

RUN python -m pip install uv && \
    uv export -o requirements.prod.txt --no-hashes && \
    uv export --dev -o requirements.dev.txt --no-hashes

FROM python:3.12.1-slim-bullseye AS dev

WORKDIR /app

ENV PYTHONUNNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY --from=builder requirements.dev.txt /app

RUN apt update -y && \
    apt install -y python3-dev gcc musl-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.dev.txt && \
    apt-get clean

COPY ./src ./src

EXPOSE 8000