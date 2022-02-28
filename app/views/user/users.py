from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    JWTStrategy,
    BearerTransport
)
from fastapi_users.db import SQLAlchemyUserDatabase

from Config import globalConfig
from exceptions.DatabaseException import DatabaseCreateException
from exceptions.GeoserverException import CreateWorkspaceException, CreateFeatureStoreException, BaseGeoserverException
from views.map.db import create_user_database
from views.map.geoserver import geoserver
from views.user.db import get_user_db
from views.user.models import User, UserCreate, UserDB, UserUpdate
from loguru import logger

SECRET = globalConfig.USER_PASSWD_SECRET


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    # TODO 优化回滚
    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        raster_db = user.nick_name + "_feature"
        feature_db = user.nick_name + "_raster"
        try:
            create_user_database(raster_db)
            create_user_database(feature_db)
            geoserver.create_workspace(raster_db)
            geoserver.create_workspace(feature_db)
            geoserver.create_feature_store(raster_db, raster_db)
            geoserver.create_feature_store(feature_db, feature_db)
            logger.info(f"User {user.id} has registered.")

        except DatabaseCreateException:
            raise

        except BaseGeoserverException:
            try:
                await self.delete(user)
                geoserver.delete_workspace(raster_db)
                geoserver.delete_workspace(feature_db)
                geoserver.delete_featurestore(raster_db, raster_db)
                geoserver.delete_featurestore(feature_db, feature_db)
            except:
                pass
            raise

    async def on_after_forgot_password(
            self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
users = FastAPIUsers(
    get_user_manager,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)


def current_user(active: bool = False, verified: bool = False, superuser: bool = False):
    return users.current_user(active=active, verified=verified, superuser=superuser)
