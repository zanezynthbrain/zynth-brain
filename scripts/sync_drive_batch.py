from pathlib import Path
import subprocess, json, sys, time
ROOT=Path('/home/ubuntu/zynth-brain'); OUT=ROOT/'daily_proposals'/'2026-08-21_Retail_Bilingual'; LOG=OUT/'drive_sync_log.json'

def run(args):
    p=subprocess.run(args,capture_output=True,text=True)
    return p.returncode,p.stdout.strip(),p.stderr.strip()

result={'status':'Pending','folderId':None,'folderUrl':None,'uploaded':[],'failed':[],'retries':[]}
# Create a dated child folder; if duplicate exists, list and reuse.
q=json.dumps({'q':"name = '2026-08-21_Retail_Bilingual' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",'pageSize':100,'fields':'files(id,name,mimeType,webViewLink,parents)'})
rc,out,err=run(['gws','drive','files','list','--params',q,'--format','json'])
if rc==0:
    try:
        fs=json.loads(out).get('files',[])
        if fs: result['folderId']=fs[0]['id']; result['folderUrl']=fs[0].get('webViewLink') or f"https://drive.google.com/drive/folders/{fs[0]['id']}"
    except Exception as e: result['failed'].append({'stage':'list','error':str(e)})
if not result['folderId']:
    body=json.dumps({'name':'2026-08-21_Retail_Bilingual','mimeType':'application/vnd.google-apps.folder','parents':['10TDzVgj0iBxvULvGnrsXtjVnAcA8gNj-']})
    rc,out,err=run(['gws','drive','files','create','--json',body,'--format','json'])
    if rc==0:
        try:
            d=json.loads(out); result['folderId']=d['id']; result['folderUrl']=d.get('webViewLink') or f"https://drive.google.com/drive/folders/{d['id']}"
        except Exception as e: result['failed'].append({'stage':'create_folder','error':str(e),'stdout':out})
    else: result['failed'].append({'stage':'create_folder','error':err or out})

files=sorted([p for p in OUT.rglob('*') if p.is_file() and p.name!='drive_sync_log.json'])
if result['folderId']:
    for p in files:
        uploaded=False; last=''
        for attempt in range(2):
            rc,out,err=run(['gws','drive','+upload',str(p),'--parent',result['folderId'],'--format','json'])
            if rc==0:
                try:
                    d=json.loads(out); result['uploaded'].append({'path':str(p.relative_to(OUT)),'id':d.get('id'),'name':d.get('name'),'webViewLink':d.get('webViewLink')}); uploaded=True; break
                except Exception as e: last=str(e)
            else: last=err or out
            if attempt==0: result['retries'].append({'path':str(p.relative_to(OUT)),'retryAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
        if not uploaded: result['failed'].append({'path':str(p.relative_to(OUT)),'error':last})
result['status']='Synced' if result['folderUrl'] and not result['failed'] and len(result['uploaded'])==len(files) else ('Failed' if result['failed'] else 'Pending')
result['expectedFiles']=len(files); result['uploadedCount']=len(result['uploaded']); result['failedCount']=len(result['failed']); LOG.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(result,ensure_ascii=False))
