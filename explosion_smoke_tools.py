#!/usr/bin/env python3
"""
Explosion Smoke Simulation Tools
Creates realistic explosion effects with smoke and a bob/ball object
"""

from typing import Dict, Any, Optional, List
from smoke_simulation_tools import (
    create_smoke_domain_code,
    create_smoke_flow_code,
    create_smoke_collision_code
)


def create_explosion_smoke_code(
    bob_location: Optional[List[float]] = None,
    explosion_location: Optional[List[float]] = None,
    domain_size: Optional[List[float]] = None,
    resolution: int = 128,
    explosion_intensity: str = "high"
) -> str:
    """
    Create smoke explosion with bob (ball) object
    
    Args:
        bob_location: Bob/ball position [x, y, z]
        explosion_location: Explosion center [x, y, z]
        domain_size: Domain size [x, y, z]
        resolution: Simulation resolution
        explosion_intensity: low, medium, high
    
    Returns:
        Complete explosion smoke setup code
    """
    bob_location = bob_location or [0, 0, 2]
    explosion_location = explosion_location or [0, 0, 1]
    domain_size = domain_size or [8, 8, 8]
    
    # Explosion intensity presets
    intensity_presets = {
        "low": {"density": 0.5, "temperature": 2.0, "velocity": [0, 0, 2]},
        "medium": {"density": 1.0, "temperature": 3.0, "velocity": [0, 0, 3]},
        "high": {"density": 1.5, "temperature": 4.0, "velocity": [0, 0, 4]}
    }
    
    preset = intensity_presets.get(explosion_intensity.lower(), intensity_presets["high"])
    
    # Build code string
    code_parts = []
    
    code_parts.append("""# Smoke Explosion with Bob (Ball) Object
import bpy
import mathutils
import math

# Clear existing objects
for obj in ["Bob", "ExplosionSmokeDomain", "ExplosionFlow"]:
    if obj in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj])

# ============================================
# 1. CREATE BOB (BALL) OBJECT
# ============================================
bpy.ops.mesh.primitive_ico_sphere_add(
    radius=0.5,
    location=""" + str(bob_location) + """
)
bob = bpy.context.active_object
bob.name = "Bob"

# Add material to bob
bob_mat = bpy.data.materials.new(name="BobMaterial")
bob_mat.use_nodes = True
nodes = bob_mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
if principled:
    principled.inputs['Base Color'].default_value = (0.2, 0.2, 0.8, 1.0)  # Blue
    principled.inputs['Metallic'].default_value = 0.8
    principled.inputs['Roughness'].default_value = 0.2
bob.data.materials.append(bob_mat)

# ============================================
# 2. CREATE EXPLOSION SMOKE DOMAIN
# ============================================
domain_loc = """ + str([explosion_location[0], explosion_location[1], explosion_location[2] + 2]) + """
domain_sz = """ + str(domain_size) + """

# Create domain cube
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=domain_loc
)
domain_obj = bpy.context.active_object
domain_obj.name = "ExplosionSmokeDomain"
domain_obj.scale = domain_sz

# Add Fluid modifier (smoke domain)
fluid_mod = domain_obj.modifiers.new(name="Fluid", type='FLUID')
fluid_mod.fluid_type = 'DOMAIN'
domain = fluid_mod.domain_settings
domain.domain_type = 'GAS'
domain.resolution_max = """ + str(resolution) + """
# High resolution smoke (Blender 3.0+)
try:
    domain.use_high_resolution = True
    domain.high_resolution_max = """ + str(resolution) + """ // 2
except AttributeError:
    # Fallback for older Blender versions
    pass
domain.use_noise = True
domain.noise_scale = 1  # Integer value
domain.noise_strength = 0.5
# Temperature and velocity (may not be available in all Blender versions)
try:
    domain.use_temperature = True
except AttributeError:
    pass
try:
    domain.use_velocity = True
except AttributeError:
    pass
domain.cache_type = 'MODULAR'
domain.cache_directory = "//cache_explosion_smoke"

# ============================================
# 3. CREATE EXPLOSION FLOW (Multiple Sources)
# ============================================
# Main explosion flow at center
explosion_loc = """ + str(explosion_location) + """
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=explosion_loc
)
flow_obj = bpy.context.active_object
flow_obj.name = "ExplosionFlow"
flow_obj.scale = [0.2, 0.2, 0.2]

# Add Fluid modifier (smoke flow)
fluid_mod = flow_obj.modifiers.new(name="Fluid", type='FLUID')
fluid_mod.fluid_type = 'FLOW'
flow = fluid_mod.flow_settings
flow.flow_type = 'SMOKE'
flow.flow_behavior = 'INFLOW'
flow.subframes = 1
flow.density = """ + str(preset["density"]) + """
flow.temperature = """ + str(preset["temperature"]) + """
flow.smoke_color = [0.7, 0.7, 0.7]
# Initial velocity (may not be available in all versions)
try:
    flow.use_initial_velocity = True
    flow.velocity_factor = 1.0
    # Velocity might be set differently
    if hasattr(flow, 'velocity'):
        flow.velocity = """ + str(preset["velocity"]) + """
except AttributeError:
    pass

# Additional explosion flows for more realistic effect
for i in range(3):
    angle = (i * 120) * math.pi / 180
    offset_x = math.cos(angle) * 0.3
    offset_y = math.sin(angle) * 0.3
    
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=[explosion_loc[0] + offset_x, explosion_loc[1] + offset_y, explosion_loc[2]]
    )
    flow_obj = bpy.context.active_object
    flow_obj.name = "ExplosionFlow_" + str(i+1)
    flow_obj.scale = [0.15, 0.15, 0.15]
    
    # Add fluid modifier
    fluid_mod = flow_obj.modifiers.new(name="Fluid", type='FLUID')
    fluid_mod.fluid_type = 'FLOW'
    flow = fluid_mod.flow_settings
    flow.flow_type = 'SMOKE'
    flow.flow_behavior = 'INFLOW'
    flow.subframes = 1
    flow.density = """ + str(preset["density"] * 0.8) + """
    flow.temperature = """ + str(preset["temperature"] * 0.9) + """
    flow.smoke_color = [0.7, 0.7, 0.7]
    
    # Radial explosion velocity
    try:
        flow.use_initial_velocity = True
        flow.velocity_factor = 1.0
        if hasattr(flow, 'velocity'):
            flow.velocity = [offset_x * 2, offset_y * 2, """ + str(preset["velocity"][2] * 0.8) + """]
    except AttributeError:
        pass

# ============================================
# 4. SETUP BOB AS COLLISION (Optional)
# ============================================
# Make bob interact with smoke
# Bob collision with smoke (using EFFECTOR type)
fluid_mod = bob.modifiers.new(name="Fluid", type='FLUID')
fluid_mod.fluid_type = 'EFFECTOR'  # Use EFFECTOR for collision objects
# Note: collision_settings may not be available in all Blender versions
# The EFFECTOR type should handle collision automatically

# ============================================
# 5. ADD EXPLOSION ANIMATION TO BOB
# ============================================
# Animate bob falling/exploding
bpy.context.scene.frame_set(1)
bob.location = """ + str(bob_location) + """
bob.keyframe_insert(data_path="location", frame=1)

# Bob at explosion point
bpy.context.scene.frame_set(30)
bob.location = """ + str(explosion_location) + """
bob.keyframe_insert(data_path="location", frame=30)

# Bob scale explosion effect
bob.scale = [1, 1, 1]
bob.keyframe_insert(data_path="scale", frame=30)

bpy.context.scene.frame_set(35)
bob.scale = [3, 3, 3]  # Explosion expansion
bob.keyframe_insert(data_path="scale", frame=35)

# Hide bob after explosion
bpy.context.scene.frame_set(40)
bob.hide_render = True
bob.keyframe_insert(data_path="hide_render", frame=40)

# ============================================
# 6. SETUP CAMERA WITH MOVEMENT
# ============================================
# Set frame range for explosion
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

# Remove all existing cameras first
for obj in list(bpy.data.objects):
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# Create single camera
bpy.ops.object.camera_add(location=[8, -8, 6])
camera = bpy.context.active_object
camera.name = "ExplosionCamera"
camera.rotation_euler = [1.1, 0, 0.785]
bpy.context.scene.camera = camera

# Camera animation - starts wide, moves closer during explosion
bpy.context.scene.frame_set(1)
camera.location = [8, -8, 6]  # Wide shot
camera.rotation_euler = [1.1, 0, 0.785]
camera.keyframe_insert(data_path="location", frame=1)
camera.keyframe_insert(data_path="rotation_euler", frame=1)

# Camera moves closer as bob falls
bpy.context.scene.frame_set(25)
camera.location = [6, -6, 5]  # Closer
camera.rotation_euler = [1.0, 0, 0.785]
camera.keyframe_insert(data_path="location", frame=25)
camera.keyframe_insert(data_path="rotation_euler", frame=25)

# Camera at explosion moment - dramatic close-up
bpy.context.scene.frame_set(30)
camera.location = [3, -3, 3]  # Very close
camera.rotation_euler = [0.9, 0, 0.785]
camera.keyframe_insert(data_path="location", frame=30)
camera.keyframe_insert(data_path="rotation_euler", frame=30)

# Camera pulls back to show smoke expansion
bpy.context.scene.frame_set(60)
camera.location = [5, -5, 4]  # Medium distance
camera.rotation_euler = [1.0, 0, 0.785]
camera.keyframe_insert(data_path="location", frame=60)
camera.keyframe_insert(data_path="rotation_euler", frame=60)

# Camera wide shot for smoke dissipation
bpy.context.scene.frame_set(120)
camera.location = [10, -10, 7]  # Wide shot
camera.rotation_euler = [1.1, 0, 0.785]
camera.keyframe_insert(data_path="location", frame=120)
camera.keyframe_insert(data_path="rotation_euler", frame=120)

# Add camera tracking to bob (before explosion)
bpy.context.scene.frame_set(1)
bpy.ops.object.constraint_add(type='TRACK_TO')
camera.constraints["Track To"].target = bob
camera.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
camera.constraints["Track To"].up_axis = 'UP_Y'

# Disable tracking after explosion (frame 35)
bpy.context.scene.frame_set(35)
camera.constraints["Track To"].influence = 1.0
camera.constraints["Track To"].keyframe_insert(data_path="influence", frame=35)
bpy.context.scene.frame_set(36)
camera.constraints["Track To"].influence = 0.0
camera.constraints["Track To"].keyframe_insert(data_path="influence", frame=36)

# ============================================
# 7. SETUP LIGHTING
# ============================================
# Add lighting
bpy.ops.object.light_add(type='SUN', location=[5, -5, 10])
sun = bpy.context.active_object
sun.data.energy = 5.0

# Point light for explosion glow (animated)
bpy.ops.object.light_add(type='POINT', location=""" + str(explosion_location) + """)
point_light = bpy.context.active_object
point_light.name = "ExplosionLight"
point_light.data.energy = 50.0
point_light.data.color = (1.0, 0.5, 0.1)  # Orange explosion light

# Animate explosion light intensity
bpy.context.scene.frame_set(30)
point_light.data.energy = 200.0  # Bright at explosion
point_light.data.keyframe_insert(data_path="energy", frame=30)

bpy.context.scene.frame_set(50)
point_light.data.energy = 100.0  # Dimming
point_light.data.keyframe_insert(data_path="energy", frame=50)

bpy.context.scene.frame_set(100)
point_light.data.energy = 20.0  # Fading
point_light.data.keyframe_insert(data_path="energy", frame=100)

print("\\n=== Smoke Explosion with Bob Created ===")
print("Bob location: """ + str(bob_location) + """")
print("Explosion location: """ + str(explosion_location) + """")
print("Explosion intensity: """ + explosion_intensity + """")
print("Domain size: """ + str(domain_size) + """")
print("Resolution: """ + str(resolution) + """")
print("\\nNext steps:")
print("1. Preview bob animation (frames 1-40)")
print("2. Bake smoke simulation")
print("3. Render explosion sequence")
""")
    
    return "\n".join(code_parts).strip()


def create_bob_explosion_scene_code(
    bob_start_height: float = 5.0,
    explosion_height: float = 1.0,
    explosion_intensity: str = "high"
) -> str:
    """
    Create complete bob explosion scene with animation
    
    Args:
        bob_start_height: Starting height of bob
        explosion_height: Height where explosion occurs
        explosion_intensity: low, medium, high
    
    Returns:
        Complete scene setup code
    """
    return create_explosion_smoke_code(
        bob_location=[0, 0, bob_start_height],
        explosion_location=[0, 0, explosion_height],
        domain_size=[10, 10, 10],
        resolution=128,
        explosion_intensity=explosion_intensity
    )

