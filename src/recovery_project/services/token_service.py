"""Token generation/validation helpers"""
import math
import multiprocessing
import secrets
import string
import itertools
import time
import hashlib

# This token generation and validation is mainly for the first reasearch question, where we have to vary the entropy of the token

# Characters included in the token. We can increase this by adding string.digits (digits from 0 to 9) and/or string.punctuation (special characters)
default_alphabet = string.ascii_letters

class TokenService:
    def __init__(self, alphabet: str = None, token_length: int=10):
        self.alphabet = alphabet or string.ascii_letters + string.digits
        self.token_length = token_length

# Generates the token using a given length. secrets.choice takes a random character from a sequence
# then create the token hash with the hashlib library
    def generate_token(self) -> tuple:
        token = "".join(secrets.choice(self.alphabet) for _ in range(self.token_length))
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, token_hash
    
    #this is verifying the token based on the hash
    def verify_token(self, provided_token: str, stored_hash: str) -> bool:
        provided_hash = hashlib.sha256(provided_token.encode()).hexdigest()
        return provided_hash == stored_hash

# Splits the alphabet into chunksize chunks
def split_string(s, chunksize):
    chunks = []
    for i in range(0, len(s), chunksize):
        chunks.append(s[i:i+chunksize])
    return chunks

# Guesses the token serially by testing every single combination using itertool.product. The return None is for guessing for every length. Explained later on
def guess_serial(token, token_length, alphabet):
    for tuple in itertools.product(alphabet, repeat=token_length):
        candidate = "".join(tuple)
        if candidate == token:
            print(f"Token found: {candidate}")
            return
    # return None

# Guesses the token by keeping the first character in the chunk fixed, then trying every combination with that character as the first character
# Then the next character in the chunk turns into the fixed character and so on
def guess_parallel(token, token_length, alphabet_chunk, found_event):
    for first_char in alphabet_chunk:
        for rest in itertools.product(default_alphabet, repeat = token_length - 1):
            if found_event.is_set():
                return
            candidate = first_char + "".join(rest)
            if candidate == token:
                print(f"Token found: {candidate}") 
                found_event.set()
                return

# For testing only
if __name__ == "__main__":
    # Ask for user input (includes number of processes for parallel version)
    try:
        length = int(input("Select token length: "))
        num_processes = int(input("Select number of threads to be used: "))
    except ValueError:
        print("Enter a valid integers")
        exit()
    
    # Make sure there are no more processes than characters in the alphabet
    num_processes = min(num_processes, len(default_alphabet))

    # Generate a token
    service = TokenService(alphabet=default_alphabet, token_length=length)
    token, token_hash =service.generate_token()
    print(f"Token to find: {token}") 
    print(f"Token hash: {token_hash}")
    found_event = multiprocessing.Event()

    # HASH CHECK
    # timing and printing the result of the hashing check
    print("\nHash check:")
    start = time.time()
    is_valid =service.verify_token(token, token_hash)
    end = time.time()
    print(f"verification result: {is_valid}")
    print(f"It took {(end - start) * 1000} ms to guess the token")

    # BRUTE FORCE
    print("\n Brute force check:")
    start = time.time()

    # Calculate the chunksize and the number of chunks based on the number of workers
    alphabet_chunksize = math.ceil(len(default_alphabet) / num_processes)
    alphabet_chunks = split_string(default_alphabet, alphabet_chunksize)

    processes = []

    # Right now, the uncommented code guesses only tokens with the given length. To make it truly bruteforce, ucomment the for loop and the found event check
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

    # Guess the token serially
    '''start = time.time()
    for length in range(1, max_length + 1):
    result = guess_serial(token, length, alphabet)
    if result is not None:
        break
    print(result)
    end = time.time()
    print(f"It took {(end - start) * 1000} ms to guess the token")'''



