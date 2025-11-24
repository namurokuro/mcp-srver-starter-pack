#!/usr/bin/env python3
"""
Fire Simulation Tools for VFX Agent
Enhances smoke simulation with comprehensive fire effects
Based on Blender 3.0+ fire and smoke simulation best practices
"""

from typing import Dict, Any, Optional, List
from smoke_simulation_tools import (
    create_smoke_domain_code,
    create_smoke_flow_code,
    create_smoke_collision_code
)


def create_fire_and_smoke_setup_code(
    domain_location: Optional[List[float]] = None,
    domain_size: Optional[List[float]] = None,
    flow_location: Optional[List[float]] = None,
    resolution: int = 64,
    smoke_density: float = 1.0,
    fire_fuel: float = 0.5,
    fire_brightness: float = 2.0,
    fire_heat: float = 2.0,
    temperature: float = 2.0
) -> str:
    """
    Create complete fire and smoke simulation setup
    
    Args:
        domain_location: Domain position
        domain_size: Domain size
        flow_location: Flow emitter position
        resolution: Simulation resolution
        smoke_density: Smoke density
        fire_fuel: Fuel amount for fire
        fire_brightness: Fire brightness
        fire_heat: Fire heat intensity
        temperature: Temperature
    
    Returns:
        Complete fire and smoke setup code
    """
    domain_location = domain_location or [0, 0, 2]
    domain_size = domain_size or [6, 6, 6]
    flow_location = flow_location or [0, 0, 0]
    
    code = f"""
# Complete Fire and Smoke Simulation Setup
# Based on Blender 3.0+ best practices

{create_smoke_domain_code(
    domain_name="FireSmokeDomain",
    location=domain_location,
    size=domain_size,
    resolution=resolution,
    use_high_resolution=True,
    high_resolution_divider=2
)}

# Create fire and smoke flow source
{create_smoke_flow_code(
    flow_name="FireSmokeFlow",
    location=flow_location,
    size=[0.3, 0.3, 0.3],
    flow_type="BOTH",  # Both smoke and fire
    temperature=temperature,
    density=smoke_density,
    fuel_amount=fire_fuel,
    fire_brightness=fire_brightness,
    fire_heat=fire_heat,
    use_initial_velocity=True,
    velocity=[0, 0, 1]  # Upward
)}

print("\\n=== Fire and Smoke Simulation Setup Complete ===")
print("Fire settings:")
print(f"  Fuel: {fire_fuel}")
print(f"  Brightness: {fire_brightness}")
print(f"  Heat: {fire_heat}")
print(f"  Temperature: {temperature}")
print("\\nNext steps:")
print("1. Adjust fire and smoke settings")
print("2. Bake simulation")
print("3. Setup materials for fire and smoke")
print("4. Configure lighting for fire")
"""
    
    return code.strip()


def create_fire_material_code(
    material_name: str = "FireMaterial",
    emission_strength: float = 10.0,
    emission_color: Optional[List[float]] = None,
    use_emission: bool = True
) -> str:
    """
    Create fire material with emission
    
    Args:
        material_name: Material name
        emission_strength: Emission strength
        emission_color: Emission color [r, g, b]
        use_emission: Enable emission
    
    Returns:
        Fire material setup code
    """
    emission_color = emission_color or [1.0, 0.5, 0.1]  # Orange fire color
    
    code = f"""
# Fire Material Setup
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

# Add Emission shader (for fire)
emission = nodes.new(type='ShaderNodeEmission')
emission.location = (0, -200)
emission.inputs['Strength'].default_value = {emission_strength}
emission.inputs['Color'].default_value = ({emission_color[0]}, {emission_color[1]}, {emission_color[2]}, 1.0)

# Add Material Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)

# Connect shaders
links.new(volume_shader.outputs['Volume'], output.inputs['Volume'])
if {str(use_emission).lower()}:
    links.new(emission.outputs['Emission'], output.inputs['Surface'])

# Configure smoke properties
volume_shader.inputs['Density'].default_value = 0.5
volume_shader.inputs['Color'].default_value = (0.7, 0.7, 0.7, 1.0)

# Assign to domain
domain_obj = bpy.data.objects.get("FireSmokeDomain")
if domain_obj:
    domain_obj.data.materials.append(mat)

print(f"Fire material '{material_name}' created with emission strength {emission_strength}")
"""
    
    return code.strip()


