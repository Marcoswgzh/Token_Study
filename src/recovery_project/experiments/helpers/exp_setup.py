# Main writer: Erika Skodova, Nadja Poltoracki
# Reviewer: Anna Kálmánczhelyi
from pathlib import Path

from recovery_project.domain.models import TrialResult
from recovery_project.experiments.helpers.metrics import compute_summary,save_results
from recovery_project.experiments.helpers.runner import ExperimentRunner
from recovery_project.config import load_experiment_config
from recovery_project.simulation.non_parallel_attacker import non_parallel_attacker
from recovery_project.simulation.parallel_attacker import send_attack

def exp_setup(experiment_name: str,load_exp_path: str):
    data = load_experiment_config(load_exp_path)
    base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent

    all_experiments: list[TrialResult] = []
    all_summaries: list[dict] = []
    for config in data:
        print(config.strategy)
        if config.strategy == "random" or config.strategy == "exhaustive":
            attacker = non_parallel_attacker
            config.name = config.name + "_non_parallel"
        else:
            attacker = send_attack
            config.name = config.name + "_parallel"
        # Call bruteforce attack
        runner = ExperimentRunner(config=config, run_trial=attacker)
        results = runner.run()

        all_experiments += results
        all_summaries.append(compute_summary(results, config.name))
    save_results(all_summaries,output_dir=Path(f"{base_dir}/data/processed/{experiment_name}_summary"))
    save_results(all_experiments, output_dir=Path(f"{base_dir}/data/raw/{experiment_name}_raw_results"))