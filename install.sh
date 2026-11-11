#!/usr/bin/env bash
# Cài hoặc gỡ launcher "Agent Control Center" cho user hiện tại.
# Dùng: ./install.sh            (cài/cập nhật)
#       ./install.sh --uninstall
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${XDG_DATA_HOME:-${HOME}/.local/share}/applications"
DST="${APP_DIR}/agent-control-center.desktop"

refresh_menu() {
  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${APP_DIR}" >/dev/null 2>&1 || true
  fi
}

if [[ "${1:-}" == "--uninstall" ]]; then
  rm -f "${DST}"
  refresh_menu
  echo "Đã gỡ launcher: ${DST}"
  echo "Trang web vẫn còn tại: ${DIR}"
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Cần python3 trong PATH." >&2
  exit 1
fi

mkdir -p "${APP_DIR}"
sed "s|@DIR@|${DIR}|g" "${DIR}/agent-control-center.desktop" > "${DST}"
chmod 644 "${DST}"
chmod +x "${DIR}/serve.py"
refresh_menu

echo "Đã cài launcher: ${DST}"
echo "Mở bằng app menu, hoặc chạy: python3 ${DIR}/serve.py"
