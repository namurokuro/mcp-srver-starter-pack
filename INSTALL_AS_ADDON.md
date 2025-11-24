# Install MCP Server as Blender Addon

## Quick Installation

### Method 1: Install from ZIP (Easiest)

1. **Open Blender**
2. **Edit > Preferences > Add-ons**
3. **Click "Install..."** button (top right)
4. **Select**: `mcp_server_addon_20251124.zip`
   - Location: `F:\mcp server\mcp_server_addon_20251124.zip`
5. **Search for**: "MCP Server" in the addon list
6. **Enable** the addon (check the checkbox)
7. **Done!** ✓

### Method 2: Install from GitHub ZIP

1. **Download from GitHub:**
   - Go to: https://github.com/namurokuro/mcp-srver-starter-pack
   - Click **"Code"** → **"Download ZIP"**
   - Extract the ZIP

2. **Create addon ZIP:**
   - The repository contains all files
   - You need to create a ZIP with `__init__.py` in the root
   - Or use the pre-made ZIP: `mcp_server_addon_20251124.zip`

3. **Install in Blender:**
   - Edit > Preferences > Add-ons
   - Install... > Select the ZIP file
   - Enable the addon

### Method 3: Manual Installation

1. **Copy addon folder:**
   - Copy `mcp_server_addon` folder to Blender's addons directory:
   - Windows: `%APPDATA%\Blender Foundation\Blender\[version]\scripts\addons\`
   - Or find it: `Edit > Preferences > File Paths > Scripts`

2. **Enable in Blender:**
   - Edit > Preferences > Add-ons
   - Search for "MCP Server"
   - Enable the addon

## After Installation

### Access the Addon

1. **Open 3D Viewport**
2. **Press `N`** to open the sidebar (or click the `>` arrow on the right)
3. **Look for "MCP" tab** at the top of the sidebar
4. **Click the "MCP" tab**

### Use the Panel

The MCP panel provides:
- **Status** - Check if MCP server is loaded
- **Quick Actions**:
  - Test Import - Verify modules are working
  - List Agents - See available agents
  - Check Status - Full system check

### Use in Python

After installation, you can use MCP server in any Blender script:

```python
# The addon automatically adds the path
from specialized_agents import ModelingSpecialist

agent = ModelingSpecialist()
result = agent.create_scene("Create a red cube")
```

## Verification

After installation, test it:

1. **Open MCP panel** (View3D sidebar > MCP tab)
2. **Click "Test Import"** button
3. **Check console** for success message
4. **Click "Check Status"** for detailed information

## Troubleshooting

### Addon doesn't appear
- Check that `__init__.py` is in the addon folder
- Verify the folder structure is correct
- Check Blender console for errors

### Import errors
- Click "Check Status" in the MCP panel
- Check console for specific error messages
- Verify all files are in the addon directory

### Panel not showing
- Make sure addon is enabled
- Check View3D workspace (not other workspaces)
- Press `N` to toggle sidebar if hidden

## Files Included

The addon includes:
- ✓ Core MCP server (`mcp_server.py`)
- ✓ All specialized agents
- ✓ AI generators
- ✓ All tool files
- ✓ Architecture documentation
- ✓ Configuration files

## Next Steps

After installation:
1. ✓ Test the addon (use panel buttons)
2. ✓ Try creating a scene with agents
3. ✓ Explore the documentation
4. ✓ Use in your projects!

