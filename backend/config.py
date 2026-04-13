from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017/coverd"
    database_name: str = "coverd"
    jwt_secret_key: str = "change_this_to_a_long_random_secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
