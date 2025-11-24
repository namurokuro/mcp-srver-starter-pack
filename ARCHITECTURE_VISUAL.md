# Blender-Ollama MCP Server - Visual Architecture Map

## 🎨 Node-Based Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CURSOR IDE                                            │
│                         (User Interface Layer)                                     │
└───────────────────────────────┬───────────────────────────────────────────────────┘
                                │
                                │ JSON-RPC 2.0 (stdio)
                                │ Request/Response
                                ▼
                    ┌───────────────────────────┐
                    │   MCP SERVER              │
                    │   (mcp_server.py)         │
                    │                           │
                    │  ┌─────────────────────┐ │
                    │  │ Request Router       │ │
                    │  │ • Tools             │ │
                    │  │ • Resources         │ │
                    │  │ • Prompts           │ │
                    │  └──────────┬──────────┘ │
                    └─────────────┼────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│   AGENT       │      │    MEDIA      │      │     DATA      │
│ COORDINATOR   │      │   HANDLER     │      │  COLLECTOR    │
│               │      │               │      │               │
│ Routes to:    │      │ • Load Image │      │ • Log Ops     │
│ • Modeling    │      │ • Analyze     │      │ • Track Perf  │
│ • Shading     │      │ • Process     │      │ • Store Data  │
│ • Animation   │      │               │      │               │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────┐    ┌──────────────────────┐
│ 10 SPECIALISTS   │  │   OLLAMA     │    │  11 SQLITE DBs       │
│                  │  │   (LLM)      │    │                      │
│ ┌──────────────┐ │  │              │    │ • blender_data.db   │
│ │ Modeling     │ │  │ • Generate    │    │ • modeling_data.db  │
│ │ Shading      │ │  │   Code        │    │ • shading_data.db   │
│ │ Animation    │ │  │ • Analyze     │    │ • animation_data.db  │
│ │ VFX          │ │  │   Vision      │    │ • vfx_data.db        │
│ │ MotionGraph  │ │  │              │    │ • ... (7 more)       │
│ │ Rendering    │ │  │              │    │                      │
│ │ Rigging      │ │  │              │    │                      │
│ │ Sculpting    │ │  │              │    │                      │
│ │ Camera       │ │  │              │    │                      │
│ │ Videography  │ │  │              │    │                      │
│ └──────────────┘ │  └──────────────┘    └──────────────────────┘
└────────┬──────────┘
         │
         │ Generated Blender Python Code
         │
         ▼
┌─────────────────────────────────────┐
│   BLENDER SOCKET SERVER             │
│   (Port 9876 - Python Addon)        │
│                                     │
│  ┌──────────────────────────────┐ │
│  │ execute_code()                │ │
│  │ get_scene_info()              │ │
│  └──────────────┬─────────────────┘ │
└─────────────────┼───────────────────┘
                  │
                  │ TCP Socket
                  │
                  ▼
         ┌─────────────────┐
         │     BLENDER     │
         │   (3D Software) │
         │                 │
         │ • Scene         │
         │ • Objects       │
         │ • Materials     │
         │ • Animation     │
         └─────────────────┘
```

## 🔄 Data Flow Connections

### Connection Map:

```
CURSOR
  │
  │ [1] User Command: "Create red cube"
  ▼
MCP SERVER
  │
  │ [2] Route to Agent Coordinator
  ▼
AGENT COORDINATOR
  │
  │ [3] Analyze: "cube" → Modeling
  ▼
MODELING SPECIALIST
  │
  │ [4] Request code generation
  ├─────────────────┐
  │                 │
  ▼                 ▼
OLLAMA LLM      DATA COLLECTOR
  │                 │
  │ [5] Generate    │ [6] Log operation
  │     code        │     to DB
  │                 │
  ▼                 ▼
BLENDER SOCKET  SQLITE DB
  │
  │ [7] Execute code
  ▼
BLENDER
  │
  │ [8] Create cube
  ▼
