"""
Headless Blender 3D animation & render pipeline.

Usage:
  blender -b -P scripts/render_pipeline.py -- [options]

Examples:
  # Render a 1-frame draft preview of the procedural hero scene
  blender -b -P scripts/render_pipeline.py -- --engine eevee --samples 16 --res 960x540 --frames 1-1 --out ./output/preview

  # Render a 120-frame Cycles turntable of a .glb model
  blender -b -P scripts/render_pipeline.py -- --model ./model.glb --engine cycles --samples 128 --res 1920x1080 --frames 1-120 --out ./output/frames
"""

import argparse
import math
import os
import sys
try:
    import bpy  # type: ignore[import-not-found]
    from mathutils import Vector  # type: ignore[import-not-found]
except ImportError as exc:
    raise SystemExit(
        "Error: This script must be run inside Blender:\n"
        "  blender -b -P scripts/render_pipeline.py -- [options]"
    ) from exc


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Blender 3D Render Pipeline")
    parser.add_argument("--model", type=str, default="", help="Optional path to .glb/.gltf/.fbx/.obj/.blend")
    parser.add_argument("--engine", type=str, default="cycles", choices=["cycles", "eevee"], help="Render engine")
    parser.add_argument("--samples", type=int, default=64, help="Render samples")
    parser.add_argument("--res", type=str, default="1920x1080", help="Resolution WxH (e.g. 1920x1080)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--frames", type=str, default="1-120", help="Frame range start-end (e.g. 1-120)")
    parser.add_argument("--orbit", type=float, default=360.0, help="Camera turntable orbit degrees")
    parser.add_argument("--out", type=str, default="./output/frames", help="Output directory for PNG sequence")
    return parser.parse_args(argv)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    for name in ("Studio", "Subject", "Lights", "Cameras"):
        col = bpy.data.collections.new(name)
        scene.collection.children.link(col)
    return scene


def link_to_collection(obj, col_name):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    bpy.data.collections[col_name].objects.link(obj)


def set_principled_input(bsdf, name, value):
    """Set Principled BSDF socket safely across Blender 3.x and 4.x."""
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = value
        return True
    aliases = {
        "Specular IOR Level": ["Specular"],
        "Coat Weight": ["Clearcoat"],
        "Emission Color": ["Emission"],
    }
    for alt in aliases.get(name, []):
        if alt in bsdf.inputs:
            bsdf.inputs[alt].default_value = value
            return True
    return False


def create_material(name, base_color, metallic=0.0, roughness=0.35, coat=0.0, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    set_principled_input(bsdf, "Base Color", (*base_color, 1.0))
    set_principled_input(bsdf, "Metallic", metallic)
    set_principled_input(bsdf, "Roughness", roughness)
    set_principled_input(bsdf, "Coat Weight", coat)
    if emission is not None:
        set_principled_input(bsdf, "Emission Color", (*emission, 1.0))
        set_principled_input(bsdf, "Emission Strength", emission_strength)
    return mat


def create_procedural_hero():
    """Create a sleek procedural 3D hero sculpture when no external model is provided."""
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.0,
        minor_radius=0.32,
        major_segments=96,
        minor_segments=48,
        location=(0, 0, 1.35),
        rotation=(math.radians(35), math.radians(20), 0),
    )
    torus = bpy.context.active_object
    torus.name = "HeroTorus"
    bpy.ops.object.shade_smooth()
    link_to_collection(torus, "Subject")

    metal_mat = create_material(
        "BrushedTitanium",
        base_color=(0.72, 0.75, 0.80),
        metallic=0.95,
        roughness=0.22,
        coat=0.3,
    )
    torus.data.materials.append(metal_mat)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.45, location=(0, 0, 1.35))
    core = bpy.context.active_object
    core.name = "HeroCore"
    bpy.ops.object.shade_smooth()
    link_to_collection(core, "Subject")

    glow_mat = create_material(
        "NeonCore",
        base_color=(0.1, 0.6, 1.0),
        roughness=0.1,
        emission=(0.15, 0.65, 1.0),
        emission_strength=6.0,
    )
    core.data.materials.append(glow_mat)
    return [torus, core]


def import_model(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    before = set(bpy.data.objects)
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=filepath)
        else:
            bpy.ops.import_scene.obj(filepath=filepath)
    elif ext == ".blend":
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.scene.collection.objects.link(obj)
    else:
        raise ValueError(f"Unsupported model format: {ext}")

    imported = [obj for obj in bpy.data.objects if obj not in before]
    for obj in imported:
        link_to_collection(obj, "Subject")
    return imported


def normalize_subject(objects):
    """Center subject at X=0, Y=0, resting on Z=0 and scaled to ~2.5m max dimension."""
    meshes = [o for o in objects if o.type == "MESH"]
    if not meshes:
        return Vector((0, 0, 1.0))

    coords = []
    for obj in meshes:
        for corner in obj.bound_box:
            coords.append(obj.matrix_world @ Vector(corner))

    min_v = Vector((min(c.x for c in coords), min(c.y for c in coords), min(c.z for c in coords)))
    max_v = Vector((max(c.x for c in coords), max(c.y for c in coords), max(c.z for c in coords)))
    size = max_v - min_v
    max_dim = max(size.x, size.y, size.z, 1e-4)
    scale = 2.5 / max_dim
    center_xy = Vector(((min_v.x + max_v.x) / 2.0, (min_v.y + max_v.y) / 2.0, min_v.z))

    root = bpy.data.objects.new("SubjectRoot", None)
    link_to_collection(root, "Subject")
    for obj in objects:
        if obj.parent is None:
            obj.parent = root
            obj.location -= center_xy
    root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()

    target_z = (size.z * scale) * 0.5
    return Vector((0.0, 0.0, max(target_z, 0.5)))


