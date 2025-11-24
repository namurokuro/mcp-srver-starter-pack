# specialized_agents.py - Specialized Blender Agents for Different Fields
"""
Multi-agent system with specialists for:
- Modeling
- Shading/Materials
- Animation
- VFX
- Motion Graphics
- Rendering
- Rigging
- Sculpting
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from data_collector import BlenderDataCollector, OperationRecord
from datetime import datetime
import json
import re
import socket
import requests  # pyright: ignore[reportMissingModuleSource]
import sys
import time

# Try to import activity tracker, but don't fail if not available
try:
    from agent_activity_tracker import tracker, ActivityStatus
    ACTIVITY_TRACKER_AVAILABLE = True
except ImportError:
    ACTIVITY_TRACKER_AVAILABLE = False
    tracker = None
    ActivityStatus = None


class BaseBlenderSpecialist(ABC):
    """Base class for specialized Blender agents"""
    
    def __init__(self, name: str, ollama_url="http://localhost:11434",
                 blender_host="localhost", blender_port=9876,
                 primary_model="gemma3:4b", fallback_models=None):
        self.name = name
        self.ollama_url = ollama_url
        self.blender_host = blender_host
        self.blender_port = blender_port
        self.primary_model = primary_model
        self.fallback_models = fallback_models or ["deepseek-r1:8b", "llama3.2:latest"]
        self.socket = None
        self.collector = BlenderDataCollector(f"{name.lower()}_data.db")
        self.operation_counter = 0
        self.current_activity_id = None
        
        # Register with activity tracker if available
        if ACTIVITY_TRACKER_AVAILABLE and tracker:
            tracker.register_agent(self.name)
    
    def log(self, message: str, level: str = "INFO"):
        """Log messages"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.name}] [{level}] {message}", file=sys.stderr)
        sys.stderr.flush()
        
        # Also log to activity tracker if available
        if ACTIVITY_TRACKER_AVAILABLE and tracker:
            tracker.log_message(self.name, message, level)
    
    def connect_to_blender(self) -> bool:
        """Connect to Blender"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.blender_host, self.blender_port))
            self.log("Connected to Blender")
            return True
        except Exception as e:
            self.log(f"Connection failed: {e}", "ERROR")
            return False
    
    def get_scene_info(self) -> Dict:
        """Get current scene state"""
        if not self.socket:
            if not self.connect_to_blender():
                return {"error": "Not connected"}
        
        try:
            command = {"type": "get_scene_info", "params": {}}
            self.socket.send(json.dumps(command).encode())
            response = self.socket.recv(65536)
            return json.loads(response.decode())
        except Exception as e:
            return {"error": str(e)}
    
    def execute_code(self, code: str) -> Dict:
        """Execute code in Blender"""
        if not self.socket:
            if not self.connect_to_blender():
                return {"status": "error", "message": "Not connected"}
        
        try:
            command = {
                "type": "execute_code",
                "params": {"code": code}
            }
            self.socket.send(json.dumps(command).encode())
            response = self.socket.recv(65536)
            return json.loads(response.decode())
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get specialized system prompt for this field"""
        pass
    
    @abstractmethod
    def get_field_specific_context(self) -> str:
        """Get field-specific context/knowledge"""
        pass
    
    def generate_code(self, prompt: str) -> Optional[str]:
        """Generate code using Ollama with field-specific context"""
        system_prompt = self.get_system_prompt()
        field_context = self.get_field_specific_context()
        
        full_prompt = f"{field_context}\n\n{prompt}"
        models_to_try = [self.primary_model] + self.fallback_models
        
        # Update activity if tracking
        if ACTIVITY_TRACKER_AVAILABLE and tracker and self.current_activity_id:
            tracker.update_activity(self.current_activity_id, 
                                   current_step=f"Trying model: {models_to_try[0]}", progress=0.5)
        
        for model in models_to_try:
            payload = {
                "model": model,
                "prompt": full_prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1500
                }
            }
            
            try:
                self.log(f"Generating code with {model}...")
                
                if ACTIVITY_TRACKER_AVAILABLE and tracker and self.current_activity_id:
                    tracker.update_activity(self.current_activity_id,
                                           current_step=f"Calling LLM: {model}", progress=0.6)
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=180
                )
                
                if response.status_code == 200:
                    result = response.json().get("response", "")
                    
                    # Extract code
                    if "```python" in result:
                        result = result.split("```python")[1].split("```")[0]
                    elif "```" in result:
                        result = result.split("```")[1].split("```")[0]
                    
                    code = result.strip()
                    if code:
                        self.log(f"Code generated successfully with {model}")
                        if ACTIVITY_TRACKER_AVAILABLE and tracker and self.current_activity_id:
                            tracker.update_activity(self.current_activity_id,
                                                   current_step="Code generation complete", progress=0.65)
                        return code
                
            except requests.exceptions.Timeout:
                self.log(f"{model} timed out, trying next...", "WARNING")
                if ACTIVITY_TRACKER_AVAILABLE and tracker and self.current_activity_id:
                    tracker.update_activity(self.current_activity_id,
                                           current_step=f"Model {model} timed out, trying next...")
                continue
            except Exception as e:
                self.log(f"{model} error: {e}, trying next...", "WARNING")
                if ACTIVITY_TRACKER_AVAILABLE and tracker and self.current_activity_id:
                    tracker.update_activity(self.current_activity_id,
                                           current_step=f"Model {model} error: {str(e)[:50]}...")
                continue
        
        return None
    
    def execute_task(self, description: str) -> Dict:
        """Execute a task in this specialist's domain"""
        self.log(f"Executing task: {description}")
        
        # Start tracking activity
        activity_id = None
        if ACTIVITY_TRACKER_AVAILABLE and tracker:
            activity_id = tracker.start_activity(
                self.name,
                description,
                metadata={"operation_counter": self.operation_counter}
            )
            self.current_activity_id = activity_id
            tracker.update_activity(activity_id, status=ActivityStatus.STARTING.value, current_step="Initializing task")
        
        description_lower = description.lower()
        
        # Check for clear scene / delete everything requests
        if any(keyword in description_lower for keyword in 
               ['clear scene', 'delete everything', 'remove everything', 'empty scene', 'clear all']):
            return self.handle_clear_scene(description)
        
        # Check for smoke/fire/explosion simulation requests
        if any(keyword in description_lower for keyword in 
               ['smoke', 'smoke simulation', 'realistic smoke', 'smoke domain', 'smoke flow',
                'fire', 'fire simulation', 'fire and smoke', 'fire smoke', 'flame',
                'explosion', 'explode', 'bob explosion', 'smoke explosion']):
            return self.handle_smoke_simulation(description)
        
        # Get scene state before
        if ACTIVITY_TRACKER_AVAILABLE and tracker and activity_id:
            tracker.update_activity(activity_id, status=ActivityStatus.THINKING.value, 
                                   current_step="Analyzing scene state", progress=0.1)
        
        scene_before = self.get_scene_info()
        if "error" in scene_before:
            scene_before = {"object_count": 0}
        
        # Generate code
        if ACTIVITY_TRACKER_AVAILABLE and tracker and activity_id:
            tracker.update_activity(activity_id, status=ActivityStatus.GENERATING.value,
                                   current_step="Generating code with LLM", progress=0.3)
        
        start_time = time.time()
        code = self.generate_code(description)
        
        if not code:
            error_msg = "Failed to generate code"
            if ACTIVITY_TRACKER_AVAILABLE and tracker and activity_id:
                tracker.complete_activity(activity_id, success=False, error_message=error_msg)
                self.current_activity_id = None
            return {"status": "error", "message": error_msg}
        
        # Execute
        if ACTIVITY_TRACKER_AVAILABLE and tracker and activity_id:
            tracker.update_activity(activity_id, status=ActivityStatus.EXECUTING.value,
                                   current_step="Executing code in Blender", progress=0.7)
        
        execution_start = time.time()
        result = self.execute_code(code)
        execution_time = time.time() - execution_start
        
        # Get scene state after
        scene_after = self.get_scene_info()
        if "error" in scene_after:
            scene_after = scene_before.copy()
        
        total_time = time.time() - start_time
        success = result.get("status") == "success"
        
        # Record operation
        self.operation_counter += 1
        operation_id = f"{self.name.lower()}_{self.operation_counter:06d}_{int(time.time())}"
        
        record = OperationRecord(
            id=operation_id,
            timestamp=datetime.now().isoformat(),
            description=description,
            model_used=self.primary_model,
            generated_code=code,
            execution_result=result,
            scene_before=scene_before.get("result", scene_before) if isinstance(scene_before, dict) and "result" in scene_before else scene_before,
            scene_after=scene_after.get("result", scene_after) if isinstance(scene_after, dict) and "result" in scene_after else scene_after,
            execution_time=total_time,
            success=success,
            error_message=result.get("message") if not success else None
        )
        
        self.collector.record_operation(record)
        
        # Complete activity tracking
        if ACTIVITY_TRACKER_AVAILABLE and tracker and activity_id:
            tracker.complete_activity(
                activity_id,
                success=success,
                result=result,
                error_message=result.get("message") if not success else None
            )
            self.current_activity_id = None
        
        return result
    
    def cleanup(self):
        """Clean up resources"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.collector.close()


class ModelingSpecialist(BaseBlenderSpecialist):
    """Specialist for 3D modeling operations"""
    
    def __init__(self, **kwargs):
        super().__init__("Modeling", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender 3D modeling expert specializing in:
- Mesh creation and editing
- Primitive objects (cubes, spheres, planes, etc.)
- Mesh operations (extrude, inset, bevel, etc.)
- Modifiers (subdivision, array, mirror, etc.)
- Topology optimization
- Boolean operations
- Mesh cleanup and retopology

Generate clean, efficient Python code using bpy.ops and bpy.data.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common modeling operations:
- bpy.ops.mesh.primitive_cube_add()
- bpy.ops.mesh.primitive_uv_sphere_add()
- bpy.ops.mesh.primitive_plane_add()
- bpy.ops.mesh.extrude_region()
- bpy.ops.mesh.inset_faces()
- bpy.ops.mesh.bevel()
- bpy.ops.object.modifier_add(type='SUBSURF')
- bpy.ops.object.modifier_add(type='ARRAY')
- bpy.ops.object.modifier_add(type='MIRROR')
- bpy.ops.object.modifier_add(type='BOOLEAN')
- bpy.ops.mesh.select_all(action='SELECT')
- bpy.ops.mesh.delete(type='VERT')
- bpy.ops.mesh.merge(type='CENTER')"""


