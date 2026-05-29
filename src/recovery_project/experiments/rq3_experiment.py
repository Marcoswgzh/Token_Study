import csv
import itertools
import sys
import time
from pathlib import Path

root_route = str(Path(__file__).resolve().parents[3])

if root_route not in sys.path:
    sys.path.append(root_route)

from src.recovery_project.config import TokenPolicy
from src.recovery_project.services.rate_limiter import RateLimiter
from src.recovery_project.services.token_service import TokenService


def rate_limited_attack(
    target_token: str, limiter: RateLimiter, target_email: str, policy: TokenPolicy
) -> dict:
    attempts_made = 0
    start = time.time()

    for current_length in range(1, policy.length + 1):
        if limiter.is_locked(target_email):
            break

        for guess_tuple in itertools.product(policy.alphabet, repeat=current_length):
            guess_str = "".join(guess_tuple)

            if limiter.is_locked(target_email):
                break

            attempts_made += 1

            if guess_str == target_token:
                limiter.record_success(target_email)
                break
            else:
                limiter.record_failure(target_email)

        if limiter.is_locked(target_email) or guess_str == target_token:
            break

    end = time.time()

    return {
        "Email": target_email,
        "Total guesses made": attempts_made,
        "Time alive (ms)": round((end - start) * 1000, 4),
        "Result": "Blocked" if limiter.is_locked(target_email) else "Cracked",
    }


def save_to_csv(data: list[dict], filename: str):
    if not data:
        return

    filepath = Path(filename)
    headers = data[0].keys()

    with open(filepath, mode="w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)


def run_rq3_exp(
    total_runs: int, output_filename: str, policy: TokenPolicy, limiter: RateLimiter
):
    service = TokenService(policy.alphabet, policy.length)
    results_data = []

    for id in range(1, total_runs + 1):
        email = str(id)
        target_token, _ = service.generate_token()
        result = rate_limited_attack(
            target_token=target_token,
            limiter=limiter,
            target_email=email,
            policy=policy,
        )
        results_data.append(result)

    save_to_csv(results_data, output_filename)


if __name__ == "__main__":
    policy = TokenPolicy(2, "0123456789")
    limiter = RateLimiter(100, 60)
    run_rq3_exp(
        total_runs=10, output_filename="test.csv", policy=policy, limiter=limiter
    )
