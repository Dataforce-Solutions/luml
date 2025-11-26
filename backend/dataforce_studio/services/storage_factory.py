from dataforce_studio.schemas.bucket_secrets import (
    AzureBucketSecret,
    AzureBucketSecretCreateIn,
    BucketSecret,
    BucketSecretCreateIn,
    S3BucketSecret,
    S3BucketSecretCreateIn,
)
from dataforce_studio.services.azure_storage_service import AzureBlobService
from dataforce_studio.services.base_storage_service import BaseStorageService
from dataforce_studio.services.s3_service import S3Service


def create_storage_service(
    secret: BucketSecretCreateIn | BucketSecret,
) -> BaseStorageService:
    if isinstance(secret, (S3BucketSecret, S3BucketSecretCreateIn)):
        return S3Service(secret)
    if isinstance(secret, (AzureBucketSecret, AzureBucketSecretCreateIn)):
        return AzureBlobService(secret)
    raise ValueError(f"Unsupported bucket secret type: {type(secret)}")
