"""Generate deterministic docs and indexes from content only; no network or credentials."""
import argparse, hashlib, json, re
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
        lines=[template('intro', locale, entries), '', featured_navigation(entries, locale), '', '## '+('分类浏览' if zh else 'Browse categories'), '']
        for c in categories:
            lines.append(f'- [{c["labels"][locale]}]({c["path"]}) — {c["count"]}')
        lines+=['','## '+('提示词与视频' if zh else 'Prompts & videos'),'']
        for e in featured_entries(entries):
            v=e['video']
            lines += [f'<a id="{e["slug"]}"></a>', '### '+e['title'][locale],'',presentation()['descriptions'][e['slug']][locale],'',f'@{e["author"]["handle"]} · [Prompt source / 提示词原帖]({e["promptSourceUrl"]}) · [Video source / 视频原帖]({e["videoSourceUrl"]})','',f'![{e["title"][locale]} — video preview / 视频封面]({media_url(v["posterUrl"])})','',f'[Watch original video]({e["videoSourceUrl"]}) · [Watch video / 观看视频]({media_url(v["url"])}) · {v["durationSecondsReported"]}s · {v["aspectRatioReported"][0]}:{v["aspectRatioReported"][1]}','',e['guidance'][locale],'','<details>','<summary>Complete original prompt / 完整原文</summary>','',fenced(e['originalPrompt']),'','</details>','']
            if zh:lines += ['<details>','<summary>中文编辑稿（独立改写）</summary>','',fenced(e['editorialCopies']['zh']['text']),'','</details>','']
            for a in e['referenceAssets']:
                lines += [f'- [{a["role"]}]({media_url(a["url"])}) · [Asset source / 参考图原帖]({a["sourceUrl"]})','<details>','<summary>Original asset prompt / 参考图原始提示词</summary>','',fenced(a['assetPromptOriginal']),'','</details>','']
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
