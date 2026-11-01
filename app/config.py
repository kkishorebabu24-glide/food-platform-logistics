from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "food-platform-logistics"
    environment: str = "development"
    database_url: str = "sqlite:///./food_platform.db"
    secret_key: str = "change-me"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
