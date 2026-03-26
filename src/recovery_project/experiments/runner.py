"""Experiment runner that orchestrates N trials and collects TrialResults."""

from __future__ import annotations

from typing import Callable, Protocol

from recovery_project.config import ExperimentConfig
from recovery_project.domain.models import TrialResult
from recovery_project.utils.logging import get_logger

log = get_logger(__name__)


class TrialRunner(Protocol):
    """Callable contract that service branches must satisfy."""

    def __call__(self, trial_id: int, config: ExperimentConfig) -> TrialResult: ...


class ExperimentRunner:
    def __init__(
        self,
        config: ExperimentConfig,
        run_trial: Callable[[int, ExperimentConfig], TrialResult],
    ) -> None:
        self._config = config
        self._run_trial = run_trial

    def run(self) -> list[TrialResult]:
        results: list[TrialResult] = []
        total = self._config.trials

        log.info(
            "Starting experiment '%s' — %d trials", self._config.name, total
        )

        for trial_id in range(1, total + 1):
            result = self._run_trial(trial_id, self._config)
            results.append(result)

            if trial_id % 100 == 0 or trial_id == total:
                log.info("Progress: %d / %d trials", trial_id, total)

        log.info("Experiment '%s' finished", self._config.name)
        return results
