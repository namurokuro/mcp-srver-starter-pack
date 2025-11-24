#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

from specialized_agents import RenderingSpecialist

agent = RenderingSpecialist()
if agent.connect_to_blender():
    code = """
import bpy
import os

# Създаване на директория (абсолютен път)
current_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
output_dir = os.path.join(current_dir, "vape_ad_frames")
os.makedirs(output_dir, exist_ok=True)

# Настройки
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 180
bpy.context.scene.render.fps = 30

# Output - абсолютен път
bpy.context.scene.render.filepath = os.path.join(output_dir, "vape_ad_")
bpy.context.scene.render.image_settings.file_format = 'PNG'

print("=" * 50)
print("RENDER CONFIGURATION")
print("=" * 50)
print(f"Output directory: {output_dir}")
print(f"Directory exists: {os.path.exists(output_dir)}")
print(f"Output path: {bpy.context.scene.render.filepath}")
print(f"Frames: {bpy.context.scene.frame_start}-{bpy.context.scene.frame_end}")
print()
print("Starting render...")
print()

# Стартиране
bpy.ops.render.render(animation=True)

print("Render command completed")
"""
    
    result = agent.execute_code(code)
    output = result.get("result", {}).get("output", "")
    if output:
        print(output)
    else:
        print("Render started. Check Blender for progress.")

