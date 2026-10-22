# Collection update — 2026-10-22

Added 40 works, bringing the catalog to **100 works from 34 creators**. All 40 additions are author-attributed Kling 4.0 cases; no new Flash cases were added. The seven historical Flash entries keep their original provenance.

## Curation and provenance

The collection uses Apify Actor `CJdippxWmn9uRfooo`. The runs below completed successfully; their reported aggregate usage was USD 0.461. Raw datasets remain outside the public repository. The minimal original prompt/source excerpts needed to audit the accepted entries are in [the source record](collection-2026-10-22-sources.json).

| Run | Dataset | Status |
| --- | --- | --- |
| `eGKtlmsM3qFowS4el` | `KP31Vd7rtFnuFa4zs` | SUCCEEDED |
| `DliPloLBrBtF1mCba` | `HTmYocPuk1x6MorVU` | SUCCEEDED |
| `qTRYHpg6IhfXK0vTr` | `s1hCkH8Xgku1hwfaj` | SUCCEEDED |
| `qis5796IeAclWl207` | `zgYr269qevCwic5G6` | SUCCEEDED |
| `SQCfBgHEDf0C06HDY` | `BQobAgXcZK2L67qYF` | SUCCEEDED |
| `AGcolCPSTCycbgVY6` | `syN6naprTOkHj87Rh` | SUCCEEDED |
| `AP3Gzo3wGZd6gAr6j` | `XXyUt1lwH74YTz37i` | SUCCEEDED |
| `ClApI9tXMZ3Fka0Jm` | `6wFpoDTfS342CHklg` | SUCCEEDED |
| `Gi1MURJgiyQMVCLrw` | `6oM19eeunef5rPDt8` | SUCCEEDED |

- Deduplication checked source/example IDs, exact prompt hashes, and overlapping text. The unlabelled cybernetic priestess post and a near-duplicate tactical-shooter prompt were excluded.
- Separate physical tests in one post retain their original example numbers. Consecutive concert clips and the two-part girl-and-dragon story each count as one work.
- English and Japanese original prompts stay in their original language in both READMEs. Japanese prompts have Japanese language metadata; no full translation is invented.
- Four X auto-linked word pairs in the pageant prompt were restored using the source's exact `display_url` values. The mapping is retained in the source record.
- The fridge-to-party video quotes the same author's Kling 4.0 keyframe thread. That explicit quote relationship is recorded and validated.
- The Nameless Edge post shares an English prompt; the author states the Kling run used an unpublished Chinese translation. The entry explains this distinction and links to the original comparison; the second video follows the author's Seedance/Kling ordering. Flying-car and Madara comparisons retain their original combined-video context.
- Required reference inputs are identified, but unavailable files are not invented. No new paid inference or generation-history verification was performed.

## Validation

PASS: 100 unique prompt hashes and source/example IDs; 20 unit tests; deterministic generation of 26 files; exact source-fragment checks for all 40 additions; bilingual intro rendering through GitHub's GFM API.

PASS: all 40 new poster URLs returned HTTP 200 with an image MIME type after retrying transient connection failures. Both READMEs have 100 distinct case anchors.

Media: source posters and MP4 URLs were extracted from the original posts. Targeted frame inspection confirmed the dancing output is distinct from the black-screen music reference. This is not a complete playback review of all 40 works; `playbackVerified` remains false.

`git diff --check` reports source-preserved trailing spaces inside fenced prompts (the existing Torstein example and the new concert prompt). Authored guidance whitespace was corrected; original prompt bytes remain unchanged.
