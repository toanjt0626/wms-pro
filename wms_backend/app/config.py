from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Cấu hình ứng dụng. Có thể override bằng biến môi trường hoặc file .env,
    ví dụ: DATABASE_URL=postgresql://user:pass@host:5432/wms
    """
    app_name: str = "WMS Backend"
    database_url: str = "sqlite:///./wms.db"

    class Config:
        env_file = ".env"


settings = Settings()
