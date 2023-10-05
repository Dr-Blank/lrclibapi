""" A module that provides a class to solve a cryptographic challenge. """
# https://github.com/tranxuanthang/lrcget/blob/main/src-tauri/src/lrclib/challenge_solver.rs

import hashlib
from typing import List


class CryptoChallengeSolver:
    """
    A class that provides a method to solve a cryptographic challenge.
    """

    @staticmethod
    def verify_nonce(result: List[int], target: List[int]) -> bool:
        """
        Verify if the result nonce satisfies the target.

        :param result: The nonce to verify.
        :param target: The target to satisfy.
        :return: True if the nonce satisfies the target, False otherwise.
        """
        if len(result) != len(target):
            return False

        for res, tar in zip(result, target):
            if res > tar:
                return False
            if res < tar:
                break

        return True

    @classmethod
    def solve_challenge(cls, prefix: str, target_hex: str) -> str:
        """
        Solve a cryptographic challenge by finding a nonce that satisfies the \
            target.

        :param prefix: The prefix string of the challenge.
        :param target_hex: The target hash in hexadecimal format.
        :return: The nonce that satisfies the target.
        """
        raise NotImplementedError

    @staticmethod
    def _solve_challenge_for_nonce(args):
        prefix, target, nonce = args
        input_str = f"{prefix}{nonce}"
        input_bytes = input_str.encode("utf-8")
        context = hashlib.sha256(input_bytes)
        hashed = context.digest()

        result = CryptoChallengeSolver.verify_nonce(list(hashed), list(target))
        if result:
            return nonce

        return None
