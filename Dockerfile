FROM python:3.11.7

ARG WORKSPACE=/workspace

WORKDIR ${WORKSPACE}

COPY uv.lock pyproject.toml .env ./

RUN pip install --upgrade pip && \
    pip install uv

RUN uv sync --frozen --no-dev --system

COPY ./src ./src

ENV PYTHONPATH ${WORKSPACE}

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "axionara.main"]
