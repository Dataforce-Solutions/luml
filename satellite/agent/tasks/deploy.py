import json

from agent.handlers.model_server_handler import ModelServerHandler
from agent.schemas import SatelliteQueueTask, SatelliteTaskStatus
from agent.settings import config
from agent.tasks.base import Task

model_server_handler = ModelServerHandler()


class DeployTask(Task):
    async def run(self, task: SatelliteQueueTask) -> None:
        await self.platform.update_task_status(task.id, SatelliteTaskStatus.RUNNING)

        payload = task.payload or {}
        dep_id = payload.get("deployment_id")
        if dep_id is None:
            await self.platform.update_task_status(
                task.id, SatelliteTaskStatus.FAILED, {"reason": "missing deployment_id"}
            )
            return

        name = f"sat-{dep_id}"
        container_port = int(config.CONTAINER_PORT)
        try:
            deployments = await self.platform.list_deployments()
            dep = next((d for d in deployments if int(d.get("id")) == int(dep_id)), None)
            if not dep:
                raise ValueError("deployment not found")
            model_id = int(dep.get("model_id"))
            presigned_url = await self.platform.get_model_artifact_download_url(model_id)
        except Exception as e:
            await self.platform.update_task_status(
                task.id,
                SatelliteTaskStatus.FAILED,
                {"reason": "failed to get model artifact url", "error": str(e)},
            )
            return

        secrets_payload = dep.get("secrets") or {}
        secrets_env: dict[str, str] = {}
        if isinstance(secrets_payload, dict):
            for key, secret_id in secrets_payload.items():
                try:
                    secret = await self.platform.get_orbit_secret(int(secret_id))
                    value = str(secret.get("value", ""))
                    secrets_env[str(key)] = value
                except Exception:
                    continue

        env: dict[str, str] = {"MODEL_ARTIFACT_URL": str(presigned_url)}
        for k, v in secrets_env.items():
            env[k] = v
        if secrets_env:
            env["MODEL_SECRETS"] = json.dumps(secrets_env)

        container, host_port = await self.docker.run_model_container(
            image=config.MODEL_IMAGE,
            name=name,
            container_port=container_port,
            labels={"df.deployment_id": str(dep_id)},
            env=env,
        )

        info = await container.show()
        ip = (
            info.get("NetworkSettings", {}).get("Networks", {}).get("bridge", {}).get("IPAddress")
            or info.get("NetworkSettings", {}).get("IPAddress")
            or "127.0.0.1"
        )

        health_ok = await self.docker.wait_http_ok(
            f"http://{ip}:{container_port}/healthz", timeout_s=45
        )
        if not health_ok:
            try:
                logs = await container.log(stdout=True, stderr=True, follow=False, tail=80)
                if isinstance(logs, list):
                    logs = "".join(logs)
                elif not isinstance(logs, str):
                    logs = str(logs) if logs is not None else ""
            except Exception:
                logs = ""
            await self.platform.update_task_status(
                task.id,
                SatelliteTaskStatus.FAILED,
                {"reason": "healthcheck timeout", "tail": str(logs)[-1000:]},
            )
            return

        inference_url = f"{config.BASE_URL}:{host_port}"
        await self.platform.update_deployment_inference_url(int(dep_id), inference_url)
        await self.platform.update_task_status(
            task.id,
            SatelliteTaskStatus.DONE,
            {"inference_url": inference_url},
        )

        await model_server_handler.add_deployment(dep_id, container.id, inference_url, host_port)
