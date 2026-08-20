#!/usr/bin/env python3
from pathlib import Path
import argparse, base64, gzip, json, urllib.request

UA='DaniAnaMassImageMigration/1.2 (+https://github.com/sociosofia/danieana)'

def load_manifest(parts_dir:Path):
    parts=sorted(parts_dir.glob('hg-v1.part*.b64'))
    if not parts:
        raise SystemExit(f'No migration manifest parts found in {parts_dir}')
    payload=''.join(p.read_text(encoding='utf-8').strip() for p in parts)
    try:
        return json.loads(gzip.decompress(base64.b64decode(payload)).decode('utf-8'))
    except Exception as exc:
        raise SystemExit(f'Could not decode migration manifest: {exc}')

def looks_like_image(raw:bytes, content_type:str=''):
    ct=(content_type or '').lower()
    if ct.startswith('image/'): return True
    if raw.startswith((b'\x89PNG\r\n\x1a\n',b'\xff\xd8\xff',b'GIF87a',b'GIF89a',b'RIFF')): return True
    head=raw[:500].lstrip().lower()
    return head.startswith(b'<svg') or b'<svg' in head

def download_asset(source_url:str,dest:Path):
    dest.parent.mkdir(parents=True,exist_ok=True)
    req=urllib.request.Request(source_url,headers={'User-Agent':UA,'Accept':'image/*,*/*;q=0.8'})
    with urllib.request.urlopen(req,timeout=35) as r:
        raw=r.read()
        status=getattr(r,'status',200)
        ct=r.headers.get('Content-Type','')
    if status!=200 or not raw:
        raise RuntimeError(f'HTTP {status} or empty response for {source_url}')
    if not looks_like_image(raw,ct):
        raise RuntimeError(f'Non-image response for {source_url}: {ct}')
    dest.write_bytes(raw)
    return len(raw),ct

KEEP=[
    'id','sourceQuestionId','discipline','text','support','options','correct','gabarito',
    'category','subtopic','origin','institution','year','exam_type','phase','main_topic_name',
    'answer_type','correct_percentage','total_answers','difficulty_source','difficulty_band',
    'solution','classification_method','classification_confidence','images'
]

def runtime_question(q):
    out={k:q.get(k) for k in KEEP if k in q}
    clean=[]
    for item in out.get('images') or []:
        clean.append({k:item.get(k) for k in ('url','context','alt') if item.get(k) is not None})
    out['images']=clean
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--site',default='_site')
    ap.add_argument('--parts-dir',default='data/image-dependent-migration')
    ap.add_argument('--report',default='mass-migration-build-report.json')
    ap.add_argument('--skip-downloads',action='store_true')
    args=ap.parse_args()

    site=Path(args.site)
    manifest=load_manifest(Path(args.parts_dir))
    questions=[runtime_question(q) for q in manifest.get('questions',[])]
    assets=manifest.get('assets',[])
    residual=manifest.get('residual',[])
    expected=manifest.get('meta',{})

    checks={
        'questions':(len(questions),int(expected.get('promote_total',-1))),
        'residual':(len(residual),int(expected.get('residual_total',-1))),
        'assets':(len(assets),int(expected.get('asset_total',-1))),
    }
    for label,(actual,want) in checks.items():
        if actual!=want:
            raise SystemExit(f'{label} count mismatch: {actual} != {want}')

    ids=[str(q.get('id')) for q in questions]
    source_ids=[str(q.get('sourceQuestionId')) for q in questions]
    if len(ids)!=len(set(ids)): raise SystemExit('Duplicate migrated question ids detected.')
    if len(source_ids)!=len(set(source_ids)): raise SystemExit('Duplicate migrated sourceQuestionIds detected.')

    asset_paths={str(a.get('path','')).removeprefix('./') for a in assets}
    if len(asset_paths)!=len(assets):
        raise SystemExit('Duplicate asset paths detected.')

    visible_count=0
    for q in questions:
        opts=q.get('options') or []
        if len(opts)<2: raise SystemExit(f'Question {q.get("id")} has fewer than 2 options.')
        correct=q.get('correct')
        if not isinstance(correct,int) or not (0<=correct<len(opts)):
            raise SystemExit(f'Question {q.get("id")} has invalid correct index.')
        if not str(q.get('text','')).strip():
            raise SystemExit(f'Question {q.get("id")} has empty statement.')
        imgs=q.get('images') or []
        if imgs: visible_count+=1
        for im in imgs:
            rel=str(im.get('url','')).removeprefix('./')
            if rel not in asset_paths:
                raise SystemExit(f'Question {q.get("id")} references missing asset path {rel}')

    expected_visible=int(expected.get('questions_with_visible_media',visible_count))
    if visible_count!=expected_visible:
        raise SystemExit(f'Visible-media question count mismatch: {visible_count} != {expected_visible}')

    downloaded=[]
    failures=[]
    if not args.skip_downloads:
        for i,asset in enumerate(assets,1):
            rel=str(asset['path']).removeprefix('./')
            dest=site/rel
            try:
                size,ct=download_asset(asset['source_url'],dest)
                downloaded.append({'path':rel,'bytes':size,'content_type':ct})
            except Exception as exc:
                failures.append({'path':rel,'source_url':asset.get('source_url'),'error':repr(exc)})
            if i%50==0 or i==len(assets):
                print(f'Assets: {i}/{len(assets)}; failures={len(failures)}',flush=True)
        if failures:
            Path(args.report).write_text(json.dumps({'failures':failures},ensure_ascii=False,indent=2),encoding='utf-8')
            raise SystemExit(f'{len(failures)} image asset downloads failed; migration aborted.')

    bank=site/'banks'/'image-migrated.js'
    bank.parent.mkdir(parents=True,exist_ok=True)
    bank.write_text('window.BANK_IMAGE_MIGRATED='+json.dumps(questions,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

    report={
        'version':expected.get('version','1.2'),
        'questions':len(questions),
        'by_discipline':dict(expected.get('by_discipline') or {}),
        'questions_with_visible_media':visible_count,
        'assets':len(assets),
        'asset_bytes':sum(x['bytes'] for x in downloaded),
        'residual':len(residual),
        'residual_by_discipline':dict(expected.get('residual_by_discipline') or {}),
        'duplicate_cross_discipline_total':expected.get('duplicate_cross_discipline_total'),
        'downloads_skipped':args.skip_downloads,
        'failures':failures,
        'residual_items':residual,
    }
    Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='residual_items'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
