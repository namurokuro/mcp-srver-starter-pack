#!/usr/bin/env python3
"""
Complete server status check
"""

import json
import socket
import sys
from pathlib import Path

def check_blender():
    """Check Blender connection"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(('localhost', 9876))
        
        # Quick test
        command = {"type": "get_scene_info", "params": {}}
        sock.send(json.dumps(command).encode())
        response = sock.recv(65536)
        result = json.loads(response.decode())
        sock.close()
        
        return result.get('status') == 'success'
    except:
        return False

def check_mcp_server():
    """Check MCP server"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from mcp_server import BlenderOllamaMCPServer
        
        server = BlenderOllamaMCPServer()
        
        # Test initialize
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        response = server.handle_request(request)
        return response.get("result", {}).get("serverInfo", {}).get("name") == "blender-ollama-mcp"
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def main():
    print("=" * 70)
    print("MCP SERVER STATUS CHECK")
    print("=" * 70)
    print()
    
    # Check Blender
    print("[CHECK] Blender Connection...")
    blender_ok = check_blender()
    print(f"  {'[OK]' if blender_ok else '[FAIL]'} Blender is {'connected' if blender_ok else 'not connected'}")
    print()
    
    # Check MCP Server
    print("[CHECK] MCP Server...")
    mcp_ok = check_mcp_server()
    print(f"  {'[OK]' if mcp_ok else '[FAIL]'} MCP Server is {'working' if mcp_ok else 'not working'}")
    print()
    
    # Summary
    print("=" * 70)
    print("STATUS SUMMARY")
    print("=" * 70)
    print(f"Blender Connection:  {'[OK] WORKING' if blender_ok else '[FAIL] FAILED'}")
    print(f"MCP Server:          {'[OK] WORKING' if mcp_ok else '[FAIL] FAILED'}")
    print("=" * 70)
    
    if blender_ok and mcp_ok:
        print("\n[SUCCESS] All systems operational!")
        print("\nThe server is ready to use in Cursor.")
        print("If you see errors in Cursor, try:")
        print("  1. Restart Cursor")
        print("  2. Check the MCP server configuration")
        print("  3. Verify the server path in cursor_config.json")
        return 0
    else:
        print("\n[ERROR] Some systems are not working.")
        if not blender_ok:
            print("\nBlender connection failed:")
            print("  - Ensure Blender is running")
            print("  - Check that the socket addon is enabled")
            print("  - Verify port 9876 is available")
        if not mcp_ok:
            print("\nMCP server failed:")
            print("  - Check Python imports")
            print("  - Verify all files are present")
        return 1

if __name__ == "__main__":
    sys.exit(main())

