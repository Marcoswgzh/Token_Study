from dataclasses import dataclass


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
