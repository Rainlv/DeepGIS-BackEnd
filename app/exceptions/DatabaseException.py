from loguru import logger
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from utils.constant.ResponseCode import ResponseCodeType


class BaseDatabaseException(Exception):
    pass


class TableCreateException(BaseDatabaseException):
    pass


class DatabaseCreateException(BaseDatabaseException):
    pass


async def table_create_exception_handler(request: Request, exc: TableCreateException):
    logger.warning(str(exc))
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED,
                        content={"code": ResponseCodeType.DataBaseCreateError, "message": str(exc)})
