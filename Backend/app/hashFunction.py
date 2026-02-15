import random
from app.db import hash_funcs_col


def make_hash_funcs(num_funcs=200):
    """
    Ensure a single active family of MinHash functions exists in DB and return its size.
    """
    existing = hash_funcs_col.find_one({"name": "default_minhash_funcs", "num_funcs": num_funcs})
    if existing:
        return existing["num_funcs"]

    p = 2 ** 31 - 1  # large prime
    funcs_params = []
    for _ in range(num_funcs):
        a = random.randint(1, p - 1)
        b = random.randint(0, p - 1)
        funcs_params.append({"a": a, "b": b, "p": p})

    hash_funcs_col.replace_one(
        {"name": "default_minhash_funcs"},
        {"name": "default_minhash_funcs", "num_funcs": num_funcs, "funcs": funcs_params},
        upsert=True,
    )
    return num_funcs
