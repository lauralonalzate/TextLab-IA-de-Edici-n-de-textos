"""
Storage abstraction for file storage.

Supports local filesystem and AWS S3 backends.
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, BinaryIO
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def save(self, file_path: str, content: bytes) -> str:
        """
        Save file content to storage.
        
        Args:
            file_path: Path where to save the file (relative to storage root)
            content: File content as bytes
        
        Returns:
            URL or path to the saved file
        """
        pass
    
    @abstractmethod
    def get(self, file_path: str) -> bytes:
        """
        Retrieve file content from storage.
        
        Args:
            file_path: Path to the file (relative to storage root)
        
        Returns:
            File content as bytes
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        pass
    
    @abstractmethod
    def delete(self, file_path: str) -> bool:
        """
        Delete file from storage.
        
        Args:
            file_path: Path to the file (relative to storage root)
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """
        Check if file exists in storage.
        
        Args:
            file_path: Path to the file (relative to storage root)
        
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def get_url(self, file_path: str) -> str:
        """
        Get URL or path to access the file.
        
        Args:
            file_path: Path to the file (relative to storage root)
        
        Returns:
            URL or path string
        """
        pass


class LocalStorage(StorageBackend):
    """Local filesystem storage backend"""
    
    def __init__(self, base_path: str = "exports"):
        """
        Initialize local storage.
        
        Args:
            base_path: Base directory for storing files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalStorage initialized at {self.base_path.absolute()}")
    
    def save(self, file_path: str, content: bytes) -> str:
        """Save file to local filesystem"""
        full_path = self.base_path / file_path
        
        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(full_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved to {full_path}")
        return str(full_path.relative_to(Path.cwd()))
    
    def get(self, file_path: str) -> bytes:
        """Retrieve file from local filesystem"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(full_path, "rb") as f:
            return f.read()
    
    def delete(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        full_path = self.base_path / file_path
        
        if not full_path.exists():
            return False
        
        full_path.unlink()
        logger.info(f"File deleted: {full_path}")
        return True
    
    def exists(self, file_path: str) -> bool:
        """Check if file exists in local filesystem"""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    def get_url(self, file_path: str) -> str:
        """Get relative path for local storage"""
        return f"/api/v1/downloads/{file_path}"


class S3Storage(StorageBackend):
    """AWS S3 storage backend"""
    
    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        prefix: str = "",
    ):
        """
        Initialize S3 storage.
        
        Args:
            bucket_name: S3 bucket name
            region: AWS region
            access_key_id: AWS access key ID (optional if using IAM role)
            secret_access_key: AWS secret access key (optional if using IAM role)
            prefix: Prefix for all file paths in bucket
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError(
                "boto3 is required for S3 storage. Install with: pip install boto3"
            )
        
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip("/") + "/" if prefix else ""
        self.region = region
        
        # Initialize S3 client
        if access_key_id and secret_access_key:
            self.s3_client = boto3.client(
                "s3",
                region_name=region,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
            )
        else:
            # Use default credentials (IAM role, environment variables, etc.)
            self.s3_client = boto3.client("s3", region_name=region)
        
        logger.info(f"S3Storage initialized for bucket: {bucket_name}")
    
    def _get_s3_key(self, file_path: str) -> str:
        """Get full S3 key with prefix"""
        return f"{self.prefix}{file_path}"
    
    def save(self, file_path: str, content: bytes) -> str:
        """Save file to S3"""
        s3_key = self._get_s3_key(file_path)
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
            )
            logger.info(f"File saved to S3: s3://{self.bucket_name}/{s3_key}")
            return s3_key
        except Exception as e:
            logger.error(f"Error saving file to S3: {e}")
            raise
    
    def get(self, file_path: str) -> bytes:
        """Retrieve file from S3"""
        s3_key = self._get_s3_key(file_path)
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )
            return response["Body"].read()
        except self.s3_client.exceptions.NoSuchKey:
            raise FileNotFoundError(f"File not found in S3: {file_path}")
        except Exception as e:
            logger.error(f"Error retrieving file from S3: {e}")
            raise
    
    def delete(self, file_path: str) -> bool:
        """Delete file from S3"""
        s3_key = self._get_s3_key(file_path)
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )
            logger.info(f"File deleted from S3: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file from S3: {e}")
            return False
    
    def exists(self, file_path: str) -> bool:
        """Check if file exists in S3"""
        s3_key = self._get_s3_key(file_path)
        
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )
            return True
        except self.s3_client.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise
    
    def get_url(self, file_path: str) -> str:
        """Generate presigned URL for S3 file"""
        s3_key = self._get_s3_key(file_path)
        
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=3600,  # 1 hour
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            # Fallback to S3 URL
            return f"s3://{self.bucket_name}/{s3_key}"


def get_storage() -> StorageBackend:
    """
    Factory function to get storage backend based on configuration.
    
    Returns:
        StorageBackend instance (LocalStorage or S3Storage)
    """
    from app.core.config import settings
    
    if settings.STORAGE_BACKEND == "s3":
        if not settings.S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME must be set when using S3 storage")
        
        return S3Storage(
            bucket_name=settings.S3_BUCKET_NAME,
            region=settings.AWS_REGION,
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            prefix=settings.S3_BUCKET_PREFIX,
        )
    else:
        return LocalStorage(base_path=settings.STORAGE_PATH)