class ShadingSpecialist(BaseBlenderSpecialist):
    """Specialist for materials and shading"""
    
    def __init__(self, **kwargs):
        super().__init__("Shading", **kwargs)
        # Import Sanctus Library tools
        try:
            from sanctus_library_tools import (
                check_sanctus_installed,
                apply_sanctus_material_to_object,
                create_code_apply_sanctus_material,
                create_code_list_sanctus_materials,
                create_code_setup_sanctus_material_workflow,
                get_sanctus_material_categories,
                create_code_apply_sanctus_by_category
            )
            self.sanctus_tools_available = True
        except ImportError:
            self.sanctus_tools_available = False
    
    def get_system_prompt(self) -> str:
        return """You are a Blender shading and materials expert specializing in:
- Material creation and setup
- Node-based shader editing
- Principled BSDF setup
- Texture mapping and UVs
- Procedural textures
- Material properties (roughness, metallic, etc.)
- Shader node trees
- Material slots and assignments
- Sanctus Library procedural shaders integration

Generate Python code for material and shader operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        context = """Common shading operations:
- bpy.data.materials.new(name='Material')
- mat.use_nodes = True
- nodes = mat.node_tree.nodes
- principled = nodes.new(type='ShaderNodeBsdfPrincipled')
- tex_coord = nodes.new(type='ShaderNodeTexCoord')
- mapping = nodes.new(type='ShaderNodeMapping')
- image_tex = nodes.new(type='ShaderNodeTexImage')
- normal_map = nodes.new(type='ShaderNodeNormalMap')
- obj.data.materials.append(mat)
- bpy.context.object.active_material = mat
- mat.node_tree.links.new(node1.outputs[0], node2.inputs[0])

Sanctus Library Integration:
- Sanctus Library provides 690+ procedural shaders
- Access through Asset Browser (Shift+A) or Python API
- Use sanctus_library_tools module for programmatic access
- Materials organized by categories: Metals, Fabrics, Wood, Stone, Glass, etc.
- Install from: https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/"""
        return context
    
    def handle_sanctus_material_request(self, description: str) -> Dict:
        """Handle requests for Sanctus Library materials"""
        if not self.sanctus_tools_available:
            return super().execute_task(description)
        
        try:
            from sanctus_library_tools import (
                create_code_apply_sanctus_material,
                create_code_list_sanctus_materials,
                create_code_setup_sanctus_material_workflow,
                create_code_apply_sanctus_by_category,
                get_sanctus_material_categories
            )
            
            description_lower = description.lower()
            
            # Check for Sanctus Library specific requests
            if "sanctus" in description_lower or "procedural shader" in description_lower:
                # Check if listing materials
                if "list" in description_lower or "show" in description_lower or "available" in description_lower:
                    code = create_code_list_sanctus_materials()
                    result = self.execute_code(code)
                    return result
                
                # Check if setup/install instructions
                if "setup" in description_lower or "install" in description_lower or "workflow" in description_lower:
                    code = create_code_setup_sanctus_material_workflow()
                    result = self.execute_code(code)
                    return result
                
                # Check for category-based material application
                categories = get_sanctus_material_categories()
                for category in categories:
                    if category.lower() in description_lower:
                        # Try to find object name in description
                        scene_info = self.get_scene_info()
                        if "objects" in scene_info:
                            # Use first mesh object or active object
                            obj_name = None
                            if "active_object" in scene_info and scene_info["active_object"]:
                                obj_name = scene_info["active_object"]
                            elif scene_info.get("objects"):
                                for obj in scene_info["objects"]:
                                    if obj.get("type") == "MESH":
                                        obj_name = obj.get("name")
                                        break
                            
                            if obj_name:
                                code = create_code_apply_sanctus_by_category(obj_name, category)
                                result = self.execute_code(code)
                                return result
                
                # Generic Sanctus material application
                # Try to extract material name and object name from description
                # This is a simplified approach - could be enhanced with NLP
                code = create_code_setup_sanctus_material_workflow()
                result = self.execute_code(code)
                return result
            
            # Not a Sanctus-specific request, use standard handling
            return super().execute_task(description)
            
        except Exception as e:
            self.log(f"Error in Sanctus material handling: {e}", "ERROR")
            return super().execute_task(description)
    
    def execute_task(self, description: str) -> Dict:
        """Execute shading task with Sanctus Library support"""
        description_lower = description.lower()
        
        # Check if this is a Sanctus Library request
        if "sanctus" in description_lower or "procedural shader" in description_lower:
            return self.handle_sanctus_material_request(description)
        
        # Standard shading task execution
        return super().execute_task(description)


class AnimationSpecialist(BaseBlenderSpecialist):
    """Specialist for animation and keyframes"""
    
    def __init__(self, **kwargs):
        super().__init__("Animation", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender animation expert specializing in:
- Keyframe animation
- Object animation (location, rotation, scale)
- Armature and bone animation
- Animation curves and F-curves
- Animation constraints
- Timeline and keyframe management
- Animation drivers
- Shape keys and morphing

Generate Python code for animation operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common animation operations:
- obj.keyframe_insert(data_path='location', frame=1)
- obj.keyframe_insert(data_path='rotation_euler', frame=1)
- obj.keyframe_insert(data_path='scale', frame=1)
- bpy.context.scene.frame_set(frame_number)
- bpy.context.scene.frame_start = 1
- bpy.context.scene.frame_end = 250
- bpy.ops.anim.keyframe_insert(type='Location')
- bpy.ops.anim.keyframe_insert(type='Rotation')
- bpy.ops.anim.keyframe_insert(type='Scaling')
- obj.animation_data_create()
- fcurve = obj.animation_data.action.fcurves.find('location', index=0)
- bpy.ops.object.constraint_add(type='FOLLOW_PATH')"""


