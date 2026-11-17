# Lighting & PBR Material Recipes (`bpy`)

## 1. Studio 3-Point Lighting Setup

| Light | Role | Recommended Energy | Area Size | Color Temp / Tint |
| :--- | :--- | :--- | :--- | :--- |
| **Key Light** | Primary directional highlight & shadow | 400–600 W | 2.5–3.5 m | Warm white `(1.0, 0.96, 0.92)` |
| **Fill Light** | Soften harsh shadows on opposite side | 120–200 W | 4.0–5.0 m | Cool neutral `(0.85, 0.92, 1.0)` |
| **Rim / Back Light** | Separate subject silhouette from backdrop | 250–400 W | 2.0–3.0 m | Cool accent `(0.65, 0.82, 1.0)` |

### HDRI Environment Lighting
For realistic metallic and glass reflections, attach an `.exr` or `.hdr`
environment map to the World shader:

```python
world = bpy.context.scene.world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()

bg = nt.nodes.new("ShaderNodeBackground")
env = nt.nodes.new("ShaderNodeTexEnvironment")
env.image = bpy.data.images.load("/path/to/studio.hdr")
out = nt.nodes.new("ShaderNodeOutputWorld")

nt.links.new(env.outputs["Color"], bg.inputs["Color"])
nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
bg.inputs["Strength"].default_value = 0.8
```

## 2. PBR Material Presets (Principled BSDF)

- **Brushed Metal / Titanium**: `Metallic = 0.95`, `Roughness = 0.20–0.28`, `Coat Weight = 0.25`.
- **Frosted Glass (Cycles)**: `Transmission Weight = 0.95` (Blender 4.x) or `Transmission = 0.95` (3.x), `Roughness = 0.12`, `IOR = 1.45`.
- **Matte Studio Clay**: `Metallic = 0.0`, `Roughness = 0.65`, `Specular IOR Level = 0.35`.
- **Emissive Accent / Neon**: `Emission Color = (0.15, 0.65, 1.0, 1.0)`, `Emission Strength = 5.0–12.0`.
