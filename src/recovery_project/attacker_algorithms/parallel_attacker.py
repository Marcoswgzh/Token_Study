#refactored by Erika Skodova
# Writer: Marcos Wang Zhu

import math
import multiprocessing
import sys
import time
from datetime import datetime

from recovery_project.config import ExperimentConfig
from recovery_project.domain.models import TrialResult
import recovery_project.attacker_algorithms.bruteforce as bf

def send_attack(trail_id: int, target: str, configs: ExperimentConfig) -> TrialResult:
        # Initialize variables
        global found_token
        length = configs.token_policy.length
        tp = configs.token_policy
        rlp =  configs.rate_limit_policy
        ttl_seconds = tp.ttl_seconds if rlp.enabled else sys.maxsize
        alphabet = tp.alphabet
        num_processes = min(multiprocessing.cpu_count(), len(alphabet))
        start = time.time()
        with multiprocessing.Manager():

            print("\nBrute force check:")
            # Split alphabet into chunks for faster checking
            print(f"Trying all combinations of length {length}")
            chunk_size = math.ceil(len(alphabet) / num_processes)
            alphabet_chunks = split_string(alphabet, chunk_size)

            # Initialize variables used in parallel processes
            result = multiprocessing.Value('b', 0)
            multi_value = multiprocessing.Value('i', 0)
            found_token_buf = multiprocessing.Array('c', 256)
            processes = []
            suffix_length = length - 1

            # Run parallel bruteforce
            for chunk in alphabet_chunks:
                process = multiprocessing.Process(target=bf.guess_parallel, args=(ttl_seconds + time.time(), target, chunk, alphabet, suffix_length, multi_value, result,found_token_buf))
                processes.append(process)
                process.start()

            for process in processes:
                process.join()

            total_attempts = multi_value.value
            success = bool(result.value)
            found_token = found_token_buf.value.decode() if success else ""
        end = time.time()

        return TrialResult(
            trial_id=trail_id,
            experiment_name=configs.name,
            token_length=length,
            alphabet_size=len(alphabet),
            ttl_seconds=tp.ttl_seconds,
            rate_limit_enabled=rlp.enabled,
            rate_limit_max_attempts=rlp.max_attempts,
            rate_limit_window_seconds=rlp.window_seconds,
            success=success,
            attempts_made=total_attempts,
            attempts_blocked= total_attempts - 1 if success else total_attempts,
            time_elapsed_ms=round((end - start) * 1000, 4),
            token_expired=not success,
            timestamp=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

# Splits the alphabet into chunksize chunks
def split_string(s: str, chunksize: int) -> list:
    chunks = []
    for i in range(0, len(s), chunksize):
        chunks.append(s[i:i+chunksize])
    return chunks

found_token = ""

def get_token()->str:
    return found_token