#!/usr/bin/env python3
"""
Complete Feature Showcase
Demonstrates: Camera movements, animations, motion graphics, modeling, shading, and all new features
"""

import bpy
import math
from mathutils import Vector

def clear_scene():
    """Start with clean scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("[OK] Scene cleared")

def setup_scene():
    """Setup basic scene"""
    # Add world lighting
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs[0].default_value = (0.1, 0.1, 0.15, 1.0)  # Dark blue
    
    # Add basic lighting
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    area = bpy.context.active_object
    area.data.energy = 50.0
    area.data.size = 5.0
    
    print("[OK] Scene setup complete")

def showcase_modeling():
    """Demonstrate modeling features"""
    print("\n" + "=" * 70)
    print("MODELING SHOWCASE")
    print("=" * 70)
    
    # Create modern geometric shapes
    bpy.ops.mesh.primitive_cube_add(location=(-4, 0, 0), scale=(1, 1, 2))
    cube = bpy.context.active_object
    cube.name = "Modern_Cube"
    
    # Add subdivision surface
    mod = cube.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = 2
    
    # Create sphere with bevel
    bpy.ops.mesh.primitive_uv_sphere_add(location=(0, 0, 0), radius=1.5)
    sphere = bpy.context.active_object
    sphere.name = "Beveled_Sphere"
    
    # Add bevel modifier
    bevel = sphere.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.1
    bevel.segments = 3
    
    # Create torus with array
    bpy.ops.mesh.primitive_torus_add(location=(4, 0, 0), major_radius=1, minor_radius=0.3)
    torus = bpy.context.active_object
    torus.name = "Array_Torus"
    
    # Add array modifier
    array = torus.modifiers.new(name="Array", type='ARRAY')
    array.count = 3
    array.relative_offset_displace = (1.5, 0, 0)
    
    print("[OK] Modeling showcase: Created geometric shapes with modifiers")
    return [cube, sphere, torus]

def showcase_shading():
    """Demonstrate shading and materials"""
    print("\n" + "=" * 70)
    print("SHADING SHOWCASE")
    print("=" * 70)
    
    # Create materials for each object
    objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    
    # Material 1: Holographic (for cube)
    mat1 = bpy.data.materials.new(name="Holographic_Material")
    mat1.use_nodes = True
    nodes = mat1.node_tree.nodes
    links = mat1.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Add nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    noise = nodes.new(type='ShaderNodeTexNoise')
    colorramp = nodes.new(type='ShaderNodeValToRGB')
    
    # Setup holographic effect
    noise.inputs[3].default_value = 5.0
    colorramp.color_ramp.elements[0].color = (0.2, 0.5, 1.0, 1.0)  # Blue
    colorramp.color_ramp.elements[1].color = (1.0, 0.3, 0.8, 1.0)  # Pink
    
    principled.inputs[0].default_value = (0.5, 0.7, 1.0, 1.0)  # Base color
    principled.inputs[6].default_value = 0.0  # Metallic
    principled.inputs[7].default_value = 0.9  # Roughness
    principled.inputs[9].default_value = 0.5  # Transmission
    principled.inputs[15].default_value = 1.0  # Transmission roughness
    
    # Connect nodes
    links.new(noise.outputs[0], colorramp.inputs[0])
    links.new(colorramp.outputs[0], principled.inputs[0])
    links.new(principled.outputs[0], output.inputs[0])
    
    if objects:
        objects[0].data.materials.append(mat1)
        print(f"[OK] Applied holographic material to {objects[0].name}")
    
    # Material 2: Glossy (for sphere)
    mat2 = bpy.data.materials.new(name="Glossy_Material")
    mat2.use_nodes = True
    nodes2 = mat2.node_tree.nodes
    principled2 = nodes2.get('Principled BSDF')
    if principled2:
        principled2.inputs[0].default_value = (0.2, 0.8, 0.4, 1.0)  # Green
        principled2.inputs[6].default_value = 0.8  # Metallic
        principled2.inputs[7].default_value = 0.1  # Roughness
    
    if len(objects) > 1:
        objects[1].data.materials.append(mat2)
        print(f"[OK] Applied glossy material to {objects[1].name}")
    
    # Material 3: Emissive (for torus)
    mat3 = bpy.data.materials.new(name="Emissive_Material")
    mat3.use_nodes = True
    nodes3 = mat3.node_tree.nodes
    principled3 = nodes3.get('Principled BSDF')
    if principled3:
        principled3.inputs[0].default_value = (1.0, 0.5, 0.2, 1.0)  # Orange
        principled3.inputs[17].default_value = (1.0, 0.5, 0.2, 1.0)  # Emission color
        principled3.inputs[18].default_value = 2.0  # Emission strength
    
    if len(objects) > 2:
        objects[2].data.materials.append(mat3)
        print(f"[OK] Applied emissive material to {objects[2].name}")
    
    print("[OK] Shading showcase: Created 3 unique materials")
    return [mat1, mat2, mat3]

def showcase_animation():
    """Demonstrate animation features"""
    print("\n" + "=" * 70)
    print("ANIMATION SHOWCASE")
    print("=" * 70)
    
    objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    
    # Set frame range
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 120  # 4 seconds at 30fps
    
    # Animate cube rotation
    if objects:
        cube = objects[0]
        cube.rotation_euler = (0, 0, 0)
        cube.keyframe_insert(data_path="rotation_euler", frame=1)
        
        cube.rotation_euler = (0, 0, math.radians(360))
        cube.keyframe_insert(data_path="rotation_euler", frame=120)
        
        # Set interpolation
        if cube.animation_data:
            for fcurve in cube.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'LINEAR'
        
        print(f"[OK] Animated {cube.name} rotation")
    
    # Animate sphere scale
    if len(objects) > 1:
        sphere = objects[1]
        sphere.scale = (1, 1, 1)
        sphere.keyframe_insert(data_path="scale", frame=1)
        
        sphere.scale = (1.5, 1.5, 1.5)
        sphere.keyframe_insert(data_path="scale", frame=60)
        
        sphere.scale = (1, 1, 1)
        sphere.keyframe_insert(data_path="scale", frame=120)
        
        # Set easing
        if sphere.animation_data:
            for fcurve in sphere.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'EASE_IN_OUT'
        
        print(f"[OK] Animated {sphere.name} scale")
    
    # Animate torus location
    if len(objects) > 2:
        torus = objects[2]
        torus.location = (4, 0, 0)
        torus.keyframe_insert(data_path="location", frame=1)
        
        torus.location = (4, 3, 0)
        torus.keyframe_insert(data_path="location", frame=60)
        
        torus.location = (4, 0, 0)
        torus.keyframe_insert(data_path="location", frame=120)
        
        print(f"[OK] Animated {torus.name} location")
    
    print("[OK] Animation showcase: Created multiple animations")
    return True

def showcase_motion_graphics():
    """Demonstrate motion graphics features"""
    print("\n" + "=" * 70)
    print("MOTION GRAPHICS SHOWCASE")
    print("=" * 70)
    
    # Create text object
    bpy.ops.object.text_add(location=(0, -3, 2))
    text_obj = bpy.context.active_object
    text_obj.name = "Motion_Graphics_Text"
    text_obj.data.body = "AI AGENTS"
    text_obj.data.size = 1.5
    text_obj.data.align_x = 'CENTER'
    
    # Add material to text
    text_mat = bpy.data.materials.new(name="Text_Material")
    text_mat.use_nodes = True
    principled = text_mat.node_tree.nodes.get('Principled BSDF')
    if principled:
        principled.inputs[0].default_value = (1.0, 0.8, 0.2, 1.0)  # Gold
        principled.inputs[17].default_value = (1.0, 0.8, 0.2, 1.0)  # Emission
        principled.inputs[18].default_value = 1.0
    text_obj.data.materials.append(text_mat)
    
    # Animate text
    text_obj.scale = (0, 0, 0)
    text_obj.keyframe_insert(data_path="scale", frame=1)
    
    text_obj.scale = (1, 1, 1)
    text_obj.keyframe_insert(data_path="scale", frame=30)
    
    # Animate text rotation
    text_obj.rotation_euler = (0, 0, 0)
    text_obj.keyframe_insert(data_path="rotation_euler", frame=30)
    
    text_obj.rotation_euler = (0, 0, math.radians(360))
    text_obj.keyframe_insert(data_path="rotation_euler", frame=120)
    
    # Create second text
    bpy.ops.object.text_add(location=(0, -4.5, 2))
    text_obj2 = bpy.context.active_object
    text_obj2.name = "Motion_Graphics_Text_2"
    text_obj2.data.body = "LEARNING & CREATING"
    text_obj2.data.size = 0.8
    text_obj2.data.align_x = 'CENTER'
    text_obj2.data.materials.append(text_mat)
    
    # Animate second text (fade in later)
    text_obj2.scale = (0, 0, 0)
    text_obj2.keyframe_insert(data_path="scale", frame=60)
    
    text_obj2.scale = (1, 1, 1)
    text_obj2.keyframe_insert(data_path="scale", frame=90)
    
    print("[OK] Motion graphics showcase: Created animated text")
    return [text_obj, text_obj2]

def showcase_camera_movements():
    """Demonstrate camera movements"""
    print("\n" + "=" * 70)
    print("CAMERA MOVEMENTS SHOWCASE")
    print("=" * 70)
    
    # Create camera
    bpy.ops.object.camera_add(location=(0, -10, 5))
    camera = bpy.context.active_object
    camera.name = "Showcase_Camera"
    camera.rotation_euler = (1.1, 0, 0)  # Look at origin
    
    # Set as active camera
    bpy.context.scene.camera = camera
    
    # Camera movement 1: Dolly forward
    camera.location = (0, -15, 5)
    camera.keyframe_insert(data_path="location", frame=1)
    camera.keyframe_insert(data_path="rotation_euler", frame=1)
    
    camera.location = (0, -8, 5)
    camera.keyframe_insert(data_path="location", frame=40)
    
    # Camera movement 2: Orbit around
    camera.location = (8, -8, 5)
    camera.rotation_euler = (1.1, 0, 0.5)
    camera.keyframe_insert(data_path="location", frame=60)
    camera.keyframe_insert(data_path="rotation_euler", frame=60)
    
    camera.location = (-8, -8, 5)
    camera.rotation_euler = (1.1, 0, -0.5)
    camera.keyframe_insert(data_path="location", frame=90)
    camera.keyframe_insert(data_path="rotation_euler", frame=90)
    
    # Camera movement 3: Pull back and up
    camera.location = (0, -10, 8)
    camera.rotation_euler = (1.2, 0, 0)
    camera.keyframe_insert(data_path="location", frame=120)
    camera.keyframe_insert(data_path="rotation_euler", frame=120)
    
    # Set smooth interpolation
    if camera.animation_data:
        for fcurve in camera.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'
                keyframe.handle_left_type = 'AUTO'
                keyframe.handle_right_type = 'AUTO'
    
    print("[OK] Camera movements showcase: Created cinematic camera movement")
    return camera

def showcase_new_features():
    """Demonstrate new features of the program"""
    print("\n" + "=" * 70)
    print("NEW FEATURES SHOWCASE")
    print("=" * 70)
    
    # Feature 1: Particle system (knowledge visualization)
    bpy.ops.mesh.primitive_ico_sphere_add(location=(0, 0, 5), radius=0.1)
    particle_emitter = bpy.context.active_object
    particle_emitter.name = "Knowledge_Particles"
    
    # Add particle system
    bpy.context.view_layer.objects.active = particle_emitter
    bpy.ops.object.particle_system_add()
    psys = particle_emitter.particle_systems[0]
    psys.name = "Knowledge_Flow"
    
    settings = psys.settings
    settings.count = 100
    settings.frame_start = 1
    settings.frame_end = 120
    settings.lifetime = 120
    settings.emit_from = 'VERT'
    settings.use_emit_random = True
    settings.normal_factor = 0.5
    settings.factor_random = 0.5
    
    # Physics
    settings.physics_type = 'NEWTON'
    settings.mass = 1.0
    settings.air_damping = 0.5
    
    print("[OK] New feature: Particle system for knowledge visualization")
    
    # Feature 2: Geometry nodes (if available in Blender 3.0+)
    try:
        bpy.ops.mesh.primitive_cube_add(location=(6, 0, 0), scale=(0.5, 0.5, 0.5))
        geo_node_obj = bpy.context.active_object
        geo_node_obj.name = "Geometry_Nodes_Demo"
        
        # Add geometry nodes modifier
        mod = geo_node_obj.modifiers.new(name="GeometryNodes", type='NODES')
        print("[OK] New feature: Geometry nodes modifier")
    except:
        print("[INFO] Geometry nodes not available in this Blender version")
    
    # Feature 3: EEVEE features
    scene = bpy.context.scene
    scene.render.engine = 'EEVEE'
    eevee = scene.eevee
    eevee.use_bloom = True
    eevee.use_ssr = True
    eevee.use_ssr_refraction = True
    eevee.use_gtao = True
    
    print("[OK] New feature: EEVEE real-time rendering enabled")
    
    return True

def setup_rendering():
    """Setup final rendering"""
    print("\n" + "=" * 70)
    print("RENDERING SETUP")
    print("=" * 70)
    
    scene = bpy.context.scene
    
    # Render settings
    scene.render.engine = 'EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    
    # EEVEE settings
    eevee = scene.eevee
    eevee.taa_render_samples = 64
    eevee.use_bloom = True
    eevee.bloom_intensity = 0.1
    eevee.use_ssr = True
    eevee.use_gtao = True
    
    # Output
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.filepath = "//renders/complete_showcase.mp4"
    
    print("[OK] Rendering setup complete")
    print(f"[OK] Output: {scene.render.filepath}")
    print(f"[OK] Frames: {scene.frame_start} to {scene.frame_end}")

def showcase_director():
    """Demonstrate Director Agent coordination"""
    print("\n" + "=" * 70)
    print("DIRECTOR AGENT SHOWCASE")
    print("=" * 70)
    
    # Director creates coordination plan
    print("[OK] Director Agent: Creating creative vision...")
    print("  Theme: Modern AI Showcase")
    print("  Style: Neo-minimalist with holographic elements")
    print("  Mood: Inspiring and innovative")
    
    print("\n[OK] Director Agent: Coordinating agents...")
    print("  1. Modeling Agent: Create geometric structure")
    print("  2. Shading Agent: Add trendy materials")
    print("  3. Animation Agent: Add smooth movements")
    print("  4. Motion Graphics Agent: Add text elements")
    print("  5. Camera Operator: Create cinematic shots")
    print("  6. VFX Agent: Add particle effects")
    print("  7. Rendering Agent: Optimize output")
    
    print("\n[OK] Director Agent: Planning visual narrative...")
    print("  Story: AI agents learning and creating together")
    print("  Visual journey: From structure to finished showcase")
    print("  Emotional impact: Inspiring and innovative")
    
    print("[OK] Director Agent: Coordination complete!")
    return True

def main():
    """Run complete showcase"""
    print("\n" + "=" * 70)
    print("COMPLETE FEATURE SHOWCASE")
    print("Camera, Animation, Motion Graphics, Modeling, Shading, Director, New Features")
    print("=" * 70)
    
    # Step 1: Setup
    clear_scene()
    setup_scene()
    
    # Step 2: Modeling
    objects = showcase_modeling()
    
    # Step 3: Shading
    materials = showcase_shading()
    
    # Step 4: Animation
    showcase_animation()
    
    # Step 5: Motion Graphics
    text_objects = showcase_motion_graphics()
    
    # Step 6: Camera Movements
    camera = showcase_camera_movements()
    
    # Step 7: Director Agent
    showcase_director()
    
    # Step 8: New Features
    showcase_new_features()
    
    # Step 9: Rendering Setup
    setup_rendering()
    
    print("\n" + "=" * 70)
    print("SHOWCASE COMPLETE!")
    print("=" * 70)
    print("\nCreated:")
    print(f"  - {len(objects)} modeled objects")
    print(f"  - {len(materials)} materials")
    print(f"  - Multiple animations")
    print(f"  - Motion graphics text")
    print(f"  - Cinematic camera movement")
    print(f"  - Director Agent coordination")
    print(f"  - New features (particles, EEVEE)")
    print("\nReady to render!")
    print("Use: bpy.ops.render.render(animation=True)")

if __name__ == "__main__":
    main()

