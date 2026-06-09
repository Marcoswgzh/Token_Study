#refactored by Erika Skodova
# Written by Marcos Wang Zhu, Giorgio Di Rosa

from __future__ import annotations


import itertools
import random
import sys
import time
from datetime import datetime

from recovery_project.config import ExperimentConfig
from recovery_project.domain.models import TrialResult

# Exhaustive and random bruteforce attacks on one specific user
# We are not using parallel guessing algorithms, since it could introduce race conditions
# So we will use simpler sequential algorithms
# We will see in the results that this change will not affect much, since the rate limiter will block the attacker anyway

def send_attack_sequential(trial_id : int, target_token: str, configs: ExperimentConfig) -> TrialResult:
    # initialize values
    tp = configs.token_policy
    rlp = configs.rate_limit_policy
    alphabet = tp.alphabet
    token_length = tp.length
    limit = rlp.max_attempts if rlp.enabled else sys.maxsize
    strategy = configs.strategy if configs.strategy in ("random", "exhaustive") else "random"
    ttl_seconds =  tp.ttl_seconds if tp.ttl_seconds > 0 else sys.maxsize

    attempts = 0
    start = time.time()
    success = False
    print("running trial:",end= " ")
    print(trial_id)

    # Random guessing
    if strategy == "random":
        # Generates random guesses while the attempts limit is not yet reached
        while not (attempts == limit):
            # Make a random guess of the actual token length
            guess_str = "".join(random.choices(alphabet, k=token_length))
            attempts += 1

            if ttl_seconds <= time.time()-start:
                break

            if guess_str == target_token:
                success = True
                print("token found")
                print(guess_str)
                break

    # Exhaustive guessing
    elif strategy == "exhaustive":
        # Generates every possible combination for the exact length
        for guess_tuple in itertools.product(alphabet, repeat=token_length):
            guess_str = "".join(guess_tuple)
            attempts += 1

            if ttl_seconds <= time.time()-start:
                break

            if guess_str == target_token :
                success = True
                print("token found")
                print(guess_str)
                break

    end = time.time()

    return TrialResult(
        trial_id=trial_id,
        experiment_name=configs.name,
        token_length=token_length,
        alphabet_size=len(alphabet),
        ttl_seconds=tp.ttl_seconds,
        rate_limit_enabled=rlp.enabled,
        rate_limit_max_attempts=rlp.max_attempts,
        rate_limit_window_seconds=rlp.window_seconds,
        success=success,
        attempts_made=attempts,
        attempts_blocked=attempts - 1 if success else attempts,
        time_elapsed_ms=round((end - start) * 1000, 4),
        token_expired=not success,
        timestamp=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))