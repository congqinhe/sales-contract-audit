from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://ai-model.chint.com/api"
    openai_model: str = "deepseek-v3"
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
