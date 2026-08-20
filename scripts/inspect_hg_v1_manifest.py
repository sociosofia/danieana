#!/usr/bin/env python3
import base64
import collections
import gzip
import json
import sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/hg-v1.part01.b64')
raw = ''.join(src.read_text(encoding='utf-8').split())
# The canonical development snapshot was stored without final Base64 padding.
# Restore it deterministically instead of treating the payload as corrupt.
raw += '=' * (-len(raw) % 4)
data = json.loads(gzip.decompress(base64.b64decode(raw)).decode('utf-8'))

questions = list(data.get('questions') or [])
residual = list(data.get('residual') or [])
assets = list(data.get('assets') or [])
meta = data.get('meta') or {}

print('=== META ===')
print(json.dumps(meta, ensure_ascii=False, sort_keys=True))
print('COUNTS', json.dumps({'questions': len(questions), 'residual': len(residual), 'assets': len(assets)}, ensure_ascii=False))

by_source = collections.defaultdict(list)
for q in questions:
    sid = str(q.get('sourceQuestionId') or q.get('source_question_id') or '')
    if sid:
        by_source[sid].append(q)

dups = {sid: qs for sid, qs in by_source.items() if len(qs) > 1}
print('=== DUPLICATE SOURCE IDS ===')
print('DUP_COUNT', len(dups))
for sid, qs in sorted(dups.items()):
    row = []
    for q in qs:
        row.append({
            'id': q.get('id'),
            'sourceQuestionId': sid,
            'discipline': q.get('discipline'),
            'text': str(q.get('text') or '')[:220].replace('\n', ' '),
            'images': q.get('images') or [],
        })
    print('DUP', json.dumps(row, ensure_ascii=False))

print('=== RESIDUAL ===')
print('RESIDUAL_COUNT', len(residual))
for i, item in enumerate(residual, 1):
    row = {
        'n': i,
        'id': item.get('id'),
        'sourceQuestionId': item.get('sourceQuestionId') or item.get('source_question_id'),
        'discipline': item.get('discipline'),
        'reason': item.get('reason') or item.get('residual_reason') or item.get('status'),
        'text': str(item.get('text') or item.get('statement') or item.get('question') or '')[:500].replace('\n', ' '),
        'support': str(item.get('support') or '')[:300].replace('\n', ' '),
        'images': item.get('images') or item.get('image_references') or [],
        'keys': sorted(item.keys()),
    }
    print('RES', json.dumps(row, ensure_ascii=False))

# Asset path/source duplication summary.
source_urls = collections.Counter(str(a.get('source_url') or a.get('url') or '') for a in assets)
print('=== ASSETS ===')
print('ASSET_SOURCE_DUPLICATES', sum(1 for u, n in source_urls.items() if u and n > 1))
for u, n in source_urls.most_common():
    if u and n > 1:
        print('ASSET_DUP', json.dumps({'count': n, 'url': u}, ensure_ascii=False))
