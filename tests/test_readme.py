import sys, unittest
from pathlib import Path
from html.parser import HTMLParser
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from readme import external_links

class Elements(HTMLParser):
    def __init__(self):
        super().__init__(); self.elements = []
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

class ReadmeLinks(unittest.TestCase):
    def test_linked_badge_keeps_image_and_destination_separate(self):
        source = '[![Create with ReelDance](https://img.shields.io/badge/Create-green?style=flat&x=1)](https://reeldance.ai/?utm_source=github&x=2)'
        result = external_links(source)
        p = Elements(); p.feed(result)
        self.assertEqual(p.elements[0][0], 'a')
        self.assertEqual(p.elements[0][1]['href'], 'https://reeldance.ai/?utm_source=github&x=2')
        self.assertEqual(p.elements[1][0], 'img')
        self.assertEqual(p.elements[1][1]['src'], 'https://img.shields.io/badge/Create-green?style=flat&x=1')
        self.assertNotIn('[!', result)
    def test_original_prompt_links_stay_untouched(self):
        source = '```text\n[![Example](https://example.com/a.png)](https://example.com)\n```\n'
        self.assertEqual(external_links(source), source)
    def test_plain_image_stays_markdown(self):
        source = '![Example](https://example.com/a.png)'
        self.assertEqual(external_links(source), source)
