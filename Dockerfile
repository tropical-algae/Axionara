FROM node:20 AS frontend-builder

WORKDIR /app/web

ARG VITE_WEB_PORT=8000
ARG VITE_API_BASE_URL=/

ENV VITE_WEB_PORT=${VITE_WEB_PORT} \
    VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY web/package.json web/package-lock.json ./
RUN npm install

COPY web/ .
RUN npm run build


FROM python:3.11-slim

LABEL org.opencontainers.image.authors="tropical-algae tropicalalgae@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y nginx curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock poe_tasks.toml README.md ./

RUN pip install --upgrade pip && \
    pip install uv==0.9.7 && \
    uv sync --frozen

COPY ./src ./src
COPY prompts ./prompts

COPY --from=frontend-builder /app/web/dist /app/web

COPY nginx.conf /etc/nginx/nginx.conf
COPY scripts/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh && \
    mkdir -p /cache /app/cache

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
