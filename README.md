# Blender Evolving MCP generator

Model Context Protocol (MCP) server for integrating Blender-Ollama system with Cursor.

> 📚 **Repository Index**: See [REPOSITORY.md](REPOSITORY.md) for complete documentation index and navigation guide.

## Overview

This MCP server exposes the Blender-Ollama specialized agent system to Cursor, allowing you to:
- Keep a constantly evolving workspace that individuals can tailor to their own pipelines—use the Starter Pack deliverables as stable references while experimenting freely with learning workflows, AI generators, or new agent behaviors.
- Create 3D scenes in Blender via natural language
- Query operation history from 11 specialized databases
- Access code patterns and performance metrics
- Use 14 specialized agents for different Blender domains
- **Monitor all agent activities in real-time via web viewport** (see [AGENT_VIEWPORT.md](AGENT_VIEWPORT.md))

### Starter Pack (AI-ready)

Need a lightweight bundle for onboarding, demos, or source sharing? Regenerate the curated Starter Pack anytime:

1. `python build_starter_pack.py`
2. Use the `starter_pack/` folder as the upload artifact (Git, ZIP, etc.).

The Starter Pack keeps:
- Final/future-proof documentation (all `FINAL_*`, `COMPLETE_*`, `READY*` files)
- AI generator entrypoints such as `finalize_vape_ad.py` and `render_final.py`
- Ready-to-run configs (`cursor_mcp_config_ready.json`, Docker-ready equivalent)

Together those files represent the full functionality showcase—users can study the docs, run the generator scripts, or extend them with their own models without needing the rest of the experimental workspace.

## Architecture

```
Cursor → MCP Server (stdio) → Agent Coordinator → Specialized Agents → Blender
                                              ↓
                                        11 SQLite Databases
                                         ↓
                              Agent Activity Tracker → Viewport Server (Web)
```

### Agent Activity Viewport

Monitor all agent activities in real-time through a web-based dashboard:
- **Start viewport**: `start_viewport.bat` (Windows) or `./start_viewport.sh` (Linux/Mac)
- **Access dashboard**: http://localhost:5000
- See real-time agent status, operations, progress, and activity logs
- Full documentation: [AGENT_VIEWPORT.md](AGENT_VIEWPORT.md)

## Installation

### Option 1: Direct Installation (Recommended for Development)

1. Ensure the parent `blender-ollama` directory is accessible
2. The server automatically imports from the parent directory
3. Install dependencies: `pip install -r requirements.txt`

### Option 2: Docker Installation (Recommended for Production)

1. **Prerequisites**: Docker and Docker Compose installed
2. **Migrate from direct installation**: `migrate-to-docker.bat` (Windows)
3. **Start services**: `docker-start.bat` (Windows) or `./docker-start.sh` (Linux/Mac)
4. **Pull Ollama models**: `docker-pull-models.bat`
5. **Check status**: `docker-status.bat`

For detailed Docker setup, see:
- [MIGRATE_TO_DOCKER.md](MIGRATE_TO_DOCKER.md) - **Migration guide** (start here!)
- [DOCKER_README.md](DOCKER_README.md) - Quick start guide
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Complete documentation

## Configuration

### Cursor Configuration

Add to your Cursor settings (`.cursor/mcp.json` or Cursor settings):

```json
{
  "mcpServers": {
    "blender-ollama": {
      "command": "python",
      "args": [
        "F:/mcp server/mcp_server.py"
      ],
      "env": {
        "OLLAMA_URL": "http://localhost:11434",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Available Tools

### 1. `create_scene`
Create a 3D scene in Blender from natural language description.

**Parameters:**
- `description` (required): Natural language description
- `field` (optional): Specialist agent to use

**Example:**
```json
{
  "name": "create_scene",
  "arguments": {
    "description": "Create a red cube on a blue plane",
    "field": "modeling"
  }
}
```

### 2. `get_scene_info`
Get current Blender scene information.

### 3. `execute_blender_code`
Execute Python code directly in Blender.

### 4. `query_database`
Query operation history, patterns, errors, or performance.

**Parameters:**
- `database`: Which database to query (or "all")
- `query_type`: "recent", "patterns", "errors", or "performance"
- `limit`: Maximum results

### 5. `get_model_performance`
Get LLM model performance metrics.

### 6. `get_successful_patterns`
Get successful code generation patterns.

### 7. `list_specialists`
List all available specialist agents.

### 8. `get_development_proposals`
Get development proposals based on current trends and innovations. Monitors trends in Blender, AI, video editing, fashion, furniture, TikTok, Instagram, gaming, and other project-relevant areas. Automatically adapts to your current project context.

**Parameters**:
- `focus_area` (optional): "general", "blender", "ai", "tech", "video", "fashion", "furniture", "tiktok", "instagram", "gaming", or "custom"
- `custom_topics` (optional): Array of custom topics for project-specific analysis
- `use_project_context` (optional): Use current project context to adapt proposals (default: true)

### 9. `set_project_context`
Set your current project context so trend monitoring adapts to your specific project type.

**Parameters**:
- `project_type` (required): "fashion", "furniture", "video", "tiktok", "instagram", "gaming", "blender", "3d", "modeling", or "custom"
- `project_description` (optional): Description of your project

### 10. `get_project_relevant_trends`
Get trends automatically adapted to your current project context. No parameters needed - uses your set project context.

## Available Resources

Resources provide read-only access to data:

- `blender://database/{field}/schema` - Database schema
- `blender://database/{field}/operations` - Recent operations
- `blender://database/{field}/patterns` - Code patterns
- `blender://database/{field}/errors` - Error patterns
- `blender://database/{field}/performance` - Performance metrics
- `blender://scene/current` - Current Blender scene
- `blender://agents/list` - Available agents

