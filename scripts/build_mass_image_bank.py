#!/usr/bin/env python3
from pathlib import Path
import argparse
import base64
import gzip
import json
import urllib.request

UA='DaniAnaMassImageMigration/1.0 (+https://github.com/sociosofia/danieana)'


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
    if ct.startswith('image/'):
        return True
    signatures=(b'\x89PNG\r\n\x1a\n',b'\xff\xd8\xff',b'GIF87a',b'GIF89a',b'RIFF')
    if raw.startswith(signatures):
        return True
    head=raw[:300].lstrip().lower()
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


def runtime_question(q):
    keep=['id','sourceQuestionId','discipline','text','support','options','correct','gabarito','category','subtopic','origin','institution','year','answer_type','difficulty_band','classification_method','classification_confidence','images']
    out={k:q.get(k) for k in keep if k in q}
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

    if len(questions)!=int(expected.get('promote_total',-1)):
        raise SystemExit(f'Question count mismatch: {len(questions)} != {expected.get("promote_total")}')
    if len(residual)!=int(expected.get('residual_total',-1)):
        raise SystemExit(f'Residual count mismatch: {len(residual)} != {expected.get("residual_total")}')
    if len(assets)!=int(expected.get('asset_total',-1)):
        raise SystemExit(f'Asset count mismatch: {len(assets)} != {expected.get("asset_total")}')

    ids=[q.get('id') for q in questions]
    if len(ids)!=len(set(ids)):
        raise SystemExit('Duplicate migrated question ids detected.')
    source_ids=[str(q.get('sourceQuestionId')) for q in questions]
    if len(source_ids)!=len(set(source_ids)):
        raise SystemExit('Duplicate migrated sourceQuestionIds detected.')

    for q in questions:
        opts=q.get('options') or []
        if len(opts)<2:
            raise SystemExit(f'Question {q.get("id")} has fewer than 2 options.')
        correct=q.get('correct')
        if not isinstance(correct,int) or not (0<=correct<len(opts)):
            raise SystemExit(f'Question {q.get("id")} has invalid correct index.')
        if not str(q.get('text','')).strip() and not any(str(i.get('context','')).lower() in {'enunciado','statement','support','suporte'} for i in q.get('images') or []):
            raise SystemExit(f'Question {q.get("id")} has no readable statement and no statement image.')

    downloaded=[]
    failures=[]
    if not args.skip_downloads:
        for asset in assets:
            rel=str(asset['path']).removeprefix('./')
            dest=site/rel
            try:
                size,ct=download_asset(asset['source_url'],dest)
                downloaded.append({'path':rel,'bytes':size,'content_type':ct})
            except Exception as exc:
                failures.append({'path':rel,'source_url':asset.get('source_url'),'error':repr(exc)})
        if failures:
            Path(args.report).write_text(json.dumps({'failures':failures},ensure_ascii=False,indent=2),encoding='utf-8')
            raise SystemExit(f'{len(failures)} image asset downloads failed; migration aborted.')

    bank=site/'banks'/'image-migrated.js'
    bank.parent.mkdir(parents=True,exist_ok=True)
    bank.write_text('window.BANK_IMAGE_MIGRATED='+json.dumps(questions,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

    report={
        'version':'1.0',
        'questions':len(questions),
        'by_discipline':{},
        'questions_with_visible_media':sum(1 for q in questions if q.get('images')),
        'assets':len(assets),
        'asset_bytes':sum(x['bytes'] for x in downloaded),
        'residual':len(residual),
        'residual_items':residual,
        'downloads_skipped':args.skip_downloads,
        'failures':failures,
    }
    for q in questions:
        d=q.get('discipline','unknown')
        report['by_discipline'][d]=report['by_discipline'].get(d,0)+1
    Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='residual_items'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
