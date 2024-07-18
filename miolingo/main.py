import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_users import FastAPIUsers

from miolingo import __version__ as pkg_version
from miolingo import settings
from miolingo.api.v1.router import api_router
from miolingo.backends.authentication import auth_backend
from miolingo.conf.loggers import configure_loggers
from miolingo.managers.users import get_user_manager
from miolingo.models.users import User
from miolingo.schemas.users import UserCreate, UserRead, UserUpdate

# Declare FastAPI app to server HTTP requests.
app: FastAPI = FastAPI(
    title="Miolingo",
    description="A language-learning app to suit your needs",
    version=pkg_version,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
)

fastapi_users: FastAPIUsers = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Set all CORS enabled origins (for frontend with FUN app)
if settings.BACKEND_CORS_ORIGINS:  # pragma: no cover
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Then attach users router.
# Then attach user API auth.
app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/auth",
    tags=["auth"],
)
# Attach user API register
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
# Attach user API verify
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
# Attach user API reset passwd
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
# Attach user API
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate, requires_verification=True),
    prefix="/users",
    tags=["users"],
)

# Then finally attach main API router.
app.include_router(api_router, prefix=settings.API_V1_STR)

# All loggers should be fully initialized so overriding theirs configs.
configure_loggers(handlers=settings.LOG_HANDLERS, level=settings.LOG_LEVEL)
