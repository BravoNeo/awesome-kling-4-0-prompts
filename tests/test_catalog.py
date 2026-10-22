import copy, hashlib, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog import load_entries, validate_entries
from generate import build_outputs, generate

class CatalogTests(unittest.TestCase):
    def test_one_hundred_source_linked_prompts(self):
        entries=load_entries()
        self.assertEqual(len(entries),100)
        self.assertEqual(len({e['originalPromptSha256'] for e in entries}),100)
        self.assertEqual(sum(e['modelClaim']['variant']=='full' for e in entries),93)
        self.assertEqual(sum(e['modelClaim']['variant']=='flash' for e in entries),7)
        self.assertTrue(all(e['modelClaim']['name']=='Kling 4.0' and not e['modelClaim']['independentlyVerified'] for e in entries))
    def test_unverified_playback_is_not_invented(self):
        entries=load_entries()
        self.assertEqual(sum(not e['video']['playbackVerified'] for e in entries),93)
    def test_multi_example_ids(self):
        entries=[e for e in load_entries() if 'sourcePart' in e]
        self.assertTrue(entries)
        self.assertTrue(all(e['id'].endswith('-'+str(e['sourcePart'])) for e in entries))
    def reject(self, edit):
        entries=copy.deepcopy(load_entries());edit(entries)
        with self.assertRaises(ValueError):validate_entries(entries)
    def test_tampered_prompt_fails(self):self.reject(lambda e:e[0].update(originalPrompt=e[0]['originalPrompt']+' changed'))
    def test_duplicate_fails(self):self.reject(lambda e:e.append(e[0]))
    def test_misbound_video_fails(self):self.reject(lambda e:e[0]['video'].update(sourceUrl=e[1]['videoSourceUrl']))
    def test_fake_verification_fails(self):self.reject(lambda e:e[0]['modelClaim'].update(independentlyVerified=True))
    def test_wrong_variant_fails(self):self.reject(lambda e:next(x for x in e if x['modelClaim']['variant']=='flash')['modelClaim'].update(variant='full'))
    def test_unrelated_quote_evidence_fails(self):
        self.reject(lambda e: next(x for x in e if x['modelClaim'].get('quotedBySourceUrl'))['modelClaim'].update(sourceUrl='https://x.com/shikoba_86/status/123456789'))
    def test_reference_hash_fails(self):
        self.reject(lambda e:next(x for x in e if x['referenceAssets'])['referenceAssets'][0].update(assetPromptOriginal='changed'))
    def test_exports_are_current(self):generate(check=True)
    def test_determinism(self):self.assertEqual(build_outputs(),build_outputs())
if __name__=='__main__':unittest.main()
