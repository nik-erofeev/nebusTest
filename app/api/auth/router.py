from fastapi import APIRouter, Response, Depends, status
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.dao import UsersDAO
from app.api.auth.schemas import (
    SUserRegister,
    SUserAuth,
    SUserInfo,
    RUserResponse,
    AUserResponse,
    LUserResponse,
    EmailModel,
    AUserBearerResponse,
)
from app.api.auth.utils import set_tokens, authenticate_user, create_tokens
from app.dependencies.auth_dep import (
    get_current_user_cookie,
    check_refresh_token,
    get_current_user_bearer,
    get_current_admin_user_cookie,
)
from app.dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from app.exceptions import IncorrectEmailOrPasswordException
from app.models import User

cookie_auth_router = APIRouter(tags=["auth_cookie"])


@cookie_auth_router.post(
    "/register",
    response_model=RUserResponse,
    response_class=ORJSONResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session_with_commit)):
    return await UsersDAO.register_user(user_data=user_data, session=session)


@cookie_auth_router.post(
    "/login",
    response_model=AUserResponse,
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
)
async def auth_user(
    response: Response,
    user_data: SUserAuth,
    session: AsyncSession = Depends(get_session_without_commit),
):
    return await UsersDAO.auth_user(response=response, user_data=user_data, session=session)


@cookie_auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=LUserResponse,
)
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return LUserResponse(message="Пользователь успешно вышел из системы")


@cookie_auth_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=SUserInfo,
)
async def get_me(user_data: User = Depends(get_current_user_cookie)):
    # async def get_me(user_data: User = Depends(get_current_user_bearer)):
    return SUserInfo.model_validate(user_data)


@cookie_auth_router.get(
    "/all_users",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=list[SUserInfo],
)
async def get_all_users(
    session: AsyncSession = Depends(get_session_with_commit),
    user_data: User = Depends(get_current_admin_user_cookie),
    # user_data: User = Depends(get_current_admin_user_bearer),
):
    return await UsersDAO.find_all(session)


@cookie_auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
)
async def process_refresh_token(response: Response, user: User = Depends(check_refresh_token)):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}


# Bearer
bearer_auth_router = APIRouter(
    tags=["bearer"],
)


@bearer_auth_router.post(
    "/token",
    response_model=AUserBearerResponse,
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
)
async def token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session_without_commit),
):
    user = await UsersDAO.find_one_or_none(session=session, filters=EmailModel(email=form_data.username))

    if not (user and await authenticate_user(user=user, password=form_data.password)):
        raise IncorrectEmailOrPasswordException

    tokens = create_tokens(data={"sub": str(user.id)})

    return AUserBearerResponse(access_token=tokens["access_token"], refresh_token=tokens["refresh_token"])


@bearer_auth_router.get(
    "/me_bearer",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=SUserInfo,
)
async def get_me_bearer(user_data: User = Depends(get_current_user_bearer)):
    return SUserInfo.model_validate(user_data)
