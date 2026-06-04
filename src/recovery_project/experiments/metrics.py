#class written by Erika Škodová
"""CSV persistence and summary statistics for experiment results."""

from __future__ import annotations

import csv
from dataclasses import asdict, fields
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median

from recovery_project.domain.models import TrialResult
from recovery_project.utils.logging import get_logger

log = get_logger(__name__)

_FIELD_NAMES = [f.name for f in fields(TrialResult)]


def save_results(results: list[TrialResult] or dict, output_dir: Path | str) -> Path:
    """Write trial results to a timestamped CSV and return its path."""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    output_dir = Path(base_dir / "data" /  output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not results:
        log.warning("No results to save")
        return output_dir

    if isinstance(results[0], TrialResult):
        experiment_name = results[0].experiment_name
    else:
        experiment_name = results[0].get("trial_name")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    filename = f"{experiment_name}_{ts}.csv"
    path = output_dir / filename

    with open(path, "w", newline="") as fh:
        if isinstance(results[0], TrialResult):
            writer = csv.DictWriter(fh, fieldnames=_FIELD_NAMES)
            writer.writeheader()
            for result in results:
                writer.writerow(asdict(result))
        else:
            writer = csv.DictWriter(fh, fieldnames=results[0].keys())
            writer.writeheader()
            for result in results:
                writer.writerow(result)


    log.info("Saved %d rows to %s", len(results), path)
    return path


def compute_summary(results: list[TrialResult], trial_name: str) -> dict:
    """Compute aggregate statistics and print them to the console."""
    if not results:
        return {}

    total = len(results)
    successes = [r for r in results if r.success]
    success_rate = len(successes) / total

    all_attempts = [r.attempts_made for r in results]
    all_blocked = [r.attempts_blocked for r in results]
    all_times = [r.time_elapsed_ms for r in results]
    expired_count = sum(1 for r in results if r.token_expired)

    success_attempts = [r.attempts_made for r in successes] if successes else [0]

    summary = {
        "trial_name" : trial_name,
        "total_trials": total,
        "success_count": len(successes),
        "success_rate": round(success_rate, 4),
        "mean_attempts": round(mean(all_attempts), 2),
        "median_attempts": round(median(all_attempts), 2),
        "mean_attempts_to_success": round(mean(success_attempts), 2),
        "median_attempts_to_success": round(median(success_attempts), 2),
        "mean_time_elapsed_ms": round(mean(all_times), 2),
        "median_time_elapsed_ms": round(median(all_times), 2),
        "total_blocked": sum(all_blocked),
        "mean_blocked_per_trial": round(mean(all_blocked), 2),
        "token_expired_count": expired_count,
    }

    _print_summary(summary)
    return summary


def _print_summary(summary: dict) -> None:
    width = 38
    print("\n" + "=" * width)
    print("  Experiment Summary")
    print("=" * width)
    for key, value in summary.items():
        label = key.replace("_", " ").title()
        print(f"  {label:<30} {value}")
    print("=" * width + "\n")
