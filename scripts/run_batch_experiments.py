from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from src.recovery_project.config import ExperimentConfig, load_experiment_config
from src.recovery_project.experiments.service import execute_experiment
from scripts.run_experiment import stub_trial


def build_rq1_entropy_configs(base_path: Path) -> list[ExperimentConfig]:
    """Vary token length while keeping all other parameters fixed."""
    base = load_experiment_config(base_path)
    configs: list[ExperimentConfig] = []

    for length in [4, 5, 6, 7, 8]:
        config = replace(
            base,
            name=f"rq1_entropy_len_{length}",
            token_policy=replace(base.token_policy, length=length),
        )
        configs.append(config)

    return configs


def build_rq2_ttl_configs(base_path: Path) -> list[ExperimentConfig]:
    """Vary token TTL while keeping all other parameters fixed."""
    base = load_experiment_config(base_path)
    configs: list[ExperimentConfig] = []

    for ttl in [30, 60, 120, 300, 600]:
        config = replace(
            base,
            name=f"rq2_ttl_{ttl}",
            token_policy=replace(base.token_policy, ttl_seconds=ttl),
        )
        configs.append(config)

    return configs


def build_rq3_rate_limit_configs(base_path: Path) -> list[ExperimentConfig]:
    """Vary rate limit settings while keeping all other parameters fixed."""
    base = load_experiment_config(base_path)
    configs: list[ExperimentConfig] = []

    combinations = [
        (3, 30),
        (5, 60),
        (10, 60),
        (5, 120),
    ]

    for max_attempts, window_seconds in combinations:
        config = replace(
            base,
            name=f"rq3_rl_{max_attempts}_in_{window_seconds}s",
            rate_limit_policy=replace(
                base.rate_limit_policy,
                enabled=True,
                max_attempts=max_attempts,
                window_seconds=window_seconds,
            ),
        )
        configs.append(config)

    return configs


def run_configs(configs: list[ExperimentConfig], output_dir: Path) -> None:
    """Run each experiment config and save results."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for index, config in enumerate(configs, start=1):
        print(f"[{index}/{len(configs)}] Running {config.name}...")

        _, summary, csv_path = execute_experiment(
            config=config,
            output_dir=output_dir,
            run_trial=stub_trial,
        )

        print(f"Saved results to: {csv_path}")
        print(f"Summary: {summary}")
        print("-" * 60)


def main() -> None:
    all_configs: list[ExperimentConfig] = []

    all_configs.extend(
        build_rq1_entropy_configs(Path("rq1_entropy.yaml"))
    )
    all_configs.extend(
        build_rq2_ttl_configs(Path("rq2_expiration.yaml"))
    )
    all_configs.extend(
        build_rq3_rate_limit_configs(Path("rq3_rate_limit.yaml"))
    )

    run_configs(all_configs, Path("results/batch"))


if __name__ == "__main__":
    main()