class VFXSpecialist(BaseBlenderSpecialist):
    """Specialist for visual effects"""
    
    def __init__(self, **kwargs):
        super().__init__("VFX", **kwargs)
        # Import smoke simulation tools
        try:
            from smoke_simulation_tools import (
                create_smoke_domain_code,
                create_smoke_flow_code,
                create_smoke_collision_code,
                create_complete_smoke_setup_code,
                get_smoke_material_code,
                get_smoke_baking_code
            )
            self.smoke_tools_available = True
        except ImportError:
            self.smoke_tools_available = False
    
    def get_system_prompt(self) -> str:
        return """You are a Blender VFX expert specializing in:
- Particle systems
- Fluid simulation
- Smoke and fire effects
- Cloth simulation
- Soft body physics
- Rigid body dynamics
- Force fields
- Collision detection
- Compositing nodes
- Render layers and passes

Generate Python code for VFX operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common VFX operations:
- bpy.ops.object.particle_system_add()
- psys = obj.particle_systems[0]
- psys.settings.type = 'EMITTER'
- bpy.ops.object.fluid_add(type='DOMAIN')
- bpy.ops.object.fluid_add(type='FLOW')
- bpy.ops.object.modifier_add(type='CLOTH')
- bpy.ops.object.modifier_add(type='SOFT_BODY')
- bpy.ops.object.modifier_add(type='COLLISION')
- bpy.ops.object.forcefield_toggle()
- bpy.ops.object.effector_add(type='WIND')
- bpy.context.scene.use_nodes = True
- comp_nodes = bpy.context.scene.node_tree.nodes

Realistic Smoke Simulation (Blender 3.0+):
- Fluid modifier with domain_type='GAS' for smoke
- High resolution smoke: use_high_resolution=True
- Noise settings for realistic turbulence
- Temperature and velocity for natural movement
- Principled Volume shader for smoke materials
- Modular cache system for baking"""
    
    def handle_smoke_simulation(self, description: str) -> Dict:
        """Handle smoke simulation requests using smoke_simulation_tools"""
        if not self.smoke_tools_available:
            # Fallback to standard AI generation
            return super().execute_task(description)
        
        try:
            from smoke_simulation_tools import (
                create_complete_smoke_setup_code,
                create_smoke_domain_code,
                create_smoke_flow_code,
                create_smoke_collision_code,
                get_smoke_material_code,
                get_smoke_baking_code
            )
            
            description_lower = description.lower()
            
            # Check for explosion
            has_explosion = any(keyword in description_lower for keyword in 
                               ['explosion', 'explode', 'bob explosion', 'smoke explosion'])
            
            # Check for fire simulation
            has_fire = any(keyword in description_lower for keyword in 
                          ['fire', 'flame', 'burning', 'fire and smoke'])
            
            # Determine what to create based on description
            if has_explosion:
                # Explosion smoke with bob
                from explosion_smoke_tools import create_bob_explosion_scene_code
                explosion_intensity = "high"
                if "low" in description_lower:
                    explosion_intensity = "low"
                elif "medium" in description_lower:
                    explosion_intensity = "medium"
                code = create_bob_explosion_scene_code(
                    bob_start_height=5.0,
                    explosion_height=1.0,
                    explosion_intensity=explosion_intensity
                )
            elif has_fire and ("complete" in description_lower or "full" in description_lower or "setup" in description_lower):
                # Complete fire and smoke setup
                from fire_simulation_tools import create_complete_fire_smoke_scene_code
                fire_intensity = "medium"
                if "low" in description_lower:
                    fire_intensity = "low"
                elif "high" in description_lower or "intense" in description_lower:
                    fire_intensity = "high"
                code = create_complete_fire_smoke_scene_code(
                    domain_location=[0, 0, 2],
                    domain_size=[6, 6, 6],
                    flow_location=[0, 0, 0],
                    resolution=64,
                    fire_intensity=fire_intensity
                )
            elif "complete" in description_lower or "full" in description_lower or "setup" in description_lower:
                # Complete smoke setup
                code = create_complete_smoke_setup_code(
                    domain_location=[0, 0, 2],
                    domain_size=[6, 6, 6],
                    flow_location=[0, 0, 0],
                    resolution=64,
                    smoke_density=1.0,
                    smoke_temperature=1.0
                )
            elif has_fire and ("flow" in description_lower or "emitter" in description_lower):
                # Fire flow
                code = create_smoke_flow_code(
                    flow_type="BOTH",  # Fire and smoke
                    density=1.0,
                    temperature=2.0,
                    fuel_amount=0.5,
                    fire_brightness=2.0,
                    fire_heat=2.0
                )
            elif "domain" in description_lower and "flow" not in description_lower:
                # Just domain
                code = create_smoke_domain_code(
                    resolution=64,
                    use_high_resolution=True
                )
            elif "flow" in description_lower or "emitter" in description_lower:
                # Just flow
                code = create_smoke_flow_code(
                    flow_type="SMOKE",
                    density=1.0,
                    temperature=1.0
                )
            elif "collision" in description_lower:
                # Collision object
                code = create_smoke_collision_code()
            elif "material" in description_lower or "shader" in description_lower:
                # Material setup
                code = get_smoke_material_code()
            elif "bake" in description_lower or "baking" in description_lower:
                # Baking setup
                code = get_smoke_baking_code()
            else:
                # Default: complete setup
                code = create_complete_smoke_setup_code()
            
            # Execute the code
            result = self.execute_code(code)
            
            # Record operation
            scene_before = self.get_scene_info()
            scene_after = self.get_scene_info()
            
            record = OperationRecord(
                id=f"vfx_smoke_{int(time.time())}",
                timestamp=datetime.now().isoformat(),
                description=description,
                model_used="smoke_simulation_tools",
                generated_code=code,
                execution_result=result,
                scene_before=scene_before,
                scene_after=scene_after,
                execution_time=0.0,
                success=result.get("status") == "success"
            )
            self.collector.record_operation(record)
            
            return result
            
        except Exception as e:
            self.log(f"Error in smoke simulation: {e}", "ERROR")
            # Fallback to standard AI generation
            return super().execute_task(description)


