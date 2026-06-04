"""Bruteforce attack script: parallel approach for token guessing"""

# Writer: Marcos Wang Zhu
import time
import queue

from multiprocessing.synchronize import Event
import itertools

# Guesses the token by locking in one starting letter at a time from the assigned chunk
# It then generates and tests every possible suffix for that specific letter
# Once all suffixes for that letter are exhausted, it moves to the next starting letter
def guess_parallel(end: int, token: str, alphabet_chunk: str, full_alphabet: str, suffix_length: int, found_event: Event, result_que: queue) -> None:
    attempts = 0
    for first_char in alphabet_chunk:
        if found_event.is_set() or time.time() > end:
            result_que.put((attempts, False))
            return
        for suffix_tuple in itertools.product(full_alphabet, repeat=suffix_length):
            if found_event.is_set() or time.time() > end:
                result_que.put((attempts, False))
                return
            suffix_string = "".join(suffix_tuple)
            attempts += 1
            if first_char + suffix_string == token:
                print(f"Token found: {token}") 
                found_event.set()
                result_que.put((attempts, True))
                return
            