RESULT → MCP SERVER → CURSOR
```

## 📊 Component Details

### Node 1: CURSOR IDE
```
┌─────────────────────┐
│   CURSOR IDE        │
│                     │
│ • User Interface    │
│ • Command Input     │
│ • Result Display    │
│                     │
│ Input:              │
│ "Create red cube"   │
└─────────────────────┘
```

### Node 2: MCP SERVER
```
┌─────────────────────────────────┐
│      MCP SERVER                 │
│                                 │
│  ┌──────────────────────────┐  │
│  │ Request Handler          │  │
│  │ • Parse JSON-RPC         │  │
│  │ • Route to handler       │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │ Tool Definitions (13)    │  │
│  │ • create_scene           │  │
│  │ • get_scene_info         │  │
│  │ • query_database         │  │
│  │ • load_reference_image    │  │
│  │ • ... (9 more)           │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │ Resource Definitions (53)│  │
│  │ • Database schemas        │  │
│  │ • Scene state            │  │
│  │ • Agent list             │  │
│  └──────────────────────────┘  │
└─────────────────────────────────┘
```

### Node 3: AGENT COORDINATOR
```
┌─────────────────────────────────┐
│   AGENT COORDINATOR             │
│                                 │
│  Input: "Create red cube"       │
│                                 │
│  Analysis:                      │
│  • Keywords: "cube"             │
│  • Domain: Modeling             │
│                                 │
│  Route to:                      │
│  ┌──────────────────────────┐ │
│  │ ModelingSpecialist        │ │
│  └──────────────────────────┘ │
│                                 │
│  Available Agents:              │
│  • Modeling                    │
│  • Shading                     │
│  • Animation                   │
│  • VFX                         │
│  • Motion Graphics             │
│  • Rendering                   │
│  • Rigging                     │
│  • Sculpting                   │
│  • Camera Operator             │
│  • Videography                 │
└─────────────────────────────────┘
```

### Node 4: SPECIALIST AGENT (Example: Modeling)
```
┌─────────────────────────────────┐
│   MODELING SPECIALIST           │
│                                 │
│  Domain Knowledge:             │
│  • Meshes, geometry            │
│  • Primitive shapes             │
│  • Modifiers                    │
│                                 │
│  Process:                       │
│  1. Build prompt                │
│  2. Request Ollama             │
│  3. Generate code               │
│  4. Execute in Blender          │
│  5. Record to database          │
│                                 │
│  Output:                        │
│  bpy.ops.mesh.primitive_        │
│    cube_add()                   │
│  bpy.data.materials.new()       │
└─────────────────────────────────┘
```

### Node 5: OLLAMA LLM
```
┌─────────────────────────────────┐
│      OLLAMA LLM                 │
│   (localhost:11434)            │
│                                 │
│  Models:                        │
│  • gemma3:4b (primary)         │
│  • deepseek-r1:8b (fallback)   │
│  • llama3.2:latest             │
│  • llava (vision)              │
│                                 │
│  Functions:                     │
│  • Code Generation             │
│  • Image Analysis               │
│  • Text Understanding           │
│                                 │
│  Input:                         │
│  Prompt + Context               │
│                                 │
│  Output:                         │
│  Blender Python Code            │
└─────────────────────────────────┘
```

### Node 6: DATA COLLECTOR
```
┌─────────────────────────────────┐
│   DATA COLLECTOR                │
│                                 │
│  Records:                       │
│  • Operations                   │
│  • Model Performance            │
│  • Code Patterns               │
│  • Error Patterns               │
│  • Scene Transitions            │
│                                 │
│  Databases:                     │
│  ┌──────────────────────────┐ │
│  │ blender_data.db           │ │
│  │ (main operations log)     │ │
│  └──────────────────────────┘ │
│                                 │
│  ┌──────────────────────────┐ │
│  │ modeling_data.db          │ │
│  │ shading_data.db           │ │
│  │ animation_data.db         │ │
│  │ ... (8 more)              │ │
│  └──────────────────────────┘ │
└─────────────────────────────────┘
```

### Node 7: MEDIA HANDLER
```
┌─────────────────────────────────┐
│   MEDIA HANDLER                 │
│                                 │
│  Functions:                     │
│  • Load Images/Videos           │
│  • Cache Files                  │
│  • Analyze with Vision          │
│  • Generate Scene from Image    │
│                                 │
│  Flow:                          │
│  Image → Ollama Vision →        │
│  Analysis → Agent → Code        │
│                                 │
│  Supported:                     │
│  • JPG, PNG, WEBP              │
│  • MP4, AVI, MOV               │
└─────────────────────────────────┘
```

### Node 8: BLENDER SOCKET SERVER
```
┌─────────────────────────────────┐
│   BLENDER SOCKET SERVER         │
│   (Port 9876)                   │
│                                 │
│  Protocol:                      │
│  TCP Socket (JSON)              │
│                                 │
│  Commands:                      │
│  ┌──────────────────────────┐ │
│  │ execute_code             │ │
│  │ {                        │ │
│  │   "type": "execute_code",│ │
│  │   "params": {            │ │
│  │     "code": "..."        │ │
│  │   }                      │ │
│  │ }                        │ │
│  └──────────────────────────┘ │
│                                 │
│  ┌──────────────────────────┐ │
│  │ get_scene_info           │ │
│  │ Returns scene state      │ │
│  └──────────────────────────┘ │
└─────────────────────────────────┘
```

### Node 9: BLENDER
```
┌─────────────────────────────────┐
│      BLENDER                    │
│   (3D Software)                │
│                                 │
│  Executes:                      │
│  • Python Code                  │
│  • API Calls                    │
│  • Scene Operations             │
│                                 │
│  Results:                       │
│  • Objects Created              │
│  • Scene Modified               │
│  • State Changes                │
└─────────────────────────────────┘
```

## 🔗 Connection Types

### Connection 1: CURSOR → MCP SERVER
- **Type:** JSON-RPC 2.0
- **Transport:** stdio
- **Format:** JSON
- **Direction:** Bidirectional
- **Data:** Commands, Responses

### Connection 2: MCP SERVER → AGENT COORDINATOR
- **Type:** Function Call
- **Transport:** In-process
- **Format:** Python Objects
- **Direction:** Request → Response
- **Data:** User requests, Agent selection

### Connection 3: AGENT COORDINATOR → SPECIALISTS
- **Type:** Function Call
- **Transport:** In-process
- **Format:** Python Objects
- **Direction:** Route → Execute
- **Data:** Request, Generated code

### Connection 4: SPECIALISTS → OLLAMA
- **Type:** HTTP REST API
- **Transport:** HTTP
- **Format:** JSON
- **Direction:** Request → Response
- **Data:** Prompts, Generated code

### Connection 5: SPECIALISTS → DATA COLLECTOR
- **Type:** Database Write
- **Transport:** SQLite
- **Format:** SQL
- **Direction:** Write only
- **Data:** Operations, Performance

### Connection 6: SPECIALISTS → BLENDER SOCKET
- **Type:** TCP Socket
- **Transport:** TCP/IP
- **Format:** JSON
- **Direction:** Request → Response
- **Data:** Code, Execution results

### Connection 7: MEDIA HANDLER → OLLAMA
- **Type:** HTTP REST API
- **Transport:** HTTP
- **Format:** JSON + Binary
- **Direction:** Request → Response
- **Data:** Images, Analysis results

## 📈 Data Flow Example

### Complete Flow: "Create red cube"

```
[1] CURSOR
    │
    │ "Create red cube"
    ▼
