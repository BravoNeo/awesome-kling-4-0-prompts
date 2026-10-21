"""Generate deterministic docs and indexes from content only; no network or credentials."""
import argparse, hashlib, html, json, re
from catalog import ROOT, load_entries, read_json
from readme import template, featured_entries, featured_navigation, media_url, external_links, presentation

def dump(value): return json.dumps(value, ensure_ascii=False, indent=2)+'\n'
def fenced(value):
    fence='`'*(1+max([2]+[len(x.group()) for x in re.finditer(r'`+',value)]))
    return fence+'text\n'+value+'\n'+fence

def build_outputs():
    entries=load_entries(); taxonomy=read_json(ROOT/'content/taxonomy.json')
    outputs={'export/catalog.json':dump({'schemaVersion':1,'model':'Kling 4.0 Flash','count':len(entries),'taxonomy':taxonomy,'entries':entries})}
    categories=[]
    for axis,options in taxonomy.items():
        for key,labels in options.items():
            ids=[e['id'] for e in entries if key in e['categories'][axis]]
            path=f'references/{axis}/{key}.json'
            outputs[path]=dump({'schemaVersion':1,'axis':axis,'category':key,'labels':labels,'count':len(ids),'entryIds':ids})
            categories.append({'axis':axis,'category':key,'labels':labels,'count':len(ids),'path':path})
    for locale,path in [('en','README.md'),('zh','README.zh-CN.md')]:
        zh=locale=='zh'
        labels = {
            'prompt_source': '提示词原帖' if zh else 'Prompt source',
            'video_source': '视频原帖' if zh else 'Video source',
            'preview': '视频预览' if zh else 'Video preview',
            'watch_original': '观看原帖视频' if zh else 'Watch original video',
            'watch': '观看视频' if zh else 'Watch video',
            'prompt': '完整原始提示词' if zh else 'Complete original prompt',
            'asset_source': '参考图原帖' if zh else 'Reference source',
            'asset_prompt': '参考图原始提示词' if zh else 'Original reference prompt',
        }
        roles = {'character-sheet': '角色设定图', 'environment-sheet': '场景设定图',
                 'character-reference': '角色参考图', 'character-portrait': '角色肖像'}
        lines=[template('intro', locale, entries), '', featured_navigation(entries, locale), '', '<a id="browse-by-use"></a>', '## '+('按用途浏览' if zh else 'Browse by use'), '']
        lines += ['| '+('用途 | 案例 |' if zh else 'Use | Examples |'), '| --- | --- |']
        for c in categories:
            if c['axis'] != 'use' or not c['count']: continue
            links = ' · '.join(f"[{e['title'][locale]}](#{e['slug']})" for e in featured_entries(entries) if c['category'] in e['categories']['use'])
            lines.append(f"| {c['labels'][locale]} | {links} |")
        lines += ['', '<details>', '<summary>'+('按风格与主题浏览' if zh else 'Browse styles & subjects')+'</summary>', '']
        for c in categories:
            if c['axis'] == 'use' or not c['count']: continue
            links = ' · '.join(f"[{e['title'][locale]}](#{e['slug']})" for e in featured_entries(entries) if c['category'] in e['categories'][c['axis']])
            lines.append(f"- **{c['labels'][locale]}:** {links}")
        lines += ['', '</details>', '', '<a id="prompts-and-videos"></a>', '## '+('提示词与视频' if zh else 'Prompts & videos'),'']
        for e in featured_entries(entries):
            v=e['video']
            lines += [f'<a id="{e["slug"]}"></a>', '### '+e['title'][locale],'', '**'+e['modelClaim']['name']+'** · '+('作者标注' if zh else 'Creator-attributed')+' · '+str(len(e['referenceAssets']))+(' 个附带参考素材' if zh else ' linked input references'), '',presentation()['descriptions'][e['slug']][locale],'',f'@{e["author"]["handle"]} · [{labels["prompt_source"]}]({e["promptSourceUrl"]}) · [{labels["video_source"]}]({e["videoSourceUrl"]})','',f'<a href="{media_url(v["url"])}" rel="nofollow noreferrer" referrerpolicy="no-referrer"><img src="{media_url(v["posterUrl"])}" alt="{html.escape(e["title"][locale], quote=True)} — {labels["preview"]}" width="800" /></a>','',f'[{labels["watch_original"]}]({e["videoSourceUrl"]}) · [{labels["watch"]}]({media_url(v["url"])}) · {v["durationSecondsReported"]}s · {v["aspectRatioReported"][0]}:{v["aspectRatioReported"][1]}','',e['guidance'][locale],'','<details>',f'<summary>{labels["prompt"]}</summary>','',fenced(e['originalPrompt']),'','</details>','']
            if zh:lines += ['<details>','<summary>中文编辑稿（独立改写）</summary>','',fenced(e['editorialCopies']['zh']['text']),'','</details>','']
            for a in e['referenceAssets']:
                lines += [f'- [{roles.get(a["role"], a["role"]) if zh else a["role"].replace("-", " ")}]({media_url(a["url"])}) · [{labels["asset_source"]}]({a["sourceUrl"]})','<details>',f'<summary>{labels["asset_prompt"]}</summary>','',fenced(a['assetPromptOriginal']),'','</details>','']
        lines += [template('footer', locale, entries), '']
        outputs[path]=external_links('\n'.join(lines))
    outputs['references/manifest.json']=dump({'schemaVersion':1,'model':'Kling 4.0 Flash','count':len(entries),'catalog':'export/catalog.json','categories':categories,'sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in sorted(outputs.items())}})
    return outputs

def generate(check=False):
    outputs=build_outputs()
    actual={str(p.relative_to(ROOT)) for d in ['references','export'] for p in (ROOT/d).rglob('*.json')}
    stale=actual-set(outputs)
    changed={p for p,v in outputs.items() if not (ROOT/p).exists() or (ROOT/p).read_text()!=v}
    if check:
        if stale or changed:raise ValueError('Stale generated files: '+', '.join(sorted(stale|changed)))
    else:
        for p in stale:(ROOT/p).unlink()
        for p,v in outputs.items():
            (ROOT/p).parent.mkdir(parents=True,exist_ok=True);(ROOT/p).write_text(v)
    print(('Checked' if check else 'Generated')+f' {len(outputs)} files')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');generate(parser.parse_args().check)
