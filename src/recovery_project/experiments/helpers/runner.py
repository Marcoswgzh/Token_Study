#class written by Giorgio Di Rosa
"""Experiment runner that orchestrates N trials and collects TrialResults."""

from __future__ import annotations

from typing import Callable, Protocol

from recovery_project.config import ExperimentConfig
from recovery_project.domain.models import TrialResult
from recovery_project.utils.logging import get_logger
from recovery_project.services.token_service import TokenService as ts

log = get_logger(__name__)


class TrialRunner(Protocol):
    """Callable contract that service branches must satisfy."""

    def __call__(self, trial_id: int, config: ExperimentConfig) -> dict: ...

# Helper class for connecting to correct attacker and running correctly trials
class ExperimentRunner:
    def __init__(self,config: ExperimentConfig,run_trial: Callable[[int, str, ExperimentConfig], TrialResult],) -> None:
        self.config = config
        self.run_trial = run_trial

    def run(self) -> list[TrialResult]:
        results: list[TrialResult] = []
        total = self.config.trials

        log.info(
            "Starting experiment '%s' — %d trials", self.config.name, total
        )
        service = ts(self.config.token_policy.alphabet, self.config.token_policy.length)

        # Run all the trial we assigned
        for trial_id in range(1, total + 1):
            target, _ = service.generate_token() #only stores token, not hash
            result = self.run_trial(trial_id, target, self.config)
            results.append(result)

            if trial_id % 100 == 0 or trial_id == total:
                log.info("Progress: %d / %d trials", trial_id, total)

        log.info("Experiment '%s' finished", self.config.name)
        return results
