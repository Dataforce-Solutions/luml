import uuid
from typing import Literal

from pydantic import BaseModel

from dataforce_studio.schemas.bucket_secrets import BucketType


class MultipartUploadInfo(BaseModel):
    upload_id: str
    parts_count: int
    part_size: int


class PartDetails(BaseModel):
    part_number: int
    url: str
    start_byte: int
    end_byte: int
    part_size: int


class S3UploadDetails(BaseModel):
    type: Literal[BucketType.S3] = BucketType.S3
    url: str
    multipart: bool = False
    bucket_location: str
    bucket_secret_id: uuid.UUID


class AzureUploadDetails(BaseModel):
    type: Literal[BucketType.AZURE] = BucketType.AZURE
    url: str | None = None
    multipart: bool = False
    bucket_location: str
    bucket_secret_id: uuid.UUID


class S3MultiPartUploadDetails(BaseModel):
    type: Literal[BucketType.S3] = BucketType.S3
    upload_id: str
    parts: list[PartDetails]
    complete_url: str


class AzureMultiPartUploadDetails(BaseModel):
    type: Literal[BucketType.AZURE] = BucketType.AZURE
    parts: list[PartDetails]
    complete_url: str


class BucketMultipartUpload(BaseModel):
    bucket_id: uuid.UUID
    bucket_location: str
    size: int
    upload_id: str | None = None
