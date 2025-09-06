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
        result = {"capabilities": capabilities, "base_url": config.BASE_URL}
        await self.platform.pair_satellite(config.BASE_URL, capabilities)
        await self.platform.update_task_status(task.id, SatelliteTaskStatus.DONE, result)
