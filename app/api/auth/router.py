from fastapi import APIRouter, Response, Depends, status
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.dao import UsersDAO
from app.api.auth.schemas import (
    SUserRegister,
    SUserAuth,
    SUserInfo,
    RUserResponse,
    AUserResponse,
    LUserResponse,
)
from app.api.auth.utils import set_tokens
from app.dependencies.auth_dep import get_current_user, get_current_admin_user, check_refresh_token
from app.dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from app.models import User

router = APIRouter(tags=["auth"])


@router.post(
    "/register/",
    response_model=RUserResponse,
    response_class=ORJSONResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user_data: SUserRegister, session: AsyncSession = Depends(get_session_with_commit)):
    return await UsersDAO.register_user(user_data=user_data, session=session)


@router.post(
    "/login/",
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


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=LUserResponse,
)
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return LUserResponse(message="Пользователь успешно вышел из системы")


@router.get(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=SUserInfo,
)
async def get_me(user_data: User = Depends(get_current_user)):
    return SUserInfo.model_validate(user_data)


@router.get(
    "/all_users/",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
    response_model=list[SUserInfo],
)
async def get_all_users(
    session: AsyncSession = Depends(get_session_with_commit),
    user_data: User = Depends(get_current_admin_user),
):
    return await UsersDAO.find_all(session)


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_class=ORJSONResponse,
)
async def process_refresh_token(response: Response, user: User = Depends(check_refresh_token)):
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
