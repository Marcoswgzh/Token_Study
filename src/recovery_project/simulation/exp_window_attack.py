"""Expiration window attack script: use brute force and random sampling of tokens to try to find the active token and exploit logging in"""

# Main writer: Anna Kálmánczhelyi
# Reviewer: Timea Vojcikova

import multiprocessing
import time
import random
from typing import Any

from ..services.token_service import TokenService

# Main writer: Anna Kálmánczhelyi
# Reviewer: Timea Vojcikova
class ExpirationWindowAttacker():
    """Parallel brute force script where we try to guess randomly the token. It's not exhaustive, so we just try random combinations. 
    To generate tokens, we use the TokenService.
    The class returns the result of the attack: whether it was successful or not, how many attempts were made, how long the attack took, how many attempts per second there were made, and what the token is.

    Currently, the success rate seems very low when the alphabet of the token is long, and the token length is long, so some improvement can be researched.

    If the code doesn't run because of the TokenService import, run as a module like:
    "python -m src.recovery_project.simulation.exp_window_attack"
    """
    # Main writer: Anna Kálmánczhelyi
    # Reviewer: Timea Vojcikova
    def attack(self, 
               token_hash:str,
               alphabet: str,
               token_length: int,
               ttl_seconds: int,
               max_attempts_budget: int | None = None,
               attack_rate_per_second: int | None = None,
               num_workers: int = None):
        """Start the attack (parallel random sampling) to find an active and valid recovery token
        
        Return:
            A dict with these params: success (bool), found_token (string), num_attempts (int), time_elapsed (float), attempts_per_sec (int)
        Some of these return values are for research purposes (like time and num of attacks), other than those it's just a structure so that we can work with the results (insert them as recovery tokens)"""

        if attack_rate_per_second is not None:
            return self._rate_bounded_attack(
                token_hash=token_hash,
                alphabet=alphabet,
                token_length=token_length,
                ttl_seconds=ttl_seconds,
                max_attempts_budget=max_attempts_budget,
                attack_rate_per_second=attack_rate_per_second,
            )

        cpu_count = multiprocessing.cpu_count()
        if num_workers is None:
            num_workers = cpu_count

        shared_counter = multiprocessing.Value('i', 0)
        token_found_event = multiprocessing.Event()
        attempts_lock = multiprocessing.Lock()
        start_time = time.time()
        token_queue = multiprocessing.Queue()

        worker_budget = max_attempts_budget // num_workers

        processes = []

        for worker_id in range(num_workers):
            process = multiprocessing.Process(
                target=self._worker_loop,
                args=(worker_id, token_hash, alphabet, token_length, ttl_seconds, worker_budget, token_found_event,shared_counter, attempts_lock, start_time, token_queue)
            )
            processes.append(process)
            process.start()

        # either wait for workers to finish or timeout
        for process in processes:
            process.join(timeout=ttl_seconds +1)
            if process.is_alive():
                process.terminate()
        
        elapsed_time = time.time() - start_time
        total_attempts = shared_counter.value
        if elapsed_time > 0:
            attempts_per_second =  total_attempts / elapsed_time
        else: attempts_per_second = 0

        if token_found_event.is_set():
            found_token = token_queue.get()
        else:
            found_token = None

        return {
            "success": token_found_event.is_set(),
            "found_token": found_token,
            "attempts": total_attempts,
            "time_elapsed": elapsed_time,
            "attempts_per_second": attempts_per_second
        }

    # Main writer Anna Kálmánczhelyi 
    # Reviewer: Timea Vojcikova
    @staticmethod
    def _rate_bounded_attack(
        token_hash: str,
        alphabet: str,
        token_length: int,
        ttl_seconds: int,
        max_attempts_budget: int | None = None,
        attack_rate_per_second: int | None = None,
    ):
        """Run the expiration-window attack using real wall-clock time.
        The attack continues until either the token is found, or the TTL expires.
        """
        print("USING WALL CLOCK VERSION") #debug statement
        service = TokenService(
            alphabet=alphabet,
            token_length=token_length,
        )

        start_time = time.time()
        attempts = 0

        while (time.time() - start_time) < ttl_seconds:

            candidate = ''.join(
                random.choice(alphabet)
                for _ in range(token_length)
            )

            attempts += 1

            if service.verify_token(candidate, token_hash):
                elapsed_time = time.time() - start_time

                return {
                    "success": True,
                    "found_token": candidate,
                    "attempts": attempts,
                    "time_elapsed": elapsed_time,
                    "attempts_per_second": (
                        attempts / elapsed_time
                        if elapsed_time > 0
                        else 0
                    ),
                }

        elapsed_time = time.time() - start_time

        return {
            "success": False,
            "found_token": None,
            "attempts": attempts,
            "time_elapsed": elapsed_time,
            "attempts_per_second": (
                attempts / elapsed_time
                if elapsed_time > 0
                else 0
            ),
        }

        
    # Main writer: Anna Kálmánczhelyi
    # Reviewer: Timea Vojcikova
    @staticmethod
    def _worker_loop(worker_id: int, 
                     token_hash:str,
                     alphabet: str, 
                     token_length: int,
                     ttl_seconds: int,
                     worker_budget: int,
                     token_found_event: Any,
                     attempts_counter: Any,
                     attempts_lock: Any,
                     start_time: float,
                     token_queue: Any
                     ):
        """This is what a worker does: generates random guesses over and over in the guess-space and verifies it against the hash value.
        The search stops when 1 of these is true: a token is found, the attempt budget is exceeded, or the TTL expires.
        There's also a shared counter that needs to be updated for syncing purposes, and token_found_event notifies other threads that a valid token was found and they can stop their search.
        """
        attempts = 0
        
        while not token_found_event.is_set() and attempts < worker_budget:
            # check if time has expired
            if (time.time() - start_time) > ttl_seconds:
                break

            # generate a random canditate token (a guess)
            candidate = ''.join(random.choice(alphabet) for _ in range(token_length))

            # verify if candidate matches the hash
            service = TokenService()
            if service.verify_token(candidate, token_hash):
                token_queue.put(candidate) # send the found token back to main 
                token_found_event.set() #set flag to true
                break

            # increment attempt count
            attempts += 1

            # update shared counter (need the lock for avoiding race condition)
            with attempts_lock:
                attempts_counter.value += 1

# Main writer: Anna Kálmánczhelyi
# Reviewer: Timea Vojcikova
if __name__ == "__main__":
    """This is for testing purposes. The commented out lines are there for initial testing: smaller alphabet and token length because the brute force has a tendency to run out of time on bigger alphabets and longer token lengths before finding a good token."""

    service = TokenService()
    #service = TokenService(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", token_length=4)
    token, token_hash = service.generate_token()
    print(f"Generated token: {token}, with hash: {token_hash}")

    attacker = ExpirationWindowAttacker()
    result = attacker.attack(
        token_hash=token_hash,
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        #alphabet="0123456789",
        token_length=10,
        #token_length=4,
        ttl_seconds=3000000,
        max_attempts_budget=5000000000000000,
    )
    print(f"Success: {result['success']}")
    print(f"Found token: {result['found_token']}")
    print(f"Attempts: {result['attempts']}")
    print(f"Time: {result['time_elapsed']:.3f}s")
    print(f"Rate: {result['attempts_per_second']:.0f} attempts/sec")
