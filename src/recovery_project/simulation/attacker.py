"""Automated attacker behavior placeholder (brute-force recovery guesses)."""
# Writer: Marcos Wang Zhu

import math
import multiprocessing
import time

from src.recovery_project.simulation.bruteforce import split_string, guess_parallel

class Attacker:
    def __init__(self, alphabet: str):
        self.alphabet = alphabet
        self.num_processes = min(multiprocessing.cpu_count(), len(self.alphabet))
    
    def send_attack(self, target: str, length: int) -> None:
        start = time.time()
        with multiprocessing.Manager() as manager:
            found_event = manager.Event()
            
            print("\nBrute force check:")

            for current_length in range(1, length + 1):
                if found_event.is_set():
                    break
                
                print(f"Trying all combinations of length {current_length}")
                chunk_size = math.ceil(len(self.alphabet) / self.num_processes)
                alphabet_chunks = split_string(self.alphabet, chunk_size)

                processes = []
                suffix_length = current_length - 1

                for chunk in alphabet_chunks:
                    process = multiprocessing.Process(target=guess_parallel, args=(target, chunk, self.alphabet, suffix_length, found_event))
                    processes.append(process)
                    process.start()

                for process in processes:
                    process.join()
        
        end = time.time()
        elapsed_ms = (end - start) * 1000

        return elapsed_ms