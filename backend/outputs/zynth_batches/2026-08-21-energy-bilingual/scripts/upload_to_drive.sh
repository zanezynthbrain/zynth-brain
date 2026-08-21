#!/usr/bin/env bash
set -u
ROOT="/home/ubuntu/zynth-brain/backend/outputs/zynth_batches/2026-08-21-energy-bilingual"
PARENT="1zjGF6D7Wi7vRX9sApLAJpvlZL5vKW5Oo"
SYNC="$ROOT/sync"
LOG="$SYNC/drive_uploads.ndjson"
LIST="/tmp/zynth_drive_upload_list.txt"
mkdir -p "$SYNC"
: > "$LOG"
find "$ROOT" -type f ! -path "$ROOT/sync/*" ! -name 'upload_to_drive.sh' | sort > "$LIST"
ok=0
fail=0
while IFS= read -r file; do
  rel="${file#$ROOT/}"
  name="${rel//\//__}"
  payload=$(printf '{"name":%s,"parents":[%s]}' "$(jq -Rn --arg v "$name" '$v')" "$(jq -Rn --arg v "$PARENT" '$v')")
  if output=$(gws drive files create --upload "$file" --json "$payload" 2>&1); then
    id=$(printf '%s' "$output" | jq -r '.id // empty')
    printf '{"status":"uploaded","relativePath":%s,"fileId":%s,"url":%s}\n' \
      "$(jq -Rn --arg v "$rel" '$v')" \
      "$(jq -Rn --arg v "$id" '$v')" \
      "$(jq -Rn --arg v "https://drive.google.com/file/d/$id/view" '$v')" >> "$LOG"
    ok=$((ok+1))
  else
    printf '{"status":"failed","relativePath":%s,"error":%s}\n' \
      "$(jq -Rn --arg v "$rel" '$v')" \
      "$(jq -Rn --arg v "$output" '$v')" >> "$LOG"
    fail=$((fail+1))
  fi
done < "$LIST"
printf '{"uploaded":%d,"failed":%d,"folderUrl":"https://drive.google.com/drive/folders/%s"}\n' "$ok" "$fail" "$PARENT" > "$SYNC/drive_upload_summary.json"
cat "$SYNC/drive_upload_summary.json"
