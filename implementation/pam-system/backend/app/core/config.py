import os


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://pam:pam@postgres:5432/pam",
    )
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret")
    JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev-refresh-secret")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRES_MINUTES = _get_int("ACCESS_TOKEN_EXPIRES_MINUTES", 30)
    REFRESH_TOKEN_EXPIRES_DAYS = _get_int("REFRESH_TOKEN_EXPIRES_DAYS", 7)
    GATEWAY_JWT_SECRET = os.getenv("GATEWAY_JWT_SECRET", "dev-gateway-secret")
    GATEWAY_TOKEN_EXPIRES_MINUTES = _get_int("GATEWAY_TOKEN_EXPIRES_MINUTES", 5)
    GATEWAY_PUBLIC_WS_URL = os.getenv("GATEWAY_PUBLIC_WS_URL", "ws://localhost:8081/ws")
    GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY", "dev-gateway-key")
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_TOKEN = os.getenv("VAULT_TOKEN", "root")
    VAULT_KV_MOUNT = os.getenv("VAULT_KV_MOUNT", "secret")
    ALLOW_ADMIN_REGISTRATION = _get_bool("ALLOW_ADMIN_REGISTRATION", False)


settings = Settings()