def create_fire_lighting_code(
    light_location: Optional[List[float]] = None,
    light_type: str = "POINT",
    energy: float = 100.0,
    color: Optional[List[float]] = None
) -> str:
    """
    Create lighting for fire effect
    
    Args:
        light_location: Light position
        light_type: POINT, SUN, SPOT, AREA
        energy: Light energy
        color: Light color [r, g, b]
    
    Returns:
        Fire lighting setup code
    """
    light_location = light_location or [0, 0, 1]
    color = color or [1.0, 0.5, 0.1]  # Orange fire light
    
    code = f"""
# Fire Lighting Setup
import bpy

# Create light
bpy.ops.object.light_add(
    type='{light_type}',
    location={light_location}
)
light_obj = bpy.context.active_object
light_obj.name = "FireLight"

# Configure light
light = light_obj.data
light.energy = {energy}
light.color = ({color[0]}, {color[1]}, {color[2]})

# Enable shadows for realistic fire
light.use_shadow = True
light.shadow_soft_size = 0.5

print(f"Fire light created at {light_location} with energy {energy}")
"""
    
    return code.strip()


def create_complete_fire_smoke_scene_code(
    domain_location: Optional[List[float]] = None,
    domain_size: Optional[List[float]] = None,
    flow_location: Optional[List[float]] = None,
    resolution: int = 64,
    fire_intensity: str = "medium"
) -> str:
    """
    Create complete fire and smoke scene with materials and lighting
    
    Args:
        domain_location: Domain position
        domain_size: Domain size
        flow_location: Flow position
        resolution: Simulation resolution
        fire_intensity: low, medium, high
    
    Returns:
        Complete scene setup code
    """
    # Fire intensity presets
    intensity_presets = {
        "low": {"fuel": 0.3, "brightness": 1.0, "heat": 1.0, "temp": 1.5, "energy": 50.0},
        "medium": {"fuel": 0.5, "brightness": 2.0, "heat": 2.0, "temp": 2.0, "energy": 100.0},
        "high": {"fuel": 0.8, "brightness": 4.0, "heat": 4.0, "temp": 3.0, "energy": 200.0}
    }
    
    preset = intensity_presets.get(fire_intensity.lower(), intensity_presets["medium"])
    
    domain_location = domain_location or [0, 0, 2]
    domain_size = domain_size or [6, 6, 6]
    flow_location = flow_location or [0, 0, 0]
    
    code = f"""
# Complete Fire and Smoke Scene Setup
# Includes: Domain, Flow, Materials, and Lighting

{create_fire_and_smoke_setup_code(
    domain_location=domain_location,
    domain_size=domain_size,
    flow_location=flow_location,
    resolution=resolution,
    smoke_density=1.0,
    fire_fuel=preset["fuel"],
    fire_brightness=preset["brightness"],
    fire_heat=preset["heat"],
    temperature=preset["temp"]
)}

# Create fire material
{create_fire_material_code(
    emission_strength=preset["brightness"] * 5,
    emission_color=[1.0, 0.5, 0.1]
)}

# Create fire lighting
{create_fire_lighting_code(
    light_location=[flow_location[0], flow_location[1], flow_location[2] + 1],
    energy=preset["energy"],
    color=[1.0, 0.5, 0.1]
)}

print("\\n=== Complete Fire and Smoke Scene Ready ===")
print(f"Fire intensity: {fire_intensity}")
print("Scene includes:")
print("  - Fire and smoke domain")
print("  - Fire and smoke flow emitter")
print("  - Fire material with emission")
print("  - Fire lighting")
print("\\nReady to bake simulation!")
"""
    
    return code.strip()

