import json
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from axionara.app.api.deps import get_current_user, get_db
from axionara.app.utils import security
from axionara.app.utils.constant import CONSTANT
from axionara.common.config import settings
from axionara.core.db.crud import (
    insert_user,
    select_user_by_email,
    select_user_by_login_name,
    select_user_by_username,
)
from axionara.core.db.models import UserAccount
from axionara.core.model.user import (
    ScopeType,
    Token,
    TokenPayload,
    UserBasicInfo,
    UserProfile,
)

router = APIRouter()


@router.post("/register", response_model=UserProfile)
async def user_register(
    user: UserBasicInfo,
    db: Session = Depends(get_db),
) -> Any:
    existed_user = select_user_by_username(db=db, username=user.username)
    if existed_user is not None:
        raise HTTPException(**CONSTANT.RESP_USER_EXISTS)

    existed_user = select_user_by_email(db=db, email=user.email)
    if existed_user is not None:
        raise HTTPException(**CONSTANT.RESP_USER_EMAIL_EXISTS)

    new_user = insert_user(db=db, user=user.build_user())
    return UserProfile.model_validate(new_user)


@router.post("/access-token", response_model=Token)
async def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = select_user_by_login_name(db=db, login_name=form_data.username)
    if not user or not security.verify_password(form_data.password, str(user.password)):
        raise HTTPException(**CONSTANT.RESP_USER_INCORRECT_PASSWD)

    scopes = json.loads(str(user.scopes or "[]"))
    payload_scopes = [ScopeType(scope) for scope in scopes]
    return Token(
        access_token=security.get_access_token(
            data=TokenPayload(
                userid=user.id,
                username=user.username,
                scopes=payload_scopes,
            ),
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        token_type="bearer",
        user_id=user.id,
        scopes=scopes,
    )


@router.get("/me", response_model=UserProfile)
async def current_user_profile(
    current_user: UserAccount = Security(get_current_user, scopes=[]),
) -> Any:
    return UserProfile.model_validate(current_user)
