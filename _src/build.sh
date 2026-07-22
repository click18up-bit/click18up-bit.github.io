#!/usr/bin/env bash
# สร้าง venv (ครั้งแรกครั้งเดียว) แล้วรัน generator
#   ./build.sh <ชื่อเจ้า>      หรือ   ./build.sh --all
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "ครั้งแรก: กำลังติดตั้ง dependency ลง .venv ..."
  python3 -m venv .venv
  ./.venv/bin/pip -q install -r requirements.txt
fi
./.venv/bin/python build.py "$@"
