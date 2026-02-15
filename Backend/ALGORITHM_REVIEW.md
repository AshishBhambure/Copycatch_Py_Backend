# Plagiarism Detection Backend: Algorithm Review & Betterment Plan

## Current pipeline (as implemented)
1. Download file from URL and extract text from PDF/DOCX.
2. Normalize text (lowercase, punctuation removal, stopword removal, lemmatization).
3. Build **word shingles** (`k=2`).
4. Map shingles to global integer IDs.
5. Compute **MinHash signature** (default 200 hash functions).
6. Use **LSH bucketing** (`bands=100`, `rows=2`) to generate candidate pairs.
7. Estimate similarity from MinHash signature equality ratio.
8. Extract matching chunks using `difflib.SequenceMatcher` on raw text.

## Improvements shipped in this patch
- **Deterministic MinHash family lifecycle**
  - Keep one named hash family (`default_minhash_funcs`) in DB instead of appending multiple families.
  - Return `num_funcs` from hash setup routine.
- **Stable MinHash signature creation**
  - Signature now uses one active family; if missing, it is auto-created.
- **Deterministic LSH bucket hashing**
  - Replaced Python runtime `hash(...)` with stable SHA-1 hashing for band tuples.

These changes improve reproducibility and prevent accidental signature-length drift.

## High-priority algorithm betterments (recommended next)
1. **Use stronger shingling strategy**
   - Move from 2-word shingles to configurable `k` (e.g., 3–5 words) and compare precision/recall.
   - Add optional character 5-gram mode for paraphrase robustness.

2. **Improve preprocessing quality**
   - Keep sentence boundaries and normalize unicode.
   - Use language detection and language-specific stopword/lemmatization paths.
   - Remove boilerplate sections (headers/footers/reference blocks) before shingling.

3. **Tune LSH mathematically**
   - Current `b=100, r=2` is very high recall but can create many false positives.
   - Evaluate candidate probability curve and tune (`b`, `r`) for target similarity threshold.

4. **Upgrade matched-content extraction**
   - `SequenceMatcher` over raw text is expensive and sensitive to formatting noise.
   - Use token-aligned local alignment or suffix-array based chunk extraction on processed tokens.
   - Return chunk offsets and confidence metadata.

5. **Hybrid scoring (better plagiarism signal)**
   - Final score = weighted combination of:
     - MinHash estimate,
     - token overlap,
     - longest aligned chunk ratio,
     - semantic embedding similarity.

6. **Use ANN for semantic retrieval before expensive pairwise checks**
   - Build embedding index (FAISS/pgvector) per assignment.
   - Run deep chunk-matching only on top-N nearest neighbors.

7. **Add calibration & thresholding**
   - Build labeled dev set (positive/negative plagiarism pairs).
   - Calibrate thresholds with ROC/PR curves.
   - Output graded risk levels (low/medium/high) instead of only raw similarity.

## Data-model and reliability recommendations
- Add indexes:
  - `PreProcessing.submission_id` unique
  - `Buckets.assignment_id`
  - `SimilarityReport.submission_id + assignment_id`
- Store version metadata:
  - preprocessing version, shingle size, hash-family id, banding parameters.
- Add TTL/cleanup for temporary download files.

## Evaluation metrics to track
- Candidate generation recall at K.
- End-to-end precision/recall/F1 at policy thresholds.
- Average processing latency per submission.
- Cost per 1k submissions.
