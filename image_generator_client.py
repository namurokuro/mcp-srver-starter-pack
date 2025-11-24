"""
Image Generation Client for MCP Server
Supports Stable Diffusion, ComfyUI, and other local generators
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import base64
from io import BytesIO

class ImageGeneratorClient:
    """Client for local image generation models"""
    
    def __init__(self):
        self.stable_diffusion_url = "http://stable-diffusion:7860"
        self.comfyui_url = "http://comfyui:8188"
        self.output_dir = Path("output/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def check_stable_diffusion(self) -> bool:
        """Check if Stable Diffusion is available"""
        try:
            response = requests.get(f"{self.stable_diffusion_url}/docs", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def check_comfyui(self) -> bool:
        """Check if ComfyUI is available"""
        try:
            response = requests.get(f"{self.comfyui_url}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_image_stable_diffusion(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        seed: int = -1
    ) -> Dict[str, Any]:
        """
        Generate image using Stable Diffusion
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: What to avoid in the image
            width: Image width
            height: Image height
            steps: Number of diffusion steps
            cfg_scale: Guidance scale
            seed: Random seed (-1 for random)
            
        Returns:
            Dictionary with image path and metadata
        """
        if not self.check_stable_diffusion():
            return {
                "success": False,
                "error": "Stable Diffusion not available"
            }
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler_index": "Euler a"
        }
        
        try:
            response = requests.post(
                f"{self.stable_diffusion_url}/api/v1/txt2img",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                images = result.get("images", [])
                
                if images:
                    # Save image
                    image_data = base64.b64decode(images[0])
                    image_path = self.output_dir / f"generated_{hash(prompt) % 10000}.png"
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    return {
                        "success": True,
                        "image_path": str(image_path),
                        "info": result.get("info", {}),
                        "parameters": result.get("parameters", {})
                    }
            
            return {
                "success": False,
                "error": f"API returned status {response.status_code}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_image_comfyui(
        self,
        prompt: str,
        workflow: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate image using ComfyUI
        
        Args:
            prompt: Text prompt
            workflow: Optional custom workflow JSON
            
        Returns:
            Dictionary with image path and metadata
        """
        if not self.check_comfyui():
            return {
                "success": False,
                "error": "ComfyUI not available"
            }
        
        # Use default workflow if none provided
        if not workflow:
            workflow = self._default_comfyui_workflow(prompt)
        
        try:
            # Submit workflow
            response = requests.post(
                f"{self.comfyui_url}/api/v1/prompt",
                json={"prompt": workflow},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                prompt_id = result.get("prompt_id")
                
                # Poll for result
                # (Simplified - full implementation would poll queue)
                return {
                    "success": True,
                    "prompt_id": prompt_id,
                    "message": "Workflow submitted to ComfyUI"
                }
            
            return {
                "success": False,
                "error": f"API returned status {response.status_code}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _default_comfyui_workflow(self, prompt: str) -> Dict:
        """Generate default ComfyUI workflow"""
        return {
            "1": {
                "inputs": {
                    "text": prompt
                },
                "class_type": "CLIPTextEncode"
            }
            # Simplified - full workflow would be more complex
        }
    
    def list_available_models(self) -> Dict[str, bool]:
        """List which generators are available"""
        return {
            "stable_diffusion": self.check_stable_diffusion(),
            "comfyui": self.check_comfyui()
        }

def generate_image(prompt: str, **kwargs) -> Dict[str, Any]:
    """Convenience function to generate image"""
    client = ImageGeneratorClient()
    return client.generate_image_stable_diffusion(prompt, **kwargs)

if __name__ == "__main__":
    # Test the client
    client = ImageGeneratorClient()
    
    print("Checking available generators...")
    available = client.list_available_models()
    for name, status in available.items():
        print(f"  {name}: {'✅ Available' if status else '❌ Not available'}")
    
    if available.get("stable_diffusion"):
        print("\nTesting Stable Diffusion...")
        result = client.generate_image_stable_diffusion(
            "a beautiful landscape with mountains and a lake"
        )
        if result.get("success"):
            print(f"✅ Image generated: {result['image_path']}")
        else:
            print(f"❌ Error: {result.get('error')}")

