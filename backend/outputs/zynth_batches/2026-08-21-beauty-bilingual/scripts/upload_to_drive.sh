#!/usr/bin/env bash
set -euo pipefail
ROOT='/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-beauty-bilingual'
PARENT='1STqHBvLDMYfBcKVnZyeL1xoILAX4gfFD'
LOG="$ROOT/sync/drive_upload_log.ndjson"
mkdir -p "$ROOT/sync"; : > "$LOG"
cd "$ROOT"
upload() {
  local f="$1" out
  if out=$(gws drive +upload "$f" --parent "$PARENT" --name "$(basename "$f")" --format json 2>&1); then
    printf '%s\n' "$out" | jq -c --arg source "$f" '{source:$source,id:.id,name:.name,mimeType:.mimeType,webViewLink:.webViewLink}' >> "$LOG"
  else
    printf '{"source":%s,"status":"failed","error":%s}\n' "$(jq -Rs . <<<"$f")" "$(jq -Rs . <<<"$out")" >> "$LOG"; return 1
  fi
}
upload 'ZYNTH-20260821-BEAUTY-BILINGUAL-Complete-Batch.zip'
upload 'ZYNTH_BEAUTY_Batch_Portfolio_Overview.md'
for f in proposals/* commercial_storyboards/*; do upload "$f"; done
for f in monitoring/ZYNTH-20260821-BEAUTY-Monitoring.xlsx monitoring/monitoring_report.md monitoring/source_manifest.json; do upload "$f"; done
for f in research/beauty_social_research_notes.md research/tiktok_beauty_video_context.md validation/batch_validation.md validation/ai_council_feasibility_review.md; do upload "$f"; done
echo "Uploaded $(wc -l < "$LOG") files"
