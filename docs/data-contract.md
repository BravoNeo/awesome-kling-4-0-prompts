# Data contract

`content/entries/*.json` and `content/taxonomy.json` are the only authored catalog source. `schema/entry.schema.json` defines the allowed fields. `scripts/catalog.py` validates structure, stable source IDs, duplicate source/example pairs and slugs, categories, source pairing and original UTF-8 prompt hashes. `scripts/generate.py` deterministically creates bilingual README files, category indexes, the complete export and its manifest.

`modelClaim` records the collection display name and `flash`, `full` or `unspecified` variant, plus the unmodified supporting public source text. Independent verification is false in this collection. It does not represent provider access, supported ReelDance controls or a verified generation history.

`promptSourceUrl` and `videoSourceUrl` are separate. Pairing is `same_post` or `same_author_same_thread`. `video` is an output video, with original URL, mobile-friendly source variant, source poster, reported metadata and locally observed file metadata. Reported and observed durations may differ slightly due to container/audio timing. Reference roles distinguish portraits, character sheets and environment sheets; each retains its own source and original asset prompt hash. Do not reuse image-output fields from the GPT schema.

`originalPrompt` remains exact author text, including typos and inconsistencies. `editorialCopies.zh` is explicitly an edited adaptation, not a complete literal translation. Guidance explains actions such as choosing one duration or one aspect ratio before adapting the original. Do not silently correct source text.

Website consumers should pin a reviewed commit, validate the exported catalog and prompt hashes before building, and statically bundle content for SSR/SSG. A failed source or validation blocks a build. No credentials or automatic website deployment are part of this repository.

## Expanded collection (2026-10-21)

The display model is Kling 4.0. Historical Flash cases retain `variant: flash` and their original source wording; they are not reclassified as full. New collection entries are author-attributed full-version cases.

A post containing multiple independent examples uses `sourcePart` with the original one-based example number and an `x-{postId}-{sourcePart}` ID. Individual timeline shots are not split. Model evidence may come from the same author’s thread root instead of the video reply. `conversationId` is the actual thread root.

Observed dimensions and duration are optional when `playbackVerified` is false. Never populate observed fields from reported metadata. New video links are source-extracted, not playback-verified. Reference requirements may be declared even when the source input files are not available; `video-reference` covers editing instructions requiring the base clip. Chinese edited adaptations are optional; original prompts remain available in both READMEs.

## Multi-post and multilingual sources (2026-10-22)

`originalLanguage` includes `ja`. `additionalPromptSourceUrls` credits continuation posts belonging to one work; both READMEs expose these links. Do not split a continuing story merely to increase the count.

`modelClaim.quotedBySourceUrl` is allowed only when the bound video post explicitly quotes the same author's model evidence. The archived source relationship must match the entry, video URL, evidence URL and original evidence text. This does not weaken the rule excluding Flash evidence from full-version entries.

The batch source record retains exact extraction evidence. URL-entity restoration must use the original display text and a recorded mapping; it is not editorial rewriting. Model attribution and source matching do not imply independent verification of the actual generation settings.
