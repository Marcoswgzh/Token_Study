from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import json

## Structured data classes used throughout the project for experiment configurations
#written by Sofya Grishkova
@dataclass(slots=True)
class TokenPolicy:
    length: int = 6
    alphabet: str = "0123456789ABCDEF"
    ttl_seconds: int = 300
    single_use: bool = True

#written by Sofya Grishkova
@dataclass(slots=True)
class RateLimitPolicy:
    enabled: bool = False
    max_attempts: int = 5
    window_seconds: int = 60

#written by Sofya Grishkova
@dataclass(slots=True)
class ExperimentConfig:
    name: str
    trials: int
    strategy: str
    attack_rate_per_second: int
    token_policy: TokenPolicy
    rate_limit_policy: RateLimitPolicy

#function written by Giorgio Di Rosa
def load_experiment_config(file_name: str ) -> list[ExperimentConfig]:
    base_dir = Path(__file__).resolve().parent.parent.parent
    config_path = base_dir / "configs" / "experiments"/ file_name
    with open(config_path, "r") as f:
        raw = json.load(f)

    configs = []

    for experiment in raw:
        token_policy = TokenPolicy(**experiment["token_policy"])
        rate_limit_policy = RateLimitPolicy(**experiment["rate_limit_policy"])
        configs.append(ExperimentConfig(
            name=experiment["name"],
            trials=experiment["trials"],
            strategy= experiment["strategy"],
            attack_rate_per_second=experiment["attack_rate_per_second"],
            token_policy=token_policy,
            rate_limit_policy=rate_limit_policy,
        ))
    return configs