[2] MCP SERVER
    │
    │ Route to create_scene tool
    ▼
[3] AGENT COORDINATOR
    │
    │ Analyze: "cube" → Modeling
    ▼
[4] MODELING SPECIALIST
    │
    │ Build prompt
    ├──→ [5] OLLAMA LLM
    │       │
    │       │ Generate code
    │       │ bpy.ops.mesh.primitive_cube_add()
    │       │ material = bpy.data.materials.new("Red")
    │       │ material.diffuse_color = (1, 0, 0, 1)
    │       │
    │       └──→ [4] Return code
    │
    │ Execute code
    ├──→ [6] DATA COLLECTOR
    │       │
    │       │ Log to modeling_data.db
    │       │
    │       └──→ [SQLITE] Store
    │
    └──→ [8] BLENDER SOCKET
            │
            │ Send code via TCP
            ▼
        [9] BLENDER
            │
            │ Execute Python
            │ Create cube
            │ Apply material
            │
            └──→ [8] Return result
                    │
                    ▼
                [2] MCP SERVER
                    │
                    ▼
                [1] CURSOR
                    │
                    └──→ Display: "Cube created"
```

## 🎯 Key Features Visualization

### Multi-Agent System
```
AGENT COORDINATOR
    │
    ├──→ Modeling ────┐
    ├──→ Shading ─────┤
    ├──→ Animation ────┤
    ├──→ VFX ─────────┤
    ├──→ MotionGraph ─┤
    ├──→ Rendering ───┤
    ├──→ Rigging ─────┤
    ├──→ Sculpting ───┤
    ├──→ Camera ──────┤
    └──→ Videography ─┘
        │
        └──→ All connect to:
            • Ollama (code generation)
            • Data Collector (logging)
            • Blender Socket (execution)
```

### Learning System
```
OPERATIONS
    │
    ├──→ Record to DB
    │
    ├──→ Extract Patterns
    │
    ├──→ Update Knowledge
    │
    └──→ Improve Future
        │
        └──→ Better Code Generation
```

### Media Processing
```
IMAGE/VIDEO FILE
    │
    ├──→ Load & Cache
    │
    ├──→ Ollama Vision Analysis
    │
    ├──→ Extract Description
    │
    ├──→ Route to Agent
    │
    └──→ Generate Scene
```

---

**This visual map shows how all components connect and communicate in the Blender-Ollama MCP system.**

