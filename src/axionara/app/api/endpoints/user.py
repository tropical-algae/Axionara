import json
from datetime import datetime, timedelta
from typing import Any

import pytz
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from sqlmodel.ext.asyncio.session import AsyncSession

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.utils import security
from axionara.app.utils.constant import CONSTANT
from axionara.common.config import settings
from axionara.core.db.crud import insert_user, select_user_by_full_name, verify_password
from axionara.core.db.crud.crud_user import select_user_by_email
from axionara.core.db.models import UserAccount
from axionara.core.model.user import ScopeType, Token, TokenPayload, UserBasicInfo

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await select_user_by_full_name(db, full_name=form_data.username)
    if not user:
        raise HTTPException(**CONSTANT.RESP_USER_NOT_EXISTS)

    if not verify_password(form_data.password, str(user.password)):
        raise HTTPException(**CONSTANT.RESP_USER_INCORRECT_PASSWD)

    scopes = json.loads(str(user.scopes))
    form_data.scopes = scopes
    return Token(
        **CONSTANT.RESP_SUCCESS,
        access_token=security.get_access_token(
            data=TokenPayload(userid=user.id, username=user.full_name, scopes=scopes),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        token_type="bearer",
        user_id=user.id,
        scopes=scopes,
        timestamp=pytz.timezone("Asia/Shanghai")
        .localize(datetime.now())
        .strftime("%Y-%m-%d %H:%M:%S"),
    )


@router.post("/test-token", response_model=UserAccount)
async def token_test(
    current_user: UserAccount = Security(get_current_user, scopes=[ScopeType.ADMIN]),
) -> Any:
    """
    Test access token
    """
    del current_user.password
    return current_user


@router.post("/register", response_model=UserAccount)
async def user_register(
    user: UserBasicInfo,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register new user (This interface has not undergone login verification)
    """
    existed_user = await select_user_by_full_name(db, full_name=user.full_name)
    if existed_user is not None:
        raise HTTPException(**CONSTANT.RESP_USER_EXISTS)

    existed_user = await select_user_by_email(db, email=user.email)
    if existed_user is not None:
        raise HTTPException(**CONSTANT.RESP_USER_EMAIL_EXISTS)

    try:
        new_user = user.build_user()
        new_user = await insert_user(db=db, user=new_user)
        del new_user.password
        return new_user
    except Exception as err:
        raise HTTPException(**CONSTANT.RESP_SERVER_ERROR) from err
