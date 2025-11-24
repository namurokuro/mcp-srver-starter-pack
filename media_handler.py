#!/usr/bin/env python3
"""
Media Handler for Reference Images and Videos
Handles loading, analysis, and processing of reference media
"""

import json
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import mimetypes


class MediaHandler:
    """Handle reference images and videos"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.media_cache = {}
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
    
    def load_image(self, image_path: str) -> Dict:
        """Load and encode image for analysis"""
        path = Path(image_path)
        
        if not path.exists():
            return {"error": f"Image not found: {image_path}"}
        
        if path.suffix.lower() not in self.supported_image_formats:
            return {"error": f"Unsupported image format: {path.suffix}"}
        
        try:
            # Read image as base64
            with open(path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Get image info
            file_size = path.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(path))
            
            # Cache the image
            self.media_cache[str(path)] = {
                "type": "image",
                "path": str(path),
                "base64": image_base64,
                "size": file_size,
                "mime_type": mime_type
            }
            
            return {
                "success": True,
                "path": str(path),
                "size": file_size,
                "mime_type": mime_type,
                "format": path.suffix.lower()
            }
        except Exception as e:
            return {"error": f"Failed to load image: {str(e)}"}
    
    def analyze_image_with_llm(self, image_path: str, prompt: str, model: str = "llama3.2-vision:latest") -> Dict:
        """Analyze image using Ollama vision model"""
        # Load image first
        image_info = self.load_image(image_path)
        if "error" in image_info:
            return image_info
        
        # Get cached image data
        cached = self.media_cache.get(image_path)
        if not cached:
            return {"error": "Image not loaded"}
        
        try:
            # Use Ollama vision API
            payload = {
                "model": model,
                "prompt": prompt,
                "images": [cached["base64"]],
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "analysis": result.get("response", ""),
                    "model": model,
                    "image_path": image_path
                }
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to analyze image: {str(e)}"}
    
    def describe_image_for_blender(self, image_path: str) -> Dict:
        """Get detailed description of image for Blender scene creation"""
        prompt = """Analyze this image and provide a detailed description suitable for creating a 3D scene in Blender.

Include:
- Main objects and their positions
- Colors and materials
- Lighting conditions
- Camera angle/perspective
- Overall composition
- Any specific details that would help recreate this scene in 3D

Format the description as a natural language prompt for 3D scene creation."""
        
        return self.analyze_image_with_llm(image_path, prompt)
    
    def extract_materials_from_image(self, image_path: str) -> Dict:
        """Extract material properties from image"""
        prompt = """Analyze this image and identify material properties that would be useful for Blender material creation.

For each visible material, describe:
- Base color/reflectance
- Roughness (glossy/matte)
- Metallic properties
- Transparency/opacity
- Texture patterns
- Surface details

Format as a structured description for Blender material setup."""
        
        return self.analyze_image_with_llm(image_path, prompt)
    
    def load_video(self, video_path: str) -> Dict:
        """Load video file information"""
        path = Path(video_path)
        
        if not path.exists():
            return {"error": f"Video not found: {video_path}"}
        
        if path.suffix.lower() not in self.supported_video_formats:
            return {"error": f"Unsupported video format: {path.suffix}"}
        
        try:
            file_size = path.stat().st_size
            mime_type, _ = mimetypes.guess_type(str(path))
            
            # Cache video info
            self.media_cache[str(path)] = {
                "type": "video",
                "path": str(path),
                "size": file_size,
                "mime_type": mime_type
            }
            
            return {
                "success": True,
                "path": str(path),
                "size": file_size,
                "mime_type": mime_type,
                "format": path.suffix.lower()
            }
        except Exception as e:
            return {"error": f"Failed to load video: {str(e)}"}
    
    def analyze_video_for_blender(self, video_path: str, frame_number: Optional[int] = None) -> Dict:
        """Analyze video for Blender scene creation"""
        # For now, return video info
        # Full video analysis would require frame extraction
        video_info = self.load_video(video_path)
        if "error" in video_info:
            return video_info
        
        return {
            "success": True,
            "video_path": video_path,
            "message": "Video loaded. Use frame extraction for detailed analysis.",
            "note": "For detailed analysis, extract frames first using extract_video_frame"
        }
    
    def create_scene_from_image(self, image_path: str, description: Optional[str] = None) -> Dict:
        """Create Blender scene based on reference image"""
        # Analyze image
        if description:
            analysis = self.analyze_image_with_llm(
                image_path,
                f"Based on this image, {description}. Provide detailed 3D scene description."
            )
        else:
            analysis = self.describe_image_for_blender(image_path)
        
        if "error" in analysis:
            return analysis
        
        return {
            "success": True,
            "image_path": image_path,
            "scene_description": analysis.get("analysis", ""),
            "model_used": analysis.get("model", ""),
            "next_step": "Use create_scene tool with the scene_description"
        }
    
    def list_media_files(self, directory: str, media_type: str = "all") -> Dict:
        """List available media files in directory"""
        path = Path(directory)
        
        if not path.exists():
            return {"error": f"Directory not found: {directory}"}
        
        if not path.is_dir():
            return {"error": f"Not a directory: {directory}"}
        
        try:
            files = []
            
            if media_type in ["all", "image"]:
                for ext in self.supported_image_formats:
                    files.extend(path.glob(f"*{ext}"))
                    files.extend(path.glob(f"*{ext.upper()}"))
            
            if media_type in ["all", "video"]:
                for ext in self.supported_video_formats:
                    files.extend(path.glob(f"*{ext}"))
                    files.extend(path.glob(f"*{ext.upper()}"))
            
            return {
                "success": True,
                "directory": str(path),
                "media_type": media_type,
                "files": [
                    {
                        "path": str(f),
                        "name": f.name,
                        "size": f.stat().st_size,
                        "type": "image" if f.suffix.lower() in self.supported_image_formats else "video"
                    }
                    for f in files
                ],
                "count": len(files)
            }
        except Exception as e:
            return {"error": f"Failed to list files: {str(e)}"}
    
    def get_cached_media(self) -> Dict:
        """Get list of cached media files"""
        return {
            "cached_files": [
                {
                    "path": info["path"],
                    "type": info["type"],
                    "size": info.get("size", 0)
                }
                for info in self.media_cache.values()
            ],
            "count": len(self.media_cache)
        }

