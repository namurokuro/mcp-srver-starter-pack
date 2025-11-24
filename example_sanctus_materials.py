"""
Example: Using Sanctus Library Procedural Shaders
Creates a scene with objects and applies Sanctus Library materials

Run this script in Blender to see Sanctus Library materials in action
"""

import bpy
from sanctus_library_tools import (
    check_sanctus_installed,
    apply_sanctus_material_to_object,
    get_sanctus_material_categories
)


def clear_scene():
    """Clear the default scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)


def create_demo_scene():
    """Create a demo scene with various objects"""
    # Clear scene
    clear_scene()
    
    # Create objects
    objects = {}
    
    # Ground plane
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
    objects['ground'] = bpy.context.active_object
    objects['ground'].name = "Ground"
    
    # Cube (for metal material)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(-3, 0, 1))
    objects['cube'] = bpy.context.active_object
    objects['cube'].name = "MetalCube"
    
    # Sphere (for fabric material)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 1))
    objects['sphere'] = bpy.context.active_object
    objects['sphere'].name = "FabricSphere"
    
    # Cylinder (for wood material)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=2, location=(3, 0, 1))
    objects['cylinder'] = bpy.context.active_object
    objects['cylinder'].name = "WoodCylinder"
    
    return objects


def apply_sanctus_materials(objects):
    """Apply Sanctus Library materials to objects"""
    if not check_sanctus_installed():
        print("Sanctus Library not installed. Using default materials.")
        return False
    
    # Get all materials
    all_materials = list(bpy.data.materials)
    
    # Try to find Sanctus Library materials by category
    metal_materials = [m for m in all_materials if any(
        keyword in m.name.lower() for keyword in ['metal', 'metallic', 'steel', 'iron']
    )]
    
    fabric_materials = [m for m in all_materials if any(
        keyword in m.name.lower() for keyword in ['fabric', 'cloth', 'textile', 'fabric']
    )]
    
    wood_materials = [m for m in all_materials if any(
        keyword in m.name.lower() for keyword in ['wood', 'wooden', 'timber', 'oak']
    )]
    
    stone_materials = [m for m in all_materials if any(
        keyword in m.name.lower() for keyword in ['stone', 'rock', 'concrete', 'marble']
    )]
    
    # Apply materials
    applied = False
    
    if metal_materials and 'cube' in objects:
        mat = metal_materials[0]
        result = apply_sanctus_material_to_object(objects['cube'].name, mat.name)
        if result["status"] == "success":
            print(f"✅ Applied {mat.name} to {objects['cube'].name}")
            applied = True
    
    if fabric_materials and 'sphere' in objects:
        mat = fabric_materials[0]
        result = apply_sanctus_material_to_object(objects['sphere'].name, mat.name)
        if result["status"] == "success":
            print(f"✅ Applied {mat.name} to {objects['sphere'].name}")
            applied = True
    
    if wood_materials and 'cylinder' in objects:
        mat = wood_materials[0]
        result = apply_sanctus_material_to_object(objects['cylinder'].name, mat.name)
        if result["status"] == "success":
            print(f"✅ Applied {mat.name} to {objects['cylinder'].name}")
            applied = True
    
    if stone_materials and 'ground' in objects:
        mat = stone_materials[0]
        result = apply_sanctus_material_to_object(objects['ground'].name, mat.name)
        if result["status"] == "success":
            print(f"✅ Applied {mat.name} to {objects['ground'].name}")
            applied = True
    
    if not applied:
        print("\n⚠️  No Sanctus Library materials found in scene")
        print("To use Sanctus Library materials:")
        print("1. Open Asset Browser (Shift+A)")
        print("2. Browse Sanctus Library materials")
        print("3. Link or append materials to the scene")
        print("4. Run this script again")
    
    return applied


def setup_lighting():
    """Setup basic lighting"""
    # Add sun light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3
    sun.rotation_euler = (0.785, 0, 0.785)
    
    # Add area light
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 100
    area.data.size = 5


def setup_camera():
    """Setup camera"""
    bpy.ops.object.camera_add(location=(7, -7, 5))
    camera = bpy.context.active_object
    camera.rotation_euler = (1.1, 0, 0.785)
    
    # Set as active camera
    bpy.context.scene.camera = camera


def main():
    """Main function"""
    print("=" * 70)
    print("Sanctus Library Material Demo")
    print("=" * 70)
    
    # Check Sanctus Library
    if not check_sanctus_installed():
        print("\n⚠️  Sanctus Library addon not installed")
        print("Install from: https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/")
        print("\nCreating scene with default materials...")
    
    # Create scene
    print("\nCreating demo scene...")
    objects = create_demo_scene()
    
    # Setup lighting and camera
    print("Setting up lighting and camera...")
    setup_lighting()
    setup_camera()
    
    # Apply Sanctus Library materials
    print("\nApplying Sanctus Library materials...")
    applied = apply_sanctus_materials(objects)
    
    if applied:
        print("\n✅ Sanctus Library materials applied successfully!")
    else:
        print("\n⚠️  Using default materials")
        print("Load Sanctus Library materials from Asset Browser to see them applied")
    
    print("\n" + "=" * 70)
    print("Scene created! Press F12 to render")
    print("=" * 70)


if __name__ == "__main__":
    main()

