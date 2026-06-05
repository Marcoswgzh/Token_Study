from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import json

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

#todo fix .json files: include strategy (rq2 = NONE), attack_rate_per_seconds(rq2 = -1), in token_policy ttl(rq3 = -1), in rate_limit_policy everything(rq2 = everything -1)
#TODO delete attack_attempt_budget from rq2 and 3 .jsons
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