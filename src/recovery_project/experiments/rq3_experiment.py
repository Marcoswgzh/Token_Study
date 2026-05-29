import csv
import itertools
import json
import sys
import time
from pathlib import Path

root_route = str(Path(__file__).resolve().parents[3])

if root_route not in sys.path:
    sys.path.append(root_route)

from src.recovery_project.config import TokenPolicy
from src.recovery_project.services.rate_limiter import RateLimiter
from src.recovery_project.services.token_service import TokenService


# Bruteforce attack on one specific user (target_email), respecting the rate limiter. Returns a dictionary with different metrics
# We are not using the parallel guessing algorithm, since it would require making the rate limiter parallel to avoid race conditions
# So we will use a simpler sequential algorithm
# We will see in the results that this change will not affect too much, since the rate limiter will block the attacker anyways
def rate_limited_attack(
    target_token: str, limiter: RateLimiter, target_email: str, policy: TokenPolicy
) -> dict:
    attempts_made = 0
    start = time.time()

    # This outer loop controls the length of the token we are guessing, so it first guesses token with length 1, then length 2, and so on
    # We could potentially change this so that it only guesses tokens with the correct length
    for current_length in range(1, policy.length + 1):
        # Check if the user is already locked out before we even start generating combinations
        if limiter.is_locked(target_email):
            break
        
        # Generates every possible combination for the current length
        for guess_tuple in itertools.product(policy.alphabet, repeat=current_length):
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

        # If the inner loop stopped because the token was guessed,
        # or we got locked out, we must also break the outer loop to completely stop.
        if limiter.is_locked(target_email) or guess_str == target_token:
            break

    end = time.time()

    return {
        "Email": target_email,
        "Total guesses made": attempts_made,
        "Time alive (ms)": round((end - start) * 1000, 4),
        "Result": "Blocked" if limiter.is_locked(target_email) else "Cracked",
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


# Run a batch of attacks and save results to csv
def run_rq3_exp(
    total_runs: int, output_filename: str, policy: TokenPolicy, limiter: RateLimiter
):
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
        )

        results_data.append(result)

    save_to_csv(results_data, output_filename)


# Run the experiments using the parameters in the JSON file
def run_with_json(json_filepath: str):
    with open(json_filepath, 'r') as file:
        experiments_data = json.load(file)

    # Iterate over every experiment in the JSON file
    for experiments in experiments_data:
        exp_name = experiments["name"] 
        trials = experiments["trials"]

        # Extract token settings and build token policy object
        token_config = experiments["token_policy"]
        policy = TokenPolicy(length=token_config["length"], alphabet=token_config["alphabet"])

        # Extract rate limiter settings and build rate limiter object
        rate_config = experiments["rate_limit_policy"]
        limiter = RateLimiter(max_attempts=rate_config["max_attempts"], window_seconds=rate_config["window_seconds"])

        # Name the output file based on the experiment name
        # Each experiment will have a different csv file
        output_csv = f"{exp_name}_results.csv"

        # Pass all objects to the runner to perform the experiments
        run_rq3_exp(
            total_runs=trials,
            output_filename=output_csv,
            policy=policy,
            limiter=limiter
        )

        
if __name__ == "__main__":
    run_with_json("configs/experiments/rq3_rate_limiting.json")
