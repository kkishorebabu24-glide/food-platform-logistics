from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "food-platform-logistics"
    environment: str = "development"
    database_url: str = "sqlite:///./food_platform.db"
    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
