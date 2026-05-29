import hashlib

from recovery_project.simulation.exp_window_attack import ExpirationWindowAttacker


def test_expiration_attack_is_limited_by_ttl_and_attack_rate():
    attacker = ExpirationWindowAttacker()
    impossible_hash = hashlib.sha256("B".encode()).hexdigest()

    result = attacker.attack(
        token_hash=impossible_hash,
        alphabet="A",
        token_length=1,
        ttl_seconds=3,
        max_attempts_budget=100,
        attack_rate_per_second=2,
    )

    assert result["success"] is False
    assert result["attempts"] == 6
    assert result["time_elapsed"] == 3
    assert result["attempts_per_second"] == 2


def test_expiration_attack_is_limited_by_budget_when_budget_is_smaller():
    attacker = ExpirationWindowAttacker()
    impossible_hash = hashlib.sha256("B".encode()).hexdigest()

    result = attacker.attack(
        token_hash=impossible_hash,
        alphabet="A",
        token_length=1,
        ttl_seconds=30,
        max_attempts_budget=5,
        attack_rate_per_second=2,
    )

    assert result["success"] is False
    assert result["attempts"] == 5
    assert result["time_elapsed"] == 2.5
    assert result["attempts_per_second"] == 2
