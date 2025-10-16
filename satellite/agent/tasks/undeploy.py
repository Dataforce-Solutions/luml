from agent.handlers.handler_instances import ms_handler
from agent.schemas import SatelliteQueueTask, SatelliteTaskStatus
from agent.tasks.base import Task


class UndeployTask(Task):
    async def run(self, task: SatelliteQueueTask) -> None:
        await self.platform.update_task_status(task.id, SatelliteTaskStatus.RUNNING)

        payload = task.payload or {}
        deployment_id = payload.get("deployment_id")

        try:
            container_removed = await self.docker.remove_model_container(
                deployment_id=deployment_id
            )
        except Exception as error:  # pragma: no cover - defensive
            await self.platform.update_task_status(
                task.id,
                SatelliteTaskStatus.FAILED,
                {
                    "reason": "failed to remove container",
                    "error": str(error),
                },
            )
            return

        try:
            await self.platform.delete_deployment(deployment_id)
        except Exception as error:
            await self.platform.update_task_status(
                task.id,
                SatelliteTaskStatus.FAILED,
                {
                    "reason": "failed to mark deployment deleted",
                    "error": str(error),
                },
            )
            return

        await ms_handler.remove_deployment(deployment_id)

        await self.platform.update_task_status(
            task.id,
            SatelliteTaskStatus.DONE,
            {"container_removed": container_removed},
        )
