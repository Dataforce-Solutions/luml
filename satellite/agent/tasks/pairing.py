from typing import Any

from agent.schemas import SatelliteQueueTask, SatelliteTaskStatus
from agent.settings import config
from agent.tasks.base import Task


class PairingTask(Task):
    async def run(self, task: SatelliteQueueTask) -> None:
        await self.platform.update_task_status(task.id, SatelliteTaskStatus.RUNNING)
        capabilities: dict[str, Any] = {
            "deploy": {"max_concurrency": 2, "labels": ["docker", "demo"]}
        }
        base_url = config.BASE_URL.rstrip("/")
        result = {"capabilities": capabilities, "base_url": base_url}
        await self.platform.pair_satellite(base_url, capabilities)
        await self.platform.update_task_status(task.id, SatelliteTaskStatus.DONE, result)
