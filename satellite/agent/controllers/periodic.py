import asyncio
from contextlib import suppress

from agent.handlers import TaskHandler
from agent.schemas import SatelliteTaskStatus


class PeriodicController:
    def __init__(self, *, handler: TaskHandler, poll_interval_s: float) -> None:
        self.handler = handler
        self.poll_interval_s = poll_interval_s
        self._stopped = False

    def stop(self) -> None:
        self._stopped = True

    async def tick(self) -> None:
        tasks = await self.handler.platform.list_tasks(SatelliteTaskStatus.PENDING)
        for t in tasks:
            try:
                await self.handler.dispatch(t)
            except Exception as e:
                with suppress(Exception):
                    await self.handler.platform.update_task_status(
                        int(t["id"]),
                        SatelliteTaskStatus.FAILED,
                        {"reason": f"handler error: {e}"},
                    )

    async def run_forever(self) -> None:
        print("[satellite] starting periodic controller…", flush=True)
        while not self._stopped:
            try:
                await self.tick()
            except KeyboardInterrupt:
                self._stopped = True
                break
            except Exception as e:
                print(f"[satellite] tick error: {e}", flush=True)
            await asyncio.sleep(self.poll_interval_s)
