#!/usr/bin/env python3
"""
Blender Generator Evolving and Teaching AI Assistant
An intelligent workflow pipeline system that:
1. Understands user ideas through conversation
2. Researches tutorials, addons, and database patterns
3. Creates comprehensive project plans with recommendations
4. Delegates tasks to specialist agents
5. Learns from completed projects to build user's style

Implements Model Context Protocol for Cursor integration
Based on: https://cursor.com/docs/cookbook/building-mcp-server
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add paths to import specialized agents
# Priority: 1. Local files (same directory), 2. Environment variable, 3. Hardcoded path, 4. Relative path
current_dir = Path(__file__).parent

# First, try local files in the same directory
if (current_dir / "specialized_agents.py").exists() and (current_dir / "data_collector.py").exists():
    sys.path.insert(0, str(current_dir))
    print(f"[INFO] Using local files from: {current_dir}", file=sys.stderr)
else:
    # Try environment variable
    blender_ollama_path = None
    if os.getenv("BLENDER_OLLAMA_PATH"):
        blender_ollama_path = Path(os.getenv("BLENDER_OLLAMA_PATH"))
    elif Path(r"C:\Users\User\Desktop\blender-ollama").exists():
        blender_ollama_path = Path(r"C:\Users\User\Desktop\blender-ollama")
    else:
        # Try relative path as fallback
        blender_ollama_path = Path(__file__).parent.parent / "blender-ollama"
    
    if blender_ollama_path and blender_ollama_path.exists():
        sys.path.insert(0, str(blender_ollama_path))
        print(f"[INFO] Using Blender-Ollama path: {blender_ollama_path}", file=sys.stderr)
    else:
        print(f"[WARNING] Blender-Ollama path not found. Tried: {blender_ollama_path}", file=sys.stderr)

try:
    from specialized_agents import (
        AudioMusicSpecialist,
        AgentCoordinator, ModelingSpecialist, ShadingSpecialist,
        AnimationSpecialist, VFXSpecialist, MotionGraphicsSpecialist,
        RenderingSpecialist, RiggingSpecialist, SculptingSpecialist,
        CameraOperatorSpecialist, VideographySpecialist, DirectorSpecialist,
        ScreenwriterSpecialist, IdeasGeneratorSpecialist, ColleagueAgent
    )
    # Import YouTube scraper
    try:
        from youtube_scraper import YouTubeScraper, scrape_youtube_video, search_youtube
        YOUTUBE_SCRAPER_AVAILABLE = True
    except ImportError:
        YOUTUBE_SCRAPER_AVAILABLE = False
        YouTubeScraper = None
        print(f"[INFO] YouTube scraper not available (install yt-dlp)", file=sys.stderr)
    # Import AddonManager agent
    try:
        from addon_manager_agent import AddonManagerSpecialist
        ADDON_MANAGER_AVAILABLE = True
    except ImportError:
        ADDON_MANAGER_AVAILABLE = False
        AddonManagerSpecialist = None
        print(f"[INFO] AddonManager Specialist not available", file=sys.stderr)
    
    # Import AddonExecutor agent
    try:
        from addon_executor_agent import AddonExecutorSpecialist
        ADDON_EXECUTOR_AVAILABLE = True
    except ImportError:
        ADDON_EXECUTOR_AVAILABLE = False
        AddonExecutorSpecialist = None
        print(f"[INFO] AddonExecutor Specialist not available", file=sys.stderr)
    # Import workflow pipeline
    try:
        from workflow_pipeline import MainCoordinatorAgent, run_complete_workflow
        WORKFLOW_PIPELINE_AVAILABLE = True
    except ImportError:
        WORKFLOW_PIPELINE_AVAILABLE = False
        MainCoordinatorAgent = None
        print(f"[INFO] Workflow pipeline not available", file=sys.stderr)
    from data_collector import BlenderDataCollector
    from media_handler import MediaHandler
    # Optional: Trends & Innovations Specialist
    try:
        from trends_innovations_specialist import TrendsInnovationsSpecialist
        TRENDS_SPECIALIST_AVAILABLE = True
    except ImportError:
        TRENDS_SPECIALIST_AVAILABLE = False
        TrendsInnovationsSpecialist = None
        print(f"[INFO] Trends & Innovations Specialist not available", file=sys.stderr)
except ImportError as e:
    print(f"[ERROR] Failed to import modules: {e}", file=sys.stderr)
    print(f"[ERROR] Make sure specialized_agents.py and data_collector.py are accessible", file=sys.stderr)
    sys.exit(1)


class BlenderGeneratorEvolvingTeachingAIAssistant:
    """
    Blender Generator Evolving and Teaching AI Assistant
    
    Main coordinator that orchestrates the complete workflow:
    - User conversation and understanding
    - Research (internet + database)
    - Planning with recommendations
    - Task delegation to specialists
    - Learning and style building
    """
    
    def __init__(self):
        self.coordinator = AgentCoordinator()
        self._register_all_specialists()
        # Initialize media handler
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.media_handler = MediaHandler(ollama_url=ollama_url)
        # Initialize workflow pipeline coordinator
        if WORKFLOW_PIPELINE_AVAILABLE and MainCoordinatorAgent:
            self.workflow_coordinator = MainCoordinatorAgent(ollama_url=ollama_url)
        else:
            self.workflow_coordinator = None
        # Initialize trends & innovations specialist (if available)
        try:
            if TRENDS_SPECIALIST_AVAILABLE and TrendsInnovationsSpecialist:
                self.trends_specialist = TrendsInnovationsSpecialist(ollama_url=ollama_url)
            else:
                self.trends_specialist = None
        except NameError:
            self.trends_specialist = None
        self._init_capabilities()
        # Set base path to blender-ollama directory
        # Priority: 1. Environment variable, 2. Hardcoded path, 3. Relative path
        if os.getenv("BLENDER_OLLAMA_PATH"):
            self.base_path = Path(os.getenv("BLENDER_OLLAMA_PATH"))
        elif Path(r"C:\Users\User\Desktop\blender-ollama").exists():
            self.base_path = Path(r"C:\Users\User\Desktop\blender-ollama")
        else:
            # Fallback to relative path
            self.base_path = Path(__file__).parent.parent / "blender-ollama"
        
        if not self.base_path.exists():
            self._log_error(f"Blender-Ollama directory not found at: {self.base_path}")
            self._log_error("Set BLENDER_OLLAMA_PATH environment variable or ensure the directory exists")
    
    def _register_all_specialists(self):
        """Register all specialized agents"""
        try:
            self.coordinator.register_specialist(ModelingSpecialist())
            self.coordinator.register_specialist(ShadingSpecialist())
            self.coordinator.register_specialist(AnimationSpecialist())
            self.coordinator.register_specialist(VFXSpecialist())
            self.coordinator.register_specialist(MotionGraphicsSpecialist())
            self.coordinator.register_specialist(RenderingSpecialist())
            self.coordinator.register_specialist(RiggingSpecialist())
            self.coordinator.register_specialist(SculptingSpecialist())
            self.coordinator.register_specialist(CameraOperatorSpecialist())
            self.coordinator.register_specialist(VideographySpecialist())
            self.coordinator.register_specialist(DirectorSpecialist())
            self.coordinator.register_specialist(ScreenwriterSpecialist())
            self.coordinator.register_specialist(IdeasGeneratorSpecialist())
            self.coordinator.register_specialist(ColleagueAgent())
            self.coordinator.register_specialist(AudioMusicSpecialist())
            # Register AddonManager if available
            if ADDON_MANAGER_AVAILABLE and AddonManagerSpecialist:
                self.coordinator.register_specialist(AddonManagerSpecialist())
            # Register AddonExecutor if available
            if ADDON_EXECUTOR_AVAILABLE and AddonExecutorSpecialist:
                self.coordinator.register_specialist(AddonExecutorSpecialist())
            self._log(f"Registered {len(self.coordinator.specialists)} specialists")
        except Exception as e:
            self._log_error(f"Error registering specialists: {e}")
    
    def _init_capabilities(self):
        """Initialize MCP capabilities"""
        self.tools = self._define_tools()
        self.resources = self._define_resources()
        self.prompts = self._define_prompts()
    
    def _define_tools(self) -> List[Dict]:
        """Define available MCP tools"""
        return [
            {
                "name": "create_scene",
                "description": "Create a 3D scene in Blender from natural language description. Automatically routes to the appropriate specialist agent.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Natural language description of the scene to create"
                        },
            "field": {
                "type": "string",
                "enum": ["modeling", "shading", "animation", "vfx",
                         "motiongraphics", "rendering", "rigging",
                         "sculpting", "cameraoperator", "videography", "director", "screenwriter", "ideasgenerator", "colleague", "addonmanager", "addonexecutor"],
                "description": "Optional: Specify specialist agent (auto-detected if omitted). Use 'director' for AI coordination, 'screenwriter' for story/script creation, 'ideasgenerator' for brainstorming and idea generation, 'addonmanager' for addon scraping and control protocols, 'addonexecutor' for running addon operations and maintaining addon database."
            }
                    },
                    "required": ["description"]
                }
            },
            {
                "name": "get_scene_info",
                "description": "Get current Blender scene information including objects, materials, and settings",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "execute_blender_code",
                "description": "Execute Python code directly in Blender",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute in Blender"
                        }
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "query_database",
                "description": "Query operation history, patterns, errors, or performance from specialized agent databases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "enum": ["modeling", "shading", "animation", "vfx",
                                     "motiongraphics", "rendering", "rigging",
                                     "sculpting", "cameraoperator", "videography", "all"],
                            "description": "Which database to query (or 'all' for all databases)"
                        },
                        "query_type": {
                            "type": "string",
                            "enum": ["recent", "patterns", "errors", "performance"],
                            "description": "Type of query: recent operations, successful patterns, common errors, or model performance",
                            "default": "recent"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["database"]
                }
            },
            {
                "name": "get_model_performance",
                "description": "Get performance metrics for LLM models across databases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "description": "Specific database to query (optional, defaults to all)"
                        },
                        "model": {
                            "type": "string",
                            "description": "Specific model to query (optional)"
                        }
                    }
                }
            },
            {
                "name": "get_successful_patterns",
                "description": "Get successful code generation patterns from databases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "enum": ["modeling", "shading", "animation", "vfx",
                                     "motiongraphics", "rendering", "rigging",
                                     "sculpting", "cameraoperator", "videography"],
                            "description": "Database to query"
                        },
                        "limit": {
                            "type": "number",
                            "description": "Maximum number of patterns to return",
                            "default": 10
                        }
                    },
                    "required": ["database"]
                }
            },
            {
                "name": "list_specialists",
                "description": "List all available specialist agents and their capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "load_reference_image",
                "description": "Load a reference image for analysis and scene creation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Path to the reference image file"
                        }
                    },
                    "required": ["image_path"]
                }
            },
            {
                "name": "analyze_image",
                "description": "Analyze a reference image using LLM vision model to extract scene information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Path to the image file"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["scene_description", "materials", "custom"],
                            "description": "Type of analysis: scene_description (for 3D recreation), materials (for material extraction), or custom",
                            "default": "scene_description"
                        },
                        "custom_prompt": {
                            "type": "string",
                            "description": "Custom analysis prompt (used when analysis_type is 'custom')"
                        },
                        "model": {
                            "type": "string",
                            "description": "Vision model to use (default: llama3.2-vision:latest)",
                            "default": "llama3.2-vision:latest"
                        }
                    },
                    "required": ["image_path"]
                }
            },
            {
                "name": "create_scene_from_image",
                "description": "Create a Blender scene based on a reference image using vision model analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "image_path": {
                            "type": "string",
                            "description": "Path to the reference image"
                        },
                        "description": {
                            "type": "string",
                            "description": "Additional description or modifications to apply"
                        },
                        "field": {
                            "type": "string",
                            "enum": ["modeling", "shading", "animation", "vfx",
                                     "motiongraphics", "rendering", "rigging",
                                     "sculpting", "cameraoperator", "videography"],
                            "description": "Optional: Specify specialist agent"
                        }
                    },
                    "required": ["image_path"]
                }
            },
            {
                "name": "load_reference_video",
                "description": "Load a reference video file for analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "video_path": {
                            "type": "string",
                            "description": "Path to the video file"
                        }
                    },
                    "required": ["video_path"]
                }
            },
            {
                "name": "analyze_video",
                "description": "Analyze a reference video for Blender scene creation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "video_path": {
                            "type": "string",
                            "description": "Path to the video file"
                        },
                        "frame_number": {
                            "type": "number",
                            "description": "Optional: Specific frame number to analyze"
                        }
                    },
                    "required": ["video_path"]
                }
            },
            {
                "name": "list_media_files",
                "description": "List available reference images and videos in a directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path to search for media files"
                        },
                        "media_type": {
                            "type": "string",
                            "enum": ["all", "image", "video"],
                            "description": "Type of media to list",
                            "default": "all"
                        }
                    },
                    "required": ["directory"]
                }
            },
            {
                "name": "get_development_proposals",
                "description": "Get development proposals based on current trends and innovations. Monitors trends in Blender, AI, video editing, fashion, furniture, TikTok, Instagram, gaming, and other project-relevant areas. Automatically adapts to current project context if set. Provides actionable development suggestions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "focus_area": {
                            "type": "string",
                            "enum": ["general", "blender", "ai", "tech", "video", "fashion", "furniture", "tiktok", "instagram", "gaming", "custom"],
                            "description": "Focus area: general (all, adapts to project context), blender, ai, tech, video, fashion, furniture, tiktok, instagram, gaming, or custom (requires custom_topics)",
                            "default": "general"
                        },
                        "custom_topics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Custom topics for project-specific trend analysis (required if focus_area is 'custom')"
                        },
                        "use_project_context": {
                            "type": "boolean",
                            "description": "Use current project context to adapt proposals (default: true)",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "set_project_context",
                "description": "Set the current project context so trend monitoring adapts to your specific project. The specialist will automatically monitor relevant trends based on project type.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_type": {
                            "type": "string",
                            "enum": ["fashion", "furniture", "video", "tiktok", "instagram", "gaming", "blender", "3d", "modeling", "custom"],
                            "description": "Type of project you're working on"
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Optional description of your project for better trend adaptation"
                        }
                    },
                    "required": ["project_type"]
                }
            },
            {
                "name": "get_project_relevant_trends",
                "description": "Get trends and proposals automatically adapted to your current project context. Uses the project type you've set to monitor relevant trends.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "create_mesh_object",
                "description": "Create a mesh primitive object (cube, sphere, cylinder, etc.) with full control over size, location, rotation, and scale",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "primitive_type": {
                            "type": "string",
                            "enum": ["cube", "sphere", "cylinder", "cone", "torus", "plane", "ico_sphere", "monkey", "grid"],
                            "description": "Type of primitive to create",
                            "default": "cube"
                        },
                        "size": {
                            "type": "number",
                            "description": "Base size of the object",
                            "default": 2.0
                        },
                        "location": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "3D position [x, y, z]",
                            "default": [0, 0, 0]
                        },
                        "rotation": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Rotation in degrees [x, y, z]"
                        },
                        "scale": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Scale factors [x, y, z]",
                            "default": [1, 1, 1]
                        },
                        "name": {
                            "type": "string",
                            "description": "Custom name for the object"
                        },
                        "subdivisions": {
                            "type": "number",
                            "description": "Subdivision surface levels",
                            "default": 0
                        }
                    }
                }
            },
            {
                "name": "transform_object",
                "description": "Transform an object (move, rotate, scale) with precise control",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {
                            "type": "string",
                            "description": "Name of the object to transform"
                        },
                        "location": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "New location [x, y, z]"
                        },
                        "rotation": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Rotation in degrees [x, y, z]"
                        },
                        "scale": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Scale factors [x, y, z]"
                        }
                    },
                    "required": ["object_name"]
                }
            },
            {
                "name": "duplicate_object",
                "description": "Duplicate an object with optional offset and linking",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {
                            "type": "string",
                            "description": "Name of object to duplicate"
                        },
                        "linked": {
                            "type": "boolean",
                            "description": "Create linked duplicate (instance)",
                            "default": False
                        },
                        "offset": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "Position offset for duplicate [x, y, z]",
                            "default": [0, 0, 0]
                        }
                    },
                    "required": ["object_name"]
                }
            },
            {
                "name": "add_modifier",
                "description": "Add a modifier to an object (subdivision, array, mirror, etc.)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "object_name": {
                            "type": "string",
                            "description": "Name of the object"
                        },
                        "modifier_type": {
                            "type": "string",
                            "enum": ["SUBSURF", "ARRAY", "MIRROR", "BEVEL", "BOOLEAN", "SOLIDIFY", "DECIMATE"],
                            "description": "Type of modifier to add"
                        },
                        "name": {
                            "type": "string",
                            "description": "Custom name for the modifier"
                        },
                        "settings": {
                            "type": "object",
                            "description": "Modifier-specific settings (e.g., levels for SUBSURF, count for ARRAY)"
                        }
                    },
                    "required": ["object_name", "modifier_type"]
                }
            }
        ]
        
        # Add YouTube scraper tools if available
        if YOUTUBE_SCRAPER_AVAILABLE:
            tools.extend([
                {
                    "name": "scrape_youtube_video",
                    "description": "Extract information from a YouTube video including title, description, metadata, and transcript availability",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "YouTube video URL"
                            },
                            "include_transcript": {
                                "type": "boolean",
                                "description": "Whether to check for transcript/subtitle availability",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "search_youtube",
                    "description": "Search for YouTube videos by query",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            ])
        
        # Add workflow pipeline tools if available
        if WORKFLOW_PIPELINE_AVAILABLE:
            tools.extend([
                {
                    "name": "start_project_workflow",
                    "description": "Start a complete project workflow: understand user idea, research resources, create plan, and execute. This is the main entry point for the Blender Generator Evolving and Teaching AI Assistant.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "user_idea": {
                                "type": "string",
                                "description": "User's idea or request - can include tutorial links, reference images/videos, or description of what to create"
                            },
                            "has_tutorial_link": {
                                "type": "boolean",
                                "description": "Whether user provided a tutorial link",
                                "default": False
                            },
                            "tutorial_url": {
                                "type": "string",
                                "description": "YouTube tutorial URL (if provided)"
                            },
                            "has_reference_images": {
                                "type": "boolean",
                                "description": "Whether user has reference images",
                                "default": False
                            },
                            "reference_images": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of reference image paths"
                            },
                            "has_own_footage": {
                                "type": "boolean",
                                "description": "Whether user has their own footage to edit",
                                "default": False
                            },
                            "footage_path": {
                                "type": "string",
                                "description": "Path to user's footage (if provided)"
                            }
                        },
                        "required": ["user_idea"]
                    }
                },
                {
                    "name": "research_project_resources",
                    "description": "Research tutorials, addons, plugins, and database patterns for a project idea",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "idea": {
                                "type": "string",
                                "description": "Project idea to research"
                            },
                            "tutorial_url": {
                                "type": "string",
                                "description": "Optional tutorial URL to analyze"
                            }
                        },
                        "required": ["idea"]
                    }
                },
                {
                    "name": "create_project_plan",
                    "description": "Create a comprehensive project plan with addon/plugin recommendations and workflow steps",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "user_request": {
                                "type": "object",
                                "description": "User request object (from start_project_workflow)"
                            },
                            "research_results": {
                                "type": "object",
                                "description": "Research results (from research_project_resources)"
                            }
                        },
                        "required": ["user_request"]
                    }
                },
                {
                    "name": "save_project_to_database",
                    "description": "Save completed project techniques and resources to database for learning",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID to save"
                            },
                            "save_techniques": {
                                "type": "boolean",
                                "description": "Whether to save techniques used",
                                "default": True
                            },
                            "save_resources": {
                                "type": "boolean",
                                "description": "Whether to save resources used",
                                "default": True
                            }
                        },
                        "required": ["project_id"]
                    }
                }
            ])
        
        return tools
    
    def _define_resources(self) -> List[Dict]:
        """Define available MCP resources"""
        databases = ["modeling", "shading", "animation", "vfx", "motiongraphics",
                     "rendering", "rigging", "sculpting", "cameraoperator", "videography"]
        
        resources = []
        for db in databases:
            resources.extend([
                {
                    "uri": f"blender://database/{db}/schema",
                    "name": f"{db.title()} Database Schema",
                    "description": f"Schema information for {db}_data.db",
                    "mimeType": "application/json"
                },
                {
                    "uri": f"blender://database/{db}/operations",
                    "name": f"{db.title()} Recent Operations",
                    "description": f"Recent operations from {db} database",
                    "mimeType": "application/json"
                },
                {
                    "uri": f"blender://database/{db}/patterns",
                    "name": f"{db.title()} Code Patterns",
                    "description": f"Successful code patterns for {db}",
                    "mimeType": "application/json"
                },
                {
                    "uri": f"blender://database/{db}/errors",
                    "name": f"{db.title()} Error Patterns",
                    "description": f"Common errors in {db} operations",
                    "mimeType": "application/json"
                },
                {
                    "uri": f"blender://database/{db}/performance",
                    "name": f"{db.title()} Model Performance",
                    "description": f"LLM performance metrics for {db}",
                    "mimeType": "application/json"
                }
            ])
        
        resources.extend([
            {
                "uri": "blender://scene/current",
                "name": "Current Blender Scene",
                "description": "Current state of Blender scene",
                "mimeType": "application/json"
            },
            {
                "uri": "blender://agents/list",
                "name": "Available Agents",
                "description": "List of all specialist agents",
                "mimeType": "application/json"
            },
            {
                "uri": "blender://media/cached",
                "name": "Cached Media Files",
                "description": "List of currently loaded reference images and videos",
                "mimeType": "application/json"
            },
        ])
        
        return resources
    
    def _define_prompts(self) -> List[Dict]:
        """Define available MCP prompts"""
        return [
            {
                "name": "create_modeling_scene",
                "description": "Create a 3D modeling scene with best practices",
                "arguments": [
                    {
                        "name": "description",
                        "description": "What to model",
                        "required": True
                    }
                ]
            },
            {
                "name": "create_material_setup",
                "description": "Create a complete material setup workflow",
                "arguments": [
                    {
                        "name": "material_type",
                        "description": "Type of material (metallic, glass, etc.)",
                        "required": True
                    }
                ]
            },
            {
                "name": "analyze_performance",
                "description": "Analyze performance across all databases",
                "arguments": []
            },
            {
                "name": "find_similar_operations",
                "description": "Find similar successful operations from history",
                "arguments": [
                    {
                        "name": "description",
                        "description": "Operation description to match",
                        "required": True
                    },
                    {
                        "name": "database",
                        "description": "Database to search (optional)",
                        "required": False
                    }
                ]
            },
            {
                "name": "create_scene_from_reference_image",
                "description": "Complete workflow: Analyze reference image and create 3D scene in Blender",
                "arguments": [
                    {
                        "name": "image_path",
                        "description": "Path to reference image",
                        "required": True
                    },
                    {
                        "name": "field",
                        "description": "Specialist agent to use (optional)",
                        "required": False
                    }
                ]
            }
        ]
    
    def handle_request(self, request: Dict) -> Dict:
        """Handle MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return self._handle_initialize(params, request_id)
            elif method == "tools/list":
                return self._handle_tools_list(request_id)
            elif method == "tools/call":
                return self._handle_tool_call(params, request_id)
            elif method == "resources/list":
                return self._handle_resources_list(request_id)
            elif method == "resources/read":
                return self._handle_resource_read(params, request_id)
            elif method == "prompts/list":
                return self._handle_prompts_list(request_id)
            elif method == "prompts/get":
                return self._handle_prompt_get(params, request_id)
            else:
                return self._error_response(request_id, f"Unknown method: {method}")
        except Exception as e:
            self._log_error(f"Error handling request: {e}")
            import traceback
            traceback.print_exc()
            return self._error_response(request_id, str(e))
    
    def _handle_initialize(self, params: Dict, request_id: Any) -> Dict:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "blender-ollama-mcp",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list(self, request_id: Any) -> Dict:
        """List all available tools"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": self.tools}
        }
    
    def _handle_tool_call(self, params: Dict, request_id: Any) -> Dict:
        """Call a tool"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if name == "create_scene":
                result = self._tool_create_scene(arguments)
            elif name == "get_scene_info":
                result = self._tool_get_scene_info(arguments)
            elif name == "execute_blender_code":
                result = self._tool_execute_code(arguments)
            elif name == "query_database":
                result = self._tool_query_database(arguments)
            elif name == "get_model_performance":
                result = self._tool_get_performance(arguments)
            elif name == "get_successful_patterns":
                result = self._tool_get_patterns(arguments)
            elif name == "list_specialists":
                result = self._tool_list_specialists(arguments)
            elif name == "load_reference_image":
                result = self._tool_load_image(arguments)
            elif name == "analyze_image":
                result = self._tool_analyze_image(arguments)
            elif name == "create_scene_from_image":
                result = self._tool_create_scene_from_image(arguments)
            elif name == "load_reference_video":
                result = self._tool_load_video(arguments)
            elif name == "analyze_video":
                result = self._tool_analyze_video(arguments)
            elif name == "list_media_files":
                result = self._tool_list_media_files(arguments)
            elif name == "get_development_proposals":
                result = self._tool_get_development_proposals(arguments)
            elif name == "set_project_context":
                result = self._tool_set_project_context(arguments)
            elif name == "get_project_relevant_trends":
                result = self._tool_get_project_relevant_trends(arguments)
            elif name == "create_mesh_object":
                result = self._tool_create_mesh_object(arguments)
            elif name == "transform_object":
                result = self._tool_transform_object(arguments)
            elif name == "duplicate_object":
                result = self._tool_duplicate_object(arguments)
            elif name == "add_modifier":
                result = self._tool_add_modifier(arguments)
            elif name == "scrape_youtube_video":
                result = self._tool_scrape_youtube_video(arguments)
            elif name == "search_youtube":
                result = self._tool_search_youtube(arguments)
            elif name == "start_project_workflow":
                result = self._tool_start_project_workflow(arguments)
            elif name == "research_project_resources":
                result = self._tool_research_project_resources(arguments)
            elif name == "create_project_plan":
                result = self._tool_create_project_plan(arguments)
            elif name == "save_project_to_database":
                result = self._tool_save_project_to_database(arguments)
            else:
                return self._error_response(request_id, f"Unknown tool: {name}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, default=str)
                        }
                    ]
                }
            }
        except Exception as e:
            self._log_error(f"Tool call error: {e}")
            import traceback
            traceback.print_exc()
            return self._error_response(request_id, str(e))
    
    def _tool_create_scene(self, arguments: Dict) -> Dict:
        """Tool: Create scene"""
        description = arguments.get("description", "")
        field = arguments.get("field")
        
        if not description:
            return {"error": "Description is required"}
        
        self._log(f"Creating scene: {description} (field: {field or 'auto'})")
        result = self.coordinator.route_task(description, field)
        return result
    
    def _tool_get_scene_info(self, arguments: Dict) -> Dict:
        """Tool: Get scene info"""
        if "Modeling" in self.coordinator.specialists:
            specialist = self.coordinator.specialists["Modeling"]
            return specialist.get_scene_info()
        return {"error": "No specialist available"}
    
    def _tool_create_mesh_object(self, arguments: Dict) -> Dict:
        """Tool: Create mesh object"""
        from integrated_tools import create_mesh_object_code
        
        primitive_type = arguments.get("primitive_type", "cube")
        size = arguments.get("size", 2.0)
        location = arguments.get("location", [0, 0, 0])
        rotation = arguments.get("rotation")
        scale = arguments.get("scale", [1, 1, 1])
        name = arguments.get("name")
        subdivisions = arguments.get("subdivisions", 0)
        
        try:
            code = create_mesh_object_code(
                primitive_type=primitive_type,
                size=size,
                location=location,
                rotation=rotation,
                scale=scale,
                name=name,
                subdivisions=subdivisions
            )
            
            # Execute via Modeling agent
            if "Modeling" in self.coordinator.specialists:
                specialist = self.coordinator.specialists["Modeling"]
                result = specialist.execute_code(code)
                return result
            else:
                return {"status": "error", "message": "Modeling agent not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_transform_object(self, arguments: Dict) -> Dict:
        """Tool: Transform object"""
        from integrated_tools import transform_object_code
        
        object_name = arguments.get("object_name")
        location = arguments.get("location")
        rotation = arguments.get("rotation")
        scale = arguments.get("scale")
        
        if not object_name:
            return {"status": "error", "message": "object_name is required"}
        
        try:
            code = transform_object_code(
                object_name=object_name,
                location=location,
                rotation=rotation,
                scale=scale
            )
            
            # Execute via Modeling agent
            if "Modeling" in self.coordinator.specialists:
                specialist = self.coordinator.specialists["Modeling"]
                result = specialist.execute_code(code)
                return result
            else:
                return {"status": "error", "message": "Modeling agent not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_duplicate_object(self, arguments: Dict) -> Dict:
        """Tool: Duplicate object"""
        from integrated_tools import duplicate_object_code
        
        object_name = arguments.get("object_name")
        linked = arguments.get("linked", False)
        offset = arguments.get("offset", [0, 0, 0])
        
        if not object_name:
            return {"status": "error", "message": "object_name is required"}
        
        try:
            code = duplicate_object_code(
                object_name=object_name,
                linked=linked,
                offset=offset
            )
            
            # Execute via Modeling agent
            if "Modeling" in self.coordinator.specialists:
                specialist = self.coordinator.specialists["Modeling"]
                result = specialist.execute_code(code)
                return result
            else:
                return {"status": "error", "message": "Modeling agent not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_add_modifier(self, arguments: Dict) -> Dict:
        """Tool: Add modifier"""
        from integrated_tools import add_modifier_code
        
        object_name = arguments.get("object_name")
        modifier_type = arguments.get("modifier_type")
        name = arguments.get("name")
        settings = arguments.get("settings", {})
        
        if not object_name or not modifier_type:
            return {"status": "error", "message": "object_name and modifier_type are required"}
        
        try:
            code = add_modifier_code(
                object_name=object_name,
                modifier_type=modifier_type,
                name=name,
                settings=settings
            )
            
            # Execute via Modeling agent
            if "Modeling" in self.coordinator.specialists:
                specialist = self.coordinator.specialists["Modeling"]
                result = specialist.execute_code(code)
                return result
            else:
                return {"status": "error", "message": "Modeling agent not available"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_scrape_youtube_video(self, arguments: Dict) -> Dict:
        """Tool: Scrape YouTube video information"""
        if not YOUTUBE_SCRAPER_AVAILABLE:
            return {
                "status": "error",
                "message": "YouTube scraper not available. Install yt-dlp: pip install yt-dlp"
            }
        
        url = arguments.get("url", "")
        include_transcript = arguments.get("include_transcript", False)
        
        if not url:
            return {"status": "error", "message": "URL is required"}
        
        try:
            self._log(f"Scraping YouTube video: {url}")
            info = scrape_youtube_video(url, include_transcript=include_transcript)
            
            if info.get("success"):
                return {
                    "status": "success",
                    "video_info": {
                        "video_id": info.get("video_id"),
                        "title": info.get("title"),
                        "description": info.get("description", "")[:500],  # Limit description length
                        "duration": info.get("duration"),
                        "duration_string": info.get("duration_string"),
                        "uploader": info.get("uploader"),
                        "upload_date": info.get("upload_date"),
                        "view_count": info.get("view_count"),
                        "like_count": info.get("like_count"),
                        "thumbnail": info.get("thumbnail"),
                        "tags": info.get("tags", [])[:10],  # Limit tags
                        "url": info.get("webpage_url", url),
                        "transcript": info.get("transcript") if include_transcript else None
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": info.get("error", "Failed to scrape video"),
                    "video_id": info.get("video_id")
                }
        except Exception as e:
            self._log_error(f"YouTube scraping error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _tool_search_youtube(self, arguments: Dict) -> Dict:
        """Tool: Search YouTube videos"""
        if not YOUTUBE_SCRAPER_AVAILABLE:
            return {
                "status": "error",
                "message": "YouTube scraper not available. Install yt-dlp: pip install yt-dlp"
            }
        
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)
        
        if not query:
            return {"status": "error", "message": "Query is required"}
        
        try:
            self._log(f"Searching YouTube: {query}")
            results = search_youtube(query, max_results=max_results)
            
            return {
                "status": "success",
                "query": query,
                "count": len(results),
                "videos": results
            }
        except Exception as e:
            self._log_error(f"YouTube search error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _tool_start_project_workflow(self, arguments: Dict) -> Dict:
        """Tool: Start complete project workflow"""
        if not self.workflow_coordinator:
            return {
                "status": "error",
                "message": "Workflow pipeline not available"
            }
        
        try:
            from workflow_pipeline import UserRequest
            
            # Create user request
            user_request = UserRequest(
                idea=arguments.get("user_idea", ""),
                has_tutorial_link=arguments.get("has_tutorial_link", False),
                tutorial_url=arguments.get("tutorial_url"),
                has_reference_images=arguments.get("has_reference_images", False),
                reference_images=arguments.get("reference_images", []),
                has_own_footage=arguments.get("has_own_footage", False),
                footage_path=arguments.get("footage_path")
            )
            
            # Phase 1: Understand
            user_request = self.workflow_coordinator.understand_user_request(
                user_request.idea
            )
            
            # Phase 2: Research
            research = self.workflow_coordinator.research_resources(user_request)
            
            # Phase 3: Create plan
            plan = self.workflow_coordinator.create_project_plan(user_request, research)
            
            return {
                "status": "success",
                "phase": "plan_created",
                "project_id": plan.project_id,
                "plan": {
                    "complexity": plan.complexity,
                    "recommended_resources": [
                        {
                            "name": r.name,
                            "type": r.type,
                            "cost": r.cost,
                            "description": r.description,
                            "why_recommended": r.why_recommended
                        } for r in plan.recommended_resources
                    ],
                    "workflow_steps": plan.workflow_steps,
                    "specialist_assignments": plan.specialist_assignments
                },
                "message": "Project plan created. Use execute_project to proceed."
            }
        except Exception as e:
            self._log_error(f"Workflow error: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    def _tool_research_project_resources(self, arguments: Dict) -> Dict:
        """Tool: Research project resources"""
        if not self.workflow_coordinator:
            return {"status": "error", "message": "Workflow pipeline not available"}
        
        try:
            from workflow_pipeline import UserRequest
            
            user_request = UserRequest(
                idea=arguments.get("idea", ""),
                tutorial_url=arguments.get("tutorial_url")
            )
            
            research = self.workflow_coordinator.research_resources(user_request)
            
            return {
                "status": "success",
                "research": {
                    "tutorials": research.tutorials,
                    "addons": research.addons,
                    "plugins": research.plugins,
                    "database_patterns": research.database_patterns,
                    "similar_projects": research.similar_projects
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_create_project_plan(self, arguments: Dict) -> Dict:
        """Tool: Create project plan"""
        if not self.workflow_coordinator:
            return {"status": "error", "message": "Workflow pipeline not available"}
        
        try:
            from workflow_pipeline import UserRequest, ResearchResult
            
            # Reconstruct objects from dict
            user_request_dict = arguments.get("user_request", {})
            user_request = UserRequest(**user_request_dict)
            
            research_dict = arguments.get("research_results", {})
            research = ResearchResult(**research_dict)
            
            plan = self.workflow_coordinator.create_project_plan(user_request, research)
            
            return {
                "status": "success",
                "project_id": plan.project_id,
                "plan": {
                    "complexity": plan.complexity,
                    "recommended_resources": [
                        {
                            "name": r.name,
                            "type": r.type,
                            "cost": r.cost,
                            "description": r.description
                        } for r in plan.recommended_resources
                    ],
                    "workflow_steps": plan.workflow_steps
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_save_project_to_database(self, arguments: Dict) -> Dict:
        """Tool: Save project to database"""
        if not self.workflow_coordinator:
            return {"status": "error", "message": "Workflow pipeline not available"}
        
        try:
            project_id = arguments.get("project_id")
            save_techniques = arguments.get("save_techniques", True)
            save_resources = arguments.get("save_resources", True)
            
            # Load project result
            project_dir = Path("blender_projects") / project_id
            result_file = project_dir / "project_result.json"
            
            if not result_file.exists():
                return {"status": "error", "message": "Project result not found"}
            
            with open(result_file, 'r') as f:
                result_data = json.load(f)
            
            from workflow_pipeline import ProjectResult
            result = ProjectResult(**result_data)
            
            if save_techniques or save_resources:
                self.workflow_coordinator._save_to_database(result)
            
            return {
                "status": "success",
                "message": "Project saved to database",
                "saved_techniques": save_techniques,
                "saved_resources": save_resources
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _tool_execute_code(self, arguments: Dict) -> Dict:
        """Tool: Execute Blender code"""
        code = arguments.get("code", "")
        if not code:
            return {"error": "Code is required"}
        
        if "modeling" in self.coordinator.specialists:
            specialist = self.coordinator.specialists["modeling"]
            return specialist.execute_code(code)
        return {"error": "No specialist available"}
    
    def _tool_query_database(self, arguments: Dict) -> Dict:
        """Tool: Query database"""
        database = arguments.get("database", "all")
        query_type = arguments.get("query_type", "recent")
        limit = arguments.get("limit", 10)
        
        if database == "all":
            results = {}
            for db_name in ["modeling", "shading", "animation", "vfx",
                           "motiongraphics", "rendering", "rigging",
                           "sculpting", "cameraoperator", "videography"]:
                try:
                    db_path = self.base_path / f"{db_name}_data.db"
                    collector = BlenderDataCollector(str(db_path))
                    results[db_name] = self._execute_query(collector, query_type, limit)
                    collector.close()
                except Exception as e:
                    results[db_name] = {"error": str(e)}
            return results
        else:
            try:
                db_path = self.base_path / f"{database}_data.db"
                collector = BlenderDataCollector(str(db_path))
                result = self._execute_query(collector, query_type, limit)
                collector.close()
                return result
            except Exception as e:
                return {"error": str(e)}
    
    def _execute_query(self, collector: BlenderDataCollector, 
                      query_type: str, limit: int) -> Dict:
        """Execute query on collector"""
        try:
            if query_type == "recent":
                # Get recent operations - simplified implementation
                return {"message": "Recent operations query - full implementation needed"}
            elif query_type == "patterns":
                patterns = collector.get_successful_patterns(limit)
                return {
                    "patterns": [
                        {
                            "description": p.description_pattern,
                            "success_count": p.success_count,
                            "failure_count": p.failure_count,
                            "models_used": p.models_used
                        }
                        for p in patterns
                    ]
                }
            elif query_type == "errors":
                errors = collector.get_common_errors(limit)
                return {"errors": errors}
            elif query_type == "performance":
                performance = collector.get_model_performance()
                return {
                    "performance": [
                        {
                            "model": p.model_name,
                            "success_rate": f"{p.success_rate:.2%}",
                            "total_requests": p.total_requests,
                            "successful_requests": p.successful_requests,
                            "failed_requests": p.failed_requests,
                            "average_generation_time": f"{p.average_generation_time:.2f}s"
                        }
                        for p in performance
                    ]
                }
            else:
                return {"error": f"Unknown query type: {query_type}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_get_performance(self, arguments: Dict) -> Dict:
        """Tool: Get model performance"""
        database = arguments.get("database")
        model = arguments.get("model")
        
        if database:
            try:
                db_path = self.base_path / f"{database}_data.db"
                collector = BlenderDataCollector(str(db_path))
                performance = collector.get_model_performance(model)
                collector.close()
                return {"performance": [{"model": p.model_name, "success_rate": f"{p.success_rate:.2%}",
                                       "total_requests": p.total_requests} for p in performance]}
            except Exception as e:
                return {"error": str(e)}
        else:
            # Get from all databases
            all_performance = {}
            for db_name in ["modeling", "shading", "animation", "vfx",
                           "motiongraphics", "rendering", "rigging",
                           "sculpting", "cameraoperator", "videography"]:
                try:
                    db_path = self.base_path / f"{db_name}_data.db"
                    collector = BlenderDataCollector(str(db_path))
                    perf = collector.get_model_performance(model)
                    if perf:
                        all_performance[db_name] = [{"model": p.model_name,
                                                     "success_rate": f"{p.success_rate:.2%}",
                                                     "total_requests": p.total_requests}
                                                    for p in perf]
                    collector.close()
                except:
                    pass
            return {"performance": all_performance}
    
    def _tool_get_patterns(self, arguments: Dict) -> Dict:
        """Tool: Get successful patterns"""
        database = arguments.get("database")
        limit = arguments.get("limit", 10)
        
        if not database:
            return {"error": "Database is required"}
        
        try:
            db_path = self.base_path / f"{database}_data.db"
            collector = BlenderDataCollector(str(db_path))
            patterns = collector.get_successful_patterns(limit)
            collector.close()
            return {
                "patterns": [
                    {
                        "description": p.description_pattern,
                        "success_count": p.success_count,
                        "failure_count": p.failure_count,
                        "models_used": p.models_used,
                        "code_template": p.code_template[:200] + "..." if len(p.code_template) > 200 else p.code_template
                    }
                    for p in patterns
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_list_specialists(self, arguments: Dict) -> Dict:
        """Tool: List specialists"""
        return {
            "specialists": self.coordinator.get_all_specialists(),
            "count": len(self.coordinator.specialists),
            "available_fields": [
                "modeling", "shading", "animation", "vfx",
                "motiongraphics", "rendering", "rigging",
                "sculpting", "cameraoperator", "videography"
            ]
        }
    
    def _tool_load_image(self, arguments: Dict) -> Dict:
        """Tool: Load reference image"""
        image_path = arguments.get("image_path", "")
        if not image_path:
            return {"error": "image_path is required"}
        
        return self.media_handler.load_image(image_path)
    
    def _tool_analyze_image(self, arguments: Dict) -> Dict:
        """Tool: Analyze image with LLM"""
        image_path = arguments.get("image_path", "")
        analysis_type = arguments.get("analysis_type", "scene_description")
        custom_prompt = arguments.get("custom_prompt", "")
        model = arguments.get("model", "llama3.2-vision:latest")
        
        if not image_path:
            return {"error": "image_path is required"}
        
        try:
            if analysis_type == "scene_description":
                return self.media_handler.describe_image_for_blender(image_path)
            elif analysis_type == "materials":
                return self.media_handler.extract_materials_from_image(image_path)
            elif analysis_type == "custom":
                if not custom_prompt:
                    return {"error": "custom_prompt is required for custom analysis"}
                return self.media_handler.analyze_image_with_llm(image_path, custom_prompt, model)
            else:
                return {"error": f"Unknown analysis_type: {analysis_type}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_create_scene_from_image(self, arguments: Dict) -> Dict:
        """Tool: Create scene from reference image"""
        image_path = arguments.get("image_path", "")
        description = arguments.get("description")
        field = arguments.get("field")
        
        if not image_path:
            return {"error": "image_path is required"}
        
        try:
            # Create scene description from image
            result = self.media_handler.create_scene_from_image(image_path, description)
            
            if "error" in result:
                return result
            
            # If successful, use the scene description to create the scene
            scene_description = result.get("scene_description", "")
            if scene_description:
                # Route to appropriate agent
                scene_result = self.coordinator.route_task(scene_description, field)
                return {
                    "image_analysis": result,
                    "scene_creation": scene_result
                }
            
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_load_video(self, arguments: Dict) -> Dict:
        """Tool: Load reference video"""
        video_path = arguments.get("video_path", "")
        if not video_path:
            return {"error": "video_path is required"}
        
        return self.media_handler.load_video(video_path)
    
    def _tool_analyze_video(self, arguments: Dict) -> Dict:
        """Tool: Analyze video"""
        video_path = arguments.get("video_path", "")
        frame_number = arguments.get("frame_number")
        
        if not video_path:
            return {"error": "video_path is required"}
        
        return self.media_handler.analyze_video_for_blender(video_path, frame_number)
    
    def _tool_list_media_files(self, arguments: Dict) -> Dict:
        """Tool: List media files"""
        directory = arguments.get("directory", "")
        media_type = arguments.get("media_type", "all")
        
        if not directory:
            return {"error": "directory is required"}
        
        return self.media_handler.list_media_files(directory, media_type)
    
    def _tool_get_development_proposals(self, arguments: Dict) -> Dict:
        """Tool: Get development proposals from Trends & Innovations Specialist"""
        if not self.trends_specialist:
            return {
                "content": [{
                    "type": "text",
                    "text": "Trends & Innovations Specialist is not available. Please ensure trends_innovations_specialist.py is in the same directory."
                }]
            }
        
        focus_area = arguments.get("focus_area", "general")
        custom_topics = arguments.get("custom_topics")
        use_project_context = arguments.get("use_project_context", True)
        result = self.trends_specialist.get_development_proposals(focus_area, custom_topics, use_project_context)
        
        # Add project context info if available
        context_info = ""
        if self.trends_specialist.current_project_context:
            context_info = f"\n\n*Adapted to project: {self.trends_specialist.current_project_context.get('type', 'unknown')}*"
        
        if result.get("status") == "success":
            return {
                "content": [{
                    "type": "text",
                    "text": f"# Development Proposals ({focus_area})\n\n"
                           f"## Trends Analysis\n\n{result.get('trends_analysis', '')}\n\n"
                           f"## Development Proposals\n\n{result.get('proposals', '')}\n\n"
                           f"*Generated: {result.get('timestamp', '')}*{context_info}"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error getting proposals: {result.get('message', 'Unknown error')}"
                }]
            }
    
    def _tool_set_project_context(self, arguments: Dict) -> Dict:
        """Tool: Set project context for adaptive trend monitoring"""
        if not self.trends_specialist:
            return {
                "content": [{
                    "type": "text",
                    "text": "Trends & Innovations Specialist is not available."
                }]
            }
        
        project_type = arguments.get("project_type")
        project_description = arguments.get("project_description")
        
        if not project_type:
            return {
                "content": [{
                    "type": "text",
                    "text": "Error: project_type is required"
                }]
            }
        
        self.trends_specialist.set_project_context(project_type, project_description)
        
        return {
            "content": [{
                "type": "text",
                "text": f"Project context set to: **{project_type}**\n\n"
                       f"{'Description: ' + project_description if project_description else 'The specialist will now adapt trend monitoring to this project type.'}\n\n"
                       f"Use `get_project_relevant_trends` to get trends automatically adapted to your project."
            }]
        }
    
    def _tool_get_project_relevant_trends(self, arguments: Dict) -> Dict:
        """Tool: Get trends automatically adapted to current project context"""
        if not self.trends_specialist:
            return {
                "content": [{
                    "type": "text",
                    "text": "Trends & Innovations Specialist is not available."
                }]
            }
        
        if not self.trends_specialist.current_project_context:
            return {
                "content": [{
                    "type": "text",
                    "text": "No project context set. Use `set_project_context` first to set your project type, then this tool will automatically monitor relevant trends."
                }]
            }
        
        result = self.trends_specialist.get_project_relevant_trends()
        
        project_type = self.trends_specialist.current_project_context.get("type", "unknown")
        
        if result.get("status") == "success":
            return {
                "content": [{
                    "type": "text",
                    "text": f"# Project-Relevant Trends ({project_type})\n\n"
                           f"*Automatically adapted to your current project*\n\n"
                           f"## Trends Analysis\n\n{result.get('trends_analysis', '')}\n\n"
                           f"## Development Proposals\n\n{result.get('proposals', '')}\n\n"
                           f"*Generated: {result.get('timestamp', '')}*"
                }]
            }
        else:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Error getting trends: {result.get('message', 'Unknown error')}"
                }]
            }
    
    def _handle_resources_list(self, request_id: Any) -> Dict:
        """List all available resources"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": self.resources}
        }
    
    def _handle_resource_read(self, params: Dict, request_id: Any) -> Dict:
        """Read a resource"""
        uri = params.get("uri")
        
        try:
            content = self._read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": "application/json",
                            "text": json.dumps(content, indent=2, default=str)
                        }
                    ]
                }
            }
        except Exception as e:
            self._log_error(f"Resource read error: {e}")
            return self._error_response(request_id, str(e))
    
    def _read_resource(self, uri: str) -> Dict:
        """Read resource content"""
        if uri == "blender://agents/list":
            return {
                "agents": self.coordinator.get_all_specialists(),
                "count": len(self.coordinator.specialists),
                "available_fields": [
                    "modeling", "shading", "animation", "vfx",
                    "motiongraphics", "rendering", "rigging",
                    "sculpting", "cameraoperator", "videography"
                ]
            }
        elif uri == "blender://scene/current":
            if "modeling" in self.coordinator.specialists:
                specialist = self.coordinator.specialists["modeling"]
                return specialist.get_scene_info()
            return {"error": "Scene info not available"}
        elif uri == "blender://media/cached":
            return self.media_handler.get_cached_media()
        elif uri.startswith("blender://database/"):
            parts = uri.split("/")
            if len(parts) >= 4:
                db_name = parts[2]
                resource_type = parts[3]
                
                try:
                    db_path = self.base_path / f"{db_name}_data.db"
                    collector = BlenderDataCollector(str(db_path))
                    
                    if resource_type == "schema":
                        return {
                            "database": db_name,
                            "tables": [
                                "operations",
                                "model_performance",
                                "code_patterns",
                                "error_patterns",
                                "scene_transitions",
                                "blender_api_reference"
                            ]
                        }
                    elif resource_type == "operations":
                        # Return recent operations info
                        return {"message": "Recent operations - full implementation needed"}
                    elif resource_type == "patterns":
                        patterns = collector.get_successful_patterns(10)
                        return {
                            "patterns": [
                                {
                                    "description": p.description_pattern,
                                    "success_count": p.success_count
                                }
                                for p in patterns
                            ]
                        }
                    elif resource_type == "errors":
                        errors = collector.get_common_errors(10)
                        return {"errors": errors}
                    elif resource_type == "performance":
                        performance = collector.get_model_performance()
                        return {
                            "performance": [
                                {
                                    "model": p.model_name,
                                    "success_rate": f"{p.success_rate:.2%}",
                                    "total_requests": p.total_requests
                                }
                                for p in performance
                            ]
                        }
                    
                    collector.close()
                except Exception as e:
                    return {"error": str(e)}
        
        return {"error": f"Unknown resource: {uri}"}
    
    def _handle_prompts_list(self, request_id: Any) -> Dict:
        """List all available prompts"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"prompts": self.prompts}
        }
    
    def _handle_prompt_get(self, params: Dict, request_id: Any) -> Dict:
        """Get a prompt"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            prompt_text = self._generate_prompt(name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "messages": [
                        {
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": prompt_text
                            }
                        }
                    ]
                }
            }
        except Exception as e:
            return self._error_response(request_id, str(e))
    
    def _generate_prompt(self, name: str, arguments: Dict) -> str:
        """Generate prompt text"""
        if name == "create_modeling_scene":
            description = arguments.get("description", "")
            return f"""Create a 3D modeling scene in Blender.

Description: {description}

Use the create_scene tool with field='modeling' to execute this task.

Best practices:
- Use appropriate primitive objects
- Apply modifiers for better topology
- Organize objects with proper naming
- Consider scale and proportions
"""
        elif name == "create_material_setup":
            material_type = arguments.get("material_type", "")
            return f"""Create a complete material setup in Blender.

Material Type: {material_type}

Use the create_scene tool with field='shading' to execute this task.

Steps:
1. Create material with appropriate shader
2. Set up node tree
3. Configure material properties
4. Apply to objects
"""
        elif name == "analyze_performance":
            return """Analyze performance across all databases.

Use the query_database tool with query_type='performance' and database='all' to get performance metrics.

This will show:
- Success rates per model
- Average generation times
- Total requests per database
- Model comparison across domains
"""
        elif name == "find_similar_operations":
            description = arguments.get("description", "")
            database = arguments.get("database", "")
            return f"""Find similar successful operations from history.

Description to match: {description}
Database: {database or "all"}

Use the query_database tool to search for similar operations.
This helps find successful patterns and code examples.
"""
        elif name == "create_scene_from_reference_image":
            image_path = arguments.get("image_path", "")
            field = arguments.get("field", "")
            return f"""Create a 3D scene in Blender from a reference image.

Image Path: {image_path}
Specialist: {field or "auto-detect"}

Workflow:
1. Use analyze_image tool to analyze the reference image
2. Extract scene description using vision model
3. Use create_scene_from_image tool to create the scene
4. The system will automatically route to the appropriate specialist

This workflow uses vision models to understand the image and generate appropriate Blender code.
"""
        else:
            raise ValueError(f"Unknown prompt: {name}")
    
    def _error_response(self, request_id: Any, message: str) -> Dict:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": message
            }
        }
    
    def _log(self, message: str):
        """Log message to stderr"""
        print(f"[MCP Server] {message}", file=sys.stderr)
        sys.stderr.flush()
    
    def _log_error(self, message: str):
        """Log error to stderr"""
        print(f"[MCP Server Error] {message}", file=sys.stderr)
        sys.stderr.flush()
    
    def run_stdio(self):
        """Run server over stdio"""
        self._log("🚀 Blender-Ollama MCP Server Started")
        self._log(f"📋 Registered {len(self.coordinator.specialists)} specialists")
        self._log("📡 Waiting for MCP requests...")
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                self._log("Server stopped by user")
                break
            except Exception as e:
                self._log_error(f"Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
        
        # Cleanup
        self._log("Cleaning up...")
        self.coordinator.cleanup_all()
        self._log("Server stopped")


def main():
    """Main entry point"""
    server = BlenderGeneratorEvolvingTeachingAIAssistant()
    server.run_stdio()


if __name__ == "__main__":
    main()

