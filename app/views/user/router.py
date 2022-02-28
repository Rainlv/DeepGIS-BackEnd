from fastapi import APIRouter
from views.user.users import auth_backend, users

router = APIRouter()

router.include_router(
    users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(users.get_register_router(), prefix="/auth", tags=["auth"])
router.include_router(
    users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(users.get_users_router(), prefix="/users", tags=["users"])
