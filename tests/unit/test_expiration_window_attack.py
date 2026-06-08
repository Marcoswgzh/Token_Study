#written by Erika Skodova
import recovery_project.attacker_algorithms.non_parallel_attacker as non_parallel_attacker
from recovery_project.config import ExperimentConfig, TokenPolicy, RateLimitPolicy
from recovery_project.attacker_algorithms import parallel_attacker


def test_expiration_attack_is_limited_by_ttl_using_random_algorithm():
    attacker = non_parallel_attacker

    result = attacker.send_attack_sequential(1, "B",
                                             ExperimentConfig(name = "test1",
                                                             trials = 1,
                                                             strategy = "random",
                                                             attack_rate_per_second = 2,
                                                             token_policy = TokenPolicy(length = 1,
                                                                                        alphabet = "A",
                                                                                        ttl_seconds = 1,
                                                                                        single_use = True),
                                                             rate_limit_policy = RateLimitPolicy(enabled = True,
                                                                                                 max_attempts= 100000000,
                                                                                                 window_seconds = 60)))

    assert result.success is False
    assert result.attempts_made <= 100000000
    assert 1000 < result.time_elapsed_ms < 1100

def test_expiration_attack_is_limited_by_ttl_using_exhaustive_algorithm():
    attacker = non_parallel_attacker

    result = attacker.send_attack_sequential(1, "BCDEFGH",
                                             ExperimentConfig(name = "test1",
                                                             trials = 1,
                                                             strategy = "exhaustive",
                                                             attack_rate_per_second = 2,
                                                             token_policy = TokenPolicy(length = 7,
                                                                                        alphabet = "ACDEFG1234567890",
                                                                                        ttl_seconds = 1,
                                                                                        single_use = True),
                                                             rate_limit_policy = RateLimitPolicy(enabled = True,
                                                                                                 max_attempts= 100000000,
                                                                                                 window_seconds = 60)))

    assert result.success is False
    assert result.attempts_made <= 100000000
    assert result.time_elapsed_ms < 1100

def test_expiration_attack_is_limited_by_ttl_using_parallel_algorithm():
    attacker = parallel_attacker

    result = attacker.send_attack_parallel(1, "B123456",
                                           ExperimentConfig(name = "test1",
                                                             trials = 1,
                                                             strategy = "parallel",
                                                             attack_rate_per_second = 2,
                                                             token_policy = TokenPolicy(length = 7,
                                                                                        alphabet = "ACDEFG1234567890",
                                                                                        ttl_seconds = 1,
                                                                                        single_use = True),
                                                             rate_limit_policy = RateLimitPolicy(enabled = True,
                                                                                                 max_attempts= -1,
                                                                                                 window_seconds = -1)))

    assert result.success is False
    assert 1000 < result.time_elapsed_ms < 3000 #added 2s buffer for initialization and data collection

def test_expiration_attack_is_limited_by_budget_when_budget_is_smaller_using_exhaustive():
    attacker = non_parallel_attacker

    result=attacker.send_attack_sequential(1, "B",
                                           ExperimentConfig(name="test1",
                                                     trials=1,
                                                     strategy="exhaustive",
                                                     attack_rate_per_second=2,
                                                     token_policy=TokenPolicy(length=1,
                                                                              alphabet="A",
                                                                              ttl_seconds=30,
                                                                              single_use=True),
                                                     rate_limit_policy=RateLimitPolicy(enabled=True,
                                                                                       max_attempts=5,
                                                                                       window_seconds=60)))

    assert result.success is False
    assert result.attempts_made == 1
    assert result.time_elapsed_ms < 3000


def test_expiration_attack_is_limited_by_budget_when_budget_is_smaller_using_random():
    attacker = non_parallel_attacker

    result=attacker.send_attack_sequential(1, "B",
                                           ExperimentConfig(name="test1",
                                                     trials=1,
                                                     strategy="random",
                                                     attack_rate_per_second=2,
                                                     token_policy=TokenPolicy(length=1,
                                                                              alphabet="A",
                                                                              ttl_seconds=30,
                                                                              single_use=True),
                                                     rate_limit_policy=RateLimitPolicy(enabled=True,
                                                                                       max_attempts=5,
                                                                                       window_seconds=60)))

    assert result.success is False
    assert result.attempts_made == 5
    assert result.time_elapsed_ms < 3000

def test_expiration_attack_successful_when_using_exhaustive():
    attacker = non_parallel_attacker

    result=attacker.send_attack_sequential(1, "B",
                                           ExperimentConfig(name="test1",
                                                     trials=1,
                                                     strategy="exhaustive",
                                                     attack_rate_per_second=2,
                                                     token_policy=TokenPolicy(length=1,
                                                                              alphabet="ABC",
                                                                              ttl_seconds=30,
                                                                              single_use=True),
                                                     rate_limit_policy=RateLimitPolicy(enabled=True,
                                                                                       max_attempts=5,
                                                                                       window_seconds=60)))

    assert result.success is True
    assert result.attempts_made <= 3
    assert result.time_elapsed_ms < 3000


#might fail bc it guesses random so it can reuse already tried variation thus never actually trying the correct one
def test_expiration_attack_successful_when_using_random():
    attacker = non_parallel_attacker

    result=attacker.send_attack_sequential(1, "B",
                                           ExperimentConfig(name="test1",
                                                     trials=1,
                                                     strategy="random",
                                                     attack_rate_per_second=2,
                                                     token_policy=TokenPolicy(length=1,
                                                                              alphabet="ABC",
                                                                              ttl_seconds=30,
                                                                              single_use=True),
                                                     rate_limit_policy=RateLimitPolicy(enabled=True,
                                                                                       max_attempts=5,
                                                                                       window_seconds=60)))

    assert result.success is True
    assert result.attempts_made <= 5
    assert result.time_elapsed_ms < 3000

def test_expiration_attack_successful_when_using_random_with_alphabet_len_1():
    attacker = non_parallel_attacker

    result=attacker.send_attack_sequential(1, "B",
                                           ExperimentConfig(name="test1",
                                                     trials=1,
                                                     strategy="random",
                                                     attack_rate_per_second=2,
                                                     token_policy=TokenPolicy(length=1,
                                                                              alphabet="B",
                                                                              ttl_seconds=30,
                                                                              single_use=True),
                                                     rate_limit_policy=RateLimitPolicy(enabled=True,
                                                                                       max_attempts=5,
                                                                                       window_seconds=60)))

    assert result.success is True
    assert result.attempts_made <= 1
    assert result.time_elapsed_ms < 3000


def test_expiration_attack_successful_when_using_parallel():
    attacker = parallel_attacker

    result=attacker.send_attack_parallel(1, "B",
                                         ExperimentConfig(name="test1",
                                                     trials=1,
                                                     strategy="parallel",
                                                     attack_rate_per_second=2,
                                                     token_policy=TokenPolicy(length=1,
                                                                              alphabet="ABC",
                                                                              ttl_seconds=30,
                                                                              single_use=True),
                                                     rate_limit_policy=RateLimitPolicy(enabled=True,
                                                                                       max_attempts=5,
                                                                                       window_seconds=60)))

    assert result.success is True
    assert result.attempts_made <= 3
    assert result.time_elapsed_ms < 5000 #added 2 s buffer for initialization and data collection