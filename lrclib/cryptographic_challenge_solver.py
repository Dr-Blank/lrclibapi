""" A module that provides a class to solve a cryptographic challenge. """

# https://github.com/tranxuanthang/lrcget/blob/main/src-tauri/src/lrclib/challenge_solver.rs

import hashlib
import threading
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Solution:
    """Class for storing the solution of a cryptographic challenge."""

    prefix: str
    """The prefix string of the challenge."""
    target_hex: str
    """The target hash in hexadecimal format."""
    nonce: Optional[int] = None
    """The nonce that satisfies the target hash."""

    @property
    def is_solved(self) -> bool:
        """Check if the challenge is solved."""
        return self.nonce is not None


def is_nonce_valid(prefix: str, nonce: "int | str", target: bytes) -> bool:
    """Check if the given nonce satisfies the target hash."""
    message = f"{prefix}{nonce}".encode()
    hash_value = hashlib.sha256(message).digest()
    return hash_value < target


def find_nonce(
    prefix: str,
    target: bytes,
    solution: Optional[Solution] = None,
    start: int = 0,
    step: int = 1,
) -> Solution:
    """Find the nonce that satisfies the target hash such that the hash of \
    the prefix concatenated with the nonce is less than the target hash.
    """
    if solution is None:
        solution = Solution(prefix, target.hex())

    nonce = start
    while not solution.is_solved:
        if is_nonce_valid(prefix, nonce, target):
            solution.nonce = nonce
            print(f"Found nonce: {nonce}")
            break
        nonce += step

    return solution


class CryptoChallengeSolver:
    """Class for solving cryptographic challenges."""

    @staticmethod
    def solve(prefix: str, target_hex: str, num_threads: int = 1):
        """Solve the cryptographic challenge.

        Parameters
        ----------
        prefix : str
            The prefix string of the challenge.
        target_hex : str
            The target hash in hexadecimal format.
        num_threads : int
            The number of threads to use for solving the challenge.

        Returns
        -------
        nonce : str
            The nonce that satisfies the target hash.
        """
        target = bytes.fromhex(target_hex)
        step = num_threads
        threads: List[threading.Thread] = []
        solution = Solution(prefix, target.hex())

        for i in range(num_threads):
            start = i
            thread = threading.Thread(
                target=find_nonce,
                args=(prefix, target, solution, start, step),
            )
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return str(solution.nonce)
