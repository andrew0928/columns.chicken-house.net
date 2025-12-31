#!/usr/bin/env bash
set -euo pipefail

log() { echo "[seed][$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

DEST_DIR="${SEED_DEST:-/seed}" # 共享 ephemeral volume 掛載點
SRC_DIR="/seed-src"
FLAG_FILE="${DEST_DIR}/.seed_done"

log "Start seeding to ${DEST_DIR} (force overwrite)"

# 確保目標目錄存在
mkdir -p "${DEST_DIR}"

# 移除舊資料 (強制覆蓋策略)
rm -rf "${DEST_DIR}/_files" "${DEST_DIR}/_qdrant_data" "${DEST_DIR}/synthesis" "${DEST_DIR}/appsettings.json" || true

# 複製 _files 和 _qdrant_data
cp -a "${SRC_DIR}/_files/."       "${DEST_DIR}/_files"
cp -a "${SRC_DIR}/_qdrant_data/." "${DEST_DIR}/_qdrant_data"

# 組合 synthesis 目錄 (向前相容舊 artifacts/synthesis 結構)
# 結構: synthesis/{postid}/ 包含 content.md, metadata.json, summary.md, faq.md, solution.md, checklist.md
log "Building synthesis directory (backward compatible)"
mkdir -p "${DEST_DIR}/synthesis"

# 1. 複製 _synthesis 內容 (metadata/summary/faq/solution/checklist)
if [[ -d "${SRC_DIR}/_synthesis" ]]; then
  cp -a "${SRC_DIR}/_synthesis/." "${DEST_DIR}/synthesis/"
  log "Copied _synthesis content"
fi

# 2. 將 _posts/{year}/{postid}.md 複製為 synthesis/{postid}/content.md
if [[ -d "${SRC_DIR}/_posts" ]]; then
  for md in "${SRC_DIR}/_posts"/*/*.md; do
    [[ -f "$md" ]] || continue
    postid=$(basename "$md" .md)
    if [[ -d "${DEST_DIR}/synthesis/${postid}" ]]; then
      cp "$md" "${DEST_DIR}/synthesis/${postid}/content.md"
    fi
  done
  log "Copied _posts as content.md"
fi

# 權限 (如果掛載 volume 需要特定 UID/GID)
if [[ -n "${SEED_CHOWN_UID:-}" && -n "${SEED_CHOWN_GID:-}" ]]; then
  log "chown -R ${SEED_CHOWN_UID}:${SEED_CHOWN_GID}"
  chown -R "${SEED_CHOWN_UID}:${SEED_CHOWN_GID}" "${DEST_DIR}/_files" "${DEST_DIR}/_qdrant_data" "${DEST_DIR}/synthesis" || true
fi

# 旗標檔
echo "seeded $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${FLAG_FILE}"

log "Seeding completed. Created ${FLAG_FILE}"
exit 0
