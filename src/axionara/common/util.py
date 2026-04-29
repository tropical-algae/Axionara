import importlib
import pkgutil
import secrets
import string
from collections.abc import Callable
from types import ModuleType
from typing import Any

import yaml

from axionara.core.db.session import local_session

TOKEN_SEQUENCE = string.ascii_uppercase + string.digits


async def async_db_wrapper(func: Callable, *args, **kwargs) -> Any:
    try:
        with local_session() as db:
            return await func(*args, db=db, **kwargs)
    except Exception:
        return None


def load_yaml(yaml_path: str) -> dict:
    try:
        with open(yaml_path) as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as err:
        raise Exception(
            f"Error occurred when read YAML from path '{yaml_path}'. Error: {err}"
        ) from err


def import_all_modules_from_package(package: ModuleType) -> None:
    """Import all models from pkg

    Args:
        package (str): pkg name
    """
    for _, modname, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        importlib.import_module(modname)


def generate_random_token(prefix: str = "", length: int = 32) -> str:
    """Generate random token

    Args:
        length (int, optional): the length of token. Defaults to 32.

    Returns:
        str: random token
    """
    key_length = length - len(prefix)
    assert key_length > 0, "The length of the token must greater than the prefix."
    return prefix + "".join(secrets.choice(TOKEN_SEQUENCE) for _ in range(key_length))
