# Blender-Ollama MCP Server Architecture

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CURSOR IDE                                     │
│                    (User Interface & Commands)                           │
└────────────────────────────┬────────────────────────────────────────────┘
                              │
                              │ JSON-RPC 2.0 (stdio)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    MCP SERVER (mcp_server.py)                            │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  • Tool Handlers (create_scene, get_scene_info, etc.)           │   │
│  │  • Resource Handlers (database schemas, scene state, etc.)      │   │
│  │  • Prompt Templates (common workflows)                           │   │
│  │  • Request Router (JSON-RPC → Tool/Resource/Prompt)             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────┬───────────────────────┬──────────────────────┬────────────┘
             │                       │                      │
             │                       │                      │
             ▼                       ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │   AGENT      │      │     MEDIA    │      │     DATA     │
    │ COORDINATOR  │      │   HANDLER    │      │  COLLECTOR   │
    └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
           │                     │                      │
           │                     │                      │
           ▼                     ▼                      ▼
┌──────────────────────┐  ┌──────────────┐    ┌──────────────────────┐
│  SPECIALIZED AGENTS  │  │   OLLAMA    │    │   SQLITE DATABASES   │
│  (10 Specialists)    │  │  (Vision)   │    │  (11 Databases)      │
└──────────┬───────────┘  └──────────────┘    └──────────────────────┘
           │
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BLENDER SOCKET SERVER                                │
│                    (Port 9876 - Python Addon)                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  • execute_code() - Runs Python code in Blender                │   │
│  │  • get_scene_info() - Returns scene state                       │   │
│  │  • TCP Socket Communication                                     │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     BLENDER     │
                    │   (3D Software) │
                    └─────────────────┘
```

## 📊 Component Details

### 1. **MCP Server** (`mcp_server.py`)
**Role:** Main entry point, handles all Cursor communication

**Responsibilities:**
- Receives JSON-RPC 2.0 requests from Cursor
- Routes requests to appropriate handlers (tools/resources/prompts)
- Formats responses back to Cursor
- Manages server lifecycle

**Key Components:**
```
MCP Server
├── Tool Definitions (13 tools)
│   ├── create_scene
│   ├── get_scene_info
│   ├── query_database
│   ├── list_specialists
│   ├── load_reference_image
│   ├── analyze_image
│   ├── create_scene_from_image
│   ├── load_reference_video
│   ├── analyze_video
│   └── list_media_files
├── Resource Definitions (53 resources)
│   ├── Database schemas (10 specialists × 5 types)
│   ├── Scene state
│   ├── Agent list
│   └── Cached media
└── Prompt Templates
    └── Common workflows
```

### 2. **Agent Coordinator** (`specialized_agents.py`)
**Role:** Routes user requests to the appropriate specialist

**Architecture:**
```
Agent Coordinator
│
├── Routing Logic
│   └── Analyzes request → Selects best specialist
│
└── 10 Specialized Agents
    ├── ModelingSpecialist
    ├── ShadingSpecialist
    ├── AnimationSpecialist
    ├── VFXSpecialist
    ├── MotionGraphicsSpecialist
    ├── RenderingSpecialist
    ├── RiggingSpecialist
    ├── SculptingSpecialist
    ├── CameraOperatorSpecialist
    └── VideographySpecialist
