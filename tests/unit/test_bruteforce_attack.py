# Writer: Marcos Wang Zhu

import multiprocessing
import time

from recovery_project.attacker_algorithms.bruteforce import guess_parallel
from recovery_project.attacker_algorithms.parallel_attacker import split_string


def test_split_string():
    """Tests if the alphabet chunking math works correctly."""
    alphabet = "abcdef"
    
    # Split into chunks of 2
    chunks_even = split_string(alphabet, chunksize=2)
    assert chunks_even == ["ab", "cd", "ef"]
    
    # Split into chunks of 4 (tests uneven division)
    chunks_uneven = split_string(alphabet, chunksize=4)
    assert chunks_uneven == ["abcd", "ef"]

def test_guess_parallel_success():
    """Tests if the worker can actually find a known token."""
    result = multiprocessing.Value('b', 0)
    value = multiprocessing.Value('i', 0)
    token = multiprocessing.Array('c', 256)

    guess_parallel(
        end=int(time.time() + 30000),
        token="cat", 
        alphabet_chunk="c", 
        full_alphabet="abcdefghijklmnopqrstuvwxyz", 
        suffix_length=2, 
        result=result,
        value=value,
        found_token_buf=token
    )
    
    # If it worked, the event flag should be flipped to True
    assert result.value == 1

def test_guess_parallel_failure():
    """Tests if the worker correctly ignores impossible tokens."""
    result = multiprocessing.Value('b', 0)
    value = multiprocessing.Value('i', 0)
    token = multiprocessing.Array('c', 256)

    guess_parallel(
        end = int(time.time() + 30000),
        token="zz", 
        alphabet_chunk="ab", 
        full_alphabet="ab", 
        suffix_length=1, 
        result=result,
        value = value,
        found_token_buf = token
    )
    
    # Because 'zz' was never found, the event flag should remain False
    assert result.value == 0
