import hashlib
from app.db import buckets_col


def _stable_band_hash(band_tuple):
    payload = "|".join(str(x) for x in band_tuple).encode("utf-8")
    return hashlib.sha1(payload).hexdigest()


def lsh_buckets(sig, bands, rows, assignment_id, submission_id, candidate_pairs):
    """Apply LSH to a single document's signature and update buckets and candidate pairs."""

    assignment_bucket = buckets_col.find_one({"assignment_id": assignment_id})

    if assignment_bucket is None:
        assignment_bucket = {
            "assignment_id": assignment_id,
            "buckets": []
        }
        buckets_col.insert_one(assignment_bucket)

    buckets = assignment_bucket.get("buckets", [])

    for b in range(bands):
        start = b * rows
        end = start + rows
        band_tuple = tuple(sig[start:end])
        band_hash = _stable_band_hash(band_tuple)

        bucket_found = None
        for bucket in buckets:
            if bucket["hash_val"] == band_hash:
                bucket_found = bucket
                break

        if bucket_found:
            for existing_id in bucket_found["submission_ids"]:
                if existing_id != submission_id:
                    pair = tuple(sorted((existing_id, submission_id)))
                    candidate_pairs.add(pair)

            if submission_id not in bucket_found["submission_ids"]:
                bucket_found["submission_ids"].append(submission_id)

        else:
            new_bucket = {
                "hash_val": band_hash,
                "submission_ids": [submission_id]
            }
            buckets.append(new_bucket)

    buckets_col.update_one(
        {"assignment_id": assignment_id},
        {"$set": {"buckets": buckets}}
    )

    return candidate_pairs, buckets
