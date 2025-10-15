import contextlib
import logging
import subprocess
import time
import traceback
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any

import httpx
from handlers.conda_custom import CondaLikeEnvManager, install_micromamba

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - [web_worker] %(message)s"
)
logger = logging.getLogger(__name__)


class ModelCondaManager:
    def __init__(self, env_spec: dict | None, extracted_path: str) -> None:
        self.env_spec = self.get_default_env_spec() if env_spec is None else env_spec
        self.extracted_path = extracted_path
        self.model_envs = None
        self.process = None
        self.port = 8081
        self.worker_script = Path(__file__).parent / "conda_worker.py"

    @property
    def worker_url(self) -> str | None:
        return f"http://0.0.0.0:{self.port}" if self.port else None

    def get_env_name(self) -> str:
        if self.model_envs["path"]:
            return self.model_envs["path"].split("/")[-1]
        else:
            return self.model_envs["name"]

    @staticmethod
    def get_default_env_spec() -> dict[str, Any]:
        return {
            "python3::conda_pip": {
                "python_version": "3.12.6",
                "build_dependencies": [],
                "dependencies": [
                    {
                        "package": f"uvicorn=={importlib_metadata.version('uvicorn')}",
                        "extra_pip_args": None,
                        "condition": None,
                    },
                    {
                        "package": f"fnnx[core]=={importlib_metadata.version('fnnx')}",
                        "extra_pip_args": None,
                        "condition": None,
                    },
                ],
            }
        }

    def create_model_env(self) -> None:
        try:
            install_micromamba()
            env_name, env_config = next(iter(self.env_spec.items()))

            if "dependencies" not in env_config:
                env_config["dependencies"] = []

            existing_packages = set()
            for dep in env_config["dependencies"]:
                if isinstance(dep, dict) and "package" in dep:
                    existing_packages.add(
                        dep["package"].split("==")[0].split(">=")[0].split("<=")[0].strip()
                    )
            for pkg_name in ["uvicorn"]:
                if pkg_name not in existing_packages:
                    version = importlib_metadata.version(pkg_name)
                    env_config["dependencies"].append({"package": f"{pkg_name}=={version}"})

            env_manager = CondaLikeEnvManager(env_config)
            env_path = env_manager.ensure()
            logger.info("[CREATE_ENV] Env created successfully.")

            self.model_envs = {"name": env_name, "path": env_path, "manager": env_manager}

        except Exception as e:
            logger.error(
                f"[CREATE_ENV] Failed to create model environment: {e}\n"
                f"Traceback: {traceback.format_exc()}"
            )

    def start(self) -> subprocess.Popen:
        env_name = self.get_env_name()

        cmd = [
            self.model_envs["manager"]._exe,
            "run",
            "-n",
            env_name,
            "python",
            str(self.worker_script),
            self.extracted_path,
            str(self.port),
        ]

        self.process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        try:
            self._wait_for_health_check()
            logger.info("[START] Worker health check passed")
            return self.process
        except Exception as error:
            logger.error(f"[START] Failed to start worker: {error}")
            if self.process:
                self.process.terminate()
            raise RuntimeError(f"Failed to start worker: {error}") from error

    def _wait_for_health_check(self, timeout: int = 90) -> None:
        with httpx.Client() as client:
            for _ in range(timeout):
                with contextlib.suppress(Exception):
                    response = client.get(f"{self.worker_url}/health", timeout=5.0)
                    if response.status_code == 200:
                        return
                time.sleep(1)

        raise RuntimeError(f"Worker health check failed after {timeout}s")

    def is_alive(self) -> bool:
        return self.process and self.process.poll() is None

    def stop(self) -> None:
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.port = None