## Available Prompts

- `create_modeling_scene` - Create modeling scene workflow
- `create_material_setup` - Material setup workflow
- `analyze_performance` - Performance analysis workflow
- `find_similar_operations` - Find similar operations

## Testing

### Using MCP Inspector

```bash
npx @modelcontextprotocol/inspector python "F:/mcp server/mcp_server.py"
```

### Manual Testing

```bash
python "F:/mcp server/mcp_server.py"
```

Then send JSON-RPC requests via stdin.

## Specialized Agents

The server routes tasks to 10 specialized agents:

1. **Modeling** - 3D modeling and mesh operations
2. **Shading** - Materials and shaders (includes Sanctus Library procedural shaders support)
3. **Animation** - Animation and keyframes
4. **VFX** - Visual effects and simulations
5. **Motion Graphics** - Text and motion graphics
6. **Rendering** - Rendering and export
7. **Rigging** - Armatures and rigging
8. **Sculpting** - Digital sculpting
9. **Camera Operator** - Camera operations
10. **Videography** - Video editing

## Databases

Each agent maintains its own SQLite database:

- `modeling_data.db`
- `shading_data.db`
- `animation_data.db`
- `vfx_data.db`
- `motiongraphics_data.db`
- `rendering_data.db`
- `rigging_data.db`
- `sculpting_data.db`
- `cameraoperator_data.db`
- `videography_data.db`

## Troubleshooting

### Import Errors
- Ensure the parent `blender-ollama` directory is accessible
- Check that `specialized_agents.py` and `data_collector.py` exist
- Verify Python path includes the parent directory

### Connection Errors
- Ensure Ollama is running on `localhost:11434`
- Ensure Blender addon is running on `localhost:9876`
- Check firewall settings

### Database Errors
- Ensure database files exist in the parent directory
- Check file permissions
- Verify database paths are correct

## Sanctus Library Integration

The Shading agent now supports **Sanctus Library** procedural shaders collection, providing access to 690+ high-quality procedural materials.

### Installation

1. Purchase and download Sanctus Library from:
   https://superhivemarket.com/products/sanctus-library-addon---procedural-shaders-collection-for-blender/

2. Install in Blender:
   - Edit > Preferences > Add-ons
   - Click "Install..." and select the Sanctus Library .zip file
   - Enable the addon

3. Access materials through Asset Browser (Shift+A) or use the Python API

### Usage

**Via MCP Server:**
```json
{
  "name": "create_scene",
  "arguments": {
    "description": "Apply Sanctus Library metal material to cube",
    "field": "shading"
  }
}
```

**Via Python Script:**
```python
from sanctus_library_tools import apply_sanctus_material_to_object

# Apply material to object
result = apply_sanctus_material_to_object("Cube", "MetalMaterial")
```

**Example Scripts:**
- `use_sanctus_library.py` - Check installation and list materials
- `example_sanctus_materials.py` - Create scene with Sanctus materials

### Available Functions

The `sanctus_library_tools.py` module provides:
- `check_sanctus_installed()` - Check if addon is installed
- `apply_sanctus_material_to_object()` - Apply material to object
- `get_sanctus_materials()` - List available materials
- `get_sanctus_material_categories()` - Get material categories
- Code generation functions for programmatic material application

## References

### Protocol & Integration
- [Cursor MCP Server Guide](https://cursor.com/docs/cookbook/building-mcp-server) - Building MCP servers for Cursor
- [MCP Protocol Specification](https://modelcontextprotocol.io) - Model Context Protocol specification

### Blender Documentation
- [Blender Python API](https://docs.blender.org/api/current/) - Official Blender Python API reference
- [Blender Developer Documentation](https://developer.blender.org/docs/) - Blender development handbook and architecture
- [Blender Features Documentation](https://developer.blender.org/docs/features/) - Design and implementation of Blender features
- [Blender Projects](https://projects.blender.org/) - Blender source code, issues, and development platform
- [Blender Developer Forum](https://devtalk.blender.org/) - Community forum for Blender developers
- [Blender Release Notes](https://developer.blender.org/docs/releases/) - API changes and compatibility notes

## License

Same as parent Blender-Ollama project.

