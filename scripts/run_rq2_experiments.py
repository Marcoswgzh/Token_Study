"""Run RQ2 expiration window attack experiments."""
# Code by Anna Kálmánczhelyi

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "src")

from recovery_project.services.token_service import TokenService
from recovery_project.simulation.exp_window_attack import ExpirationWindowAttacker


def load_experiments(config_path: Path) -> list[dict]:
    with open(config_path, "r") as f:
        return json.load(f)


def run_experiment(experiment: dict) -> list[dict]:
    token_policy = experiment["token_policy"]

    service = TokenService(
        alphabet=token_policy["alphabet"],
        token_length=token_policy["length"],
    )

    attacker = ExpirationWindowAttacker()

    results = []

    for trial in range(1, experiment["trials"] + 1):
        _, token_hash = service.generate_token()

        attack_result = attacker.attack(
            token_hash=token_hash,
            alphabet=token_policy["alphabet"],
            token_length=token_policy["length"],
            ttl_seconds=token_policy["ttl_seconds"],
            attack_rate_per_second=experiment["attack_rate_per_second"],
        )

        results.append(
            {
                "experiment": experiment["name"],
                "trial": trial,
                "success": attack_result["success"],
                "attempts": attack_result["attempts"],
                "time_elapsed": attack_result["time_elapsed"],
                "attempts_per_second": attack_result.get(
                    "attempts_per_second"
                ),
                "token_length": token_policy["length"],
                "alphabet": token_policy["alphabet"],
                "ttl_seconds": token_policy["ttl_seconds"],
            }
        )

    return results


def save_results(
    experiment_name: str,
    results: list[dict],
    output_dir: Path,
) -> Path:
    output_path = output_dir / (
    f"{experiment_name}_{datetime.now():%Y%m%dT%H%M%S}.csv"
)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run RQ2 expiration window attack experiments"
    )
    parser.add_argument("config", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/raw"),
    )

    args = parser.parse_args()

    experiments = load_experiments(args.config)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loaded {len(experiments)} experiments")

    for experiment in experiments:
        print(f"Running {experiment['name']}")

        results = run_experiment(experiment)

        output_path = save_results(
            experiment["name"],
            results,
            args.output_dir,
        )

        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()