"""Bruteforce attack script: both serial and parallel approaches for token guessing"""
"""Right now it is too slow, so improvements are needed"""

import math
import multiprocessing
from multiprocessing.synchronize import Event
from pathlib import Path
import string
import itertools
import sys
import time

root_route = str(Path(__file__).resolve().parents[3])

if root_route not in sys.path:
    sys.path.append(root_route)
    
from src.recovery_project.services.token_service import TokenService

# Characters included in the token. We can increase this by adding string.digits (digits from 0 to 9) and/or string.punctuation (special characters)
default_alphabet = string.ascii_letters

# Splits the alphabet into chunksize chunks
def split_string(s: str, chunksize: int):
    chunks = []
    for i in range(0, len(s), chunksize):
        chunks.append(s[i:i+chunksize])
    return chunks

# Guesses the token serially by testing every single combination using itertool.product. The return None is for guessing for every length. Explained later on
def guess_serial(token: str, token_length: int, alphabet: str):
    for tuple in itertools.product(alphabet, repeat=token_length):
        candidate = "".join(tuple)
        if candidate == token:
            print(f"Token found: {candidate}")
            return
    # return None

# Guesses the token by iterating over a list of all suffixes, then trying every combination with every suffix and every first character
# Then the next suffix in the list turns into the fixed suffix and so on
def guess_parallel(token: str, suffix_combinations: list, found_event: Event):
    for first_char in default_alphabet:
        if found_event.is_set():
            return
        for rest in suffix_combinations:
            if found_event.is_set():
                return
            if first_char + "".join(rest) == token:
                print(f"Token found: {first_char + ''.join(rest)}") 
                found_event.set()
                return
            
if __name__ == "__main__":
    # Ask for user input (includes number of processes for parallel version)
    try:
        length = int(input("Select token length: "))
    except ValueError:
        print("Enter a valid integers")
        exit()
    
    # Make sure there are no more processes than characters in the alphabet
    num_processes = min(multiprocessing.cpu_count(), len(default_alphabet))

    # Generate a token
    service = TokenService(alphabet=default_alphabet, token_length=length)
    token, token_hash =service.generate_token()
    print(f"Token to find: {token}") 
    found_event = multiprocessing.Event()

    # BRUTE FORCE
    print("\nBrute force check:")
    start = time.time()

    # Create the list of suffixes and divide it in chunks
    all_suffixes = list(itertools.product(default_alphabet, repeat=length - 1))
    chunks = split_string(all_suffixes, math.ceil(len(all_suffixes)/num_processes))

    processes = []

    # Right now, the uncommented code guesses only tokens with the given length. To make it truly bruteforce, ucomment the for loop and the found event check
    # for length in range(1, max_length + 1):
    for i in range(len(chunks)):
        process = multiprocessing.Process(target=guess_parallel, args=(token, chunks[i], found_event))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # if found_event.is_set():
        #break

    end = time.time()
    print(f"It took {(end - start) * 1000} ms to guess the token")

    # Guess the token serially
    '''start = time.time()
    for length in range(1, max_length + 1):
    result = guess_serial(token, length, alphabet)
    if result is not None:
        break
    print(result)
    end = time.time()
    print(f"It took {(end - start) * 1000} ms to guess the token")'''