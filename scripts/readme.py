"""README presentation helpers; never rewrite original prompts or catalog data."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def presentation():
    return json.loads((ROOT / 'docs/readme-presentation.json').read_text(encoding='utf-8'))


def template(part, locale, entries):
    value = (ROOT / f'docs/readme-{part}.{locale}.md').read_text(encoding='utf-8')
    creators = len({e['author']['handle'] for e in entries})
    return value.replace('{{count}}', str(len(entries))).replace('{{creators}}', str(creators)).replace('{{updated}}', presentation()['presentationUpdated']).rstrip()


def featured_entries(entries):
    chosen = presentation()['featured']
    by_slug = {e['slug']: e for e in entries}
    return [by_slug[s] for s in chosen if s in by_slug] + [e for e in entries if e['slug'] not in chosen]


def featured_navigation(entries, locale):
    zh = locale == 'zh'
    config = presentation()
    selected = [e for e in featured_entries(entries) if e['slug'] in config['featured']]
    rows = ['<a id="featured-videos"></a>', '## ' + ('精选视频' if zh else 'Featured videos'), '',
            ('点击封面观看对应视频，再打开完整案例。全部为作者标注的 Kling 4.0 Flash 作品。' if zh else 'Click a cover to watch its video, then open the complete case. All featured works are creator-attributed Kling 4.0 Flash examples.'), '', '<table>']
    for i, e in enumerate(selected):
        if i % 2 == 0: rows.append('<tr>')
        title = html.escape(e['title'][locale])
        desc = html.escape(config['descriptions'][e['slug']][locale])
        poster = media_url(e['video']['posterUrl'])
        video = media_url(e['video']['url'])
        label = '完整提示词与参考图' if zh else 'Full prompt & references'
        rows.append(f'<td width="50%" valign="top"><a href="{video}" rel="nofollow noreferrer"><img src="{poster}" alt="{title}" width="480" /></a><br/><strong>{title}</strong><br/>{desc}<br/><sub>Kling 4.0 Flash · @{html.escape(e["author"]["handle"])}</sub><br/><a href="#{e["slug"]}">{label} →</a></td>')
        if i % 2 == 1 or i == len(selected)-1: rows.append('</tr>')
    rows.append('</table>')
    return '\n'.join(rows) + '\n'


def media_url(url):
    mapping = presentation().get('media', {})
    mapped = mapping.get(url, url)
    if not mapped.startswith('https://media.reeldance.ai/'):
        raise ValueError('README media requires a corresponding project CDN asset: ' + url)
    return mapped


def external_links(markdown):
    # Only authored links outside fenced prompts. Source text stays byte-for-byte.
    lines = []
    fence_length = None
    pattern = re.compile(r'(?<!!)\[([^\]\n]+)\]\((https?://[^\s)]+)\)')
    def anchor(match):
        return '<a href="' + html.escape(match[2], quote=True) + '" rel="nofollow noreferrer" referrerpolicy="no-referrer">' + html.escape(match[1]) + '</a>'
    for line in markdown.splitlines(keepends=True):
        fence = re.match(r'^(`{3,})([^`]*)$', line.rstrip('\r\n'))
        if fence and fence_length is None:
            fence_length = len(fence[1])
            lines.append(line)
        elif fence_length is not None:
            lines.append(line)
            if fence and len(fence[1]) >= fence_length and not fence[2].strip():
                fence_length = None
        else:
            lines.append(pattern.sub(anchor, line))
    return ''.join(lines)
