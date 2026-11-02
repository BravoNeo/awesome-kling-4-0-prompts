import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import catalog


class ThreadModelEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.entry = copy.deepcopy(next(e for e in catalog.load_entries() if e['modelClaim']['variant'] == 'full' and not e['modelClaim'].get('quotedBySourceUrl')))
        e = self.entry
        e['modelClaim']['sourceUrl'] = 'https://x.com/' + e['author']['handle'] + '/status/2999999999999999999'
        e['modelClaim']['sourceTextOriginal'] = 'This video was created with Kling 4.0.'
        self.record = {
            'entryId': e['id'], 'videoSourceUrl': e['videoSourceUrl'],
            'modelSourceUrl': e['modelClaim']['sourceUrl'],
            'modelSourceText': e['modelClaim']['sourceTextOriginal'],
            'modelSourceAuthorHandle': e['author']['handle'],
            'modelSourceConversationId': e['conversationId'],
            'videoConversationId': e['conversationId'],
        }
        self.read_json = catalog.read_json

    def validate(self):
        def read(path):
            return [self.record] if str(path).endswith('collection-2026-11-03-sources.json') else self.read_json(path)
        with patch.object(catalog, 'read_json', side_effect=read):
            return catalog.validate_entries([self.entry])

    def test_same_author_same_thread_reply_is_valid_model_evidence(self):
        self.assertEqual(self.validate(), [self.entry])

    def test_another_author_reply_cannot_relabel_the_video(self):
        self.record['modelSourceAuthorHandle'] = 'someone_else'
        with self.assertRaises(ValueError): self.validate()

    def test_another_thread_cannot_supply_model_evidence(self):
        self.record['modelSourceConversationId'] = '2999999999999999998'
        with self.assertRaises(ValueError): self.validate()

    def test_another_video_cannot_reuse_the_model_statement(self):
        self.record['videoSourceUrl'] = 'https://x.com/' + self.entry['author']['handle'] + '/status/2999999999999999998'
        with self.assertRaises(ValueError): self.validate()

    def test_edited_statement_is_rejected(self):
        self.record['modelSourceText'] += ' edited'
        with self.assertRaises(ValueError): self.validate()


if __name__ == '__main__': unittest.main()
