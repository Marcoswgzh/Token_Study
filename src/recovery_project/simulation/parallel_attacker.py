#refactored by Erika Skodova
# Writer: Marcos Wang Zhu

import math
import multiprocessing
import time
from datetime import datetime

from recovery_project.config import ExperimentConfig
from recovery_project.domain.models import TrialResult
from src.recovery_project.simulation.bruteforce import guess_parallel

def send_attack(trail_id: int, target: str, configs: ExperimentConfig) -> TrialResult:
        length = configs.token_policy.length
        tp = configs.token_policy
        rlp =  configs.rate_limit_policy
        ttl_seconds = tp.ttl_seconds
        alphabet = tp.alphabet
        num_processes = min(multiprocessing.cpu_count(), len(alphabet))
        start = time.time()
        with multiprocessing.Manager() as manager:
            found_event = manager.Event()

            print("\nBrute force check:")

            print(f"Trying all combinations of length {length}")
            chunk_size = math.ceil(len(alphabet) / num_processes)
            alphabet_chunks = split_string(alphabet, chunk_size)

            result_queue = multiprocessing.Queue()
            processes = []
            suffix_length = length - 1

            for chunk in alphabet_chunks:
                process = multiprocessing.Process(target=guess_parallel, args=(ttl_seconds + time.time(), target, chunk, alphabet, suffix_length, found_event,result_queue))
                processes.append(process)
                process.start()

            for process in processes:
                process.join()

            total_attempts = 0
            success = False
            for _ in processes:
                attempts, found = result_queue.get()
                total_attempts += attempts

                if found:
                    success = True

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
            attempts_blocked= total_attempts - 1 if not success else total_attempts,
            time_elapsed_ms=round((end - start) * 1000, 4),
            token_expired=not success,
            timestamp=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

# Splits the alphabet into chunksize chunks
def split_string(s: str, chunksize: int) -> list:
    chunks = []
    for i in range(0, len(s), chunksize):
        chunks.append(s[i:i+chunksize])
    return chunks