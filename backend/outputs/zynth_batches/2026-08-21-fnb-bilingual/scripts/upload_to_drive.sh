#!/usr/bin/env bash
set -euo pipefail
ROOT='/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-fnb-bilingual'
PARENT='1ro6elw2QGkIy7kxcw5zm5AScZRg3vaN_'
LOG="$ROOT/sync/drive_upload_log.ndjson"
: > "$LOG"

cd "$ROOT"
zip -qr ZYNTH-20260821-FNB-BILINGUAL-Complete-Batch.zip data research proposals commercial_storyboards monitoring validation scripts ZYNTH_FNB_Batch_Portfolio_Overview.md

upload() {
  local f="$1"
  local out
  if out=$(gws drive +upload "$f" --parent "$PARENT" --name "$(basename "$f")" --format json 2>&1); then
    printf '%s\n' "$out" | jq -c --arg source "$f" '{source:$source,id:.id,name:.name,mimeType:.mimeType,webViewLink:.webViewLink}' >> "$LOG"
  else
    printf '{"source":%s,"status":"failed","error":%s}\n' "$(jq -Rs . <<<"$f")" "$(jq -Rs . <<<"$out")" >> "$LOG"
    return 1
  fi
}

upload 'ZYNTH-20260821-FNB-BILINGUAL-Complete-Batch.zip'
upload 'ZYNTH_FNB_Batch_Portfolio_Overview.md'
for f in proposals/* commercial_storyboards/*; do upload "$f"; done
for f in monitoring/ZYNTH-20260821-FNB-Monitoring.xlsx monitoring/monitoring_report.md monitoring/source_manifest.json; do upload "$f"; done
for f in research/verified_source_notes.md validation/batch_validation.md validation/proposal_visual_qc.md validation/ai_council_feasibility_review.md validation/ai_council_register.csv; do upload "$f"; done

echo "Uploaded $(wc -l < "$LOG") files"
