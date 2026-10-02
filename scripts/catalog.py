"""Dependency-free catalog validation. Implements only the keywords our schema uses."""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_keys)


def https_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or re.search(r'[\s<>"\\]', value):
        raise ValueError('Expected public HTTPS URL without credentials or unsafe characters')
    if parsed.hostname in {'localhost', '127.0.0.1', '::1'}:
        raise ValueError('Local URLs are not public sources')
    return value


def canonical_source(value):
    https_url(value)
    p = urlsplit(value)
    host = p.hostname.lower()
    if host in {'x.com', 'www.x.com', 'twitter.com', 'www.twitter.com'}:
        match = re.fullmatch(r'/[^/]+/status/([0-9]+)/?', p.path)
        if not match:
            raise ValueError('X sources must be original status URLs')
        return 'https://x.com/i/status/' + match.group(1)
    return urlunsplit(('https', p.netloc.lower(), p.path.rstrip('/'), p.query, ''))


def stable_id(source):
    canonical = canonical_source(source)
    if canonical.startswith('https://x.com/i/status/'):
        return 'x-' + canonical.rsplit('/', 1)[1]
    return 'web-' + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def validate_schema(value, schema, path='$'):
    supported = {'$schema', '$id', 'title', 'type', 'properties', 'required', 'additionalProperties', 'enum', 'pattern', 'format', 'minLength', 'maxLength', 'minItems', 'maxItems', 'uniqueItems', 'items'}
    if set(schema) - supported:
        raise ValueError(f'Unsupported schema keyword at {path}: {set(schema) - supported}')
    kind = schema.get('type')
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'number': (int, float), 'integer': int}
    if kind and not isinstance(value, types[kind]):
        raise ValueError(f'{path}: expected {kind}')
    if 'enum' in schema and value not in schema['enum']:
        raise ValueError(f'{path}: value outside enum')
    if kind == 'object':
        props = schema['properties']
        missing = set(schema.get('required', [])) - set(value)
        unknown = set(value) - set(props)
        if missing or (unknown and schema.get('additionalProperties') is False):
            raise ValueError(f'{path}: missing {sorted(missing)} / unknown {sorted(unknown)}')
        for key, item in value.items():
            validate_schema(item, props[key], f'{path}.{key}')
    elif kind == 'array':
        if len(value) < schema.get('minItems', 0) or len(value) > schema.get('maxItems', float('inf')):
            raise ValueError(f'{path}: invalid item count')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise ValueError(f'{path}: duplicate items')
        for i, item in enumerate(value):
            validate_schema(item, schema['items'], f'{path}[{i}]')
    elif kind == 'string':
        if not value.strip() or len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            raise ValueError(f'{path}: invalid text length')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise ValueError(f'{path}: invalid pattern')
        if schema.get('format') == 'uri':
            https_url(value)



def validate_cdn(cdn, image=False):
    mime = 'image/webp' if image else 'video/mp4'
    suffix = '.webp' if image else '.mp4'
    if cdn['mimeType'] != mime or cdn['url'] != 'https://media.reeldance.ai/galleries/assets/' + cdn['sha256'] + suffix or type(cdn['bytes']) is not int or cdn['bytes'] <= 0:
        raise ValueError('Invalid CDN content-address/type/size')
    if image:
        if type(cdn.get('width')) is not int or type(cdn.get('height')) is not int or cdn['width'] <= 0 or cdn['height'] <= 0 or not cdn.get('variants'):
            raise ValueError('Invalid CDN image dimensions/variants')
        for variant in cdn['variants']:
            if variant['mimeType'] != mime or variant['url'] != 'https://media.reeldance.ai/galleries/assets/' + variant['sha256'] + suffix or any(type(variant[k]) is not int or variant[k] <= 0 for k in ['width', 'height', 'bytes']):
                raise ValueError('Invalid CDN responsive variant')


