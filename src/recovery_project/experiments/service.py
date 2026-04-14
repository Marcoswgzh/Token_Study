# making run_experiment services logic reusable because we need it for the GUI

from __future__ import annotations

from pathlib import Path
from typing import Callable

from recovery_project.config import ExperimentConfig
from recovery_project.domain.models import TrialResult
from recovery_project.experiments.metrics import compute_summary, save_results
from recovery_project.experiments.runner import ExperimentRunner


def execute_experiment(
    config: ExperimentConfig,
    output_dir: Path,
    run_trial: Callable[[int, ExperimentConfig], TrialResult],
) -> tuple[list[TrialResult], dict, Path]:
    """ Run one configured experiment, save CSV results, and return summary."""
    runner = ExperimentRunner(config, run_trial=run_trial)
    results = runner.run()
    csv_path = save_results(results, output_dir)
    summary = compute_summary(results)
    return results, summary, csv_path