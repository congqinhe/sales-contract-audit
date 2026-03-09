from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_base_url: str = "https://ai-model.chint.com/api"
    openai_model: str = "deepseek-v3"
    upload_dir: str = "./uploads"
    # 切片审核参数（可通过 AUDIT_CHUNK_SIZE、AUDIT_CHUNK_OVERLAP 覆盖）
    audit_chunk_size: int = 300
    audit_chunk_overlap: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