class MotionGraphicsSpecialist(BaseBlenderSpecialist):
    """Specialist for motion graphics"""
    
    def __init__(self, **kwargs):
        super().__init__("MotionGraphics", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender motion graphics expert specializing in:
- Text objects and typography
- Logo animation
- Camera movement and tracking
- Motion blur
- Color grading
- Transitions
- 2D/3D integration
- Grease Pencil
- Video editing
- Sequencer operations

Generate Python code for motion graphics operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common motion graphics operations:
- bpy.ops.object.text_add()
- text_obj.data.body = 'Text'
- text_obj.data.extrude = 0.1
- bpy.ops.object.camera_add()
- bpy.context.scene.camera = camera_obj
- bpy.ops.sequencer.movie_strip_add()
- bpy.ops.sequencer.sound_strip_add()
- bpy.ops.gpencil.data_add()
- bpy.ops.gpencil.layer_add()
- bpy.ops.gpencil.draw(mode='DRAW')
- bpy.ops.transform.translate(value=(x, y, z))
- bpy.ops.anim.keyframe_insert_menu(type='Location')"""


class RenderingSpecialist(BaseBlenderSpecialist):
    """Specialist for rendering and output"""
    
    def __init__(self, **kwargs):
        super().__init__("Rendering", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender rendering expert specializing in:
- Render engine setup (Cycles, Eevee)
- Render settings and quality
- Lighting for rendering
- Camera setup
- Render output settings
- Image and video export
- Render layers and passes
- Compositing
- Denoising
- Render optimization

Generate Python code for rendering operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common rendering operations:
- bpy.context.scene.render.engine = 'CYCLES'
- bpy.context.scene.render.engine = 'EEVEE'
- bpy.context.scene.render.resolution_x = 1920
- bpy.context.scene.render.resolution_y = 1080
- bpy.context.scene.render.filepath = '/path/to/output.png'
- bpy.ops.render.render(write_still=True)
- bpy.ops.render.render(animation=True)
- bpy.context.scene.render.image_settings.file_format = 'PNG'
- bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
- bpy.context.scene.cycles.samples = 128
- bpy.context.scene.eevee.taa_render_samples = 64"""


class RiggingSpecialist(BaseBlenderSpecialist):
    """Specialist for rigging and armatures"""
    
    def __init__(self, **kwargs):
        super().__init__("Rigging", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender rigging expert specializing in:
- Armature creation
- Bone creation and hierarchy
- IK/FK setup
- Constraints
- Weight painting
- Automatic weights
- Bone properties
- Rig controls
- Deform bones vs control bones

Generate Python code for rigging operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common rigging operations:
- bpy.ops.object.armature_add()
- armature = bpy.data.armatures['Armature']
- bone = armature.edit_bones.new('Bone')
- bpy.ops.object.mode_set(mode='EDIT')
- bpy.ops.object.mode_set(mode='POSE')
- bone.constraints.new(type='IK')
- bpy.ops.object.parent_set(type='ARMATURE')
- bpy.ops.object.parent_set(type='ARMATURE_AUTO')
- bpy.ops.pose.ik_add()
- bpy.ops.paint.weight_paint_toggle()
- bpy.ops.object.vertex_group_add()"""


class SculptingSpecialist(BaseBlenderSpecialist):
    """Specialist for digital sculpting"""
    
    def __init__(self, **kwargs):
        super().__init__("Sculpting", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender sculpting expert specializing in:
- Sculpt mode operations
- Brush settings
- Dynamic topology
- Multiresolution
- Sculpting tools (grab, smooth, inflate, etc.)
- Masking
- Symmetry
- Remesh operations

Generate Python code for sculpting operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common sculpting operations:
- bpy.ops.object.mode_set(mode='SCULPT')
- bpy.context.sculpt_object.use_dynamic_topology_sculpting = True
- bpy.ops.sculpt.dynamic_topology_toggle()
- bpy.ops.sculpt.symmetrize()
- bpy.ops.sculpt.remesh()
- bpy.context.tool_settings.sculpt.brush = brush
- bpy.context.tool_settings.sculpt.brush.size = 50
- bpy.context.tool_settings.sculpt.brush.strength = 0.5"""


class CameraOperatorSpecialist(BaseBlenderSpecialist):
    """Specialist for camera operations, movement, and tracking"""
    
    def __init__(self, **kwargs):
        super().__init__("CameraOperator", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender camera operator expert specializing in:
- Camera creation and setup
- Camera movement and animation
- Camera tracking and following
- Camera constraints (track to, follow path, etc.)
- Camera properties (focal length, sensor size, depth of field)
- Camera switching and multiple cameras
- Camera framing and composition
- Camera shake and motion blur
- Camera rigs and setups
- Viewport camera control

Generate Python code for camera operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common camera operations:
- bpy.ops.object.camera_add(location=(x, y, z))
- bpy.context.scene.camera = camera_obj
- camera.data.lens = 50  # Focal length in mm
- camera.data.sensor_width = 36  # Sensor size
- camera.data.dof.use_dof = True  # Depth of field
- camera.data.dof.focus_distance = 10.0
- camera.data.dof.aperture_fstop = 2.8
- bpy.ops.object.constraint_add(type='TRACK_TO')
- bpy.ops.object.constraint_add(type='FOLLOW_PATH')
- constraint = camera.constraints.new(type='TRACK_TO')
- constraint.target = target_obj
- constraint.track_axis = 'TRACK_NEGATIVE_Z'
- constraint.up_axis = 'UP_Y'
- bpy.ops.object.camera_add(align='VIEW')
- bpy.context.scene.camera = bpy.data.objects['Camera']
- camera.keyframe_insert(data_path='location', frame=1)
- camera.keyframe_insert(data_path='rotation_euler', frame=1)
- bpy.ops.view3d.camera_to_view()
- bpy.ops.view3d.view_camera()
- bpy.ops.view3d.view_center_camera()
- camera.data.type = 'ORTHO'  # Orthographic camera
- camera.data.type = 'PERSP'  # Perspective camera
- camera.data.ortho_scale = 10.0  # Orthographic scale
- bpy.ops.object.camera_add(align='WORLD', location=(0, 0, 10))"""


class ScreenwriterSpecialist(BaseBlenderSpecialist):
    """Screenwriter - Creates scripts, stories, and scene descriptions for visual narratives"""
    
    def __init__(self, **kwargs):
        super().__init__("Screenwriter", **kwargs)
        self.scripts = []
        self.scene_descriptions = []
    
    def get_system_prompt(self) -> str:
        return """You are a Screenwriter for Blender 3D projects specializing in:
- Creating visual narratives and stories
- Writing scene descriptions and scripts
- Planning visual sequences and shots
- Describing characters, objects, and environments
- Creating emotional and engaging stories
- Structuring scenes and sequences
- Writing dialogue and narration (if needed)
- Visual storytelling through 3D scenes
- Scene breakdown and shot lists
- Creative writing for 3D visualization

You think like a screenwriter, considering:
- Story structure and narrative flow
- Character development and arcs
- Visual metaphors and symbolism
- Emotional beats and pacing
- Scene transitions and continuity
- Visual descriptions for 3D creation
- Creative concepts and themes

Generate Python code that creates scenes based on written descriptions.
Transform written narratives into 3D visualizations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Screenwriter operations:
- Create scene from story description
- Write visual narrative
- Plan scene sequences
- Describe visual elements
- Create story structure
- Write scene breakdowns
- Visual storytelling
- Narrative visualization

Example screenwriter tasks:
- Write a story about a futuristic city
- Create a scene from a script description
- Plan a visual sequence
- Describe a character's environment
- Create a narrative scene
- Write scene breakdown
- Visualize a story concept"""
    
    def create_script(self, story_description: str) -> Dict:
        """Create a script from story description"""
        self.log(f"Creating script: {story_description}")
        
        # Generate script structure
        script_prompt = f"""Create a Blender scene script based on this story:
{story_description}

The script should include:
1. Scene description
2. Visual elements needed
3. Camera angles
4. Lighting mood
5. Animation timing
6. Visual style

Generate Python code to create this scene."""
        
        code = self.generate_code(script_prompt)
        if not code:
            return {"status": "error", "message": "Failed to generate script code"}
        
        result = self.execute_code(code)
        
        # Store script
        self.scripts.append({
            "description": story_description,
            "code": code,
            "result": result
        })
        
        return result
    
    def execute_task(self, description: str) -> Dict:
        """Execute task as screenwriter"""
        self.log(f"Screenwriter executing: {description}")
        
        description_lower = description.lower()
        
        # Check for script creation
        if any(keyword in description_lower for keyword in 
               ['script', 'story', 'narrative', 'write', 'scene description', 'visual story']):
            return self.create_script(description)
        
        # Default: generate code for scene creation
        code = self.generate_code(description)
        if not code:
            return {"status": "error", "message": "Failed to generate code"}
        
        result = self.execute_code(code)
        
        # Record operation
        scene_before = self.get_scene_info()
        scene_after = self.get_scene_info()
        
        record = OperationRecord(
            id=f"screenwriter_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            description=description,
            model_used=self.primary_model,
            generated_code=code,
            execution_result=result,
            scene_before=scene_before,
            scene_after=scene_after,
            execution_time=0.0,
            success=result.get("status") == "success"
        )
        self.collector.record_operation(record)
        
        return result


class IdeasGeneratorSpecialist(BaseBlenderSpecialist):
    """Ideas Generator - Brainstorms and generates creative ideas for Blender projects"""
    
    def __init__(self, **kwargs):
        super().__init__("IdeasGenerator", **kwargs)
        self.ideas_history = []
        self.brainstorming_sessions = []
    
    def get_system_prompt(self) -> str:
        return """You are a Creative Ideas Generator and Brainstorming Specialist for Blender 3D projects specializing in:
- Generating creative ideas and concepts
- Brainstorming visual concepts
- Creating innovative scene ideas
- Combining different elements creatively
- Suggesting unique visual approaches
- Developing creative themes and styles
- Generating multiple variations of ideas
- Creating mood boards and concept descriptions
- Thinking outside the box
- Inspiring creative solutions

You think creatively, considering:
- Visual impact and uniqueness
- Creative combinations
- Innovative approaches
- Trend awareness
- Artistic styles
- Emotional resonance
- Technical feasibility
- Storytelling potential
- Audience appeal

Generate creative ideas, brainstorm concepts, and suggest innovative approaches.
Return creative, inspiring, and unique ideas."""
    
    def get_field_specific_context(self) -> str:
        return """Ideas Generator operations:
- Brainstorm creative concepts
- Generate scene ideas
- Suggest visual styles
- Create mood boards
- Generate multiple variations
- Combine different elements
- Suggest unique approaches
- Create concept descriptions
- Generate creative themes
- Inspire innovative solutions

Example brainstorming tasks:
- Brainstorm ideas for a futuristic showcase
- Generate 10 creative scene concepts
- Suggest visual styles for a space adventure
- Create mood board ideas
- Generate variations of a bedroom scene
- Brainstorm unique camera angles
- Suggest creative lighting setups
- Generate story concepts"""
    
    def brainstorm(self, topic: str, count: int = 10) -> Dict:
        """Generate multiple creative ideas for a topic"""
        self.log(f"Brainstorming ideas for: {topic}")
        
        brainstorm_prompt = f"""Brainstorm {count} creative and unique ideas for: {topic}

For each idea, provide:
1. Title/Name
2. Brief description
3. Visual style
4. Key elements
5. Why it's interesting/unique

Make the ideas:
- Creative and original
- Visually interesting
- Technically feasible in Blender
- Engaging and inspiring
- Diverse and varied

Return as a structured list of ideas."""
        
        # Use AI to generate ideas
        ideas_text = self.generate_code(brainstorm_prompt)
        
        if not ideas_text:
            return {"status": "error", "message": "Failed to generate ideas"}
        
        # Parse ideas (simple parsing - can be improved)
        ideas = self._parse_ideas(ideas_text, count)
        
        # Store brainstorming session
        session = {
            "topic": topic,
            "ideas": ideas,
            "timestamp": datetime.now().isoformat()
        }
        self.brainstorming_sessions.append(session)
        self.ideas_history.extend(ideas)
        
        return {
            "status": "success",
            "topic": topic,
            "ideas": ideas,
            "count": len(ideas),
            "message": f"Generated {len(ideas)} creative ideas"
        }
    
    def generate_variations(self, base_idea: str, count: int = 5) -> Dict:
        """Generate variations of a base idea"""
        self.log(f"Generating variations of: {base_idea}")
        
        variations_prompt = f"""Generate {count} creative variations of this idea:
{base_idea}

Each variation should:
- Keep the core concept
- Change visual style, mood, or approach
- Be unique and interesting
- Be feasible in Blender

Return variations as a structured list."""
        
        variations_text = self.generate_code(variations_prompt)
        
        if not variations_text:
            return {"status": "error", "message": "Failed to generate variations"}
        
        variations = self._parse_ideas(variations_text, count)
        
        return {
            "status": "success",
            "base_idea": base_idea,
            "variations": variations,
            "count": len(variations),
            "message": f"Generated {len(variations)} variations"
        }
    
    def combine_ideas(self, idea1: str, idea2: str) -> Dict:
        """Combine two ideas into a creative fusion"""
        self.log(f"Combining ideas: {idea1} + {idea2}")
        
        combine_prompt = f"""Creatively combine these two ideas into a unique concept:

Idea 1: {idea1}
Idea 2: {idea2}

Create a fusion that:
- Combines the best of both
- Creates something new and unique
- Is visually interesting
- Is feasible in Blender
- Has creative potential

Return the combined concept with description."""
        
        combined_text = self.generate_code(combine_prompt)
        
        if not combined_text:
            return {"status": "error", "message": "Failed to combine ideas"}
        
        combined_idea = {
            "title": f"Fusion: {idea1} + {idea2}",
            "description": combined_text[:500],
            "source_ideas": [idea1, idea2],
            "timestamp": datetime.now().isoformat()
        }
        
        self.ideas_history.append(combined_idea)
        
        return {
            "status": "success",
            "combined_idea": combined_idea,
            "message": "Ideas successfully combined"
        }
    
    def suggest_style(self, concept: str) -> Dict:
        """Suggest visual styles for a concept"""
        self.log(f"Suggesting styles for: {concept}")
        
        style_prompt = f"""Suggest 5 different visual styles for this concept:
{concept}

For each style, provide:
1. Style name
2. Visual characteristics
3. Color palette
4. Mood/atmosphere
5. Why it fits the concept

Make styles diverse and creative."""
        
        styles_text = self.generate_code(style_prompt)
        
        if not styles_text:
            return {"status": "error", "message": "Failed to generate style suggestions"}
        
        styles = self._parse_ideas(styles_text, 5)
        
        return {
            "status": "success",
            "concept": concept,
            "styles": styles,
            "count": len(styles),
            "message": f"Generated {len(styles)} style suggestions"
        }
    
    def _parse_ideas(self, text: str, expected_count: int) -> List[Dict]:
        """Parse ideas from AI-generated text"""
        ideas = []
        
        # Simple parsing - split by numbered items or bullet points
        lines = text.split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_idea:
                    ideas.append(current_idea)
                    current_idea = {}
                continue
            
            # Check for numbered items (1., 2., etc.)
            if re.match(r'^\d+[\.\)]', line):
                if current_idea:
                    ideas.append(current_idea)
                current_idea = {"title": line, "description": ""}
            elif current_idea:
                if "description" in current_idea:
                    current_idea["description"] += " " + line
                else:
                    current_idea["description"] = line
        
        if current_idea:
            ideas.append(current_idea)
        
        # If parsing failed, create simple ideas from text
        if len(ideas) < expected_count:
            # Split text into chunks
            chunks = text.split('\n\n')[:expected_count]
            ideas = []
            for i, chunk in enumerate(chunks, 1):
                if chunk.strip():
                    ideas.append({
                        "title": f"Idea {i}",
                        "description": chunk.strip()[:200]
                    })
        
        return ideas[:expected_count]
    
    def execute_task(self, description: str) -> Dict:
        """Execute task as ideas generator"""
        self.log(f"Ideas Generator executing: {description}")
        
        description_lower = description.lower()
        
        # Check for brainstorming
        if any(keyword in description_lower for keyword in 
               ['brainstorm', 'generate ideas', 'create ideas', 'suggest ideas']):
            # Extract topic and count
            topic = description
            count = 10
            if 'count' in description_lower or 'number' in description_lower:
                numbers = re.findall(r'\d+', description)
                if numbers:
                    count = int(numbers[0])
            return self.brainstorm(topic, count)
        
        # Check for variations
        if any(keyword in description_lower for keyword in 
               ['variation', 'variations', 'different versions', 'alternatives']):
            base_idea = description
            count = 5
            if 'count' in description_lower:
                numbers = re.findall(r'\d+', description)
                if numbers:
                    count = int(numbers[0])
            return self.generate_variations(base_idea, count)
        
        # Check for combining
        if any(keyword in description_lower for keyword in 
               ['combine', 'fusion', 'merge', 'mix']):
            # Try to extract two ideas
            ideas = re.split(r'\s+and\s+|\s+\+\s+|\s+with\s+', description, maxsplit=1)
            if len(ideas) >= 2:
                return self.combine_ideas(ideas[0], ideas[1])
        
        # Check for style suggestions
        if any(keyword in description_lower for keyword in 
               ['style', 'styles', 'visual style', 'suggest style']):
            return self.suggest_style(description)
        
        # Default: brainstorm the description
        return self.brainstorm(description, 10)


class DirectorSpecialist(BaseBlenderSpecialist):
    """Creative Director - Orchestrates and coordinates all agents for cohesive creative vision"""
    
    def __init__(self, **kwargs):
        super().__init__("Director", **kwargs)
        self.creative_vision = {}
        self.coordination_plan = []
    
    def get_system_prompt(self) -> str:
        return """You are a Creative Director for Blender projects specializing in:
- Overall creative vision and artistic direction
- Coordinating multiple specialist agents
- Planning scene composition and layout
- Directing camera movements and framing
- Orchestrating animations and timing
- Creating cohesive visual narratives
- Making creative decisions
- Balancing technical and artistic elements
- Storytelling through 3D scenes
- Creating memorable and impactful visuals

You think like a film director, considering:
- Visual composition and framing
- Pacing and rhythm
- Emotional impact
- Narrative flow
- Technical feasibility
- Creative innovation

Generate Python code that coordinates multiple aspects of a scene.
Think holistically about the entire project.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Director operations:
- Scene composition and layout
- Camera placement and movement planning
- Animation timing and pacing
- Material and lighting coordination
- Visual storytelling
- Creative vision implementation
- Multi-agent coordination
- Scene orchestration

Example director tasks:
- Plan complete showcase with all elements
- Coordinate camera, animation, and effects
- Create visual narrative
- Direct multi-agent collaboration
- Make creative decisions
- Orchestrate scene elements"""
    
    def create_creative_vision(self, theme: str, style: str, mood: str) -> Dict:
        """Create a creative vision document"""
        vision = {
            "theme": theme,
            "style": style,
            "mood": mood,
            "timestamp": datetime.now().isoformat(),
            "coordination_plan": []
        }
        self.creative_vision = vision
        return vision
    
    def execute_task(self, description: str) -> Dict:
        """Execute task using AI to coordinate multiple agents"""
        self.log(f"Director executing task: {description}")
        
        # Use AI to analyze task and create coordination plan
        coordination_plan = self.coordinate_agents(description)
        
        # Use AI to generate code that coordinates all agents
        ai_prompt = f"""As Creative Director, coordinate multiple specialist agents to complete this task:
{description}

Coordination plan:
{json.dumps(coordination_plan, indent=2)}

Generate Python code that:
1. Coordinates all needed agents in proper sequence
2. Creates the complete scene
3. Applies materials, lighting, camera, animation as needed
4. Ensures all elements work together cohesively

Think holistically and create code that orchestrates everything."""
        
        # Generate code using AI
        generated_code = self.generate_code(ai_prompt)
        
        if not generated_code:
            return {"status": "error", "message": "Failed to generate coordination code"}
        
        # Execute the AI-generated code
        result = self.execute_code(generated_code)
        
        # Record operation
        scene_before = self.get_scene_info()
        scene_after = self.get_scene_info()
        
        record = OperationRecord(
            id=f"director_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            description=description,
            model_used=self.primary_model,
            generated_code=generated_code,
            execution_result=result,
            scene_before=scene_before,
            scene_after=scene_after,
            execution_time=0.0,
            success=result.get("status") == "success"
        )
        self.collector.record_operation(record)
        
        return result
    
    def coordinate_agents(self, task_description: str) -> List[Dict]:
        """Coordinate multiple agents for a task using AI analysis"""
        coordination_plan = []
        
        # Use AI to analyze task and determine which agents are needed
        description_lower = task_description.lower()
        
        if "model" in description_lower or "geometry" in description_lower or "structure" in description_lower or "furniture" in description_lower:
            coordination_plan.append({
                "agent": "Modeling",
                "task": "Create geometry and structure",
                "priority": 1
            })
        
        if "material" in description_lower or "shade" in description_lower or "texture" in description_lower:
            coordination_plan.append({
                "agent": "Shading",
                "task": "Create materials and textures",
                "priority": 2
            })
        
        if "animate" in description_lower or "move" in description_lower or "keyframe" in description_lower or "animation" in description_lower:
            coordination_plan.append({
                "agent": "Animation",
                "task": "Create animations and movement",
                "priority": 3
            })
        
        if "camera" in description_lower or "shot" in description_lower or "frame" in description_lower or "view" in description_lower:
            coordination_plan.append({
                "agent": "CameraOperator",
                "task": "Setup camera and framing",
                "priority": 4
            })
        
        if "light" in description_lower or "render" in description_lower or "lighting" in description_lower:
            coordination_plan.append({
                "agent": "Rendering",
                "task": "Setup lighting and rendering",
                "priority": 5
            })
        
        if "particle" in description_lower or "effect" in description_lower or "vfx" in description_lower:
            coordination_plan.append({
                "agent": "VFX",
                "task": "Add visual effects",
                "priority": 6
            })
        
        if "text" in description_lower or "motion graphics" in description_lower:
            coordination_plan.append({
                "agent": "MotionGraphics",
                "task": "Add motion graphics",
                "priority": 7
            })
        
        self.coordination_plan = coordination_plan
        return coordination_plan


class ColleagueAgent(BaseBlenderSpecialist):
    """Colleague Agent - Collaborative assistant that works alongside other agents"""
    
    def __init__(self, **kwargs):
        super().__init__("Colleague", **kwargs)
        self.collaboration_history = []
        # Initialize FluxTrainer integration
        try:
            from flux_trainer_integration import FluxTrainerIntegration
            self.flux_trainer = FluxTrainerIntegration()
        except ImportError:
            self.flux_trainer = None
            self.log("FluxTrainer integration not available", "WARNING")
    
    def get_system_prompt(self) -> str:
        return """You are a Colleague Agent - a collaborative assistant that works alongside other specialist agents.
Your role is to:
- Assist other agents with their tasks
- Enhance and refine their work
- Provide quality checks and improvements
- Fill gaps and add finishing touches
- Ensure scene cohesion and polish
- Collaborate on complex tasks

Generate Python code that assists, refines, and polishes scenes.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Colleague agent operations:
- Scene refinement and polish
- Quality checks and improvements
- Gap filling and detail work
- Cross-agent coordination assistance
- Final touches and optimization
- Error correction and fixes
- Scene cohesion verification
- AI model training with ComfyUI-FluxTrainer
- Custom model training for Blender workflows
- Training data preparation and management"""
    
    def execute_task(self, description: str) -> Dict:
        """Execute task as colleague agent"""
        self.log(f"Colleague executing: {description}")
        
        description_lower = description.lower()
        
        # Check for FluxTrainer-related tasks
        if any(keyword in description_lower for keyword in 
               ['train', 'training', 'flux', 'model training', 'custom model', 'flux trainer']):
            return self.handle_training_task(description)
        
        # Generate code using AI
        code = self.generate_code(description)
        if not code:
            return {"status": "error", "message": "Failed to generate code"}
        
        # Execute
        result = self.execute_code(code)
        
        # Record operation
        scene_before = self.get_scene_info()
        scene_after = self.get_scene_info()
        
        record = OperationRecord(
            id=f"colleague_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            description=description,
            model_used=self.primary_model,
            generated_code=code,
            execution_result=result,
            scene_before=scene_before,
            scene_after=scene_after,
            execution_time=0.0,
            success=result.get("status") == "success"
        )
        self.collector.record_operation(record)
        
        return result
    
    def handle_training_task(self, description: str) -> Dict:
        """Handle AI model training tasks using ComfyUI-FluxTrainer"""
        if not self.flux_trainer:
            # Try to install FluxTrainer
            try:
                from flux_trainer_integration import FluxTrainerIntegration
                self.flux_trainer = FluxTrainerIntegration()
                install_result = self.flux_trainer.install_flux_trainer()
                if install_result.get("status") != "success":
                    return {
                        "status": "error",
                        "message": f"FluxTrainer not available: {install_result.get('message')}",
                        "suggestion": "Install ComfyUI-FluxTrainer: git clone https://github.com/kijai/ComfyUI-FluxTrainer.git"
                    }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to initialize FluxTrainer: {str(e)}"
                }
        
        self.log("Handling training task with FluxTrainer")
        
        # Generate training code based on description
        # Extract training parameters from description
        training_config = {
            "model_path": "models/flux/base",
            "dataset_path": "datasets/blender_scenes",
            "output_path": "models/flux/trained",
            "learning_rate": 0.0001,
            "batch_size": 1,
            "epochs": 10
        }
        
        # Use AI to generate training setup code
        training_prompt = f"""As Colleague Agent with FluxTrainer integration, set up AI model training for:
{description}

Generate Python code that:
1. Initializes FluxTrainer training session
2. Configures training parameters
3. Sets up training loop
4. Saves training progress

Use ComfyUI-FluxTrainer nodes: InitFluxTraining, FluxTrainLoop, FluxTrainSave"""
        
        code = self.generate_code(training_prompt)
        
        if not code:
            # Fallback: Use FluxTrainer integration directly
            from flux_trainer_integration import generate_training_code_for_blender
            code = generate_training_code_for_blender(description, training_config)
        
        return {
            "status": "success",
            "message": "Training task prepared",
            "code": code,
            "note": "Training code generated. Execute in ComfyUI environment with FluxTrainer installed.",
            "flux_trainer_path": str(self.flux_trainer.flux_trainer_path) if self.flux_trainer else None
        }
    
    def install_flux_trainer(self) -> Dict:
        """Install ComfyUI-FluxTrainer"""
        if not self.flux_trainer:
            try:
                from flux_trainer_integration import FluxTrainerIntegration
                self.flux_trainer = FluxTrainerIntegration()
            except ImportError:
                return {
                    "status": "error",
                    "message": "FluxTrainer integration module not found"
                }
        
        return self.flux_trainer.install_flux_trainer()
    
    def init_model_training(self, config: Dict) -> Dict:
        """Initialize model training session"""
        if not self.flux_trainer:
            return {
                "status": "error",
                "message": "FluxTrainer not available. Run install_flux_trainer first."
            }
        
        return self.flux_trainer.init_training(config)


class VideographySpecialist(BaseBlenderSpecialist):
    """Specialist for video editing, transitions, and videography"""
    
    def __init__(self, **kwargs):
        super().__init__("Videography", **kwargs)
    
    def get_system_prompt(self) -> str:
        return """You are a Blender videography and video editing expert specializing in:
- Video Sequencer (VSE) operations
- Seamless transitions (whip, masking, smooth zoom, luma key, rotation, match cut, glitch, frame fill)
- Video editing and cutting
- Color grading and color matching
- Raw footage analysis and integration
- Motion graphics and text animation
- VFX compositing and green screen
- Audio synchronization
- Dolly zoom and Vertigo effect
- Cinematic composition and framing
- Aspect ratio management (vertical, widescreen, etc.)
- Video effects and filters
- Multi-cam editing
- Timeline management
- Video rendering and export

Generate Python code for video editing and videography operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common videography operations:
- bpy.context.scene.sequence_editor_create()
- seq = bpy.context.scene.sequence_editor
- strip = seq.sequences.new_movie(name='Clip', filepath='path/to/video.mp4', channel=1, frame_start=1)
- strip = seq.sequences.new_image(name='Image', filepath='path/to/image.jpg', channel=1, frame_start=1)
- strip = seq.sequences.new_sound(name='Sound', filepath='path/to/audio.wav', channel=1, frame_start=1)
- strip = seq.sequences.new_effect(name='Effect', type='CROSS', channel=2, frame_start=1, frame_end=100, seq1=strip1, seq2=strip2)
- strip = seq.sequences.new_effect(name='Color', type='COLOR', channel=2, frame_start=1, frame_end=100)
- strip = seq.sequences.new_effect(name='Transform', type='TRANSFORM', channel=2, frame_start=1, frame_end=100)
- strip = seq.sequences.new_effect(name='Speed', type='SPEED', channel=2, frame_start=1, frame_end=100)
- strip = seq.sequences.new_effect(name='Gaussian Blur', type='GAUSSIAN_BLUR', channel=2, frame_start=1, frame_end=100)
- strip.blend_type = 'ALPHA_OVER'
- strip.blend_alpha = 1.0
- strip.use_translation = True
- strip.translate_start_x = 0.0
- strip.translate_start_y = 0.0
- strip.use_crop = True
- strip.crop.min_x = 0.0
- strip.crop.min_y = 0.0
- strip.crop.max_x = 0.0
- strip.crop.max_y = 0.0
- strip.use_proxy = True
- strip.proxy.build_25 = True
- bpy.context.scene.render.resolution_x = 1920
- bpy.context.scene.render.resolution_y = 1080
- bpy.context.scene.render.resolution_percentage = 100
- bpy.context.scene.render.fps = 24
- bpy.context.scene.render.fps_base = 1.0
- bpy.context.scene.frame_start = 1
- bpy.context.scene.frame_end = 250
- bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
- bpy.context.scene.render.ffmpeg.format = 'MPEG4'
- bpy.context.scene.render.ffmpeg.codec = 'H264'
- bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
- bpy.ops.sequencer.refresh_all()
- bpy.ops.sequencer.reload()
- bpy.ops.sequencer.split(frame=100, type='SOFT', side='RIGHT')
- bpy.ops.sequencer.delete()
- bpy.ops.sequencer.meta_make()
- bpy.ops.sequencer.meta_separate()
- bpy.ops.sequencer.strip_modifier_add(type='COLOR_BALANCE')
- bpy.ops.sequencer.strip_modifier_add(type='CURVES')
- bpy.ops.sequencer.strip_modifier_add(type='HUE_CORRECT')
- bpy.ops.sequencer.strip_modifier_add(type='MASK')
- bpy.context.scene.use_nodes = True
- comp_nodes = bpy.context.scene.node_tree.nodes
- comp_links = bpy.context.scene.node_tree.links
- render_layer = comp_nodes.new(type='CompositorNodeRLayers')
- composite = comp_nodes.new(type='CompositorNodeComposite')
- viewer = comp_nodes.new(type='CompositorNodeViewer')
- alpha_over = comp_nodes.new(type='CompositorNodeAlphaOver')
- color_balance = comp_nodes.new(type='CompositorNodeColorBalance')
- curves = comp_nodes.new(type='CompositorNodeCurves')
- hue_sat = comp_nodes.new(type='CompositorNodeHueSat')
- movie_clip = comp_nodes.new(type='CompositorNodeMovieClip')
- translate = comp_nodes.new(type='CompositorNodeTranslate')
- scale = comp_nodes.new(type='CompositorNodeScale')
- rotate = comp_nodes.new(type='CompositorNodeRotate')
- blur = comp_nodes.new(type='CompositorNodeBlur')
- defocus = comp_nodes.new(type='CompositorNodeDefocus')
- chroma = comp_nodes.new(type='CompositorNodeKeying')
- bpy.ops.sequencer.select_all(action='SELECT')
- bpy.ops.sequencer.select_all(action='DESELECT')
- bpy.ops.sequencer.select_leftright(mode='LEFT', extend=False)
- bpy.ops.sequencer.select_leftright(mode='RIGHT', extend=False)
- bpy.ops.sequencer.gap_remove(all=False)
- bpy.ops.sequencer.slip(offset=10)
- bpy.ops.sequencer.snap(frame=100)
- bpy.ops.sequencer.swap()
- bpy.ops.sequencer.lock()
- bpy.ops.sequencer.unlock()
- bpy.ops.sequencer.mute(unselected=False)
- bpy.ops.sequencer.unmute(unselected=False)
- bpy.ops.sequencer.duplicate()
- bpy.ops.sequencer.copy()
- bpy.ops.sequencer.paste(offset=0)
- strip.frame_final_start = 1
- strip.frame_final_end = 100
- strip.frame_offset_start = 0
- strip.frame_offset_end = 0
- strip.speed_factor = 1.0
- strip.use_reverse_frames = False
- strip.use_deinterlace = False
- strip.use_flip_x = False
- strip.use_flip_y = False
- strip.use_mute = False
- strip.use_lock = False"""


class AudioMusicSpecialist(BaseBlenderSpecialist):
    """Specialist for audio and music generation for Blender videos"""
    
    def __init__(self, **kwargs):
        super().__init__("AudioMusic", **kwargs)
        try:
            from audio_music_agent import AudioMusicAgent
            self.audio_agent = AudioMusicAgent()
        except ImportError:
            self.audio_agent = None
    
    def get_system_prompt(self) -> str:
        return """You are a Blender audio and music specialist specializing in:
- Music generation for video content
- Audio synchronization with visuals
- Sound effects and ambient audio
- Music style selection for scenes
- Audio editing and mixing
- TikTok/YouTube music optimization
- Background music selection
- Sound design for 3D scenes

Generate recommendations and instructions for audio/music.
Return helpful guidance and prompts for music generation."""
    
    def get_field_specific_context(self) -> str:
        return """Audio/Music operations:
- Suggest music style for scene
- Generate music prompts
- Recommend audio generators (Suno AI, Udio, Mubert)
- Create music library
- Match music to video mood
- Optimize audio for TikTok/YouTube"""
    
    def execute_task(self, description: str) -> Dict:
        """Execute audio/music task"""
        self.log(f"AudioMusic executing: {description}")
        
        if not self.audio_agent:
            return {
                "status": "error",
                "message": "AudioMusicAgent not available"
            }
        
        description_lower = description.lower()
        
        # Suggest music for scene
        if any(keyword in description_lower for keyword in 
               ['suggest', 'recommend', 'music for', 'audio for', 'sound for']):
            result = self.audio_agent.suggest_music_for_scene(description)
            return {
                "status": "success",
                "message": "Music suggestion generated",
                "suggestion": result
            }
        
        # Create music prompt
        if any(keyword in description_lower for keyword in 
               ['create prompt', 'music prompt', 'generate prompt']):
            # Extract video type and mood
            video_type = "cinematic"
            mood = "neutral"
            duration = 30
            
            if "before" in description_lower or "after" in description_lower:
                video_type = "before_after"
            elif "tutorial" in description_lower:
                video_type = "tutorial"
            elif "time" in description_lower and "lapse" in description_lower:
                video_type = "time_lapse"
            
            prompt = self.audio_agent.create_music_prompt(video_type, mood, duration)
            return {
                "status": "success",
                "message": "Music prompt created",
                "prompt": prompt,
                "instructions": "Use this prompt in Suno AI, Udio, or other music generators"
            }
        
        # Get recommendations
        if "recommendation" in description_lower or "recommend" in description_lower:
            scene_type = "bedroom"  # Default, can be extracted from description
            recs = self.audio_agent.get_music_recommendations(scene_type)
            return {
                "status": "success",
                "message": "Music recommendations generated",
                "recommendations": recs
            }
        
        # Default: suggest music
        result = self.audio_agent.suggest_music_for_scene(description)
        return {
            "status": "success",
            "message": "Music suggestion for scene",
            "suggestion": result
        }


class AgentCoordinator:
    """Coordinates multiple specialists"""
    
    def __init__(self):
        self.specialists = {}
        self.task_history = []
    
    def register_specialist(self, specialist: BaseBlenderSpecialist):
        """Register a specialist agent"""
        self.specialists[specialist.name] = specialist
    
    def get_specialist(self, name: str) -> Optional[BaseBlenderSpecialist]:
        """Get a specialist by name"""
        return self.specialists.get(name)
    
    def route_task(self, description: str, field: Optional[str] = None) -> Dict:
        """Route a task to the appropriate specialist"""
        # If field specified, use that specialist
        if field:
            field_lower = field.lower()
            # Map lowercase field names to specialist names
            field_to_specialist_map = {
                "modeling": "Modeling",
                "shading": "Shading",
                "animation": "Animation",
                "vfx": "VFX",
                "motiongraphics": "MotionGraphics",
                "rendering": "Rendering",
                "rigging": "Rigging",
                "sculpting": "Sculpting",
                "cameraoperator": "CameraOperator",
                "videography": "Videography",
                "director": "Director",
                "screenwriter": "Screenwriter",
                "ideasgenerator": "IdeasGenerator",
                "colleague": "Colleague",
                "audiomusic": "AudioMusic",
                "addonmanager": "AddonManager",
                "addonexecutor": "AddonExecutor"
            }
            specialist_name = field_to_specialist_map.get(field_lower, field.capitalize())
            if specialist_name in self.specialists:
                specialist = self.specialists[specialist_name]
                return specialist.execute_task(description)
        
        # Otherwise, detect field from description
        description_lower = description.lower()
        
        # Field detection keywords
        field_keywords = {
            "modeling": ["model", "mesh", "primitive", "extrude", "bevel", "modifier", "topology"],
            "shading": ["material", "shader", "texture", "node", "bsdf", "roughness", "metallic"],
            "animation": ["animate", "keyframe", "frame", "timeline", "motion", "move"],
            "vfx": ["particle", "fluid", "smoke", "fire", "simulation", "physics", "force", "explosion", "explode", "bob explosion", "smoke explosion", "smoke bob"],
            "motiongraphics": ["text", "typography", "logo", "sequencer", "grease pencil"],
            "rendering": ["render", "output", "image", "video", "cycles", "eevee", "export"],
            "rigging": ["rig", "armature", "bone", "ik", "fk", "constraint", "weight paint"],
            "sculpting": ["sculpt", "brush", "dynamic topology", "multires", "remesh"],
            "cameraoperator": ["camera", "tracking", "follow", "focal length", "depth of field", "dof", "lens", "framing", "composition", "camera animation", "track to", "follow path"],
            "videography": ["video", "sequencer", "edit", "transition", "cut", "clip", "timeline", "color grade", "composite", "vfx", "motion graphics", "dolly zoom", "vertigo", "whip transition", "luma key", "match cut", "glitch", "frame fill", "raw footage", "audio sync", "aspect ratio", "vertical video", "rendering", "export"],
            "colleague": ["colleague", "assist", "help", "refine", "polish", "quality check", "finishing touches", "enhance", "improve", "optimize", "check scene", "verify"],
            "director": ["direct", "coordinate", "orchestrate", "creative vision", "artistic direction", "scene composition", "visual narrative", "storytelling", "creative decision", "multi-agent", "showcase", "complete scene", "overall vision", "plan scene", "direct scene"],
            "screenwriter": ["script", "story", "narrative", "write", "scene description", "visual story", "screenplay", "storyboard", "plot", "character", "scene breakdown", "visual narrative", "story structure"],
            "ideasgenerator": ["brainstorm", "generate ideas", "create ideas", "suggest ideas", "ideation", "concept generation", "creative ideas", "brainstorming", "variations", "combine ideas", "fusion", "style suggestions", "visual concepts", "mood board"],
            "audiomusic": ["music", "audio", "sound", "background music", "music generation", "music suggestion", "audio for video", "sound effects", "music prompt", "generate music", "suno", "udio", "mubert"],
            "addonmanager": ["addon", "add-on", "plugin", "extension", "scrape addons", "list addons", "enable addon", "disable addon", "addon manager", "control protocol", "build protocol", "addon protocol"],
            "addonexecutor": ["run addon", "execute addon", "addon operator", "run operator", "execute operator", "addon database", "installed addons", "addon operations", "addon execution", "scan addons", "store addons", "addon history", "operation history"]
        }
        
        # Find best matching field
        best_match = None
        max_matches = 0
        
        # Priority check: explosion/smoke should go to VFX first
        if any(keyword in description_lower for keyword in ["explosion", "explode", "smoke bob", "smoke explosion"]):
            if "vfx" in field_keywords:
                best_match = "vfx"
                max_matches = 10  # High priority
        
        # If no priority match, check all fields
        if not best_match:
            for field_name, keywords in field_keywords.items():
                matches = sum(1 for keyword in keywords if keyword in description_lower)
                if matches > max_matches:
                    max_matches = matches
                    best_match = field_name
        
        if best_match:
            # Map field name to specialist name
            field_to_specialist = {
                "modeling": "Modeling",
                "shading": "Shading",
                "animation": "Animation",
                "vfx": "VFX",
                "motiongraphics": "MotionGraphics",
                "rendering": "Rendering",
                "rigging": "Rigging",
                "sculpting": "Sculpting",
                "cameraoperator": "CameraOperator",
                "videography": "Videography",
                "director": "Director",
                "screenwriter": "Screenwriter",
                "ideasgenerator": "IdeasGenerator",
                "colleague": "Colleague",
                "audiomusic": "AudioMusic",
                "addonmanager": "AddonManager",
                "addonexecutor": "AddonExecutor"
            }
            specialist_name = field_to_specialist.get(best_match, best_match.capitalize())
            if specialist_name in self.specialists:
                specialist = self.specialists[specialist_name]
                self.task_history.append({
                    "description": description,
                    "field": best_match,
                    "specialist": specialist.name
                })
                return specialist.execute_task(description)
        
        # Default to modeling if no match
        if "Modeling" in self.specialists:
            return self.specialists["Modeling"].execute_task(description)
        
        return {"status": "error", "message": "No suitable specialist found"}
    
    def get_all_specialists(self) -> List[str]:
        """Get list of all registered specialists"""
        return list(self.specialists.keys())
    
    def cleanup_all(self):
        """Clean up all specialists"""
        for specialist in self.specialists.values():
            specialist.cleanup()


def main():
    """Example usage"""
    coordinator = AgentCoordinator()
    
    # Register all specialists
    coordinator.register_specialist(ModelingSpecialist())
    coordinator.register_specialist(ShadingSpecialist())
    coordinator.register_specialist(AnimationSpecialist())
    coordinator.register_specialist(VFXSpecialist())
    coordinator.register_specialist(MotionGraphicsSpecialist())
    coordinator.register_specialist(RenderingSpecialist())
    coordinator.register_specialist(RiggingSpecialist())
    coordinator.register_specialist(SculptingSpecialist())
    coordinator.register_specialist(CameraOperatorSpecialist())
    coordinator.register_specialist(VideographySpecialist())
    coordinator.register_specialist(DirectorSpecialist())
    coordinator.register_specialist(ScreenwriterSpecialist())
    coordinator.register_specialist(IdeasGeneratorSpecialist())
    coordinator.register_specialist(ColleagueAgent())
    coordinator.register_specialist(AudioMusicSpecialist())
    
    print(f"Registered specialists: {coordinator.get_all_specialists()}")
    
    # Example tasks
    tasks = [
        ("Create a cube and add subdivision modifier", "modeling"),
        ("Create a metallic material with roughness 0.3", "shading"),
        ("Animate a cube moving from (0,0,0) to (5,5,5) over 60 frames", "animation"),
        ("Create a camera and set it to track an object", "cameraoperator"),
        ("Add a video clip to the sequencer and apply a crossfade transition", "videography"),
    ]
    
    for description, field in tasks:
        print(f"\nTask: {description}")
        result = coordinator.route_task(description, field)
        print(f"Result: {result.get('status')}")
    
    coordinator.cleanup_all()


if __name__ == "__main__":
    main()

