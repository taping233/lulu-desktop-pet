#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller LuluLinux.spec

echo "Linux executable written to dist/"
