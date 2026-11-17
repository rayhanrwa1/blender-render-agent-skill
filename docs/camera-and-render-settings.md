# Camera & Render Settings Reference

## 1. Blender 3.x vs 4.x API Compatibility

| Feature | Blender 3.x | Blender 4.0+ / 4.2+ |
| :--- | :--- | :--- |
| **EEVEE Engine ID** | `BLENDER_EEVEE` | `BLENDER_EEVEE_NEXT` (4.2+) |
| **OBJ Import** | `bpy.ops.import_scene.obj` | `bpy.ops.wm.obj_import` |
| **Principled Specular** | `Specular` | `Specular IOR Level` |
| **Principled Coat** | `Clearcoat` | `Coat Weight` |
| **Principled Transmission** | `Transmission` | `Transmission Weight` |
| **Color Management** | `Filmic` | `AgX` |

## 2. Cycles GPU Acceleration

- **macOS (Apple Silicon)**: Uses `METAL` (`cycles_prefs.compute_device_type = "METAL"`).
- **NVIDIA (Windows/Linux)**: Uses `OPTIX` (RTX) or `CUDA`.
- **AMD (Windows/Linux)**: Uses `HIP`.

Always enable **OpenImageDenoise** (`scene.cycles.use_denoising = True`,
`scene.cycles.denoiser = "OPENIMAGEDENOISE"`) so 64–128 samples look clean
without fireflies or noise.

## 3. Recommended Resolution & Frame Rates

- **16:9 Landscape (YouTube / GitHub README)**: `1920x1080` or `3840x2160` @ `30fps` or `60fps`.
- **9:16 Vertical (Reels / TikTok / Shorts)**: `1080x1920` @ `30fps` or `60fps`.
- **1:1 Square (Product Showcase)**: `1080x1080` @ `30fps`.
