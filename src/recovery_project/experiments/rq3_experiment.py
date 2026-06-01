# Writers: Marcos Wang Zhu, Giorgio Di Rosa

import csv
import itertools
import json
import sys
import time
import random
from pathlib import Path

root_route = str(Path(__file__).resolve().parents[3])

if root_route not in sys.path:
    sys.path.append(root_route)

from src.recovery_project.config import TokenPolicy
from src.recovery_project.services.rate_limiter import RateLimiter
from src.recovery_project.services.token_service import TokenService


# Exhaustive and random bruteforce attacks on one specific user (target_email), respecting the rate limiter. Returns a dictionary with different metrics
# We are not using parallel guessing algorithms, since it would require making the rate limiter parallel to avoid race conditions
# So we will use simpler sequential algorithms
# We will see in the results that this change will not affect much, since the rate limiter will block the attacker anyway
def rate_limited_attack(
    target_token: str, limiter: RateLimiter, target_email: str, policy: TokenPolicy, strategy: str
) -> dict:
    attempts_made = 0
    start = time.time()

    # Check if the user is already locked out before we even start generating combinations
    if not limiter.is_locked(target_email):
        # Random guessing
        if strategy == "random":
            # Generates random guesses while the attempts limit is not yet reached
            while not limiter.is_locked(target_email):
                # Make a random guess of the actual token length
                guess_str = "".join(random.choices(policy.alphabet, k=policy.length))

                attempts_made += 1

                # Check if the token was correctly guessed
                if guess_str == target_token:
                    limiter.record_success(target_email)
                    break
                else:
                    limiter.record_failure(target_email)
        elif strategy == "exhaustive":
            # Generates every possible combination for the exact length
            for guess_tuple in itertools.product(policy.alphabet, repeat=policy.length):
                guess_str = "".join(guess_tuple)

                # Stop processing if the email is locked
                if limiter.is_locked(target_email):
                    break

                attempts_made += 1

                # Check if the token was correctly guessed
                if guess_str == target_token:
                    limiter.record_success(target_email)
                    break
                else:
                    limiter.record_failure(target_email)

    end = time.time()

    return {
        "Strategy": strategy,
        "Email": target_email,
        "Total guesses made": attempts_made,
        "Time alive (ms)": round((end - start) * 1000, 4),
        "Result": "Blocked" if limiter.is_locked(target_email) else "Cracked"
    }


# Take a list of dictionaries and export them into a csv file
def save_to_csv(data: list[dict], filename: str):
    # Do nothing if the data is empty
    if not data:
        return

    filepath = Path(filename)
    # Take the column names from the keys of the very first dictionary
    headers = data[0].keys()

    with open(filepath, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        # Writes the top row (column names)
        writer.writeheader()
        # Writes all the actual data rows at once
        writer.writerows(data)


# Run a batch of attacks and return results as a list
def run_rq3_exp(
    total_runs: int, exp_name: str, policy: TokenPolicy, limiter: RateLimiter, strategy: str
) -> list[dict]:
    service = TokenService(policy.alphabet, policy.length)
    results_data = []

    # Run the exact number of trials requested
    for id in range(1, total_runs + 1):
        # Generate an email so the rate limiter treats each loop as a new user
        email = str(id)
        target_token, _ = service.generate_token()

        # Launch the attack and capture the resulting dictionary
        result = rate_limited_attack(
            target_token=target_token,
            limiter=limiter,
            target_email=email,
            policy=policy,
            strategy=strategy
        )

        result["Experiment"] = exp_name
        results_data.append(result)

    return results_data


# Run the experiments using the parameters in the JSON file
def run_with_json(json_filepath: str):
    with open(json_filepath, "r") as file:
        experiments_data = json.load(file)

    all_results = []

    # Iterate over every experiment in the JSON file
    for experiments in experiments_data:
        exp_name = experiments["name"]
        trials = experiments["trials"]
        strategy = experiments["strategy"]

        # Extract token settings and build token policy object
        token_config = experiments["token_policy"]
        policy = TokenPolicy(
            length=token_config["length"], alphabet=token_config["alphabet"]
        )

        # Extract rate limiter settings and build rate limiter object
        rate_config = experiments["rate_limit_policy"]
        limiter = RateLimiter(
            max_attempts=rate_config["max_attempts"],
            window_seconds=rate_config["window_seconds"],
        )

        results = run_rq3_exp(
            total_runs=trials,
            exp_name=exp_name,
            policy=policy,
            limiter=limiter,
            strategy=strategy
        )
        all_results.extend(results)
    
    # Create a separate CSV file for each strategy
    exhaustive_results = []
    random_results = []

    for row in all_results:
        if row["Strategy"] == "exhaustive":
            exhaustive_results.append(row)
        elif row["Strategy"] == "random":
            random_results.append(row)
        
    save_to_csv(exhaustive_results, "rq3_exhaustive_results.csv")
    save_to_csv(random_results, "rq3_random_results.csv")


if __name__ == "__main__":
    run_with_json("configs/experiments/rq3_rate_limiting.json")
