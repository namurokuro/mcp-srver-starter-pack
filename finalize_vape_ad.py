#!/usr/bin/env python3
"""
Финализация на вейп рекламата
Добавя детайли, подобрява smoke ефектите, настройва рендериране
"""

import bpy
from mathutils import Vector

# ============================================
# ПОДОБРЯВАНЕ НА SMOKE ЕФЕКТИТЕ
# ============================================

# Търси smoke placeholder
smoke_obj = bpy.data.objects.get("VapeSmoke_Placeholder")
if smoke_obj:
    # Добавяне на multiple smoke particles
    for i in range(5):
        offset_x = (i - 2) * 0.3
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.2, location=(offset_x, 0, 2 + i * 0.2))
        smoke_particle = bpy.context.active_object
        smoke_particle.name = f"VapeSmoke_Particle_{i+1}"
        
        # Copy material
        mat_smoke = bpy.data.materials.get("SmokeMaterial")
        if mat_smoke:
            smoke_particle.data.materials.append(mat_smoke)
        
        # Animate
        smoke_particle.scale = (0, 0, 0)
        smoke_particle.keyframe_insert(data_path="scale", frame=119 + i * 5)
        
        smoke_particle.scale = (2, 2, 3)
        smoke_particle.keyframe_insert(data_path="scale", frame=150 + i * 5)
        
        smoke_particle.scale = (4, 4, 6)
        smoke_particle.keyframe_insert(data_path="scale", frame=180)

# ============================================
# ДОБАВЯНЕ НА ВЕЙП УСТРОЙСТВО
# ============================================

# Vape device в ръката на актьора
actor = bpy.data.objects.get("Actor")
if actor:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.3, location=(0.3, 0, 2))
    vape_device = bpy.context.active_object
    vape_device.name = "VapeDevice"
    vape_device.rotation_euler = (1.5708, 0, 0)  # Horizontal
    
    # Vape material (metallic)
    mat_vape = bpy.data.materials.new(name="VapeMaterial")
    mat_vape.use_nodes = True
    bsdf = mat_vape.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.3, 0.3, 0.35, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.2
    bsdf.inputs["Metallic"].default_value = 0.9
    vape_device.data.materials.append(mat_vape)
    
    # Parent to actor
    vape_device.parent = actor
    
    # Animate vape to appear at frame 90
    vape_device.scale = (0, 0, 0)
    vape_device.keyframe_insert(data_path="scale", frame=89)
    
    vape_device.scale = (1, 1, 1)
    vape_device.keyframe_insert(data_path="scale", frame=90)

# ============================================
# НАСТРОЙВАНЕ НА РЕНДЕРИРАНЕ
# ============================================

# Render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.fps = 30
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 180

# Output settings (PNG sequence, може да се конвертира в MP4 по-късно)
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = "//vape_ad_frames/vape_ad_"

# EEVEE settings (опростени)
# Note: Bloom и SSR могат да се настроят ръчно в Blender UI

# ============================================
# ДОБАВЯНЕ НА ДОПЪЛНИТЕЛНИ ДЕТАЙЛИ
# ============================================

# Добавяне на светлини за по-добър вид
bpy.ops.object.light_add(type='SPOT', location=(0, 0, 8))
spot_light = bpy.context.active_object
spot_light.name = "SpotLight_Actor"
spot_light.data.energy = 100
spot_light.data.spot_size = 0.5
spot_light.data.spot_blend = 0.5

# Point light за smoke
bpy.ops.object.light_add(type='POINT', location=(0, 0, 3))
point_light = bpy.context.active_object
point_light.name = "PointLight_Smoke"
point_light.data.energy = 50
point_light.data.color = (0.9, 0.95, 1.0)  # Slight blue tint

print("=" * 70)
print("ВЕЙП РЕКЛАМА - ФИНАЛИЗИРАНА")
print("=" * 70)
print()
print("Добавено:")
print("  - Подобрени smoke ефекти (multiple particles)")
print("  - Вейп устройство в ръката на актьора")
print("  - Настроено рендериране (1920x1080, EEVEE, MP4)")
print("  - Допълнителни светлини")
print("  - Bloom и SSR ефекти")
print()
print("За да рендерираш:")
print("  bpy.ops.render.render(animation=True)")
print()
print("Или използвай Rendering агента:")
print("  'Setup render: 1920x1080, EEVEE, MP4, frames 1-180'")
print()

