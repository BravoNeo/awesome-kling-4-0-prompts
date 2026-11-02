import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from catalog import ROOT, load_entries, read_json


class AisaBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = {e['id']: e for e in load_entries()}
        cls.receipt = read_json(ROOT / 'docs/collection-2026-11-03.json')
        cls.records = read_json(ROOT / 'docs/collection-2026-11-03-sources.json')

    def test_exactly_one_hundred_new_complete_prompt_video_works(self):
        ids = self.receipt['newEntryIds']
        self.assertEqual(len(ids), 100)
        self.assertEqual(len(set(ids)), 100)
        self.assertEqual(len(self.records), 100)
        self.assertEqual({r['entryId'] for r in self.records}, set(ids))
        self.assertEqual(len({e['video']['mediaId'] for e in self.entries.values()}), 200)

    def test_new_batch_has_one_hundred_distinct_prompt_and_video_posts(self):
        batch = [self.entries[eid] for eid in self.receipt['newEntryIds']]
        self.assertEqual(self.receipt['sourcePromptPosts'], 100)
        self.assertEqual(len({e['promptSourceUrl'] for e in batch}), 100)
        self.assertEqual(len({e['videoSourceUrl'] for e in batch}), 100)

    def test_previous_one_hundred_records_are_unchanged(self):
        for eid, expected in self.receipt['baselineEntrySha256'].items():
            value = json.dumps(self.entries[eid], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
            self.assertEqual(hashlib.sha256(value).hexdigest(), expected, eid)

    def test_original_prompts_have_exact_source_and_hash_without_social_tags(self):
        for record in self.records:
            e = self.entries[record['entryId']]
            with self.subTest(entry=e['id']):
                self.assertIn(e['originalPrompt'], '\n\n'.join(p['text'] for p in record['promptSources']))
                self.assertEqual(hashlib.sha256(e['originalPrompt'].encode()).hexdigest(), e['originalPromptSha256'])
                self.assertNotRegex(e['originalPrompt'], r'(?im)^\s*#(?:kling|aivideo|pixverse|pollo)\b|https://t\.co/')
                self.assertEqual(e['referenceAssets'], [])
                self.assertIs(e['showGuidance'], False)
                self.assertEqual(e['modelClaim']['variant'], 'full')
                self.assertIs(e['modelClaim']['independentlyVerified'], False)


if __name__ == '__main__': unittest.main()
