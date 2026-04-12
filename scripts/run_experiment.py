"""CLI entry point for running a configured experiment batch."""

from __future__ import annotations
 
import argparse
from datetime import datetime, timezone
from pathlib import Path
 
from recovery_project.config import ExperimentConfig, load_experiment_config
from recovery_project.domain.models import TrialResult
from recovery_project.experiments.metrics import compute_summary, save_results
from recovery_project.experiments.runner import ExperimentRunner
from recovery_project.services.token_service import TokenService
from recovery_project.simulation.exp_window_attack import ExpirationWindowAttacker


# Main writer: Timea Vojcikova
# Contributor: Anna Kalmanczhelyi
def run_trial(trial_id: int, config: ExperimentConfig) -> TrialResult:
    """Run one real expiration-window attack trial.
 
    Steps:
      1. Generate a fresh token using the configured alphabet and length.
      2. Run ExpirationWindowAttacker against the token hash, bounded by the
         TTL and attempt budget from the config.
      3. Map the attacker's result dict into a TrialResult dataclass.
    """
    tp = config.token_policy
    rl = config.rate_limit_policy
 
    # 1. Generate a real token with policy's alphabet and length
    service = TokenService(alphabet=tp.alphabet, token_length=tp.length)
    _token, token_hash = service.generate_token()
 
    # 2. Run attack
    attacker = ExpirationWindowAttacker()
    result = attacker.attack(
        token_hash=token_hash,
        alphabet=tp.alphabet,
        token_length=tp.length,
        ttl_seconds=tp.ttl_seconds,
        max_attempts_budget=config.attack_attempt_budget,
    )
 
    # 3. Derive fields that TrialResult needs but the attacker doesn't return
    time_elapsed_ms = round(result["time_elapsed"] * 1000, 2)
    token_expired = (not result["success"]) and (result["time_elapsed"] >= tp.ttl_seconds)
 
    # attempts_blocked: only meaningful when rate-limiting is active
    # The current attacker doesn't interact with a rate limiter, so we
    # record 0 here
    attempts_blocked = 0
 
    return TrialResult(
        trial_id=trial_id,
        experiment_name=config.name,
        token_length=tp.length,
        alphabet_size=len(tp.alphabet),
        ttl_seconds=tp.ttl_seconds,
        rate_limit_enabled=rl.enabled,
        rate_limit_max_attempts=rl.max_attempts,
        rate_limit_window_seconds=rl.window_seconds,
        success=result["success"],
        attempts_made=result["attempts"],
        attempts_blocked=attempts_blocked,
        time_elapsed_ms=time_elapsed_ms,
        token_expired=token_expired,
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
    runner = ExperimentRunner(config, run_trial=run_trial)
    results = runner.run()
 
    csv_path = save_results(results, args.output_dir)
    compute_summary(results)
 
    print(f"Results written to {csv_path}")
 
 
if __name__ == "__main__":
    main()