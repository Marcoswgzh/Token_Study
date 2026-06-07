# written by Erika Škodová
from recovery_project.config import ExperimentConfig
from recovery_project.experiments.helpers.metrics import compute_summary
from recovery_project.experiments.helpers.runner import ExperimentRunner
from recovery_project.attacker_algorithms.non_parallel_attacker import send_attack
from recovery_project.attacker_algorithms.parallel_attacker import send_attack


def demo_run(demo_config: ExperimentConfig) -> dict:
    if demo_config.strategy is "random" or demo_config.strategy is "exhaustive":
        print(demo_config.strategy)
        attacker = send_attack
    else:
        print(demo_config.strategy)
        attacker = send_attack
    runner = ExperimentRunner(config=demo_config, run_trial=attacker)
    results = runner.run()

    return compute_summary(results, demo_config.name)