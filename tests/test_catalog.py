import copy, hashlib, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog import load_entries, validate_entries
from generate import build_outputs, generate

class CatalogTests(unittest.TestCase):
    def test_seven_unique_flash_pairs(self):
        entries=load_entries()
        self.assertEqual(len(entries),7)
        self.assertEqual(sum(e['pairing']=='same_post' for e in entries),3)
        self.assertEqual(sum(len(e['referenceAssets']) for e in entries),6)
        self.assertTrue(all(e['modelClaim']['name']=='Kling 4.0 Flash' and not e['modelClaim']['independentlyVerified'] for e in entries))
    def reject(self, edit):
        entries=copy.deepcopy(load_entries());edit(entries)
        with self.assertRaises(ValueError):validate_entries(entries)
    def test_tampered_prompt_fails(self):self.reject(lambda e:e[0].update(originalPrompt=e[0]['originalPrompt']+' changed'))
    def test_duplicate_fails(self):self.reject(lambda e:e.append(e[0]))
    def test_misbound_video_fails(self):self.reject(lambda e:e[0]['video'].update(sourceUrl=e[1]['videoSourceUrl']))
    def test_fake_verification_fails(self):self.reject(lambda e:e[0]['modelClaim'].update(independentlyVerified=True))
    def test_wrong_variant_fails(self):self.reject(lambda e:e[0]['modelClaim'].update(name='Kling 4.0'))
    def test_reference_hash_fails(self):
        self.reject(lambda e:next(x for x in e if x['referenceAssets'])['referenceAssets'][0].update(assetPromptOriginal='changed'))
    def test_exports_are_current(self):generate(check=True)
    def test_determinism(self):self.assertEqual(build_outputs(),build_outputs())
if __name__=='__main__':unittest.main()
