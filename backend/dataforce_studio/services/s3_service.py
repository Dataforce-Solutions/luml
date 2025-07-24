from datetime import timedelta

from minio import Minio

from dataforce_studio.infra.exceptions import BucketConnectionError
from dataforce_studio.schemas.bucket_secrets import BucketSecret


class S3Service:
    def _create_minio_client(self, secret: BucketSecret) -> Minio:
        return Minio(
            secret.endpoint,
            access_key=secret.access_key,
            secret_key=secret.secret_key,
            session_token=secret.session_token,
            secure=secret.secure if secret.secure is not None else True,
            region=secret.region,
            cert_check=secret.cert_check if secret.cert_check is not None else True,
        )

    async def get_presigned_url(self, secret: BucketSecret, object_name: str) -> str:
        try:
            client = self._create_minio_client(secret)

            return client.presigned_put_object(
                bucket_name=secret.bucket_name,
                object_name=object_name,
                expires=timedelta(hours=1),
            )
        except Exception as e:
            raise BucketConnectionError(
                f"Failed to generate upload URL: {str(e)}"
            ) from e

    async def get_download_url(self, secret: BucketSecret, object_name: str) -> str:
        try:
            client = self._create_minio_client(secret)

            return client.presigned_get_object(
                bucket_name=secret.bucket_name,
                object_name=object_name,
                expires=timedelta(hours=1),
            )
        except Exception as e:
            raise BucketConnectionError(
                f"Failed to generate download URL: {str(e)}"
            ) from e

    async def get_delete_url(self, secret: BucketSecret, object_name: str) -> str:
        try:
            client = self._create_minio_client(secret)

            return client.get_presigned_url(
                "DELETE",
                bucket_name=secret.bucket_name,
                object_name=object_name,
                expires=timedelta(hours=1),
            )
        except Exception as e:
            raise BucketConnectionError(
                f"Failed to generate delete URL: {str(e)}"
            ) from e
