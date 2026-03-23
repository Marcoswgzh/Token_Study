"""Token generation/validation helpers placeholder."""

import math
import multiprocessing
import secrets
import string
import itertools
import time

alphabet = string.ascii_letters

def generate_token(length):
    token = ""
    for i in range(length):
        token += secrets.choice(alphabet)
    return token

def guess_parallel(token, token_length, alphabet_chunk, found_event):
    for first_char in alphabet_chunk:
        for rest in itertools.product(alphabet, repeat = token_length - 1):
            if found_event.is_set():
                return
            candidate = first_char + "".join(rest)
            if candidate == token:
                print(f"Token found: {candidate}") 
                found_event.set()
                return
    
def guess_serial(token, token_length, alphabet):
    for tuple in itertools.product(alphabet, repeat=token_length):
        candidate = "".join(tuple)
        if candidate == token:
            print(f"Token found: {candidate}")
            return

def split_string(s, chunksize):
    chunks = []
    for i in range(0, len(s), chunksize):
        chunks.append(s[i:i+chunksize])
    return chunks

if __name__ == "__main__":
    try:
        length = int(input("Select token length: "))
        num_processes = int(input("Select number of threads to be used: "))
    except ValueError:
        print("Enter a valid integers")
        exit()
    
    num_processes = min(num_processes, len(alphabet))

    token = generate_token(length)
    print(f"Token to find: {token}") 
    found_event = multiprocessing.Event()

    start = time.time()

    alphabet_chunksize = math.ceil(len(alphabet) / num_processes)
    alphabet_chunks = split_string(alphabet, alphabet_chunksize)

    processes = []

    # for length in range(1, max_length + 1):
    for i in range(num_processes):
        process = multiprocessing.Process(target=guess_parallel, args=(token, length, alphabet_chunks[i], found_event))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    # if found_event.is_set():
        #break

    end = time.time()
    print(f"It took {(end - start) * 1000} ms to guess the token")

    '''start = time.time()
    print(guess_serial(token, length, alphabet))
    end = time.time()
    print(f"It took {(end - start) * 1000} ms to guess the token")'''



