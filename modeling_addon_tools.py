"""
Modeling Addon Integration Tools (ND Addon)
Integrates advanced modeling addon features for Blender
"""

import bpy
from typing import Dict, List, Optional, Any


def check_modeling_addon_installed() -> bool:
    """Check if modeling addon (ND addon) is installed and enabled"""
    addons = bpy.context.preferences.addons
    # Check for exact addon name "ND" or variations
    if 'ND' in addons or 'nd' in addons:
        return True
    # Also check for common modeling addon names
    modeling_keywords = ['nd', 'modeling', 'mesh', 'edit', 'bevel', 'subdivision']
    for addon_name in addons.keys():
        addon_lower = addon_name.lower()
        if any(keyword in addon_lower for keyword in modeling_keywords):
            return True
    return False


def get_modeling_addon_name() -> Optional[str]:
    """Get the name of the installed modeling addon"""
    addons = bpy.context.preferences.addons
    # Check for exact "ND" addon first
    if 'ND' in addons:
        return 'ND'
    if 'nd' in addons:
        return 'nd'
    # Check for variations
    modeling_keywords = ['nd', 'modeling', 'mesh', 'edit']
    for addon_name in addons.keys():
        addon_lower = addon_name.lower()
        if any(keyword in addon_lower for keyword in modeling_keywords):
            return addon_name
    return None


def apply_bevel_modifier(obj_name: str, width: float = 0.1, segments: int = 3, 
                        affect: str = 'EDGES') -> Dict[str, Any]:
    """
    Apply bevel modifier to object (using addon if available)
    
    Args:
        obj_name: Name of the object
        width: Bevel width
        segments: Number of segments
        affect: What to bevel ('EDGES', 'VERTICES', 'FACES')
    
    Returns:
        Dict with status
    """
    result = {"status": "error", "message": ""}
    
    try:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            result["message"] = f"Object '{obj_name}' not found"
            return result
        
        if obj.type != 'MESH':
            result["message"] = f"Object '{obj_name}' is not a mesh"
            return result
        
        # Check if addon provides enhanced bevel
        if check_modeling_addon_installed():
            addon_name = get_modeling_addon_name()
            if addon_name:
                # Try addon-specific bevel operators
                try:
                    # Common addon patterns for bevel
                    if hasattr(bpy.ops, f'{addon_name.replace(".", "_")}.bevel'):
                        op = getattr(bpy.ops, f'{addon_name.replace(".", "_")}.bevel')
                        op(width=width, segments=segments)
                        result["status"] = "success"
                        result["message"] = f"Applied addon bevel to '{obj_name}'"
                        return result
                except:
                    pass
        
        # Fallback to standard bevel modifier
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        
        # Add bevel modifier
        bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
        bevel.width = width
        bevel.segments = segments
        bevel.affect = affect
        
        result["status"] = "success"
        result["message"] = f"Applied bevel modifier to '{obj_name}'"
        return result
        
    except Exception as e:
        result["message"] = f"Error applying bevel: {str(e)}"
        return result


def apply_subdivision_modifier(obj_name: str, levels: int = 2, 
                              render_levels: int = 3) -> Dict[str, Any]:
    """
    Apply subdivision surface modifier (using addon if available)
    
    Args:
        obj_name: Name of the object
        levels: Viewport subdivision levels
        render_levels: Render subdivision levels
    
    Returns:
        Dict with status
    """
    result = {"status": "error", "message": ""}
    
    try:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            result["message"] = f"Object '{obj_name}' not found"
            return result
        
        if obj.type != 'MESH':
            result["message"] = f"Object '{obj_name}' is not a mesh"
            return result
        
        # Check if addon provides enhanced subdivision
        if check_modeling_addon_installed():
            addon_name = get_modeling_addon_name()
            if addon_name:
                try:
                    # Try addon-specific subdivision
                    if hasattr(bpy.ops, f'{addon_name.replace(".", "_")}.subdivide'):
                        op = getattr(bpy.ops, f'{addon_name.replace(".", "_")}.subdivide')
                        op(levels=levels)
                        result["status"] = "success"
                        result["message"] = f"Applied addon subdivision to '{obj_name}'"
                        return result
                except:
                    pass
        
        # Fallback to standard subdivision modifier
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        
        # Add subdivision modifier
        subsurf = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        subsurf.levels = levels
        subsurf.render_levels = render_levels
        
        result["status"] = "success"
        result["message"] = f"Applied subdivision modifier to '{obj_name}'"
        return result
        
    except Exception as e:
        result["message"] = f"Error applying subdivision: {str(e)}"
        return result


def enhance_object_with_modeling_addon(obj_name: str, operations: List[str] = None) -> Dict[str, Any]:
    """
    Apply multiple modeling addon operations to an object
    
    Args:
        obj_name: Name of the object
        operations: List of operations to apply (e.g., ['bevel', 'subdivision'])
    
    Returns:
        Dict with status and applied operations
    """
    result = {"status": "error", "message": "", "operations": []}
    
    if operations is None:
        operations = ['bevel', 'subdivision']
    
    try:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            result["message"] = f"Object '{obj_name}' not found"
            return result
        
        applied_ops = []
        
        for op in operations:
            if op.lower() == 'bevel':
                bevel_result = apply_bevel_modifier(obj_name, width=0.1, segments=3)
                if bevel_result["status"] == "success":
                    applied_ops.append("bevel")
            elif op.lower() in ['subdivision', 'subsurf', 'subdiv']:
                subdiv_result = apply_subdivision_modifier(obj_name, levels=2)
                if subdiv_result["status"] == "success":
                    applied_ops.append("subdivision")
        
        result["status"] = "success"
        result["message"] = f"Applied {len(applied_ops)} operations to '{obj_name}'"
        result["operations"] = applied_ops
        return result
        
    except Exception as e:
        result["message"] = f"Error enhancing object: {str(e)}"
        return result


def create_code_use_modeling_addon() -> str:
    """Generate Python code to use modeling addon"""
    code = """
# Use Modeling Addon (ND Addon)
import bpy
from modeling_addon_tools import (
    check_modeling_addon_installed,
    apply_bevel_modifier,
    apply_subdivision_modifier,
    enhance_object_with_modeling_addon
)

if not check_modeling_addon_installed():
    print("Modeling addon not installed. Using standard Blender operations.")
else:
    print("Modeling addon available!")
    
    # Example: Enhance selected object
    if bpy.context.selected_objects:
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH':
            result = enhance_object_with_modeling_addon(
                obj.name,
                operations=['bevel', 'subdivision']
            )
            print(result["message"])
"""
    return code.strip()


