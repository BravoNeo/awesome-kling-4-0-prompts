# Contributing

Submit an issue with the full original prompt, original prompt post, original video post, author, exact model variant and any required reference assets. Include public URLs only. Do not submit credentials, private logs, collector profiles or paid-provider access details.

A maintainer may apply `approved` to prepare a **pending draft artifact**. Approval does not automatically add an entry, grant a license or publish a website. Review source pairing, original hashes, exact variant, reference roles and rights before adding JSON under `content/entries/`.

Use `python3 scripts/catalog.py`, `python3 -m unittest discover -s tests` and `python3 scripts/generate.py --check`. Run generation without `--check` after editing content. Keep one entry per prompt/video group; extra variants and reference images do not increase the entry count.
