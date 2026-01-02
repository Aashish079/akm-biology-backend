import shutil
import os
from fastapi import UploadFile
from abc import ABC, abstractmethod
from uuid import uuid4

class StorageService(ABC):
    @abstractmethod
    async def save_file(self, file: UploadFile, directory: str) -> str:
        """Save file and return the path"""
        pass

class LocalStorageService(StorageService):
    def __init__(self, base_path: str = "uploads"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    async def save_file(self, file: UploadFile, directory: str = "") -> str:
        upload_dir = os.path.join(self.base_path, directory)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{uuid4()}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return file_path

storage_service = LocalStorageService()
