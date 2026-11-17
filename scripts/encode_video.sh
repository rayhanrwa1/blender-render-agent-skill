#!/usr/bin/env bash
set -euo pipefail

# Encode a PNG/JPG frame sequence into a web-compatible H.264 MP4 video.
# Usage: bash scripts/encode_video.sh <frames_dir> [fps] [output_mp4] [pattern]

FRAMES_DIR="${1:-./output/frames}"
FPS="${2:-30}"
OUTPUT_MP4="${3:-./output/render.mp4}"
PATTERN="${4:-frame_%04d.png}"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Error: ffmpeg is required but not installed." >&2
  exit 1
fi

if [ ! -d "$FRAMES_DIR" ]; then
  echo "Error: Frames directory '$FRAMES_DIR' does not exist." >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_MP4")"

echo "Encoding '$FRAMES_DIR/$PATTERN' at ${FPS}fps -> '$OUTPUT_MP4'..."
ffmpeg -y \
  -framerate "$FPS" \
  -i "$FRAMES_DIR/$PATTERN" \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -crf 18 \
  -preset slow \
  -movflags +faststart \
  "$OUTPUT_MP4"

echo "Done! Video info:"
if command -v ffprobe >/dev/null 2>&1; then
  ffprobe -v error -show_entries format=duration,size -show_entries stream=width,height,r_frame_rate -of default=noprint_wrappers=1 "$OUTPUT_MP4"
fi
