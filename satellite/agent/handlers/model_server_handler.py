import json
from pathlib import Path

import httpx

from agent.clients import PlatformClient
from agent.settings import config


class ServerClient:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            # "X-Agent-Request": "true"
        }

    async def post(self, url: str, request_data: dict, timeout: int = 45):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, json=request_data, headers=self.headers, timeout=timeout
            )
            response.raise_for_status()
            return response.json()

    async def get(self, url: str, timeout: int = 45):
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()
            return response.json()


class ModelServerHandler:
    def __init__(self, state_file="deployments.json"):
        self.state_file = Path(state_file)
        self._client = ServerClient()

    @staticmethod
    def _to_local_deployment(deployment_id: int, container_id: str, model_url: str) -> dict:
        return {
            "deployment_id": deployment_id,
            "container_id": container_id,
            "model_url": model_url,
            # "port": port,
        }

    async def _read_deployments(self) -> dict[str, dict]:
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    async def _write_deployments(self, deployments: dict[str, dict]):
        data = {str(k): v for k, v in deployments.items()}

        temp_file = self.state_file.with_suffix(".tmp")
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        temp_file.rename(self.state_file)

    async def add_deployment(
        self,
        deployment_id: int,
        container_id: str,
        model_url: str,
        port: int,
    ):
        print("add_deployment")
        deployments = await self._read_deployments()

        deployments[str(deployment_id)] = self._to_local_deployment(
            deployment_id, container_id, model_url
        )
        print(deployments)

        await self._write_deployments(deployments)

    async def get_deployment(self, deployment_id: str) -> dict | None:
        deployments = await self._read_deployments()
        return deployments.get(deployment_id)

    async def list_active_deployments(self) -> list[dict]:
        deployments = await self._read_deployments()
        return [info for info in deployments.values()]

    async def sync_deployments(self):
        async with PlatformClient(
            str(config.PLATFORM_URL), config.SATELLITE_TOKEN
        ) as platform_client:
            deployments_db = await platform_client.list_deployments()
        deployments_db = [dep for dep in deployments_db if dep.get("status", "") == "active"]
        deployments = await self._read_deployments()
        print(deployments)

        for dep in deployments_db:
            try:
                health_ok = await self._client.get(f"{dep["inference_url"]}/healthz")
            except Exception:
                health_ok = False
            print(dep)
            print(health_ok)
            if health_ok:
                deployments[str(dep["id"])] = self._to_local_deployment(
                    dep["id"], "None", dep["inference_url"]
                )

        await self._write_deployments(deployments)

    async def model_compute(self, deployment_id: int, request_data: dict):
        deployment = await self.get_deployment(str(deployment_id))
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{deployment["model_url"]}/compute", json=request_data, timeout=45
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Model server error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Connection error to model server: {str(e)}")

    async def model_manifest(self, deployment_id: int):
        deployment = await self.get_deployment(str(deployment_id))
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{deployment["model_url"]}/manifest", timeout=45)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Model server error: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"Connection error to model server: {str(e)}")

    # async def shutdown(self):
    #     print("Stopping all model servers...")
    #     for deployment_id, server_info in self.model_servers.items():
    #         try:
    #             await self._stop_container(server_info.container_id)
    #             server_info.status = "stopped"
    #             print(f"Stopped deployment {deployment_id}")
    #         except Exception as e:
    #             print(f"Error stopping {deployment_id}: {e}")
