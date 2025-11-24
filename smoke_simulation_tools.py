#!/usr/bin/env python3
"""
Realistic Smoke Simulation Tools for VFX Agent
Based on Blender 3.0+ smoke simulation best practices
Part I: Scene & Simulation Setup
"""

from typing import Dict, Any, Optional, List, Tuple


def create_smoke_domain_code(
    domain_name: str = "SmokeDomain",
    location: Optional[List[float]] = None,
    size: Optional[List[float]] = None,
    resolution: int = 64,
    time_scale: float = 1.0,
    use_high_resolution: bool = False,
    high_resolution_divider: int = 2
) -> str:
    """
    Create smoke simulation domain (Part I: Scene Setup)
    
    Args:
        domain_name: Name for the domain object
        location: Domain position [x, y, z]
        size: Domain size [x, y, z]
        resolution: Base resolution (32, 64, 128, 256)
        time_scale: Time scale factor (1.0 = normal speed)
        use_high_resolution: Enable high resolution smoke
        high_resolution_divider: High res divider (2, 4, 8)
    
    Returns:
        Blender Python code for domain setup
    """
    location = location or [0, 0, 0]
    size = size or [4, 4, 4]
    
    code = f"""
# Create Smoke Domain - Part I: Scene & Simulation Setup
import bpy
import bmesh

# Clear existing domain if it exists
if "{domain_name}" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["{domain_name}"])

# Create domain cube
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location={location}
)
domain_obj = bpy.context.active_object
domain_obj.name = "{domain_name}"

# Scale domain to desired size
domain_obj.scale = {size}

# Add Fluid modifier (smoke domain)
fluid_mod = domain_obj.modifiers.new(name="Fluid", type='FLUID')
fluid_mod.fluid_type = 'DOMAIN'

# Get domain settings
domain = fluid_mod.domain_settings

# Domain Type: Gas (for smoke)
domain.domain_type = 'GAS'

# Resolution Settings
domain.resolution_max = {resolution}
domain.time_scale = {time_scale}

# High Resolution Smoke (for realistic detail)
try:
    domain.use_high_resolution = {str(use_high_resolution).lower()}
    if {str(use_high_resolution).lower()}:
        domain.high_resolution_max = {resolution} // {high_resolution_divider}
except AttributeError:
    # High resolution not available in this Blender version
    pass

# Smoke Settings
domain.use_dissolve_smoke = True
domain.dissolve_speed = 100
domain.use_dissolve_smoke_log = True

# Noise Settings (for realistic turbulence)
domain.use_noise = True
domain.noise_scale = 1  # Integer value
domain.noise_strength = 0.5
domain.noise_pos_scale = 0.5
domain.noise_time_anim = 0.5

# Cache Settings
domain.cache_type = 'MODULAR'
domain.cache_directory = "//cache_smoke_{domain_name}"

# Boundary Settings
domain.boundary_width = 2
domain.use_collision_boundary = True

# Temperature Settings (for realistic smoke behavior)
domain.use_temperature = True
domain.temperature_threshold = 0.0

# Velocity Settings
domain.use_velocity = True

print(f"Smoke domain '{domain_obj.name}' created at {domain_obj.location}")
print(f"Domain size: {domain_obj.scale}")
print(f"Resolution: {resolution}")
"""
    
    return code.strip()


