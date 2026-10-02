"""Prepare an untrusted approved issue as a pending draft, never executable content."""
import json, os, pathlib, re

def prepare(event):
    issue=event.get('issue',{})
    body=issue.get('body','')
    if not isinstance(body,str) or len(body)>100000:raise ValueError('Invalid issue body')
    number=issue.get('number')
    if type(number) is not int or number<1:raise ValueError('Invalid issue number')
    if event.get('label',{}).get('name')!='approved':raise ValueError('Maintainer approval required')
    fields={m.group(1).strip():m.group(2).strip() for m in re.finditer(r'^### ([^\n]+)\n\n(.*?)(?=^### |\Z)',body,re.S|re.M)}
    for key in ['Exact model and variant','Original prompt source URL','Original video source URL','Author handle','Complete original prompt','Rights and attribution information']:
        if not fields.get(key) or fields[key]=='_No response_':raise ValueError('Missing '+key)
    return number,{'status':'pending-human-review','issueNumber':number,'fields':fields,'reviewRequired':['schema conversion','prompt/video source pairing','model variant','media roles','original hashes','rights']}

if __name__=='__main__':
    number,draft=prepare(json.loads(pathlib.Path(os.environ['GITHUB_EVENT_PATH']).read_text()))
    target=pathlib.Path('pending');target.mkdir(exist_ok=True)
    (target/f'issue-{number}.json').write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n')
