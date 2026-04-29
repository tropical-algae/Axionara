import asyncio
import functools
import inspect
from collections.abc import Callable
from typing import Any

from axionara.common.logging import logger


def exception_handling(func: Callable | None = None):
    """异常捕获装饰器，可用于函数/类方法，支持同步和异步函数

    Args:
        func (Callable | None, optional): _description_. Defaults to None.
        default_return (Any, optional): _description_. Defaults to None.
    """

    def decorator(inner_func: Callable):
        is_coroutine = asyncio.iscoroutinefunction(inner_func)

        @functools.wraps(inner_func)
        async def async_wrapper(*args, **kwargs):
            is_method = len(args) > 0 and inspect.isclass(type(args[0]))
            self = args[0] if is_method else None
            func_path = (
                f"{type(self).__name__ + '.' if self else ''}{inner_func.__name__}"
            )
            try:
                return await inner_func(*args, **kwargs)
            except Exception as err:
                logger.error(f"{func_path} 执行失败：{err}")
                raise

        @functools.wraps(inner_func)
        def sync_wrapper(*args, **kwargs):
            is_method = len(args) > 0 and inspect.isclass(type(args[0]))
            self = args[0] if is_method else None
            func_path = (
                f"{type(self).__name__ + '.' if self else ''}{inner_func.__name__}"
            )
            try:
                return inner_func(*args, **kwargs)
            except Exception as err:
                logger.error(f"{func_path} 执行失败：{err}")
                raise

        return async_wrapper if is_coroutine else sync_wrapper

    if callable(func):
        return decorator(func)
    return decorator