def create_smoke_flow_code(
    flow_name: str = "SmokeFlow",
    location: Optional[List[float]] = None,
    size: Optional[List[float]] = None,
    flow_type: str = "SMOKE",
    flow_behavior: str = "INFLOW",
    temperature: float = 1.0,
    density: float = 1.0,
    smoke_color: Optional[List[float]] = None,
    fuel_amount: float = 0.0,
    use_initial_velocity: bool = True,
    velocity: Optional[List[float]] = None,
    fire_brightness: float = 1.0,
    fire_heat: float = 1.0
) -> str:
    """
    Create smoke/fire flow source
    
    Args:
        flow_name: Name for the flow object
        location: Flow position [x, y, z]
        size: Flow emitter size [x, y, z]
        flow_type: SMOKE, FIRE, BOTH
        flow_behavior: INFLOW, OUTFLOW, GEOMETRY
        temperature: Temperature (affects smoke rise)
        density: Smoke density (0.0 to 1.0)
        smoke_color: Smoke color [r, g, b]
        fuel_amount: Fuel for fire (0.0 to 1.0)
        use_initial_velocity: Add initial velocity
        velocity: Initial velocity [x, y, z]
        fire_brightness: Fire brightness (0.0 to 10.0)
        fire_heat: Fire heat intensity (0.0 to 10.0)
    
    Returns:
        Blender Python code for flow setup
    """
    location = location or [0, 0, 0]
    size = size or [0.5, 0.5, 0.5]
    smoke_color = smoke_color or [0.7, 0.7, 0.7]
    velocity = velocity or [0, 0, 1]  # Default: upward
    
    code = f"""
# Create Smoke Flow Source
import bpy

# Clear existing flow if it exists
if "{flow_name}" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["{flow_name}"])

# Create flow emitter (cube or sphere)
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location={location}
)
flow_obj = bpy.context.active_object
flow_obj.name = "{flow_name}"

# Scale flow emitter
flow_obj.scale = {size}

# Add Fluid modifier (smoke flow)
fluid_mod = flow_obj.modifiers.new(name="Fluid", type='FLUID')
fluid_mod.fluid_type = 'FLOW'

# Get flow settings
flow = fluid_mod.flow_settings

# Flow Type
flow.flow_type = '{flow_type}'
flow.flow_behavior = '{flow_behavior}'

# Smoke Settings
flow.smoke_amount = {density}
flow.temperature = {temperature}

# Smoke Color
flow.smoke_color = {smoke_color}

# Fuel (for fire)
flow.fuel_amount = {fuel_amount}

# Fire Settings (if fire is enabled)
if '{flow_type}' in ['FIRE', 'BOTH']:
    flow.use_flame = True
    flow.flame_ignition = 0.0
    flow.flame_smoke = 0.0
    flow.flame_vorticity = 0.0
    flow.flame_lifetime = 0.0
    # Fire brightness and heat
    flow.flame_brightness = {fire_brightness}
    flow.flame_heat = {fire_heat}

# Initial Velocity
flow.use_initial_velocity = {str(use_initial_velocity).lower()}
if {str(use_initial_velocity).lower()}:
    flow.velocity_factor = 1.0
    flow.velocity = {velocity}

# Emission Settings
flow.use_absorbtion = False
flow.surface_emission = 0.0
flow.volume_emission = 1.0

print(f"Flow '{flow_obj.name}' created at {flow_obj.location}")
print(f"Flow type: {flow_type}, Density: {density}, Temperature: {temperature}")
if '{flow_type}' in ['FIRE', 'BOTH']:
    print(f"Fire: Fuel={fuel_amount}, Brightness={fire_brightness}, Heat={fire_heat}")
"""
    
    return code.strip()


def create_smoke_collision_code(
    collision_name: str = "SmokeCollision",
    location: Optional[List[float]] = None,
    size: Optional[List[float]] = None
) -> str:
    """
    Create collision object for smoke
    
    Args:
        collision_name: Name for collision object
        location: Collision position [x, y, z]
        size: Collision size [x, y, z]
    
    Returns:
        Blender Python code for collision setup
    """
    location = location or [0, 0, 0]
    size = size or [1, 1, 1]
    
    code = f"""
# Create Smoke Collision Object
import bpy

# Clear existing collision if it exists
if "{collision_name}" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["{collision_name}"])

# Create collision object
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location={location}
)
collision_obj = bpy.context.active_object
collision_obj.name = "{collision_name}"

# Scale collision
collision_obj.scale = {size}

# Add Fluid modifier (collision)
fluid_mod = collision_obj.modifiers.new(name="Fluid", type='FLUID')
fluid_mod.fluid_type = 'COLLISION'

# Collision settings
collision = fluid_mod.collision_settings
collision.collision_type = 'COLLISION'
collision.use_collision = True

print(f"Collision object '{collision_obj.name}' created")
"""
    
    return code.strip()


