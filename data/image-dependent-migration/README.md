# H/G mass image migration snapshot v1.2

This directory contains the conservative História/Geografia recovery snapshot used by `scripts/build_mass_image_bank.py`.

Validated snapshot:
- 353 original IMAGE_DEPENDENT records across the two source banks;
- 348 unique source question IDs after removing 5 cross-discipline duplicates;
- 322 questions promoted in the laboratory batch;
- 195 História + 127 Geografia;
- 104 questions with student-visible media;
- 503 student-visible image assets;
- 26 residual questions kept in quarantine because required visual information is unavailable (18 História + 8 Geografia).

`hg-v12.full.xz` is the authoritative manifest. Temporary multipart `hg-v12.part*.b64` files are legacy development artifacts and are ignored whenever the authoritative XZ snapshot exists.
