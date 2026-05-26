from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from axionara.common.logging import logger
from axionara.core.db.session import init_db_models

origins = ["*"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting service...")
    _ = app
    await init_db_models()

    yield
    logger.info("Shut down and clear cache...")


def add_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
