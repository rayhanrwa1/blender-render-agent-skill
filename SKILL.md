---
name: blender-3d-render
description: >-
  End-to-end Blender 3D animation and photorealistic rendering pipeline using
  Python (bpy), Cycles/EEVEE, procedural lighting, camera rigs, and FFmpeg
  video/frame export. Use this skill whenever the user asks to create 3D
  animations, 3D product renders, turntable/orbit showcases, procedural 3D scenes,
  or render .blend/.glb/.obj/.fbx models into image sequences or MP4 videos.
---

# Blender 3D Animation & Render Pipeline

This skill guides you through building, animating, lighting, and rendering
photorealistic 3D scenes headlessly with **Blender (`bpy`)** and **FFmpeg**.

## 1. Pre-Flight Environment Check

Before writing or running any Blender script, verify that `blender` and `ffmpeg`
are available on the machine by running:

```bash
bash scripts/check_env.sh
```

- On **macOS**, if `blender` is not in `$PATH`, check `/Applications/Blender.app/Contents/MacOS/Blender`.
- Always note the detected Blender major version (`3.x` vs `4.x`), because
  several `bpy` APIs changed in Blender 4.0+ (see
  [docs/camera-and-render-settings.md](./docs/camera-and-render-settings.md)).

## 2. Core Workflow

Follow this 5-stage pipeline for every 3D animation or render request:

### Stage A: Scene Setup & Asset Loading
1. Start from a clean factory scene (`bpy.ops.wm.read_factory_settings(use_empty=True)`)
   unless modifying an existing `.blend` file.
2. Organize objects into named collections (`Studio`, `Subject`, `Lights`, `Cameras`).
3. When importing external 3D models:
   - `.glb` / `.gltf`: `bpy.ops.import_scene.gltf(filepath=...)`
   - `.fbx`: `bpy.ops.import_scene.fbx(filepath=...)`
   - `.obj`: `bpy.ops.wm.obj_import(filepath=...)` (Blender 4.x) or `bpy.ops.import_scene.obj(...)` (3.x)
4. Normalize imported model scale and center its bounding box at `(0, 0, 0)`
   resting on `z = 0` so lighting and camera framing are predictable.

### Stage B: Materials & Studio Lighting
1. Use **Principled BSDF** nodes for all PBR materials.
2. Add subtle imperfections (noise/roughness variation, bevel modifiers on hard
   edges) so surfaces catch realistic specular highlights.
3. Set up a **3-Point Studio Lighting** rig (Key, Fill, Rim) with `AREA` lights
   or an HDRI environment texture (`ShaderNodeTexEnvironment`) for natural
   reflections.
4. For product/showcase renders, add a curved studio cyclorama backdrop or
   shadow-catcher floor (`obj.is_shadow_catcher = True` in Cycles).
5. See [docs/lighting-and-materials.md](./docs/lighting-and-materials.md) for
   ready-to-use material and lighting recipes.

### Stage C: Camera & Keyframe Animation
1. Create a `Target` Empty at the subject's center of interest and attach a
   `TRACK_TO` constraint (`track_axis='TRACK_NEGATIVE_Z'`, `up_axis='UP_Y'`) to
   the camera.
2. Animate either:
   - **Turntable / Orbit**: Parent the camera to a `CameraRig` Empty at `(0,0,0)`
     and keyframe `rotation_euler.z` from `0` to `2 * math.pi` with `LINEAR`
     interpolation for a seamless loop.
   - **Dolly / Hero Reveal**: Keyframe camera `location` and `lens` (35mm–85mm)
     with `BEZIER` interpolation for smooth ease-in/ease-out.
3. Enable Depth of Field (`cam.data.dof.use_dof = True`) focused on the `Target`
   Empty with `aperture_fstop` between `2.8` and `5.6` for cinematic depth.

### Stage D: Render Configuration (Preview vs Final)
Always run a **fast preview render** (single keyframe, low samples, 50%
resolution) before committing to a full animation render.

| Preset | Engine | Samples | Resolution | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Draft Preview** | `BLENDER_EEVEE_NEXT` (4.2+) / `BLENDER_EEVEE` | 16–32 | 960x540 | Check framing, motion, and basic lighting |
| **Final Render** | `CYCLES` (GPU Metal/CUDA + OpenImageDenoise) | 128–256 | 1920x1080 or 3840x2160 | Photorealistic shadows, reflections, GI |

- Set color management to `AgX` (Blender 4.x) or `Filmic` (3.x) with `Medium High Contrast` look.
- Output to **PNG image sequences** (`frame_0001.png`, ...) rather than directly
  to MP4 from Blender, so interrupted renders can resume without losing frames.

### Stage E: Headless Render & Video Encoding
Use the bundled pipeline script for standard turntable/showcase renders, or write
a custom `bpy` script for bespoke scenes:

```bash
# 1. Draft preview of frame 1
blender -b -P scripts/render_pipeline.py -- \
  --engine eevee --samples 16 --res 960x540 --frames 1-1 --out ./output/preview

# 2. Full Cycles render (120 frames @ 30fps)
blender -b -P scripts/render_pipeline.py -- \
  --engine cycles --samples 128 --res 1920x1080 --fps 30 --frames 1-120 --out ./output/frames

# 3. Encode frame sequence to web-ready MP4 (H.264 yuv420p)
bash scripts/encode_video.sh ./output/frames 30 ./output/render.mp4
```

## 3. Verification Checklist

Before reporting a render as complete:
1. Confirm the preview frame exists and check its dimensions/visual quality.
2. Verify all expected frames (`frame_0001.png` ... `frame_NNNN.png`) were
   written with non-zero file sizes.
3. If encoding video, verify the output `.mp4` plays cleanly and has the
   expected duration and resolution via `ffprobe`.
