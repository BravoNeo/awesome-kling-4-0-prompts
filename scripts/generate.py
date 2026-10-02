"""Generate deterministic docs and indexes from content only; no network or credentials."""
import argparse, hashlib, json, re
from catalog import ROOT, load_entries, read_json

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
        lines=['<!-- Generated from content/ by scripts/generate.py -->','# Awesome Kling 4.0 Flash Prompts','','[English](README.md) · [简体中文](README.zh-CN.md)','',
            ('7组作者公开分享的Kling 4.0 Flash提示词与视频：完整原文、作者原帖、视频来源、封面、时长、比例及参考素材。' if zh else 'Seven author-shared Kling 4.0 Flash prompt/video pairs, with complete original prompts, author credits, separate prompt and video sources, posters, durations, aspect ratios and reference assets.'),'',
            ('模型名称依据作者声明；并未核验作者生成后台。本合集不将Flash混作完整非Flash 4.0。' if zh else 'Model names follow author statements; generation histories are not independently verified. Flash is kept distinct from full non-Flash 4.0.'),'',
            ('中文编辑稿是独立改写起点，不替代完整英文原文。复制前选择画幅、总时长，并为参考素材类准备对应图像。' if zh else 'Chinese editorial copies are separate adaptations. Choose framing and duration, and prepare required references before adapting a prompt.'),'','## '+('分类' if zh else 'Categories'),'']
        for c in categories:
            lines.append(f'- [{c["labels"][locale]}]({c["path"]}) — {c["count"]}')
        lines+=['','## '+('提示词与视频' if zh else 'Prompts & videos'),'']
        for e in entries:
            v=e['video']
            lines += ['### '+e['title'][locale],'',e['description'][locale],'',f'@{e["author"]["handle"]} · [Prompt source]({e["promptSourceUrl"]}) · [Video source]({e["videoSourceUrl"]})','',f'![{e["title"][locale]} — author video poster]({v["posterUrl"]})','',f'[Watch original video]({e["videoSourceUrl"]}) · [MP4 source]({v["url"]}) · {v["durationSecondsReported"]}s (source metadata) · {v["aspectRatioReported"][0]}:{v["aspectRatioReported"][1]}','',e['guidance'][locale],'','<details>','<summary>Complete original prompt / 完整原文</summary>','',fenced(e['originalPrompt']),'','</details>','']
            if zh:lines += ['<details>','<summary>中文编辑稿（独立改写）</summary>','',fenced(e['editorialCopies']['zh']['text']),'','</details>','']
            for a in e['referenceAssets']:
                lines += [f'- [{a["role"]}]({a["url"]}) · [Asset source]({a["sourceUrl"]})','<details>','<summary>Original asset prompt</summary>','',fenced(a['assetPromptOriginal']),'','</details>','']
        lines += ['## '+('投稿与维护' if zh else 'Contribute & maintain'),'','[Submit a prompt](https://github.com/BravoNeo/awesome-kling-4-0-flash-prompts/issues/new?template=submit-prompt.yml) · [CONTRIBUTING](CONTRIBUTING.md) · [Data contract](docs/data-contract.md)','',
            ('维护者标记 `approved` 后仅生成待审JSON草稿，不自动合并、发布或改网站。`content/` 是唯一编辑源；README、分类和导出必须通过同步检查。' if zh else 'A maintainer’s `approved` label creates a pending JSON draft for review. It never merges content or deploys a website. Edit only `content/`; generated docs and exports must pass freshness checks.'),'','## '+('归属与许可' if zh else 'Attribution & rights'),'','Repository code is MIT licensed. Third-party prompts, reference images and videos remain the property of their authors. Public source links do not grant a redistribution license. See [CONTENT_RIGHTS](CONTENT_RIGHTS.md).','', 'Validation utilities adapted from [BravoNeo’s GPT Image 2.5 repository](https://github.com/BravoNeo/awesome-gpt-image-2-5-prompts).','']
        outputs[path]='\n'.join(lines)
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
