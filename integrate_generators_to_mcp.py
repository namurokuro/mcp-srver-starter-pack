#!/usr/bin/env python3
"""
Add image/video generation tools to MCP Server
Integrates generators with tutorial workflows
"""

import json
import sys
from pathlib import Path

# Read current mcp_server.py to find where to add tools
mcp_server_path = Path("mcp_server.py")

def add_generator_tools_to_mcp():
    """Add image/video generation tools to MCP server"""
    
    print("="*70)
    print("INTEGRATING GENERATORS INTO MCP SERVER")
    print("="*70)
    print()
    
    # Read current server file
    with open(mcp_server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if tools already exist
    if 'generate_reference_image' in content:
        print("[INFO] Generator tools already exist in mcp_server.py")
        return
    
    # Find where to add import
    import_section = """try:
    from youtube_scraper import YouTubeScraper, scrape_youtube_video, search_youtube
    YOUTUBE_SCRAPER_AVAILABLE = True
except ImportError:
    YOUTUBE_SCRAPER_AVAILABLE = False
    YouTubeScraper = None
    print(f"[INFO] YouTube scraper not available (install yt-dlp)", file=sys.stderr)"""
    
    new_import = """try:
    from youtube_scraper import YouTubeScraper, scrape_youtube_video, search_youtube
    YOUTUBE_SCRAPER_AVAILABLE = True
except ImportError:
    YOUTUBE_SCRAPER_AVAILABLE = False
    YouTubeScraper = None
    print(f"[INFO] YouTube scraper not available (install yt-dlp)", file=sys.stderr)

# Import image generator client
try:
    from image_generator_client import ImageGeneratorClient, generate_image
    IMAGE_GENERATOR_AVAILABLE = True
except ImportError:
    IMAGE_GENERATOR_AVAILABLE = False
    ImageGeneratorClient = None
    print(f"[INFO] Image generator not available", file=sys.stderr)"""
    
    if 'IMAGE_GENERATOR_AVAILABLE' not in content:
        content = content.replace(import_section, new_import)
        print("[OK] Added image generator import")
    
    # Find tools definition section
    tools_end_marker = '            }\n        ]'
    
    # New tools to add
    new_tools = """            }
        ]
        
        # Add image/video generator tools if available
        if IMAGE_GENERATOR_AVAILABLE:
            tools.extend([
                {
                    "name": "generate_reference_image",
                    "description": "Generate reference image for Blender scene creation using Stable Diffusion. Perfect for concept art, matte paintings, or texture references.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Text description of the image to generate"
                            },
                            "negative_prompt": {
                                "type": "string",
                                "description": "What to avoid in the image",
                                "default": ""
                            },
                            "width": {
                                "type": "number",
                                "description": "Image width in pixels",
                                "default": 512
                            },
                            "height": {
                                "type": "number",
                                "description": "Image height in pixels",
                                "default": 512
                            },
                            "steps": {
                                "type": "number",
                                "description": "Number of diffusion steps (more = better quality, slower)",
                                "default": 20
                            },
                            "use_for": {
                                "type": "string",
                                "enum": ["camera_projection", "texture_reference", "lighting_reference", "concept_art", "general"],
                                "description": "Intended use for the generated image",
                                "default": "general"
                            }
                        },
                        "required": ["prompt"]
                    }
                },
                {
                    "name": "generate_video_from_image",
                    "description": "Generate video from an image using Stable Video Diffusion. Useful for creating reference videos or motion studies.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "image_path": {
                                "type": "string",
                                "description": "Path to the source image"
                            },
                            "duration": {
                                "type": "number",
                                "description": "Video duration in seconds",
                                "default": 4
                            }
                        },
                        "required": ["image_path"]
                    }
                },
                {
                    "name": "create_scene_with_ai_reference",
                    "description": "Complete workflow: Generate AI reference image, then create Blender scene using tutorial workflow techniques. Combines AI generation with extracted tutorial workflows.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "concept_prompt": {
                                "type": "string",
                                "description": "Description of the scene to create"
                            },
                            "tutorial_technique": {
                                "type": "string",
                                "enum": ["camera_projection", "camera_projection_mapping", "greenscreen", "auto"],
                                "description": "Tutorial technique to apply (auto = detect from prompt)",
                                "default": "auto"
                            },
                            "generate_reference": {
                                "type": "boolean",
                                "description": "Generate AI reference image first",
                                "default": True
                            },
                            "field": {
                                "type": "string",
                                "enum": ["modeling", "shading", "animation", "vfx", "motiongraphics", "rendering"],
                                "description": "Blender specialist to use"
                            }
                        },
                        "required": ["concept_prompt"]
                    }
                }
            ])
        
        return tools"""
    
    # Check if tools section needs updating
    if 'generate_reference_image' not in content:
        # Find the end of tools list
        if 'return tools' in content and 'generate_reference_image' not in content:
            # Find where tools list ends
            tools_pattern = '            }\n        ]\n    \n    def _define_resources'
            if tools_pattern in content:
                content = content.replace(
                    '            }\n        ]\n    \n    def _define_resources',
                    new_tools + '\n    \n    def _define_resources'
                )
                print("[OK] Added generator tools to _define_tools method")
    
    # Add tool handlers
    handler_section = """            elif name == "search_youtube":
                result = self._tool_search_youtube(arguments)
            else:
                return self._error_response(request_id, f"Unknown tool: {name}")"""
    
    new_handlers = """            elif name == "search_youtube":
                result = self._tool_search_youtube(arguments)
            elif name == "generate_reference_image":
                result = self._tool_generate_reference_image(arguments)
            elif name == "generate_video_from_image":
                result = self._tool_generate_video_from_image(arguments)
            elif name == "create_scene_with_ai_reference":
                result = self._tool_create_scene_with_ai_reference(arguments)
            else:
                return self._error_response(request_id, f"Unknown tool: {name}")"""
    
    if 'generate_reference_image' not in content:
        content = content.replace(handler_section, new_handlers)
        print("[OK] Added generator tool handlers")
    
    # Add handler methods
    methods_section = """    def _tool_execute_code(self, arguments: Dict) -> Dict:"""
    
    new_methods = """    def _tool_generate_reference_image(self, arguments: Dict) -> Dict:
        \"\"\"Tool: Generate reference image using AI\"\"\"
        if not IMAGE_GENERATOR_AVAILABLE:
            return {
                "status": "error",
                "message": "Image generator not available. Start Stable Diffusion: docker-compose -f docker-compose.generators.yml up -d stable-diffusion"
            }
        
        prompt = arguments.get("prompt", "")
        negative_prompt = arguments.get("negative_prompt", "")
        width = arguments.get("width", 512)
        height = arguments.get("height", 512)
        steps = arguments.get("steps", 20)
        use_for = arguments.get("use_for", "general")
        
        if not prompt:
            return {"status": "error", "message": "Prompt is required"}
        
        try:
            self._log(f"Generating reference image: {prompt}")
            client = ImageGeneratorClient()
            result = client.generate_image_stable_diffusion(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps
            )
            
            if result.get("success"):
                return {
                    "status": "success",
                    "image_path": result["image_path"],
                    "use_for": use_for,
                    "message": f"Reference image generated for {use_for}"
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("error", "Failed to generate image")
                }
        except Exception as e:
            self._log_error(f"Image generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _tool_generate_video_from_image(self, arguments: Dict) -> Dict:
        \"\"\"Tool: Generate video from image\"\"\"
        image_path = arguments.get("image_path", "")
        duration = arguments.get("duration", 4)
        
        if not image_path:
            return {"status": "error", "message": "Image path is required"}
        
        # Implementation would call Stable Video Diffusion
        return {
            "status": "info",
            "message": "Video generation from image - implementation needed",
            "image_path": image_path,
            "duration": duration
        }
    
    def _tool_create_scene_with_ai_reference(self, arguments: Dict) -> Dict:
        \"\"\"Tool: Complete workflow - Generate AI reference then create Blender scene\"\"\"
        concept_prompt = arguments.get("concept_prompt", "")
        tutorial_technique = arguments.get("tutorial_technique", "auto")
        generate_reference = arguments.get("generate_reference", True)
        field = arguments.get("field")
        
        if not concept_prompt:
            return {"status": "error", "message": "Concept prompt is required"}
        
        try:
            result_steps = []
            
            # Step 1: Generate reference image
            if generate_reference and IMAGE_GENERATOR_AVAILABLE:
                self._log(f"Step 1: Generating reference image for: {concept_prompt}")
                client = ImageGeneratorClient()
                image_result = client.generate_image_stable_diffusion(
                    prompt=concept_prompt,
                    width=1024,
                    height=1024,
                    steps=25
                )
                
                if image_result.get("success"):
                    result_steps.append({
                        "step": 1,
                        "action": "generate_reference",
                        "status": "success",
                        "image_path": image_result["image_path"]
                    })
                else:
                    result_steps.append({
                        "step": 1,
                        "action": "generate_reference",
                        "status": "skipped",
                        "reason": image_result.get("error")
                    })
            
            # Step 2: Determine tutorial technique
            if tutorial_technique == "auto":
                # Auto-detect based on prompt
                if "camera" in concept_prompt.lower() or "projection" in concept_prompt.lower():
                    tutorial_technique = "camera_projection"
                elif "green" in concept_prompt.lower() or "screen" in concept_prompt.lower():
                    tutorial_technique = "greenscreen"
                else:
                    tutorial_technique = "camera_projection_mapping"
            
            result_steps.append({
                "step": 2,
                "action": "detect_technique",
                "technique": tutorial_technique
            })
            
            # Step 3: Create Blender scene
            self._log(f"Step 3: Creating Blender scene using {tutorial_technique}")
            scene_description = f"Create a scene based on: {concept_prompt}. Use {tutorial_technique} technique."
            
            scene_result = self._tool_create_scene({
                "description": scene_description,
                "field": field
            })
            
            result_steps.append({
                "step": 3,
                "action": "create_scene",
                "status": scene_result.get("status", "unknown"),
                "result": scene_result
            })
            
            return {
                "status": "success",
                "workflow": "ai_reference_to_scene",
                "steps": result_steps,
                "final_scene": scene_result
            }
            
        except Exception as e:
            self._log_error(f"AI reference scene creation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _tool_execute_code(self, arguments: Dict) -> Dict:"""
    
    if '_tool_generate_reference_image' not in content:
        content = content.replace(methods_section, new_methods)
        print("[OK] Added generator tool handler methods")
    
    # Write updated file
    backup_path = mcp_server_path.with_suffix('.py.backup')
    if not backup_path.exists():
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(open(mcp_server_path, 'r', encoding='utf-8').read())
        print(f"[OK] Created backup: {backup_path}")
    
    with open(mcp_server_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print()
    print("[SUCCESS] Generator tools integrated into MCP server!")
    print()
    print("New tools added:")
    print("  - generate_reference_image")
    print("  - generate_video_from_image")
    print("  - create_scene_with_ai_reference")
    print()
    print("Next steps:")
    print("  1. Start image generator: setup-generators.bat")
    print("  2. Restart MCP server")
    print("  3. Test new tools in Cursor")

if __name__ == "__main__":
    try:
        add_generator_tools_to_mcp()
    except Exception as e:
        print(f"\n[ERROR] Integration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

