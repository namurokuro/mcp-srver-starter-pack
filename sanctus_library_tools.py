"""
Sanctus Library Addon Integration Tools
Integrates Sanctus Library procedural shaders collection for Blender
https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/
"""

import bpy
from typing import Dict, List, Optional, Any


def check_sanctus_installed() -> bool:
    """Check if Sanctus Library addon is installed and enabled"""
    addons = bpy.context.preferences.addons
    # Check for exact addon names: "Sanctus - Library" or "Sanctus Bake"
    if 'Sanctus - Library' in addons or 'Sanctus Bake' in addons:
        return True
    # Check for variations
    sanctus_addons = [addon for addon in addons.keys() if 'sanctus' in addon.lower()]
    return len(sanctus_addons) > 0


def get_sanctus_materials() -> List[str]:
    """Get list of available Sanctus Library materials"""
    materials = []
    if not check_sanctus_installed():
        return materials
    
    # Access Sanctus Library materials through asset library
    # Sanctus Library stores materials in its asset library
    try:
        # Try to access Sanctus materials through asset browser
        # Materials are typically stored in the addon's asset library
        for mat in bpy.data.materials:
            # Check if material is from Sanctus Library
            # This may vary based on how Sanctus Library names/organizes materials
            if hasattr(mat, 'asset_data') and mat.asset_data:
                materials.append(mat.name)
    except Exception:
        pass
    
    return materials


def apply_sanctus_material_to_object(obj_name: str, material_name: str) -> Dict[str, Any]:
    """
    Apply a Sanctus Library material to an object
    
    Args:
        obj_name: Name of the object to apply material to
        material_name: Name of the Sanctus Library material
    
    Returns:
        Dict with status and message
    """
    result = {"status": "error", "message": ""}
    
    if not check_sanctus_installed():
        result["message"] = "Sanctus Library addon is not installed or enabled"
        return result
    
    try:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            result["message"] = f"Object '{obj_name}' not found"
            return result
        
        # Get material from Sanctus Library
        mat = bpy.data.materials.get(material_name)
        if not mat:
            # Try to load from asset library
            mat = load_sanctus_material_from_assets(material_name)
            if not mat:
                result["message"] = f"Material '{material_name}' not found in Sanctus Library"
                return result
        
        # Ensure object has material slots
        if len(obj.data.materials) == 0:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat
        
        obj.active_material = mat
        result["status"] = "success"
        result["message"] = f"Applied Sanctus Library material '{material_name}' to '{obj_name}'"
        return result
        
    except Exception as e:
        result["message"] = f"Error applying material: {str(e)}"
        return result


def load_sanctus_material_from_assets(material_name: str) -> Optional[bpy.types.Material]:
    """Load a Sanctus Library material from the asset library"""
    try:
        # Access asset library through Blender's asset browser API
        # This may require the material to be marked as an asset
        for mat in bpy.data.materials:
            if mat.name == material_name:
                if hasattr(mat, 'asset_data') and mat.asset_data:
                    return mat
        
        # Alternative: Try to append from Sanctus Library blend file
        # This would require knowing the path to Sanctus Library assets
        return None
    except Exception:
        return None


def create_code_apply_sanctus_material(obj_name: str, material_name: str) -> str:
    """
    Generate Python code to apply Sanctus Library material
    
    Args:
        obj_name: Name of the object
        material_name: Name of the Sanctus Library material
    
    Returns:
        Python code as string
    """
    code = f"""
# Apply Sanctus Library material
import bpy

# Check if Sanctus Library is available
addons = bpy.context.preferences.addons
sanctus_installed = any('sanctus' in addon.lower() for addon in addons.keys())

if not sanctus_installed:
    print("Warning: Sanctus Library addon not found. Install from: https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/")
else:
    # Get object
    obj = bpy.data.objects.get('{obj_name}')
    if obj:
        # Get Sanctus Library material
        mat = bpy.data.materials.get('{material_name}')
        if mat:
            # Apply material to object
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
            obj.active_material = mat
            print(f"Applied Sanctus Library material '{{mat.name}}' to '{{obj.name}}'")
        else:
            # Try to load from asset library
            # Note: You may need to manually link/append the material from Sanctus Library asset browser
            print(f"Material '{{'{material_name}'}}' not found. Please ensure it's loaded in the asset browser.")
    else:
        print(f"Object '{{'{obj_name}'}}' not found")
"""
    return code.strip()


