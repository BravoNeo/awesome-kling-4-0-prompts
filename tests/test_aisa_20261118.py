import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from catalog import ROOT, load_entries, read_json

class AisaNovember18Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = {e['id']: e for e in load_entries()}
        cls.receipt = read_json(ROOT / 'docs/collection-2026-11-18.json')
        cls.sources = read_json(ROOT / 'docs/collection-2026-11-18-sources.json')

    def test_fifty_new_distinct_source_and_video_pairs(self):
        ids = self.receipt['newEntryIds']
        batch = [self.entries[id] for id in ids]
        self.assertEqual(len(ids), 50)
        self.assertEqual(len(set(ids)), 50)
        self.assertEqual(len({e['promptSourceUrl'] for e in batch}), 50)
        self.assertEqual(len({e['video']['mediaId'] for e in batch}), 50)
        self.assertEqual({r['entryId'] for r in self.sources}, set(ids))

    def test_previous_two_hundred_records_are_unchanged(self):
        self.assertEqual(len(self.receipt['baselineEntrySha256']), 200)
        for id, expected in self.receipt['baselineEntrySha256'].items():
            raw = json.dumps(self.entries[id], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), expected, id)

    def test_clean_prompts_are_exact_author_substrings_with_bound_media(self):
        for record in self.sources:
            e = self.entries[record['entryId']]
            with self.subTest(entry=e['id']):
                self.assertIn(e['originalPrompt'], '\n\n'.join(p['text'] for p in record['promptSources']))
                self.assertEqual(hashlib.sha256(e['originalPrompt'].encode()).hexdigest(), e['originalPromptSha256'])
                self.assertEqual(e['video']['mediaId'], record['mediaId'])
                self.assertEqual(e['videoSourceUrl'], record['videoSourceUrl'])
                self.assertEqual(e['modelClaim']['sourceTextOriginal'], record['modelSourceText'])
                self.assertFalse(e['modelClaim']['independentlyVerified'])
                self.assertTrue(e['video']['playbackVerified'])
                self.assertGreater(e['video']['widthObserved'], 0)
                self.assertGreater(e['video']['durationSecondsObserved'], 0)
                self.assertNotRegex(e['originalPrompt'], r'(?im)^\s*#(?:Wizstar|Kling|PixVerse)|https://t\.co/')
                self.assertEqual(e['referenceAssets'], [])
                self.assertFalse(e['showGuidance'])

    def test_normalized_prompts_are_unique_across_the_whole_catalog(self):
        import re
        import unicodedata
        keys = [re.sub(r'[^\w]', '', unicodedata.normalize('NFKC', e['originalPrompt']).lower()) for e in self.entries.values()]
        self.assertEqual(len(keys), len(set(keys)))
