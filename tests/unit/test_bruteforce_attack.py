# Writer: Marcos Wang Zhu

import multiprocessing

from recovery_project.simulation.bruteforce import split_string, guess_parallel

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
    found_event = multiprocessing.Event()
    
    guess_parallel(
        token="cat", 
        alphabet_chunk="c", 
        full_alphabet="abcdefghijklmnopqrstuvwxyz", 
        suffix_length=2, 
        found_event=found_event
    )
    
    # If it worked, the event flag should be flipped to True
    assert found_event.is_set() is True

def test_guess_parallel_failure():
    """Tests if the worker correctly ignores impossible tokens."""
    found_event = multiprocessing.Event()
    
    guess_parallel(
        token="zz", 
        alphabet_chunk="ab", 
        full_alphabet="ab", 
        suffix_length=1, 
        found_event=found_event
    )
    
    # Because 'zz' was never found, the event flag should remain False
    assert found_event.is_set() is False