def create_complete_smoke_setup_code(
    domain_location: Optional[List[float]] = None,
    domain_size: Optional[List[float]] = None,
    flow_location: Optional[List[float]] = None,
    resolution: int = 64,
    smoke_density: float = 1.0,
    smoke_temperature: float = 1.0
) -> str:
    """
    Create complete realistic smoke setup (Part I: Scene & Simulation Setup)
    
    Args:
        domain_location: Domain position
        domain_size: Domain size
        flow_location: Flow emitter position
        resolution: Simulation resolution
        smoke_density: Smoke density
        smoke_temperature: Smoke temperature
    
    Returns:
        Complete setup code
    """
    domain_location = domain_location or [0, 0, 2]
    domain_size = domain_size or [6, 6, 6]
    flow_location = flow_location or [0, 0, 0]
    
    code = f"""
# Complete Realistic Smoke Setup - Part I: Scene & Simulation Setup
# Based on Blender 3.0+ best practices

{create_smoke_domain_code(
    domain_name="SmokeDomain",
    location=domain_location,
    size=domain_size,
    resolution=resolution,
    use_high_resolution=True,
    high_resolution_divider=2
)}

# Create smoke flow source
{create_smoke_flow_code(
    flow_name="SmokeFlow",
    location=flow_location,
    size=[0.3, 0.3, 0.3],
    flow_type="SMOKE",
    temperature=smoke_temperature,
    density=smoke_density,
    use_initial_velocity=True,
    velocity=[0, 0, 1]
)}

print("\\n=== Smoke Simulation Setup Complete ===")
print("Next steps:")
print("1. Position domain and flow objects")
print("2. Adjust resolution and settings")
print("3. Bake simulation (Part II)")
print("4. Setup materials and lighting (Part III)")
"""
    
    return code.strip()


def get_smoke_material_code(
    material_name: str = "SmokeMaterial",
    color: Optional[List[float]] = None,
    density: float = 1.0,
    anisotropy: float = 0.0
) -> str:
    """
    Create smoke material (for Part III)
    
    Args:
        material_name: Material name
        color: Smoke color [r, g, b]
        density: Material density
        anisotropy: Anisotropy factor
    
    Returns:
        Material setup code
    """
    color = color or [0.7, 0.7, 0.7]
    
    code = f"""
# Smoke Material Setup (Part III: Materials)
import bpy

# Create material
mat = bpy.data.materials.new(name="{material_name}")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add Principled Volume shader (for smoke)
volume_shader = nodes.new(type='ShaderNodeVolumePrincipled')
volume_shader.location = (0, 0)

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Connect volume shader
links.new(volume_shader.outputs['Volume'], output.inputs['Volume'])

# Configure smoke properties
volume_shader.inputs['Density'].default_value = {density}
volume_shader.inputs['Color'].default_value = ({color[0]}, {color[1]}, {color[2]}, 1.0)
volume_shader.inputs['Anisotropy'].default_value = {anisotropy}

# Assign to domain
domain_obj = bpy.data.objects.get("SmokeDomain")
if domain_obj:
    domain_obj.data.materials.append(mat)

print(f"Smoke material '{material_name}' created and assigned")
"""
    
    return code.strip()


def get_smoke_baking_code(
    domain_name: str = "SmokeDomain",
    start_frame: int = 1,
    end_frame: int = 250,
    use_high_resolution: bool = True
) -> str:
    """
    Get smoke baking code (for Part II)
    
    Args:
        domain_name: Domain object name
        start_frame: Start frame
        end_frame: End frame
        use_high_resolution: Bake high resolution
    
    Returns:
        Baking code
    """
    code = f"""
# Smoke Simulation Baking (Part II: Baking)
import bpy

domain_obj = bpy.data.objects.get("{domain_name}")
if not domain_obj:
    raise ValueError("Domain object '{domain_name}' not found")

# Get domain settings
fluid_mod = domain_obj.modifiers.get("Fluid")
if not fluid_mod:
    raise ValueError("Fluid modifier not found")

domain = fluid_mod.domain_settings

# Set frame range
bpy.context.scene.frame_start = {start_frame}
bpy.context.scene.frame_end = {end_frame}

# Baking settings
domain.cache_frame_start = {start_frame}
domain.cache_frame_end = {end_frame}

# High resolution baking
domain.use_high_resolution = {str(use_high_resolution).lower()}

print(f"Ready to bake smoke simulation from frame {start_frame} to {end_frame}")
print("Use: bpy.ops.fluid.bake() to start baking")
"""
    
    return code.strip()

