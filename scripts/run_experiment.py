"""CLI entry point for running a configured experiment batch."""

from __future__ import annotations

import argparse
import random
from datetime import datetime, timezone
from pathlib import Path

from recovery_project.config import ExperimentConfig, load_experiment_config
from recovery_project.domain.models import TrialResult
from recovery_project.experiments.service import execute_experiment


def stub_trial(trial_id: int, config: ExperimentConfig) -> TrialResult:
    """Produce a randomised TrialResult for pipeline testing.

    Replace this with the real attacker implementation once the
    simulation branch is merged.
    """
    tp = config.token_policy
    rl = config.rate_limit_policy
    alphabet_size = len(tp.alphabet)
    search_space = alphabet_size ** tp.length

    budget = config.attack_attempt_budget
    attempts = random.randint(1, budget)
    success = random.random() < (attempts / search_space)
    blocked = random.randint(0, attempts // 3) if rl.enabled else 0
    elapsed = attempts * (1000.0 / config.attack_rate_per_second)
    expired = elapsed > tp.ttl_seconds * 1000 and not success

    return TrialResult(
        trial_id=trial_id,
        experiment_name=config.name,
        token_length=tp.length,
        alphabet_size=alphabet_size,
        ttl_seconds=tp.ttl_seconds,
        rate_limit_enabled=rl.enabled,
        rate_limit_max_attempts=rl.max_attempts,
        rate_limit_window_seconds=rl.window_seconds,
        success=success,
        attempts_made=attempts,
        attempts_blocked=blocked,
        time_elapsed_ms=round(elapsed, 2),
        token_expired=expired,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run an experiment batch from a YAML config."
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to the experiment YAML config file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
        help="Directory for result CSVs (default: data/raw).",
    )
    args = parser.parse_args()

    config = load_experiment_config(args.config)
    results, summary, csv_path = execute_experiment(
        config=config,
        output_dir=args.output_dir,
        run_trial=stub_trial,
    )

    print(f"Results written to {csv_path}")


if __name__ == "__main__":
    main()
