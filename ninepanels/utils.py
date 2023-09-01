import hashlib
import os

def generate_random_hash() -> str:
    """ Generate a random hash

    Returns
        hash: 64 character hexademcial string

    """

    random_bytes = os.urandom(32)
    hash_bytes = hashlib.sha256(random_bytes)
    hash = hash_bytes.hexdigest()

    return hash