def validate_entries(entries, taxonomy=None):
    taxonomy = taxonomy or read_json(ROOT / 'content/taxonomy.json')
    schema = read_json(ROOT / 'schema/entry.schema.json')
    seen = {'id': set(), 'slug': set(), 'source': set()}
    for e in entries:
        validate_schema(e, schema)
        if 'cdn' in e['video']:
            validate_cdn(e['video']['cdn'])
            validate_cdn(e['video']['posterCdn'], image=True)
        for asset in e['referenceAssets']:
            if 'cdn' in asset: validate_cdn(asset['cdn'], image=True)
        if e['id'] != stable_id(e['promptSourceUrl']):
            raise ValueError('ID must be derived from the canonical original source URL')
        for field, value in [('id', e['id']), ('slug', e['slug']), ('source', canonical_source(e['promptSourceUrl']))]:
            if value in seen[field]:
                raise ValueError(f'Duplicate {field}: {value}')
            seen[field].add(value)
        for axis, values in e['categories'].items():
            if set(values) - set(taxonomy[axis]):
                raise ValueError(f'Unknown category in {axis}: {values}')
        if e['originalPromptSha256'] != hashlib.sha256(e['originalPrompt'].encode()).hexdigest():
            raise ValueError('Original prompt hash mismatch')
        if e['video']['sourceUrl'] != e['videoSourceUrl']:
            raise ValueError('Video must credit the bound video source')
        same = canonical_source(e['promptSourceUrl']) == canonical_source(e['videoSourceUrl'])
        if same != (e['pairing'] == 'same_post'):
            raise ValueError('Source pairing mismatch')
        if urlsplit(e['promptSourceUrl']).path.split('/')[1].lower() != e['author']['handle'].lower() or urlsplit(e['videoSourceUrl']).path.split('/')[1].lower() != e['author']['handle'].lower():
            raise ValueError('Both bound sources must match the credited author')
        if e['conversationId'] != e['videoSourceUrl'].rstrip('/').split('/')[-1]:
            raise ValueError('Thread root must match the original video post')
        if e['modelClaim']['sourceUrl'] != e['videoSourceUrl']:
            raise ValueError('Model claim must credit the original supporting video post')
        if any(type(e['video'][k]) is not int or e['video'][k] <= 0 for k in ['widthObserved', 'heightObserved']) or any(e['video'][k] <= 0 for k in ['durationSecondsReported', 'durationSecondsObserved']):
            raise ValueError('Invalid observed video dimensions or duration')
        if e['modelClaim']['variant'] == 'flash' and e['modelClaim']['name'] != 'Kling 4.0 Flash':
            raise ValueError('Flash claim must name Flash')
        if e['modelClaim']['independentlyVerified']:
            raise ValueError('This source-linked catalog has no generation-history verification')
        urls = [m['url'] for m in e['referenceAssets']]
        if len(urls) != len(set(urls)):
            raise ValueError('Duplicate media URL within one artwork')
        for asset in e['referenceAssets']:
            if asset['assetPromptSha256'] != hashlib.sha256(asset['assetPromptOriginal'].encode()).hexdigest():
                raise ValueError('Asset prompt hash mismatch')
        if bool(e['referenceAssets']) != (e['inputRequirement'] == 'reference-images'):
            raise ValueError('Reference requirement mismatch')
    return entries


def load_entries():
    entries = []
    for path in sorted((ROOT / 'content/entries').glob('*.json')):
        e = read_json(path)
        if path.stem != e['id']:
            raise ValueError(f'Filename must equal entry ID: {path.name}')
        entries.append(e)
    return validate_entries(entries)


def prompt_for(entry, locale):
    if locale == entry['originalLanguage']:
        return entry['originalPrompt'], locale, False
    return entry['originalPrompt'], entry['originalLanguage'], True


if __name__ == '__main__':
    entries = load_entries()
    print(f'Valid: {len(entries)} prompt/video pairs, {sum(len(e["referenceAssets"]) for e in entries)} reference images')
