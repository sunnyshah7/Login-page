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
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").lower()

    def validate_security_settings(self) -> None:
        if self.ENVIRONMENT in {"development", "local", "test"}:
            return

        if not self.JWT_SECRET_KEY:
            raise RuntimeError(
                "JWT_SECRET_KEY must be configured outside local development"
            )
        if len(self.JWT_SECRET_KEY.encode("utf-8")) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY must contain at least 32 bytes outside local development"
            )


settings = Settings()
