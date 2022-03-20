
from fastapi import APIRouter, Depends

from Schemas.Response import BaseResponse
from views.code_server.CodeServerDocker import codeServerDocker
from views.user.models import User
from views.user.users import current_user

router = APIRouter(tags=['coder'], prefix="/coder")


@router.get("/get_container")
def _(user: User = Depends(current_user())):
    user_name = user.nick_name
    url = codeServerDocker.get_or_create_container_url(user_name=user_name)
    return BaseResponse(code=0, message='', result=[{"url": url}])
