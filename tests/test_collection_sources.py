"""Regression checks for the audited Apify batch, including multi-post provenance."""
import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from catalog import ROOT, load_entries

class CollectionSourcesTests(unittest.TestCase):
    def test_source_fragments_and_bindings(self):
        entries={e['id']:e for e in load_entries()}
        sources=json.loads((ROOT/'docs/collection-2026-10-22-sources.json').read_text())
        self.assertEqual(len(sources),40)
        for record in sources:
            with self.subTest(entry=record['entryId']):
                e=entries[record['entryId']]
                text='\n\n'.join(s['text'] for s in record['promptSources'])
                for u in record['urlEntityRestoration']:
                    text=text.replace(u['url'],u['display_url'])
                self.assertIn(e['originalPrompt'],text)
                self.assertEqual(e['originalPromptSha256'],record['originalPromptSha256'])
                self.assertEqual(e['video']['mediaId'],record['mediaId'])
                self.assertEqual(e['videoSourceUrl'],record['videoSourceUrl'])
                self.assertEqual(e['modelClaim']['sourceUrl'],record['modelSourceUrl'])
                self.assertEqual(e['modelClaim']['sourceTextOriginal'],record['modelSourceText'])
                self.assertEqual(e.get('additionalPromptSourceUrls',[]),[s['url'] for s in record['promptSources'][1:]])
                self.assertEqual(e['modelClaim']['variant'],'full')
                if e['modelClaim'].get('quotedBySourceUrl'):
                    self.assertEqual(record['quotedModelSourceUrl'],e['modelClaim']['sourceUrl'])
                else:
                    self.assertIn(e['modelClaim']['sourceUrl'].rsplit('/',1)[-1],{e['videoSourceUrl'].rsplit('/',1)[-1],record['videoConversationId']})
    def test_prompt_continuation_and_japanese_are_rendered(self):
        for file in ['README.md','README.zh-CN.md']:
            text=(ROOT/file).read_text()
            self.assertIn('https://x.com/Ukiyo_il/status/2112483978523320442',text)
            self.assertIn('Japanese' if file=='README.md' else '日语',text)
