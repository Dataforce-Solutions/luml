from luml.api._types import BucketType
from luml.api.utils.azure_file_handler import AzureFileHandler
from luml.api.utils.base_file_handler import BaseFileHandler
from luml.api.utils.s3_file_handler import S3FileHandler


def create_file_handler(bucket_type: BucketType) -> BaseFileHandler:
    if bucket_type == BucketType.S3:
        return S3FileHandler()
    if bucket_type == BucketType.AZURE:
        return AzureFileHandler()
    raise ValueError(
        f"Unsupported bucket type: {bucket_type}. "
        f"Supported types: {[t.value for t in BucketType]}"
    )
