"""Bruteforce attack script: parallel approach for token guessing"""
# Writer: Marcos Wang Zhu
import time
import itertools

# Guesses the token by locking in one starting letter at a time from the assigned chunk
# It then generates and tests every possible suffix for that specific letter
# Once all suffixes for that letter are exhausted, it moves to the next starting letter
def guess_parallel(end: int, token: str, alphabet_chunk: str, full_alphabet: str, suffix_length: int, value: int, result: bytes,found_token_buf=None) -> None:
    global token_found
    attempts = 0
    for first_char in alphabet_chunk:
        if result.value or time.time() > end:
            break
        for suffix_tuple in itertools.product(full_alphabet, repeat=suffix_length):
            if result.value or time.time() > end:
                break
            suffix_string = "".join(suffix_tuple)
            attempts += 1
            if first_char + suffix_string == token:
                print(f"Token found: {token}")
                found_token_buf.value = (first_char + suffix_string).encode()
                result.value = 1
                break

    with value.get_lock():
        value.value += attempts
    return