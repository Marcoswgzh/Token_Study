# Main writer: Anna Kálmánczhelyi
from pathlib import Path

from recovery_project.domain.models import TrialResult
from recovery_project.experiments.metrics import compute_summary,save_results
from runner import ExperimentRunner
from recovery_project.config import load_experiment_config, ExperimentConfig
from typing import Callable

def exp_setup(experiment_name: str,load_exp_path: str, attacker: Callable[[int, str, ExperimentConfig], TrialResult]):
    data = load_experiment_config(load_exp_path)

    all_experiments: list[TrialResult] = []
    all_summaries: list[dict] = []
    for config in data:

        # Call bruteforce attack
        runner = ExperimentRunner(config=config, run_trial=attacker)
        results = runner.run()

        all_experiments += results
        all_summaries.append(compute_summary(results, config.name))
    save_results(all_summaries,output_dir=Path(f"processed/{experiment_name}_summary"))
    save_results(all_experiments, output_dir=Path(f"raw/{experiment_name}_raw_results"))