def setup_studio(scene):
    # Studio floor
    bpy.ops.mesh.primitive_plane_add(size=40.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "StudioFloor"
    link_to_collection(floor, "Studio")
    floor_mat = create_material("StudioFloorMat", base_color=(0.04, 0.045, 0.055), roughness=0.45)
    floor.data.materials.append(floor_mat)

    # Dark world background
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.018, 0.025, 1.0)
        bg.inputs["Strength"].default_value = 1.0

    # 3-Point Studio Area Lights
    lights = [
        ("KeyLight", (4.5, -4.5, 5.5), 450.0, 3.0, (1.0, 0.96, 0.92)),
        ("FillLight", (-5.0, -3.0, 3.0), 160.0, 4.5, (0.85, 0.92, 1.0)),
        ("RimLight", (0.0, 5.5, 4.0), 320.0, 2.5, (0.65, 0.82, 1.0)),
    ]
    for name, loc, energy, size, color in lights:
        light_data = bpy.data.lights.new(name=name, type="AREA")
        light_data.energy = energy
        light_data.size = size
        light_data.color = color
        light_obj = bpy.data.objects.new(name=name, object_data=light_data)
        light_obj.location = loc
        link_to_collection(light_obj, "Lights")

        constraint = light_obj.constraints.new(type="TRACK_TO")
        target = bpy.data.objects.get("LookTarget")
        if target is None:
            target = bpy.data.objects.new("LookTarget", None)
            target.location = (0, 0, 1.0)
            link_to_collection(target, "Cameras")
        constraint.target = target
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"


def setup_camera_and_animation(scene, target_loc, frame_start, frame_end, orbit_deg):
    target = bpy.data.objects.get("LookTarget")
    if target is None:
        target = bpy.data.objects.new("LookTarget", None)
        link_to_collection(target, "Cameras")
    target.location = target_loc

    rig = bpy.data.objects.new("CameraRig", None)
    rig.location = (0, 0, 0)
    link_to_collection(rig, "Cameras")

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 50.0
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 4.0

    cam = bpy.data.objects.new("MainCamera", cam_data)
    cam.location = (0.0, -5.8, target_loc.z + 1.1)
    cam.parent = rig
    link_to_collection(cam, "Cameras")
    scene.camera = cam

    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Keyframe seamless turntable orbit
    rig.rotation_euler = (0, 0, 0)
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_start)
    rig.rotation_euler = (0, 0, math.radians(orbit_deg))
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_end + 1)

    if rig.animation_data and rig.animation_data.action:
        for fcurve in rig.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = "LINEAR"


def configure_render(scene, args, frame_start, frame_end):
    width, height = map(int, args.res.lower().split("x"))
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.fps = args.fps
    scene.frame_start = frame_start
    scene.frame_end = frame_end

    if args.engine == "cycles":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
        try:
            scene.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass

        # Enable GPU if available (Metal on macOS, CUDA/OPTIX on Linux/Win)
        prefs = bpy.context.preferences.addons.get("cycles")
        if prefs:
            cprefs = prefs.preferences
            for compute_type in ("METAL", "OPTIX", "CUDA"):
                try:
                    cprefs.compute_device_type = compute_type
                    cprefs.get_devices()
                    if any(d.type == compute_type for d in cprefs.devices):
                        for d in cprefs.devices:
                            d.use = True
                        scene.cycles.device = "GPU"
                        break
                except Exception:
                    continue
    else:
        # Blender 4.2+ uses BLENDER_EEVEE_NEXT, older uses BLENDER_EEVEE
        eevee_id = "BLENDER_EEVEE_NEXT" if bpy.app.version >= (4, 2, 0) else "BLENDER_EEVEE"
        scene.render.engine = eevee_id
        if hasattr(scene, "eevee"):
            scene.eevee.taa_render_samples = args.samples

    # Color management
    for vt in ("AgX", "Filmic"):
        try:
            scene.view_settings.view_transform = vt
            break
        except Exception:
            continue
    for look in ("AgX - Medium High Contrast", "Medium High Contrast", "None"):
        try:
            scene.view_settings.look = look
            break
        except Exception:
            continue

    os.makedirs(args.out, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = os.path.join(args.out, "frame_")


def main():
    args = parse_args()
    if "-" in args.frames:
        f_start, f_end = map(int, args.frames.split("-", 1))
    else:
        f_start = f_end = int(args.frames)

    scene = reset_scene()
    if args.model:
        subjects = import_model(args.model)
    else:
        subjects = create_procedural_hero()

    target_loc = normalize_subject(subjects)
    setup_studio(scene)
    setup_camera_and_animation(scene, target_loc, f_start, f_end, args.orbit)
    configure_render(scene, args, f_start, f_end)

    bpy.ops.render.render(animation=(f_end > f_start), write_still=(f_end == f_start))
    print(f"Render finished: {args.out} (frames {f_start}-{f_end})")


if __name__ == "__main__":
    main()
