from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import ExpiredSignatureError, exceptions, jwt
from passlib.hash import pbkdf2_sha256
from pydantic import ValidationError

from axionara.app.utils.constant import CONSTANT
from axionara.common.config import settings
from axionara.common.logging import logger
from axionara.core.model.user import TokenPayload


def get_access_token(
    data: TokenPayload, expires_delta: timedelta = timedelta(minutes=30)
) -> str:
    data.exp = datetime.now(timezone.utc) + expires_delta
    encoded_jwt = jwt.encode(
        data.to_dict(), settings.ACCESS_TOKEN_SECRET_KEY, algorithm="HS256"
    )
    return encoded_jwt


def verift_access_token(token: str | None, headers: dict | None = None):
    headers = headers or {}
    if token is None:
        raise HTTPException(headers=headers, **CONSTANT.RESP_TOKEN_NOT_EXISTED)
    try:
        decoded_token = jwt.decode(
            token, settings.ACCESS_TOKEN_SECRET_KEY, algorithms="HS256"
        )
        payload = TokenPayload.model_validate(decoded_token)
        return payload
    except (exceptions.JWTError, ValidationError) as err:
        logger.error(f"Security verification failed: {err}")
        raise HTTPException(headers=headers, **CONSTANT.RESP_TOKEN_VERIFY_ERR) from err
    except ExpiredSignatureError as err:
        logger.error(f"Token expired: {err}")
        raise HTTPException(headers=headers, **CONSTANT.RESP_TOKEN_EXPIRED) from err


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pbkdf2_sha256.hash(password)
