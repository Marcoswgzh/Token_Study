from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class TokenPolicy:
    length: int = 6
    alphabet: str = "0123456789ABCDEF"
    ttl_seconds: int = 300
    single_use: bool = True


@dataclass(slots=True)
class RateLimitPolicy:
    enabled: bool = False
    max_attempts: int = 5
    window_seconds: int = 60


@dataclass(slots=True)
class ExperimentConfig:
    name: str
    trials: int
    attack_attempt_budget: int
    attack_rate_per_second: int
    token_policy: TokenPolicy
    rate_limit_policy: RateLimitPolicy

#function written by Giorgio Di Rosa
def load_experiment_config(path: Path | str) -> ExperimentConfig:
    """Load an experiment configuration from a YAML file."""
    with open(path, "r") as fh:
        raw = yaml.safe_load(fh)

    token_policy = TokenPolicy(**raw.get("token_policy", {}))
    rate_limit_policy = RateLimitPolicy(**raw.get("rate_limit_policy", {}))

    return ExperimentConfig(
        name=raw["name"],
        trials=raw["trials"],
        attack_attempt_budget=raw["attack_attempt_budget"],
        attack_rate_per_second=raw["attack_rate_per_second"],
        token_policy=token_policy,
        rate_limit_policy=rate_limit_policy,
    )
