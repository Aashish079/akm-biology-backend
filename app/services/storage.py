import shutil
import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from abc import ABC, abstractmethod
from uuid import uuid4
from app.core.config import settings

class StorageService(ABC):
    @abstractmethod
    async def save_file(self, file: UploadFile, directory: str) -> str:
        """Save file and return the path/url"""
        pass

class LocalStorageService(StorageService):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save_file(self, file: UploadFile, directory: str = "") -> str:
        upload_dir = os.path.join(self.base_path, directory)
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        return f"/api/v1/static/{directory}/{filename}" if directory else f"/api/v1/static/{filename}"
    
class S3StorageService(StorageService):
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name
        self.cloudfront_domain = settings.cloudfront_domain

    async def save_file(self, file: UploadFile, directory: str = "") -> str:
        filename = f"{directory}/{uuid4()}_{file.filename}"
        
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                filename,
                ExtraArgs={'ContentType': file.content_type}
            )
        except ClientError as e:
            # Log the error here
            print(f"Error uploading to S3: {e}")
            raise e

        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{filename}"
        return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{filename}"

def get_storage_service() -> StorageService:
    if settings.aws_access_key_id and settings.s3_bucket_name:
        return S3StorageService()
    return LocalStorageService()

storage_service = get_storage_service()
