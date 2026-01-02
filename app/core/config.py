from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator, AnyHttpUrl, EmailStr

class Settings(BaseSettings):

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AKM SIR BIO"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    #Server Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1

    # CORS Configuration
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://127.0.0.1:3000"
    ]
    allowed_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]

    #logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"

    # Database Configuration
    database_url: str

    # Security Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


    #Admin Configuration
    admin_email: EmailStr
    admin_password: str

    # Email Configuration
    mail_username: str
    mail_password: str
    mail_from: EmailStr
    mail_port: int = 587
    mail_server: str
    mail_from_name: str = "AKM SIR BIOLOGY"
    mail_starttls: bool = True
    mail_ssl_tls: bool = False
    use_credentials: bool = True
    validate_certs: bool = True

    @validator("allowed_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator("allowed_methods", pre=True)
    def assemble_cors_methods(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()

    
    
    