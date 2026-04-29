import sys
from pathlib import Path
from types import FrameType
from typing import cast

from loguru import logger

from axionara.common.config import settings

ORIGIN_LOGGER_NAMES = ["uvicorn.asgi", "uvicorn.access", "uvicorn"]
ORIGIN_LOGGER_NAMES += (
    ["sqlalchemy.engine", "sqlalchemy.engine.Engine"] if settings.DEBUG else []
)


log_filepath = Path(settings.LOG_ROOT) / f"{settings.PROJECT_NAME}.log"
log_filepath.parent.mkdir(parents=True, exist_ok=True)

logger.remove()
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    colorize=True,
    format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "
    "{process.name} | "
    "{thread.name} | "
    "<cyan>{module}</cyan>.<cyan>{function}</cyan>"
    ":<cyan>{line}</cyan> | "
    "<level>{level}</level>: "
    "<level>{message}</level>",
)

if settings.LOG_CONSOLE_OUTPUT:
    logger.add(
        log_filepath,
        format="{time:YYYYMMDD HH:mm:ss} - "
        "{process.name} | "
        "{thread.name} | "
        "{module}.{function}:{line} - {level} -{message}",
        encoding=settings.LOG_FILE_ENCODING,
        retention="12 week",
        rotation="1 week",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )


def intercept_std_logging():
    import logging

    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = str(record.levelno)
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = cast(FrameType, frame.f_back)
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level,
                record.getMessage(),
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=settings.LOG_LEVEL)
    logging.getLogger().handlers = [InterceptHandler()]
    for logger_name in ORIGIN_LOGGER_NAMES:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.setLevel(settings.LOG_LEVEL)
