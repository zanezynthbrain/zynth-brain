from __future__ import annotations
import json
from pathlib import Path

repo=Path('/home/ubuntu/zynth-brain')
registry_path=repo/'backend'/'outputs'/'variety_registry.json'
concepts=json.loads((repo/'backend'/'outputs'/'zynth_batches'/'2026-08-21-energy-bilingual'/'data'/'concepts.json').read_text(encoding='utf-8'))
registry=json.loads(registry_path.read_text(encoding='utf-8'))
for rec in registry.get('selection_log',[]):
    if rec.get('batch_code')=='ZYNTH-20260821-ENERGY-BILINGUAL':
        rec['selection_status']='validated_locally_pending_sync'
        rec['validated_at']='2026-08-21T03:31:00Z'
        rec['proposal_count']=10
        rec['document_count']=20
        rec['video_concept_count']=10
        rec['design_package_count']=18
        rec['validation_status']='PASS 37/37'
if not any(c.get('batch_code')=='ZYNTH-20260821-ENERGY-BILINGUAL' for c in registry['cycles']):
    registry['cycles'].append({
        'industry':'Energy and solar adoption','industryCode':'energy','run_id':'2026-08-21T03:31:00Z',
        'count':10,'batch_code':'ZYNTH-20260821-ENERGY-BILINGUAL','production_status':'validated_locally_pending_sync'
    })
registry['concepts']=[c for c in registry.get('concepts',[]) if c.get('batch_code')!='ZYNTH-20260821-ENERGY-BILINGUAL']
for c in concepts:
    registry['concepts'].append({
        'industry':'Energy and solar adoption','industryCode':'energy','n':int(c['id']),'form':c['format'],
        'territory':c['territory'],'tension':c['commercial_tension'],'behaviour':c['behaviour_change'],
        'mechanic':c['conversion'],'budget_scale':c['budget_structure'],'season':c['seasonal'],
        'batch_code':'ZYNTH-20260821-ENERGY-BILINGUAL'
    })
registry['updated']='2026-08-21T03:31:00Z'
registry_path.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Registry updated with energy batch.')
