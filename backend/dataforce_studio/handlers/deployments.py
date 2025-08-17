from dataforce_studio.handlers.permissions import PermissionsHandler
from dataforce_studio.infra.db import engine
from dataforce_studio.infra.exceptions import BucketSecretNotFoundError, NotFoundError
from dataforce_studio.repositories.bucket_secrets import BucketSecretRepository
from dataforce_studio.repositories.collections import CollectionRepository
from dataforce_studio.repositories.deployments import DeploymentRepository
from dataforce_studio.repositories.model_artifacts import ModelArtifactRepository
from dataforce_studio.repositories.orbits import OrbitRepository
from dataforce_studio.repositories.satellites import SatelliteRepository
from dataforce_studio.schemas.deployment import (
    Deployment,
    DeploymentCreate,
    DeploymentCreateIn,
    DeploymentStatus,
    DeploymentUpdate,
)
from dataforce_studio.schemas.permissions import Action, Resource
from dataforce_studio.services.s3_service import S3Service


class DeploymentHandler:
    __repo = DeploymentRepository(engine)
    __sat_repo = SatelliteRepository(engine)
    __orbit_repo = OrbitRepository(engine)
    __artifact_repo = ModelArtifactRepository(engine)
    __collection_repo = CollectionRepository(engine)
    __secret_repo = BucketSecretRepository(engine)
    __permissions_handler = PermissionsHandler()

    async def _get_s3_service(self, secret_id: int) -> S3Service:
        secret = await self.__secret_repo.get_bucket_secret(secret_id)
        if not secret:
            raise BucketSecretNotFoundError()
        return S3Service(secret)

    async def create_deployment(
        self,
        user_id: int,
        organization_id: int,
        orbit_id: int,
        data: DeploymentCreateIn,
    ) -> Deployment:
        await self.__permissions_handler.check_orbit_action_access(
            organization_id,
            orbit_id,
            user_id,
            Resource.DEPLOYMENT,
            Action.CREATE,
        )

        orbit = await self.__orbit_repo.get_orbit_simple(orbit_id, organization_id)
        if not orbit:
            raise NotFoundError("Orbit not found")

        satellite = await self.__sat_repo.get_satellite(data.satellite_id)
        if not satellite or satellite.orbit_id != orbit_id:
            raise NotFoundError("Satellite not found")

        artifact = await self.__artifact_repo.get_model_artifact_by_id(
            data.model_artifact_id
        )
        if not artifact:
            raise NotFoundError("Model artifact not found")

        collection = await self.__collection_repo.get_collection(artifact.collection_id)
        if not collection or collection.orbit_id != orbit_id:
            raise NotFoundError("Model artifact not in orbit")

        s3_service = await self._get_s3_service(orbit.bucket_secret_id)
        model_uri = await s3_service.get_download_url(artifact.bucket_location)

        deployment, _ = await self.__repo.create_deployment(
            DeploymentCreate(
                orbit_id=orbit_id,
                satellite_id=data.satellite_id,
                model_uri=model_uri,
                secret_ids=data.secret_ids,
                created_by_user_id=user_id,
            )
        )
        return deployment

    async def list_deployments(
        self, user_id: int, organization_id: int, orbit_id: int
    ) -> list[Deployment]:
        await self.__permissions_handler.check_orbit_action_access(
            organization_id,
            orbit_id,
            user_id,
            Resource.DEPLOYMENT,
            Action.LIST,
        )
        return await self.__repo.list_deployments(orbit_id)

    async def get_deployment(
        self, user_id: int, organization_id: int, orbit_id: int, deployment_id: int
    ) -> Deployment:
        await self.__permissions_handler.check_orbit_action_access(
            organization_id,
            orbit_id,
            user_id,
            Resource.DEPLOYMENT,
            Action.READ,
        )
        deployment = await self.__repo.get_deployment(deployment_id, orbit_id)
        if not deployment:
            raise NotFoundError("Deployment not found")
        return deployment

    async def list_worker_deployments(self, satellite_id: int) -> list[Deployment]:
        return await self.__repo.list_satellite_deployments(satellite_id)

    async def update_worker_deployment(
        self, satellite_id: int, deployment_id: int, inference_url: str
    ) -> Deployment:
        deployment = await self.__repo.update_deployment(
            deployment_id,
            satellite_id,
            DeploymentUpdate(
                id=deployment_id,
                inference_url=inference_url,
                status=DeploymentStatus.ACTIVE,
            ),
        )
        if not deployment:
            raise NotFoundError("Deployment not found")
        return deployment
