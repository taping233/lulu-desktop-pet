#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller LuluMacOS.spec

cd dist
ditto -c -k --sequesterRsrc --keepParent "lulu在摸鱼.app" "lulu-macos.zip"
echo "macOS app written to dist/lulu在摸鱼.app"

