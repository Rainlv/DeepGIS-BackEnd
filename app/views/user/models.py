from fastapi_users import models


class User(models.BaseUser):
    nick_name: str


class UserCreate(models.BaseUserCreate):
    nick_name: str


class UserUpdate(models.BaseUserUpdate):
    nick_name: str


class UserDB(User, models.BaseUserDB):
    pass
