#!/usr/bin/env bash
set -euo pipefail

echo "=== Blender 3D Render Skill: Environment Check ==="

BLENDER_BIN=""
if command -v blender >/dev/null 2>&1; then
  BLENDER_BIN="$(command -v blender)"
elif [ -x "/Applications/Blender.app/Contents/MacOS/Blender" ]; then
  BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
fi

if [ -n "$BLENDER_BIN" ]; then
  echo "[OK] Blender found: $BLENDER_BIN"
  "$BLENDER_BIN" --version | head -n 2
else
  echo "[MISSING] Blender not found in PATH or /Applications/Blender.app."
  echo "  Install via: brew install --cask blender  (macOS) or https://www.blender.org/download/"
  exit 1
fi

if command -v ffmpeg >/dev/null 2>&1; then
  echo "[OK] FFmpeg found: $(command -v ffmpeg)"
  ffmpeg -version | head -n 1
else
  echo "[WARN] FFmpeg not found. Video encoding (scripts/encode_video.sh) requires ffmpeg."
  echo "  Install via: brew install ffmpeg (macOS) or apt install ffmpeg (Linux)"
fi

if command -v ffprobe >/dev/null 2>&1; then
  echo "[OK] FFprobe found: $(command -v ffprobe)"
fi

echo "=== Environment check complete ==="
