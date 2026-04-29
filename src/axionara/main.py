import uvicorn
from fastapi import FastAPI

from axionara.app.api.routers import router as api_router
from axionara.app.utils.errors import add_exception_handler
from axionara.app.utils.events import add_middleware, lifespan
from axionara.common.config import settings
from axionara.common.logging import intercept_std_logging

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    version=settings.VERSION,
    lifespan=lifespan,
)
app.include_router(api_router, prefix=settings.API_PREFIX)
add_middleware(app=app)
add_exception_handler(app=app)


def run() -> None:
    config = uvicorn.Config(
        "axionara.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        access_log=True,
        # reload=True,
    )
    server = uvicorn.Server(config)
    intercept_std_logging()
    server.run()


if __name__ == "__main__":
    run()
