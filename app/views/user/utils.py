import contextlib
from typing import Callable

from pydantic.networks import EmailStr

from views.user.db import get_async_session, get_user_db
from views.user.models import UserCreate, UserDB
from views.user.users import get_user_manager
from fastapi_users.manager import UserAlreadyExists, FastAPIUsersException
from loguru import logger


async def create_user(nick_name: str, email: EmailStr, password: str, is_superuser: bool = False):
    get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email, password=password, is_superuser=is_superuser, nick_name=nick_name
                        )
                    )
                    logger.info(f"User created {user}")

    except UserAlreadyExists:
        logger.error(f"User {email} already exists")

    except FastAPIUsersException:
        logger.error(f"创建用户失败: {nick_name} {email} {password}")


async def delete_user(user: UserDB):
    get_async_session_context = contextlib.asynccontextmanager(get_async_session)
    get_user_db_context = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.delete(user)
                    logger.info(f"User created {user}")


    except FastAPIUsersException:
        logger.error(f"删除用户失败: {user.nick_name} {user.email}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(create_user("610253199@qq.com", "1"))
