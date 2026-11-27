"""Render the deal shoe with a transparent backing.

blender -b --python render-baccarat-shoe.py -- /tmp/baccarat-shoe.png
"""
from math import radians
from pathlib import Path
import sys

import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, metal=0, roughness=.3, coat=.12):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metal
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Coat Weight"].default_value = coat
    return mat


body = material("Smoked dark acrylic", (.029, .033, .037), .24, .18, .44)
plate = material("Graphite front plate", (.081, .087, .092), .55, .18)
brass = material("Fine champagne inlay", (.52, .32, .14), .72, .26)
inside = material("Felt and black rubber", (.020, .023, .025), 0, .48)
paper = material("Layered playing card stock", (.77, .69, .54), 0, .64)
maroon = material("Oxblood card back", (.27, .036, .041), 0, .37)
ink = material("Warm ink", (.75, .53, .27), .05, .42)


def bevel(obj, size):
    mod = obj.modifiers.new("Machined bevel", "BEVEL")
    mod.width = size
    mod.segments = 3
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")


def block(name, coords, size, mat, edge=0, angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=coords)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler.y = angle
    obj.data.materials.append(mat)
    if edge:
        bevel(obj, edge)
    return obj


def wall(name, outline, y, thick, mat):
    n = len(outline)
    verts = [(x, y + dy, z) for dy in (-thick/2, thick/2) for x, z in outline]
    quads = [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [tuple(reversed(range(n))), tuple(range(n,n*2)), *quads])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    bevel(obj,.032)


block("Rubber base", (0,0,.045), (3.11,1.5,.09), inside, .04)
block("Beveled acrylic plinth", (0,0,.16), (3.02,1.46,.18), body, .055)
profile = [(-1.48,.19), (1.49,.19), (1.37,.52), (.44,.74), (-.85,1.01), (-1.38,.99)]
for y in (-.645,.645):
    wall("Molded side wall", profile, y, .135, body)
    wall("Brushed trim", [(-1.32,.805), (-.83,.826), (1.33,.405), (1.3,.36), (-.84,.783), (-1.34,.756)], y*1.108, .025, brass)
block("Rear stack stop", (-1.38,0,.635), (.145,1.16,.77), plate, .05)

tilt = radians(-39)
for i in range(82):
    x = -1.3 + i*.03
    h = .74 - (x+1.3)*.101
    block("Ivory card edge", (x,0,h), (.026,1.175,.69), paper, .003, tilt)
front_x, front_z = 1.159, .49
block("Last card", (front_x,0,front_z), (.034,1.175,.69), paper,.014,tilt)


def printed(name, y, z, w, h, mat, layer=.027):
    x = front_x + z*.62932*-1 + layer*.77715
    height = front_z + z*.77715 + layer*.62932
    block(name,(x,y,height),(.002,w,h),mat,0,tilt)


printed("Printed card back", 0, 0, 1.089, .61, maroon)
for y in (-.503,.503):
    printed("Ink edge",y,0,.009,.56,ink,.029)
for z in (-.275,.275):
    printed("Ink edge",0,z,1.015,.008,ink,.029)
for i in range(11):
    for j in range(5):
        printed("Ink ornament", (i-5)*.078, (j-2)*.091, .017,.012,ink,.029)

block("Dispensing throat", (1.367,0,.252), (.27,1.24,.14), plate, .037)
for y in (-.623,.623):
    block("Outlet cheek", (1.316,y,.422), (.26,.13,.49), plate,.044,tilt)
    block("Outlet trim", (1.449,y,.33), (.042,.115,.17), brass,.012,tilt)
block("Low card ramp", (1.507,0,.206), (.218,1.035,.05), body,.02,radians(7))

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 28
scene.cycles.use_denoising = False
scene.render.resolution_x = 620
scene.render.resolution_y = 425
scene.render.threads_mode = "FIXED"
scene.render.threads = 5
scene.render.film_transparent = True
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "AgX"

world = bpy.data.worlds.new("Studio reflections")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (.38,.35,.32,1)
world.node_tree.nodes["Background"].inputs[1].default_value = .56
scene.world = world


def airlight(pos, power, size, color):
    lamp = bpy.data.lights.new("Reflected light", "AREA")
    lamp.energy = power
    lamp.size = size
    lamp.color = color
    obj = bpy.data.objects.new(lamp.name, lamp)
    bpy.context.collection.objects.link(obj)
    obj.location = pos
    obj.rotation_euler = (Vector((0,0,.3)) - obj.location).to_track_quat("-Z","Y").to_euler()


airlight((-3,-4,7),720,5,(1,.8,.58))
airlight((4,-1,6),540,4,(.78,.88,1))
airlight((-1,5,5),740,4,(1,.64,.38))

bpy.ops.object.camera_add(location=(5.3,-9.0,5.5))
cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,.55))-cam.location).to_track_quat("-Z","Y").to_euler()
cam.data.type="ORTHO"
cam.data.ortho_scale=4.15
scene.camera=cam

scene.render.filepath=str(Path(sys.argv[sys.argv.index("--")+1]))
bpy.ops.render.render(write_still=True)
