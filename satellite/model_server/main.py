import sys

from handlers.model_handler import ModelHandler


if __name__ == "__main__":
    model_handler = ModelHandler()

    if model_handler.conda_worker and model_handler.conda_worker.process:
        exit_code = model_handler.conda_worker.process.wait()
        sys.exit(exit_code)

