from abc import ABC, abstractmethod
from typing import Any

from dataforce.modelref import _BaseArtifact


class Backend(ABC):
    @abstractmethod
    def __init__(self, config: str) -> None:
        pass

    @abstractmethod
    def initialize_experiment(
        self,
        experiment_id: str,
        name: str | None = None,
        group: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        pass

    @abstractmethod
    def log_static(self, experiment_id: str, key: str, value: Any) -> None:
        pass

    @abstractmethod
    def log_dynamic(
        self, experiment_id: str, key: str, value: int | float, step: int | None = None
    ) -> None:
        pass

    @abstractmethod
    def log_attachment(
        self, experiment_id: str, name: str, data: Any, binary: bool = False
    ) -> None:
        pass

    @abstractmethod
    def log_span(
        self,
        experiment_id: str,
        trace_id: str,
        span_id: str,
        name: str,
        start_time_unix_nano: int,
        end_time_unix_nano: int,
        parent_span_id: str | None = None,
        kind: int = 0,
        status_code: int = 0,
        status_message: str | None = None,
        attributes: dict[str, Any] | None = None,
        events: list[dict[str, Any]] | None = None,
        links: list[dict[str, Any]] | None = None,
        trace_flags: int = 0,
    ) -> None:
        pass

    @abstractmethod
    def log_eval_sample(
        self,
        experiment_id: str,
        eval_id: str,
        dataset_id: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any] | None = None,
        references: dict[str, Any] | None = None,
        scores: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        pass

    @abstractmethod
    def link_eval_sample_to_trace(
        self,
        experiment_id: str,
        eval_dataset_id: str,
        eval_id: str,
        trace_id: str,
    ) -> None:
        pass

    @abstractmethod
    def get_experiment_data(self, experiment_id: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def get_attachment(self, experiment_id: str, name: str) -> Any:
        pass

    @abstractmethod
    def list_experiments(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def delete_experiment(self, experiment_id: str) -> None:
        pass

    @abstractmethod
    def create_group(self, name: str, description: str | None = None) -> None:
        pass

    @abstractmethod
    def list_groups(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def end_experiment(self, experiment_id: str) -> None:
        pass

    @abstractmethod
    def get_experiment_db(self, experiment_id: str) -> _BaseArtifact:
        pass

    @abstractmethod
    def get_attachments(
        self, experiment_id: str
    ) -> tuple[_BaseArtifact, _BaseArtifact]:
        pass
