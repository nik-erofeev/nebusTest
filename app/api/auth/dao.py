from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Response

from app.api.auth.schemas import (
    SUserRegister,
    SUserAddDB,
    EmailModel,
    RUserResponse,
    SUserAuth,
    AUserResponse,
)
from app.api.auth.utils import authenticate_user, set_tokens
from app.dao.base import BaseDAO
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException
from app.models.auth import User, Role


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def register_user(cls, user_data: SUserRegister, session: AsyncSession) -> RUserResponse:
        # Проверка существования пользователя
        existing_user = await cls.find_one_or_none(session=session, filters=EmailModel(email=user_data.email))
        if existing_user:
            raise UserAlreadyExistsException

        # Подготовка данных для добавления
        user_data_dict = user_data.model_dump()
        user_data_dict.pop("confirm_password", None)

        # Добавление пользователя
        await cls.add(session=session, values=SUserAddDB(**user_data_dict))

        return RUserResponse(message="Вы успешно зарегистрированы!")

    @classmethod
    async def auth_user(
        cls,
        response: Response,
        user_data: SUserAuth,
        session: AsyncSession,
    ):
        user = await cls.find_one_or_none(session=session, filters=EmailModel(email=user_data.email))

        if not (user and await authenticate_user(user=user, password=user_data.password)):
            raise IncorrectEmailOrPasswordException
        set_tokens(response, user.id)
        return AUserResponse(message="Авторизация успешна!")


class RoleDAO(BaseDAO):
    model = Role
