"""
Demonstration script for using Sanctus Library procedural shaders
This script shows how to use Sanctus Library materials in Blender

Sanctus Library: https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/
"""

import bpy
from sanctus_library_tools import (
    check_sanctus_installed,
    apply_sanctus_material_to_object,
    create_code_apply_sanctus_material,
    create_code_list_sanctus_materials,
    create_code_setup_sanctus_material_workflow,
    get_sanctus_material_categories,
    create_code_apply_sanctus_by_category
)


def main():
    """Main demonstration function"""
    print("=" * 70)
    print("Sanctus Library Integration Demo")
    print("=" * 70)
    
    # Check if Sanctus Library is installed
    if not check_sanctus_installed():
        print("\n❌ Sanctus Library addon is not installed or enabled")
        print("\nTo install:")
        print("1. Purchase and download from:")
        print("   https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/")
        print("2. In Blender: Edit > Preferences > Add-ons")
        print("3. Click 'Install...' and select the Sanctus Library .zip file")
        print("4. Enable the addon")
        print("\nAfter installation, run this script again.")
        return
    
    print("\n✅ Sanctus Library addon is installed!")
    
    # List available materials
    print("\n" + "-" * 70)
    print("Available Sanctus Library Materials:")
    print("-" * 70)
    materials = bpy.data.materials
    sanctus_materials = []
    
    for mat in materials:
        # Check if material is from Sanctus Library
        # Materials may have specific naming patterns or asset metadata
        if hasattr(mat, 'asset_data') and mat.asset_data:
            sanctus_materials.append(mat.name)
            print(f"  • {mat.name}")
    
    if not sanctus_materials:
        print("  No Sanctus Library materials found in current scene")
        print("\n  To load Sanctus Library materials:")
        print("  1. Open Asset Browser (Shift+A)")
        print("  2. Browse Sanctus Library assets")
        print("  3. Drag materials into the scene or link them")
    
    # Show categories
    print("\n" + "-" * 70)
    print("Available Material Categories:")
    print("-" * 70)
    categories = get_sanctus_material_categories()
    for category in categories:
        print(f"  • {category}")
    
    # Example: Apply material to selected object
    print("\n" + "-" * 70)
    print("Applying Materials:")
    print("-" * 70)
    
    if bpy.context.selected_objects:
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH':
            print(f"\nSelected object: {obj.name}")
            print("\nTo apply a Sanctus Library material:")
            print("1. Use Asset Browser (Shift+A) to browse materials")
            print("2. Drag material onto object, or")
            print("3. Use Python:")
            print(f"   mat = bpy.data.materials.get('MaterialName')")
            print(f"   {obj.name}.data.materials.append(mat)")
            
            # Try to apply a material by category if available
            if sanctus_materials:
                # Example: Try to find a metal material
                metal_materials = [m for m in sanctus_materials if 'metal' in m.lower()]
                if metal_materials:
                    mat_name = metal_materials[0]
                    result = apply_sanctus_material_to_object(obj.name, mat_name)
                    if result["status"] == "success":
                        print(f"\n✅ Applied material: {mat_name}")
                    else:
                        print(f"\n⚠️  {result['message']}")
        else:
            print("\n⚠️  No mesh object selected")
    else:
        print("\n⚠️  No object selected")
        print("\nTo use Sanctus Library materials:")
        print("1. Create or select a mesh object")
        print("2. Open Asset Browser (Shift+A)")
        print("3. Browse Sanctus Library materials")
        print("4. Drag material onto object")
    
    print("\n" + "=" * 70)
    print("For more information, see: sanctus_library_tools.py")
    print("=" * 70)


if __name__ == "__main__":
    main()

