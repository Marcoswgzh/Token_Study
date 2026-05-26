"""Bruteforce attack script: parallel approach for token guessing"""
"""Right now it is too slow, so improvements are needed"""

# Writer: Marcos Wang Zhu 

from multiprocessing.synchronize import Event
import itertools

# Splits the alphabet into chunksize chunks
def split_string(s: str, chunksize: int) -> list:
    chunks = []
    for i in range(0, len(s), chunksize):
        chunks.append(s[i:i+chunksize])
    return chunks

# Guesses the token by locking in one starting letter at a time from the assigned chunk
# It then generates and tests every possible suffix for that specific letter
# Once all suffixes for that letter are exhausted, it moves to the next starting letter
def guess_parallel(token: str, alphabet_chunk: str, full_alphabet: str, suffix_length: int, found_event: Event) -> None:
    for first_char in alphabet_chunk:
        if found_event.is_set():
            return
        for suffix_tuple in itertools.product(full_alphabet, repeat=suffix_length):
            if found_event.is_set():
                return
            suffix_string = "".join(suffix_tuple)
            if first_char + suffix_string == token:
                print(f"Token found: {token}") 
                found_event.set()
                return
            
