from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from core.config import get_settings

settings = get_settings()


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.secret_key, lifetime_seconds=settings.jwt_lifetime_seconds)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl=f"{settings.api_v1_str}/auth/login"),
    get_strategy=get_jwt_strategy,
)
