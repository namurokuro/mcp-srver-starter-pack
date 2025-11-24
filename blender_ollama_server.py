# blender_ollama_server.py - FINAL WORKING VERSION
import json
import socket
import requests
import sys
import time

class BlenderOllamaBridge:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.blender_host = "localhost"
        self.blender_port = 9876
        # Try alternative models if llama3.2 hits daily limit
        self.model = "gemma3:4b"  # Local model, no daily limits
        self.fallback_models = ["deepseek-r1:8b", "llama3.2:latest"]
    
    def log(self, message):
        """Print debug messages"""
        print(f"[Blender-Ollama] {message}", file=sys.stderr)
        sys.stderr.flush()
    
    def connect_to_blender(self):
        """Connect to Blender socket server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.blender_host, self.blender_port))
            self.log("✅ Connected to Blender")
            return True
        except Exception as e:
            self.log(f"❌ Blender connection failed: {e}")
            return False
    
    def ask_ollama(self, prompt):
        """Ask Ollama to generate Blender code, trying multiple models if needed"""
        system_prompt = """You are a Blender 3D expert. Generate Python code using bpy module.
Return ONLY the code without explanations. Make sure the code is complete and runnable.

Example format:
import bpy
# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
# Create objects
bpy.ops.mesh.primitive_cube_add(location=(0,0,0))"""
        
        # Try primary model first, then fallbacks
        models_to_try = [self.model] + self.fallback_models
        
        for model in models_to_try:
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            }
            
            try:
                self.log(f"🤖 Trying {model} to generate code...")
                response = requests.post(f"{self.ollama_url}/api/generate", 
                                       json=payload, timeout=120)
                
                if response.status_code == 200:
                    result = response.json().get("response", "")
                    self.log(f"✅ Code generated successfully with {model}")
                    
                    # Extract code from response
                    if "```python" in result:
                        result = result.split("```python")[1].split("```")[0]
                    elif "```" in result:
                        result = result.split("```")[1].split("```")[0]
                    
                    return result.strip()
                else:
                    self.log(f"⚠️ {model} returned HTTP {response.status_code}, trying next model...")
                    continue
                    
            except requests.exceptions.Timeout:
                self.log(f"⚠️ {model} timed out, trying next model...")
                continue
            except Exception as e:
                self.log(f"⚠️ {model} error: {str(e)}, trying next model...")
                continue
        
        return f"Error: All models failed. Last error: {str(e) if 'e' in locals() else 'Unknown'}"
    
    def send_to_blender(self, command):
        """Send command to Blender"""
        if not hasattr(self, 'socket') or not self.socket:
            if not self.connect_to_blender():
                return {"status": "error", "message": "Blender not connected"}
        
        try:
            self.socket.send(json.dumps(command).encode())
            response_data = self.socket.recv(65536)
            return json.loads(response_data.decode())
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_scene(self, description):
        """Main function: create scene from description"""
        self.log(f"🎨 Creating scene: {description}")
        
        # Generate code with Ollama
        code = self.ask_ollama(f"Create Blender Python code for: {description}")
        
        if "Error" in code:
            return {"status": "error", "message": code}
        
        self.log("⚡ Executing code in Blender...")
        
        # Execute in Blender (correct format: type + params)
        result = self.send_to_blender({
            "type": "execute_code",
            "params": {
                "code": code
            }
        })
        
        self.log(f"📊 Result: {result.get('status', 'unknown')}")
        return result
    
    def get_scene_info(self):
        """Get current scene information"""
        return self.send_to_blender({"type": "get_scene_info"})

def main():
    bridge = BlenderOllamaBridge()
    bridge.log("🚀 Blender+Ollama MCP Server Started")
    bridge.log("📡 Waiting for commands from Cursor...")
    
    # Simple MCP protocol implementation
    try:
        while True:
            # Read from stdin (Cursor sends commands here)
            line = sys.stdin.readline().strip()
            if not line:
                break
            
            try:
                data = json.loads(line)
                method = data.get("method")
                params = data.get("params", {})
                
                if method == "create_scene":
                    description = params.get("description", "")
                    result = bridge.create_scene(description)
                    response = {"result": result, "error": None}
                    
                elif method == "get_scene_info":
                    result = bridge.get_scene_info()
                    response = {"result": result, "error": None}
                    
                elif method == "tools":
                    # Return available tools
                    tools = [
                        {
                            "name": "create_scene",
                            "description": "Create a 3D scene from text description",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "description": {
                                        "type": "string", 
                                        "description": "Description of the scene to create"
                                    }
                                },
                                "required": ["description"]
                            }
                        },
                        {
                            "name": "get_scene_info",
                            "description": "Get information about the current Blender scene", 
                            "parameters": {
                                "type": "object",
                                "properties": {}
                            }
                        }
                    ]
                    response = {"result": tools, "error": None}
                    
                else:
                    response = {"result": None, "error": f"Unknown method: {method}"}
                
                # Send response back to Cursor
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                # Ignore invalid JSON
                pass
            except Exception as e:
                error_response = {"result": None, "error": str(e)}
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        bridge.log("Server stopped by user")
    except Exception as e:
        bridge.log(f"Server error: {e}")

if __name__ == "__main__":
    main()
