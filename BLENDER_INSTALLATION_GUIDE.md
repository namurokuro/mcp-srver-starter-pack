# Blender Installation Guide - Full Repository Integration

This guide will help you install and set up the complete MCP server repository in Blender.

## Quick Installation

### Method 1: Direct Script Installation (Easiest)

1. **Open Blender**
2. **Go to Scripting workspace** (top menu)
3. **Open the installation script:**
   ```
   File > Open > Navigate to: F:\mcp server\install_in_blender.py
   ```
4. **Click "Run Script"** button
5. **Check the console output** for installation status

### Method 2: Manual Setup

#### Step 1: Add MCP Server to Blender Python Path

In Blender's Scripting workspace, run:

```python
import sys
sys.path.insert(0, r"F:\mcp server")
```

#### Step 2: Test the Connection

Run this in Blender's console:

```python
from specialized_agents import BaseBlenderSpecialist
print("MCP Server imported successfully!")
```

## Socket Server Setup (Optional - for remote control)

If you want the MCP server to control Blender remotely:

### Option A: Use Built-in Socket Server (if available)

1. **Edit > Preferences > Add-ons**
2. **Search for**: "socket" or "server"
3. **Enable** the socket server addon
4. **Configure** to listen on `localhost:9876`
5. **Start** the server

### Option B: Install Socket Server Addon

1. Download a Blender socket server addon (e.g., from GitHub)
2. **Edit > Preferences > Add-ons > Install...**
3. Select the addon `.zip` file
4. **Enable** the addon
5. **Configure** port to `9876`

### Option C: Direct Script Execution (No Socket Needed)

You can run scripts directly in Blender without a socket server:

1. **Scripting workspace**
2. **File > Open** any script from `F:\mcp server\`
3. **Click "Run Script"**

## Testing the Installation

### Test 1: Import Test

In Blender Scripting workspace, run:

```python
import sys
sys.path.insert(0, r"F:\mcp server")

from specialized_agents import ModelingSpecialist
agent = ModelingSpecialist()
print("✓ Agent created successfully")
```

### Test 2: Execute Code Test

```python
import sys
sys.path.insert(0, r"F:\mcp server")

from specialized_agents import ModelingSpecialist
agent = ModelingSpecialist()

# Test code execution
code = "import bpy; print('Blender version:', bpy.app.version_string)"
result = agent.execute_code(code)
print("Result:", result)
```

### Test 3: Full Connection Test

From command line (outside Blender):

```bash
cd "F:\mcp server"
python test_blender_connection_full.py
```

## Using the MCP Server

### Method 1: Via MCP Protocol (Cursor/Claude Desktop)

1. **Start the MCP server:**
   ```bash
   python start_server.py
   ```

2. **Configure Cursor** (or your MCP client):
   ```json
   {
     "mcpServers": {
       "blender-ollama": {
         "command": "python",
         "args": ["F:/mcp server/mcp_server.py"],
         "env": {
           "BLENDER_HOST": "localhost",
           "BLENDER_PORT": "9876"
         }
       }
     }
   }
   ```

### Method 2: Direct Python Scripts

Run any script directly in Blender:

1. **Scripting workspace**
2. **File > Open**
3. Select script (e.g., `setup_and_test_addons.py`)
4. **Run Script**

### Method 3: Via Specialized Agents

```python
import sys
sys.path.insert(0, r"F:\mcp server")

from specialized_agents import ModelingSpecialist, ShadingSpecialist

# Use modeling agent
modeling = ModelingSpecialist()
result = modeling.create_scene("Create a red cube")

# Use shading agent
shading = ShadingSpecialist()
result = shading.create_scene("Apply metal material to cube")
```

## Available Scripts

All scripts in `F:\mcp server\` can be run directly in Blender:

- `setup_and_test_addons.py` - Test all addons
- `run_fullscale_test.py` - Full functionality test
- `detect_and_list_addons.py` - List installed addons
- `create_bedroom_scene.py` - Example scene creation
- And many more...

## Troubleshooting

### Issue: "Module not found"

**Solution:** Make sure you've added the path:
```python
import sys
sys.path.insert(0, r"F:\mcp server")
```

### Issue: "Connection refused"

**Solution:** 
- Check if socket server is enabled in Blender
- Verify it's listening on port 9876
- Or use direct script execution instead

### Issue: "Import error"

**Solution:**
- Check that all files exist in `F:\mcp server\`
- Verify Python version compatibility
- Check console for detailed error messages

## Next Steps

1. ✅ Installation complete
2. ✅ Test the connection
3. ✅ Try running example scripts
4. ✅ Explore specialized agents
5. ✅ Start creating scenes!

## Support

For issues or questions:
- Check `README.md` for general information
- Check `CURSOR_TROUBLESHOOTING.md` for MCP-specific issues
- Review `ARCHITECTURE.md` for system overview

