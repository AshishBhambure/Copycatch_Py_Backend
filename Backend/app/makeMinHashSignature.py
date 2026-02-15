from app.db import hash_funcs_col
from app.hashFunction import make_hash_funcs


def minhash_signature(shingles, shinglesToIds):
    """Compute MinHash signature for a document using one hash family from DB."""

    hash_doc = hash_funcs_col.find_one({"name": "default_minhash_funcs"})
    if hash_doc is None:
        make_hash_funcs()
        hash_doc = hash_funcs_col.find_one({"name": "default_minhash_funcs"})

    hash_funcs = []
    for params in hash_doc["funcs"]:
        a = params["a"]
        b = params["b"]
        p = params["p"]
        hash_funcs.append(lambda x, a=a, b=b, p=p: (a * x + b) % p)

    sig = []
    for h in hash_funcs:
        min_val = min(h(sid) for sid in shinglesToIds)
        sig.append(min_val)

    return sig
