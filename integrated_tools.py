#!/usr/bin/env python3
"""
Integrated Tools from PolyMCP - High Priority Tools
Converted to work with our MCP server and agent system
"""

import json
from typing import Dict, Any, Optional, List
from thread_safe_executor import get_executor


def create_mesh_object_code(
    primitive_type: str = "cube",
    size: float = 2.0,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[List[float]] = None,
    name: Optional[str] = None,
    subdivisions: int = 0,
    collection: Optional[str] = None
) -> str:
    """Generate Blender Python code to create a mesh object"""
    location = location or [0, 0, 0]
    rotation = rotation or [0, 0, 0]
    scale = scale or [1, 1, 1]
    
    valid_primitives = ["cube", "sphere", "cylinder", "cone", "torus", 
                       "plane", "ico_sphere", "monkey", "grid"]
    if primitive_type not in valid_primitives:
        raise ValueError(f"Invalid primitive type. Must be one of: {valid_primitives}")
    
    code_parts = []
    
    # Create primitive
    if primitive_type == "cube":
        code_parts.append(f"bpy.ops.mesh.primitive_cube_add(size={size}, location={location})")
    elif primitive_type == "sphere":
        code_parts.append(f"bpy.ops.mesh.primitive_uv_sphere_add(radius={size/2}, location={location})")
    elif primitive_type == "cylinder":
        code_parts.append(f"bpy.ops.mesh.primitive_cylinder_add(radius={size/2}, depth={size}, location={location})")
    elif primitive_type == "cone":
        code_parts.append(f"bpy.ops.mesh.primitive_cone_add(radius1={size/2}, radius2=0, depth={size}, location={location})")
    elif primitive_type == "torus":
        code_parts.append(f"bpy.ops.mesh.primitive_torus_add(major_radius={size/2}, minor_radius={size/4}, location={location})")
    elif primitive_type == "plane":
        code_parts.append(f"bpy.ops.mesh.primitive_plane_add(size={size}, location={location})")
    elif primitive_type == "ico_sphere":
        code_parts.append(f"bpy.ops.mesh.primitive_ico_sphere_add(radius={size/2}, location={location})")
    elif primitive_type == "monkey":
        code_parts.append(f"bpy.ops.mesh.primitive_monkey_add(size={size}, location={location})")
    elif primitive_type == "grid":
        code_parts.append(f"bpy.ops.mesh.primitive_grid_add(size={size}, location={location})")
    
    code_parts.append("obj = bpy.context.active_object")
    
    # Apply name
    if name:
        code_parts.append(f'obj.name = "{name}"')
        code_parts.append(f'obj.data.name = "{name}_mesh"')
    
    # Apply transformations
    code_parts.append(f"obj.rotation_euler = [{r * 3.14159 / 180 for r in rotation}]")
    code_parts.append(f"obj.scale = {scale}")
    
    # Apply subdivision
    if subdivisions > 0:
        code_parts.append(f"modifier = obj.modifiers.new(name='Subdivision', type='SUBSURF')")
        code_parts.append(f"modifier.levels = {subdivisions}")
        code_parts.append(f"modifier.render_levels = {subdivisions}")
    
    # Move to collection
    if collection:
        code_parts.append(f'target_collection = bpy.data.collections.get("{collection}")')
        code_parts.append("if not target_collection:")
        code_parts.append(f'    target_collection = bpy.data.collections.new("{collection}")')
        code_parts.append("    bpy.context.scene.collection.children.link(target_collection)")
        code_parts.append("for coll in obj.users_collection:")
        code_parts.append("    coll.objects.unlink(obj)")
        code_parts.append("target_collection.objects.link(obj)")
    
    return "\n".join(code_parts)


def transform_object_code(
    object_name: str,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[List[float]] = None
) -> str:
    """Generate Blender Python code to transform an object"""
    code_parts = [f'obj = bpy.data.objects.get("{object_name}")']
    code_parts.append("if not obj:")
    code_parts.append(f'    raise ValueError("Object \'{object_name}\' not found")')
    
    if location:
        code_parts.append(f"obj.location = {location}")
    
    if rotation:
        code_parts.append(f"obj.rotation_euler = [{r * 3.14159 / 180 for r in rotation}]")
    
    if scale:
        code_parts.append(f"obj.scale = {scale}")
    
    return "\n".join(code_parts)


