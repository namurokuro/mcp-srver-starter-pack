#!/usr/bin/env python3
"""
Start MCP Server with full initialization and health checks
"""

import sys
import os
from pathlib import Path

def check_prerequisites():
    """Check all prerequisites before starting"""
    print("=" * 70)
    print("MCP SERVER - PREREQUISITE CHECK")
    print("=" * 70)
    print()
    
    checks = {
        "Python": False,
        "Blender Connection": False,
        "Ollama": False,
        "Required Files": False,
        "Database Access": False
    }
    
    # Check Python
    try:
        import sys
        print(f"[OK] Python {sys.version.split()[0]}")
        checks["Python"] = True
    except:
        print("[FAIL] Python not available")
    
    # Check required files
    required_files = [
        "mcp_server.py",
        "specialized_agents.py",
        "data_collector.py",
        "media_handler.py"
    ]
    
    missing_files = []
    for file in required_files:
        if (Path(__file__).parent / file).exists():
            print(f"[OK] {file}")
        else:
            print(f"[FAIL] {file} not found")
            missing_files.append(file)
    
    if not missing_files:
        checks["Required Files"] = True
    
    # Check Blender connection
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 9876))
        sock.close()
        if result == 0:
            print("[OK] Blender connection available")
            checks["Blender Connection"] = True
        else:
            print("[WARN] Blender not connected (will work but scene operations will fail)")
    except:
        print("[WARN] Could not check Blender connection")
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"[OK] Ollama running ({len(models)} models available)")
            checks["Ollama"] = True
        else:
            print("[WARN] Ollama not responding")
    except:
        print("[WARN] Ollama not available (vision features will not work)")
    
    # Check database access
    try:
        base_path = Path(os.getenv("BLENDER_OLLAMA_PATH", r"C:\Users\User\Desktop\blender-ollama"))
        if base_path.exists():
            db_files = list(base_path.glob("*_data.db"))
            print(f"[OK] Database access ({len(db_files)} databases found)")
            checks["Database Access"] = True
        else:
            print(f"[WARN] Database path not found: {base_path}")
    except Exception as e:
        print(f"[WARN] Database check failed: {e}")
    
    print()
    print("=" * 70)
    print("CHECK SUMMARY")
    print("=" * 70)
    for check, status in checks.items():
        status_str = "[OK]" if status else "[WARN]"
        print(f"{status_str} {check}")
    print("=" * 70)
    print()
    
    return all(checks.values()) or checks["Python"] and checks["Required Files"]

def start_server():
    """Start the MCP server"""
    print("=" * 70)
    print("STARTING BLENDER-OLLAMA MCP SERVER")
    print("=" * 70)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("[WARN] Some prerequisites missing, but continuing...")
        print()
    
    # Import and start server
    try:
        from mcp_server import BlenderOllamaMCPServer
        
        print("[INFO] Initializing server...")
        server = BlenderOllamaMCPServer()
        
        print("[INFO] Server initialized successfully")
        print("[INFO] Starting stdio transport...")
        print()
        print("=" * 70)
        print("SERVER READY - Waiting for MCP requests")
        print("=" * 70)
        print()
        
        # Start server
        server.run_stdio()
        
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_server()

