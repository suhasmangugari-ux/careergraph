from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cognodb_uri: str
    cognodb_username: str = "cognodb"
    cognodb_password: str

    class Config:
        env_file = ".env"

settings = Settings()