```

**How It Works:**
1. User request: "Create a red cube"
2. Coordinator analyzes keywords: "cube" → Modeling
3. Routes to `ModelingSpecialist`
4. Specialist generates Blender Python code
5. Code sent to Blender via socket

### 3. **Specialized Agents** (10 Domain Experts)

Each agent has:
- **Domain Knowledge:** Specialized prompts for their field
- **Code Generation:** Uses Ollama LLM to generate Blender Python
- **Data Collector:** Records operations to their database
- **Learning:** Improves over time from recorded patterns

**Example - Modeling Specialist:**
```
ModelingSpecialist
├── Domain: 3D modeling, meshes, geometry
├── Prompt: "You are a Blender modeling expert..."
├── Database: modeling_data.db
├── Generates: bpy.ops.mesh.primitive_cube_add()...
└── Records: Operation patterns, success rates
```

### 4. **Data Collector** (`data_collector.py`)
**Role:** Records all operations for learning and analysis

**Database Structure:**
```
11 SQLite Databases:
├── blender_data.db (Main operations log)
└── 10 Specialist Databases:
    ├── modeling_data.db
    ├── shading_data.db
    ├── animation_data.db
    ├── vfx_data.db
    ├── motiongraphics_data.db
    ├── rendering_data.db
    ├── rigging_data.db
    ├── sculpting_data.db
    ├── cameraoperator_data.db
    └── videography_data.db

Each Database Contains:
├── operations (what was done)
├── model_performance (LLM accuracy)
├── code_patterns (common code snippets)
├── error_patterns (what went wrong)
├── scene_transitions (state changes)
└── api_reference (Blender API usage)
```

### 5. **Media Handler** (`media_handler.py`)
**Role:** Processes reference images and videos

**Workflow:**
```
Media Handler
│
├── Load Image/Video
│   └── Saves to cache directory
│
├── Analyze with Ollama Vision
│   └── Uses vision-capable models (e.g., llava)
│
└── Generate Scene from Analysis
    └── Creates Blender scene based on image content
```

**Supported Formats:**
- Images: JPG, PNG, WEBP
- Videos: MP4, AVI, MOV

### 6. **Blender Socket Server** (Python Addon)
**Role:** Bridge between MCP server and Blender

**Communication:**
```
MCP Server → TCP Socket (localhost:9876) → Blender Addon
                                              │
                                              ▼
                                         Blender Python API
```

**Commands:**
- `execute_code`: Runs Python code in Blender context
- `get_scene_info`: Returns current scene state

### 7. **Ollama LLM** (Local AI)
**Role:** Generates Blender Python code

**Usage:**
```
Agent → Ollama API (localhost:11434)
         │
         ├── Text Generation (code creation)
         └── Vision Analysis (image/video understanding)
```

**Models Used:**
- Code generation: `llama3`, `codellama`, etc.
- Vision: `llava`, `bakllava` (for image analysis)

## 🔄 Data Flow

### Scene Creation Flow:
```
1. User: "Create a red cube"
   │
   ▼
2. Cursor → MCP Server (JSON-RPC)
   │
   ▼
3. MCP Server → Agent Coordinator
   │
   ▼
4. Coordinator → ModelingSpecialist
   │
   ▼
5. Specialist → Ollama LLM
   │
   ├── Generates: bpy.ops.mesh.primitive_cube_add()
   │              bpy.data.materials.new("Red")
   │              ...
   │
   ▼
6. Specialist → Blender Socket Server
   │
   ▼
7. Blender executes code
   │
   ▼
8. Data Collector records operation
   │
   ├── → modeling_data.db
   └── → blender_data.db
   │
   ▼
9. Response → MCP Server → Cursor
```

### Image Analysis Flow:
```
1. User: "Load this image and create scene"
   │
   ▼
2. MCP Server → Media Handler
   │
   ├── Loads image file
   ├── Caches locally
   │
   ▼
3. Media Handler → Ollama Vision Model
   │
   ├── Analyzes image content
   ├── Describes objects, colors, layout
   │
   ▼
4. Analysis → Agent Coordinator
   │
   ▼
5. Coordinator → Appropriate Specialist(s)
   │
   ├── Generates Blender code
   ├── Based on image analysis
   │
   ▼
