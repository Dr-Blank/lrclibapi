import random
import string

from lrclib.cryptographic_challenge_solver import (
    CryptoChallengeSolver,
    is_nonce_valid,
)

easy_target_hex = (
    "0000FFF000000000000000000000000000000000000000000000000000000000"
)


# generate a random prefixes
def random_prefix() -> str:
    return "".join(random.choice(string.ascii_letters) for _ in range(10))


def test_solve_random() -> None:
    prefix = random_prefix()
    target_hex = easy_target_hex
    nonce = CryptoChallengeSolver.solve(prefix, target_hex, 4)
    assert is_nonce_valid(prefix, nonce, bytes.fromhex(target_hex))
