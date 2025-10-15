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

# 複製
cp -a "${SRC_DIR}/_files/."       "${DEST_DIR}/_files"
cp -a "${SRC_DIR}/_qdrant_data/." "${DEST_DIR}/_qdrant_data"
cp -a "${SRC_DIR}/synthesis/."    "${DEST_DIR}/synthesis"

# 權限 (如果掛載 volume 需要特定 UID/GID)
if [[ -n "${SEED_CHOWN_UID:-}" && -n "${SEED_CHOWN_GID:-}" ]]; then
  log "chown -R ${SEED_CHOWN_UID}:${SEED_CHOWN_GID}"
  chown -R "${SEED_CHOWN_UID}:${SEED_CHOWN_GID}" "${DEST_DIR}/_files" "${DEST_DIR}/_qdrant_data" "${DEST_DIR}/synthesis" || true
fi

# 旗標檔
echo "seeded $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "${FLAG_FILE}"

log "Seeding completed. Created ${FLAG_FILE}"
exit 0