6. Code → Blender → Scene Created
```

## 🗄️ Database Architecture

### Main Database (`blender_data.db`)
**Purpose:** Central log of all operations

**Tables:**
- `operations`: All Blender operations
- `model_performance`: LLM accuracy metrics
- `code_patterns`: Reusable code snippets
- `error_patterns`: Common errors and fixes
- `scene_transitions`: Scene state changes

### Specialist Databases
**Purpose:** Domain-specific knowledge

**Structure (same for all 10):**
```sql
operations
├── id
├── timestamp
├── operation_type
├── code_generated
├── success
└── execution_time

model_performance
├── id
├── model_name
├── accuracy_score
├── response_time
└── context_used

code_patterns
├── id
├── pattern_type
├── code_snippet
├── usage_count
└── success_rate

error_patterns
├── id
├── error_type
├── error_message
├── fix_applied
└── occurrence_count
```

## 🔌 Integration Points

### 1. Cursor ↔ MCP Server
- **Protocol:** JSON-RPC 2.0
- **Transport:** stdio (standard input/output)
- **Format:** JSON messages

### 2. MCP Server ↔ Blender
- **Protocol:** Custom JSON over TCP
- **Transport:** TCP Socket (localhost:9876)
- **Format:** `{"type": "execute_code", "params": {"code": "..."}}`

### 3. MCP Server ↔ Ollama
- **Protocol:** HTTP REST API
- **Transport:** HTTP (localhost:11434)
- **Format:** Ollama API format

### 4. Agents ↔ Databases
- **Protocol:** SQL
- **Transport:** SQLite file access
- **Format:** SQL queries

## 📈 Learning & Improvement

### How the System Learns:

1. **Operation Recording:**
   - Every operation is logged
   - Success/failure tracked
   - Execution time measured

2. **Pattern Recognition:**
   - Common code patterns extracted
   - Successful patterns prioritized
   - Failed patterns avoided

3. **Error Learning:**
   - Errors recorded with context
   - Fixes applied and tracked
   - Similar errors handled automatically

4. **Performance Tracking:**
   - LLM response quality measured
   - Best models identified
   - Context optimization

## 🎯 Key Features

### 1. **Multi-Agent System**
- 10 specialized agents for different domains
- Intelligent routing based on request content
- Domain-specific expertise

### 2. **Learning System**
- Records all operations
- Learns from patterns
- Improves over time

### 3. **Media Support**
- Image analysis with vision models
- Video processing
- Scene generation from references

### 4. **Comprehensive Data**
- 11 databases tracking everything
- Queryable history
- Performance metrics

### 5. **MCP Integration**
- Full MCP protocol support
- Tools, resources, and prompts
- Seamless Cursor integration

## 🚀 Scalability

### Current Capacity:
- **Agents:** 10 specialists
- **Databases:** 11 SQLite files
- **Tools:** 13 MCP tools
- **Resources:** 53 MCP resources
- **Prompts:** Configurable templates

### Extension Points:
- Add new specialists (extend `BaseBlenderSpecialist`)
- Add new tools (extend `_define_tools()`)
- Add new resources (extend `_define_resources()`)
- Add new databases (extend `BlenderDataCollector`)

## 📝 File Structure

```
F:\mcp server\
├── mcp_server.py              # Main MCP server
├── specialized_agents.py       # Agent coordinator + 10 specialists
├── data_collector.py          # Database management
├── media_handler.py           # Image/video processing
├── blender_ollama_server.py  # Direct Blender-Ollama bridge
├── test_*.py                  # Test scripts
└── *.db                       # SQLite databases (11 files)
```

## 🔐 Security & Configuration

### Environment Variables:
- `BLENDER_OLLAMA_PATH`: Path to blender-ollama directory
- `OLLAMA_URL`: Ollama server URL (default: http://localhost:11434)

### Network:
- Blender socket: `localhost:9876` (local only)
- Ollama API: `localhost:11434` (local only)

### Data Storage:
- Databases: Same directory as server
- Media cache: Configurable directory
- Logs: stderr output

---

**This architecture enables intelligent, learning-based control of Blender through natural language commands via Cursor IDE.**

