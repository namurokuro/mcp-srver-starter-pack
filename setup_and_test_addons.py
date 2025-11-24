#!/usr/bin/env python3
"""
Setup and Test All Addons
Creates a comprehensive test scene using all three addons
Run this in Blender's text editor
"""

import bpy
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print("=" * 70)
print("SETUP AND TEST ALL ADDONS")
print("=" * 70)

# Import all addon tools
try:
    from modeling_addon_tools import (
        check_modeling_addon_installed,
        enhance_object_with_modeling_addon
    )
    MODELING_AVAILABLE = True
except ImportError:
    MODELING_AVAILABLE = False
    print("⚠ modeling_addon_tools not available")

try:
    from sanctus_library_tools import (
        check_sanctus_installed,
        get_sanctus_materials,
        apply_sanctus_material_to_object
    )
    SANCTUS_AVAILABLE = True
except ImportError:
    SANCTUS_AVAILABLE = False
    print("⚠ sanctus_library_tools not available")

try:
    from dmx_lighting_tools import (
        check_dmx_installed,
        setup_dmx_lighting_rig
    )
    DMX_AVAILABLE = True
except ImportError:
    DMX_AVAILABLE = False
    print("⚠ dmx_lighting_tools not available")

# Clear scene
print("\n[1] Clearing scene...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
print("✓ Scene cleared")

# Create objects
print("\n[2] Creating test objects...")
objects = {}

# Cube
bpy.ops.mesh.primitive_cube_add(location=(-3, 0, 1))
objects['cube'] = bpy.context.object
objects['cube'].name = "Test_Cube"
print(f"✓ Created {objects['cube'].name}")

# Sphere
bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 1))
objects['sphere'] = bpy.context.object
objects['sphere'].name = "Test_Sphere"
print(f"✓ Created {objects['sphere'].name}")

# Cylinder
bpy.ops.mesh.primitive_cylinder_add(location=(3, 0, 1))
objects['cylinder'] = bpy.context.object
objects['cylinder'].name = "Test_Cylinder"
print(f"✓ Created {objects['cylinder'].name}")

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
objects['ground'] = bpy.context.object
objects['ground'].name = "Ground_Plane"
print(f"✓ Created {objects['ground'].name}")

# Apply modeling addon
print("\n[3] Applying Modeling Addon (ND Addon)...")
if MODELING_AVAILABLE and check_modeling_addon_installed():
    for obj_name, obj in objects.items():
        if obj.type == 'MESH' and obj_name != 'ground':
            result = enhance_object_with_modeling_addon(
                obj.name, 
                operations=['bevel', 'subdivision']
            )
            if result["status"] == "success":
                print(f"✓ Applied to {obj.name}: {', '.join(result['operations'])}")
            else:
                print(f"⚠ {obj.name}: {result['message']}")
else:
    print("⚠ Modeling addon not available, using standard modifiers")
    for obj_name, obj in objects.items():
        if obj.type == 'MESH' and obj_name != 'ground':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_add(type='BEVEL')
            obj.modifiers["Bevel"].width = 0.1
            obj.modifiers["Bevel"].segments = 3
            print(f"✓ Applied standard bevel to {obj.name}")

# Apply Sanctus materials
print("\n[4] Applying Sanctus Library Materials...")
if SANCTUS_AVAILABLE and check_sanctus_installed():
    # Get available materials
    sanctus_materials = get_sanctus_materials()
    all_materials = list(bpy.data.materials)
    
    # Try to find materials by keywords
    material_map = {
        'cube': ['metal', 'red', 'chrome'],
        'sphere': ['metal', 'chrome', 'silver'],
        'cylinder': ['metal', 'blue', 'steel'],
        'ground': ['concrete', 'stone', 'floor']
    }
    
    materials_applied = 0
    for obj_key, keywords in material_map.items():
        if obj_key in objects:
            obj = objects[obj_key]
            mat_found = False
            
            # Try to find matching material
            for mat in all_materials:
                if any(kw.lower() in mat.name.lower() for kw in keywords):
                    result = apply_sanctus_material_to_object(obj.name, mat.name)
                    if result.get("status") == "success":
                        print(f"✓ Applied {mat.name} to {obj.name}")
                        materials_applied += 1
                        mat_found = True
                        break
            
            if not mat_found:
                # Create fallback material
                mat = bpy.data.materials.new(name=f"{obj.name}_Material")
                mat.use_nodes = True
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                colors = {
                    'cube': (0.8, 0.2, 0.2),
                    'sphere': (0.7, 0.7, 0.7),
                    'cylinder': (0.2, 0.2, 0.8),
                    'ground': (0.3, 0.3, 0.3)
                }
                bsdf.inputs["Base Color"].default_value = (*colors.get(obj_key, (0.5, 0.5, 0.5)), 1.0)
                if obj_key != 'ground':
                    bsdf.inputs["Metallic"].default_value = 0.8
                obj.data.materials.append(mat)
                print(f"✓ Created fallback material for {obj.name}")
    
    if materials_applied > 0:
        print(f"\n✓ Applied {materials_applied} Sanctus materials")
else:
    print("⚠ Sanctus Library not available, creating standard materials")
    for obj_key, obj in objects.items():
        mat = bpy.data.materials.new(name=f"{obj.name}_Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        colors = {
            'cube': (0.8, 0.2, 0.2),
            'sphere': (0.7, 0.7, 0.7),
            'cylinder': (0.2, 0.2, 0.8),
            'ground': (0.3, 0.3, 0.3)
        }
        bsdf.inputs["Base Color"].default_value = (*colors.get(obj_key, (0.5, 0.5, 0.5)), 1.0)
        if obj_key != 'ground':
            bsdf.inputs["Metallic"].default_value = 0.8
        obj.data.materials.append(mat)

# Setup DMX lighting
print("\n[5] Setting up DMX Lighting...")
if DMX_AVAILABLE and check_dmx_installed():
    result = setup_dmx_lighting_rig("three_point")
    if result["status"] == "success":
        print(f"✓ {result['message']}")
    else:
        print(f"⚠ {result['message']}")
        # Fallback
        bpy.ops.object.light_add(type='SUN', location=(4, -4, 5))
        sun = bpy.context.object
        sun.data.energy = 3
        print("✓ Created fallback lighting")
else:
    print("⚠ DMX not available, creating standard lighting")
    bpy.ops.object.light_add(type='SUN', location=(4, -4, 5))
    sun = bpy.context.object
    sun.data.energy = 3
    bpy.ops.object.light_add(type='AREA', location=(-2, -2, 3))
    area = bpy.context.object
    area.data.energy = 100
    area.data.size = 5
    print("✓ Created standard lighting")

# Add camera
print("\n[6] Setting up camera...")
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.object
camera.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = camera
print("✓ Camera added and set as active")

# Set render settings
print("\n[7] Setting render settings...")
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
print("✓ Render settings configured (Cycles, 1920x1080, 128 samples)")

# Summary
print("\n" + "=" * 70)
print("SETUP COMPLETE")
print("=" * 70)
print("\nAddon Status:")
print(f"  Modeling Addon (ND): {'✓ Available' if (MODELING_AVAILABLE and check_modeling_addon_installed()) else '✗ Not available'}")
print(f"  Sanctus Library: {'✓ Available' if (SANCTUS_AVAILABLE and check_sanctus_installed()) else '✗ Not available'}")
print(f"  DMX Lighting: {'✓ Available' if (DMX_AVAILABLE and check_dmx_installed()) else '✗ Not available'}")
print("\nScene ready! Press F12 to render.")
print("\nTo run full-scale render system:")
print("  - Use run_fullscale_test.py in Blender")