def duplicate_object_code(
    object_name: str,
    linked: bool = False,
    offset: Optional[List[float]] = None
) -> str:
    """Generate Blender Python code to duplicate an object"""
    offset = offset or [0, 0, 0]
    
    code_parts = [f'obj = bpy.data.objects.get("{object_name}")']
    code_parts.append("if not obj:")
    code_parts.append(f'    raise ValueError("Object \'{object_name}\' not found")')
    code_parts.append("bpy.context.view_layer.objects.active = obj")
    code_parts.append("obj.select_set(True)")
    
    if linked:
        code_parts.append("bpy.ops.object.duplicate_linked()")
    else:
        code_parts.append("bpy.ops.object.duplicate()")
    
    code_parts.append("duplicate = bpy.context.active_object")
    code_parts.append(f"duplicate.location = [obj.location[i] + {offset}[i] for i in range(3)]")
    
    return "\n".join(code_parts)


def add_modifier_code(
    object_name: str,
    modifier_type: str,
    settings: Optional[Dict[str, Any]] = None,
    name: Optional[str] = None
) -> str:
    """Generate Blender Python code to add a modifier"""
    settings = settings or {}
    name = name or modifier_type
    
    valid_modifiers = [
        'ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT',
        'MASK', 'MIRROR', 'MULTIRES', 'REMESH', 'SCREW', 'SKIN',
        'SOLIDIFY', 'SUBSURF', 'TRIANGULATE', 'WELD', 'WIREFRAME',
        'ARMATURE', 'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LAPLACIANDEFORM',
        'LAPLACIANSMOOTH', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP',
        'SIMPLE_DEFORM', 'SMOOTH', 'CORRECTIVE_SMOOTH', 'SURFACE_DEFORM',
        'WARP', 'WAVE', 'CLOTH', 'COLLISION', 'DYNAMIC_PAINT', 'EXPLODE',
        'FLUID', 'OCEAN', 'PARTICLE_INSTANCE', 'PARTICLE_SYSTEM',
        'SOFT_BODY', 'SURFACE', 'MESH_CACHE', 'MESH_SEQUENCE_CACHE',
        'NODES', 'NORMAL_EDIT', 'UV_PROJECT', 'UV_WARP', 'VERTEX_WEIGHT_EDIT',
        'VERTEX_WEIGHT_MIX', 'VERTEX_WEIGHT_PROXIMITY'
    ]
    
    code_parts = [f'obj = bpy.data.objects.get("{object_name}")']
    code_parts.append("if not obj:")
    code_parts.append(f'    raise ValueError("Object \'{object_name}\' not found")')
    code_parts.append(f'modifier = obj.modifiers.new(name="{name}", type="{modifier_type}")')
    
    # Add common settings
    if 'levels' in settings:
        code_parts.append(f"modifier.levels = {settings['levels']}")
    if 'count' in settings:
        code_parts.append(f"modifier.count = {settings['count']}")
    if 'width' in settings:
        code_parts.append(f"modifier.width = {settings['width']}")
    if 'thickness' in settings:
        code_parts.append(f"modifier.thickness = {settings['thickness']}")
    
    return "\n".join(code_parts)


def create_shader_node_tree_code(
    material_name: str,
    nodes: Optional[List[Dict[str, Any]]] = None
) -> str:
    """Generate Blender Python code to create a shader node tree"""
    code_parts = [f'mat = bpy.data.materials.new(name="{material_name}")']
    code_parts.append("mat.use_nodes = True")
    code_parts.append("nodes = mat.node_tree.nodes")
    code_parts.append("links = mat.node_tree.links")
    
    # Clear default nodes
    code_parts.append("nodes.clear()")
    
    # Add output node
    code_parts.append('output = nodes.new(type="ShaderNodeOutputMaterial")')
    code_parts.append("output.location = (300, 0)")
    
    # Add nodes from definition
    if nodes:
        for i, node_def in enumerate(nodes):
            node_type = node_def.get('type', 'BSDF_PRINCIPLED')
            node_name = node_def.get('name', f'node_{i}')
            location = node_def.get('location', [0, -i * 200])
            
            code_parts.append(f'node_{i} = nodes.new(type="ShaderNode{node_type}")')
            code_parts.append(f'node_{i}.name = "{node_name}"')
            code_parts.append(f'node_{i}.location = ({location[0]}, {location[1]})')
            
            # Add properties
            for prop, value in node_def.get('properties', {}).items():
                if hasattr(node_def, prop):
                    code_parts.append(f'node_{i}.{prop} = {value}')
    
    return "\n".join(code_parts)

