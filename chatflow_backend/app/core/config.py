import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Chatflow API"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://chatflow_user:chatflow_password@localhost:5432/chatflow",
    )
    JWT_SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").lower()

    def validate_security_settings(self) -> None:
        if self.ENVIRONMENT in {"development", "local", "test"}:
            return

        if not self.JWT_SECRET_KEY:
            raise RuntimeError(
                "JWT_SECRET_KEY is required when ENVIRONMENT is not development, "
                "local, or test. Set it in the deployment environment; generate "
                "a secure value with `openssl rand -hex 32`."
            )
        if len(self.JWT_SECRET_KEY.encode("utf-8")) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY must contain at least 32 bytes outside local "
                "development. Generate a secure value with `openssl rand -hex 32`."
            )


settings = Settings()
