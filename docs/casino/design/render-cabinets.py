"""Render the six orthographic cabinet frames.

Run in Blender: blender -b --python render-cabinets.py -- <PNG output directory>.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

THEMES = {
    "dragon": ("43100e", "c88943", "ff9f42", 0.48, 0.24),
    "thor":   ("162a3d", "758d9b", "98ceff", 0.25, 0.25),
    "gems":   ("201637", "8971ae", "b36fff", 0.60, 0.18),
    "fruit":  ("123f2d", "b48a3b", "cbe88a", 0.74, 0.32),
    "diver":  ("103647", "b48a5c", "49e5e2", 0.56, 0.33),
    "slots":  ("3d1023", "b67553", "ff8493", 0.42, 0.23),
}


def rgba(hex_color):
    def linear(n):
        x = int(n, 16) / 255
        return x / 12.92 if x <= 0.04045 else ((x + .055) / 1.055) ** 2.4

    return tuple(linear(hex_color[i:i + 2]) for i in (0, 2, 4)) + (1,)


def material(name, color, metal, roughness, light=0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    surface = nodes.get("Principled BSDF")
    surface.inputs["Base Color"].default_value = rgba(color)
    surface.inputs["Metallic"].default_value = metal
    surface.inputs["Roughness"].default_value = roughness
    if light:
        surface.inputs["Emission Color"].default_value = rgba(color)
        surface.inputs["Emission Strength"].default_value = light
    else:
        grain = nodes.new("ShaderNodeTexNoise")
        grain.inputs["Scale"].default_value = 174
        grain.inputs["Detail"].default_value = 2
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.19
        bump.inputs["Distance"].default_value = 0.018
        links.new(grain.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], surface.inputs["Normal"])
    return mat


def contour(size, radius):
    half = size / 2
    points = []
    for corner in range(4):
        a = math.pi * corner / 2
        cx = (half - radius) * (1 if corner in (0, 3) else -1)
        cy = (half - radius) * (1 if corner in (0, 1) else -1)
        for step in range(13):
            theta = a + step * math.pi / 24
            points.append((cx + radius * math.cos(theta), cy + radius * math.sin(theta)))
    return points


def ring(name, outer, inner, radius, height, depth, mat, bevel):
    out = contour(outer, radius)
    cut = contour(inner, max(.09, radius - (outer - inner) / 2))
    n = len(out)
    vertices = [(x, y, z) for path, z in ((out, height), (cut, height),
                                         (out, height - depth), (cut, height - depth))
                for x, y in path]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend(((i, j, n+j, n+i), (2*n+i, 3*n+i, 3*n+j, 2*n+j),
                      (i, 2*n+i, 2*n+j, j), (n+i, n+j, 3*n+j, 3*n+i)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    mod = obj.modifiers.new("Machined edges", "BEVEL")
    mod.width = bevel
    mod.segments = 3
    mod = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    return obj


def fastener(x, y, plate, inset):
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.073, depth=.04,
                                       location=(x, y, .45))
    bpy.context.object.data.materials.append(plate)
    mod = bpy.context.object.modifiers.new("Rounded head", "BEVEL")
    mod.width = .011
    mod.segments = 3
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, .471))
    mark = bpy.context.object
    mark.dimensions = (.098, .018, .007)
    mark.rotation_euler.z = (x + y) * .29
    mark.data.materials.append(inset)


def panel_light(name, where, target, power, size, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.size = size
    data.color = color
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = where
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render(name, theme, output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    color, metal, glow, radius, rough = theme
    base = material("Powder-coated steel", color, .47, rough + .1)
    rail = material("Machined alloy", metal, .73, rough)
    seal = material("Recessed gasket", color, .12, .61)
    light = material("Frosted edge inlay", glow, .31, .25, .65)

    ring("Die-cast case rim", 6.88, 5.88, radius + .15, .22, .38, base, .044)
    ring("Outer metal shoulder", 6.82, 6.56, radius + .11, .34, .16, rail, .043)
    ring("Recess around the display", 6.56, 5.92, radius + .03, .27, .19, seal, .027)
    ring("Colored case face", 6.56, 6.20, radius + .03, .32, .14, base, .035)
    ring("Light guide", 6.26, 6.16, radius, .355, .06, light, .023)
    ring("Glass retaining lip", 6.16, 5.91, max(.22, radius - .055), .35, .15, rail, .036)
    ring("Recessed inner shadow", 5.95, 5.80, max(.15, radius - .11), .215, .15, seal, .022)
    for a in (-1, 1):
        for b in (-1, 1):
            x = a * (3.235 - radius * .09)
            y = b * (3.235 - radius * .09)
            fastener(x, y, rail, seal)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 512
    scene.render.resolution_y = 512
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 5
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    world = bpy.data.worlds.new("Workshop reflections")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (.35, .39, .46, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = .65
    scene.world = world

    bpy.ops.object.camera_add(location=(0, 0, 12))
    cam = bpy.context.object
    cam.rotation_euler = (0, 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 7.08
    scene.camera = cam
    panel_light("Warm overhead softbox", (-3, 5, 5), (0, 1, 0), 830, 5, (1, .84, .68))
    panel_light("Cool softbox", (4, -2, 3), (0, 0, 0), 620, 4, (.60, .78, 1))
    panel_light("Front reflected fill", (0, 0, 7), (0, 0, 0), 430, 6, (1, 1, 1))

    scene.render.filepath = str(output / f"{name}.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    path = Path(sys.argv[sys.argv.index("--") + 1]).resolve()
    path.mkdir(parents=True, exist_ok=True)
    for key, settings in THEMES.items():
        render(key, settings, path)