def create_code_list_sanctus_materials() -> str:
    """Generate Python code to list available Sanctus Library materials"""
    code = """
# List Sanctus Library materials
import bpy

addons = bpy.context.preferences.addons
sanctus_installed = any('sanctus' in addon.lower() for addon in addons.keys())

if not sanctus_installed:
    print("Sanctus Library addon not installed")
    print("Install from: https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/")
else:
    print("Sanctus Library materials:")
    sanctus_materials = []
    for mat in bpy.data.materials:
        # Check if material is from Sanctus Library
        # Materials may have specific naming or metadata
        if hasattr(mat, 'asset_data') and mat.asset_data:
            sanctus_materials.append(mat.name)
            print(f"  - {mat.name}")
    
    if not sanctus_materials:
        print("  No Sanctus Library materials found in current scene")
        print("  Open Asset Browser (Shift+A) and browse Sanctus Library assets")
"""
    return code.strip()


def create_code_setup_sanctus_material_workflow() -> str:
    """Generate code for setting up Sanctus Library material workflow"""
    code = """
# Sanctus Library Material Setup Workflow
import bpy

# 1. Check if Sanctus Library is installed
addons = bpy.context.preferences.addons
sanctus_installed = any('sanctus' in addon.lower() for addon in addons.keys())

if not sanctus_installed:
    print("=" * 60)
    print("Sanctus Library Addon Not Found")
    print("=" * 60)
    print("To use Sanctus Library procedural shaders:")
    print("1. Purchase and download from:")
    print("   https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/")
    print("2. Install the addon in Blender:")
    print("   - Edit > Preferences > Add-ons")
    print("   - Click 'Install...' and select the Sanctus Library .zip file")
    print("   - Enable the addon")
    print("3. Access materials through Asset Browser (Shift+A)")
    print("=" * 60)
else:
    print("Sanctus Library addon is installed!")
    print("\\nTo use Sanctus Library materials:")
    print("1. Open Asset Browser (Shift+A)")
    print("2. Browse Sanctus Library materials")
    print("3. Drag and drop materials onto objects, or")
    print("4. Use Python API to apply materials programmatically")
    
    # Example: Apply material to selected object
    if bpy.context.selected_objects:
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH':
            print(f"\\nSelected object: {obj.name}")
            print("To apply a Sanctus material, use:")
            print(f"  mat = bpy.data.materials.get('MaterialName')")
            print(f"  obj.data.materials.append(mat)")
"""
    return code.strip()


def get_sanctus_material_categories() -> List[str]:
    """Get list of material categories available in Sanctus Library"""
    # Based on typical Sanctus Library organization
    # This may need to be updated based on actual addon structure
    categories = [
        "Metals",
        "Fabrics",
        "Wood",
        "Stone",
        "Glass",
        "Plastic",
        "Leather",
        "Concrete",
        "Ceramic",
        "Organic",
        "Abstract",
        "Sci-Fi",
        "Nature"
    ]
    return categories


def create_code_apply_sanctus_by_category(obj_name: str, category: str) -> str:
    """
    Generate code to apply a Sanctus Library material by category
    
    Args:
        obj_name: Name of the object
        category: Material category (e.g., "Metals", "Wood", "Fabric")
    """
    code = f"""
# Apply Sanctus Library material by category
import bpy

obj = bpy.data.objects.get('{obj_name}')
if not obj:
    print(f"Object '{{'{obj_name}'}}' not found")
else:
    # Search for materials in the specified category
    category = '{category}'
    matching_materials = []
    
    for mat in bpy.data.materials:
        # Check if material name contains category keyword
        if category.lower() in mat.name.lower():
            matching_materials.append(mat.name)
    
    if matching_materials:
        # Use first matching material
        mat_name = matching_materials[0]
        mat = bpy.data.materials.get(mat_name)
        if mat:
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[0] = mat
            obj.active_material = mat
            print(f"Applied {{mat_name}} to {{obj.name}}")
    else:
        print(f"No materials found in category '{{category}}'")
        print("Please ensure Sanctus Library materials are loaded in Asset Browser")
"""
    return code.strip()

