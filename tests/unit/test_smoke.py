from recovery_project.config import RateLimitPolicy, TokenPolicy


def test_config_defaults() -> None:
    token = TokenPolicy()
    rl = RateLimitPolicy()
    assert token.length > 0
    assert rl.max_attempts > 0
