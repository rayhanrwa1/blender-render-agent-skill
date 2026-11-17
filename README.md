# Blender 3D Render Skill (`blender-3d-render`)

An AI agent skill for building, lighting, animating, and rendering photorealistic **3D animations and product renders** headlessly using **Blender (`bpy`)** and **FFmpeg**.

Compatible with **Antigravity**, **Claude Code**, **Cursor**, **Codex**, and other Agent Skills-compatible tools.

---

## Repository Structure

```text
.
├── SKILL.md                          # Core agent instructions & 5-stage render workflow
├── SKILL.json                        # Skill metadata & script entrypoints
├── .claude-plugin/
│   └── plugin.json                   # Claude Code plugin manifest
├── scripts/
│   ├── check_env.sh                  # Verify Blender, FFmpeg, and FFprobe installation
│   ├── render_pipeline.py            # Headless bpy render & turntable animation script
│   └── encode_video.sh               # Convert PNG/JPG frame sequences to H.264 MP4
├── docs/
│   ├── lighting-and-materials.md     # Studio 3-point lighting & PBR material recipes
│   └── camera-and-render-settings.md # Blender 3.x/4.x API & Cycles/EEVEE settings
└── assets/                           # Sample frame sequences, videos, and audio assets
```

---

## Installation (via GitHub)

### 1. Using `skills` CLI (Claude Code / Cursor / Codex / Antigravity)
```bash
npx skills add <your-github-username>/<your-repo-name>
```

### 2. Antigravity (Manual / Project-Scoped)
Clone this repository into your project's `.agents/skills/blender-3d-render` directory (or `~/.gemini/config/skills/blender-3d-render` for global access):
```bash
git clone https://github.com/<your-github-username>/<your-repo-name>.git .agents/skills/blender-3d-render
```

### 3. Claude Code Plugin
Add as a local or GitHub plugin using `.claude-plugin/plugin.json`:
```bash
claude plugin add https://github.com/<your-github-username>/<your-repo-name>
```

---

## Prerequisites

- **Blender** (`3.6+` or `4.x` recommended)
  - macOS: `brew install --cask blender`
  - Linux: `sudo apt install blender` or download from [blender.org](https://www.blender.org/download/)
- **FFmpeg** (for encoding rendered frames into `.mp4`)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

Verify your environment:
```bash
bash scripts/check_env.sh
```

---

## Quick Start

1. **Render a fast 1-frame draft preview (EEVEE):**
   ```bash
   blender -b -P scripts/render_pipeline.py -- \
     --engine eevee --samples 16 --res 960x540 --frames 1-1 --out ./output/preview
   ```

2. **Render a 120-frame Cycles turntable animation (procedural hero or custom `.glb`/`.fbx`/`.obj`/`.blend`):**
   ```bash
   blender -b -P scripts/render_pipeline.py -- \
     --model ./path/to/model.glb \
     --engine cycles --samples 128 --res 1920x1080 --fps 30 --frames 1-120 --out ./output/frames
   ```

3. **Encode frames into a web-ready MP4:**
   ```bash
   bash scripts/encode_video.sh ./output/frames 30 ./output/render.mp4
   ```

---

## License

MIT
