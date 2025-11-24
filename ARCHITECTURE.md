# Blender-Ollama MCP Server - Complete Architecture

**Version**: 1.0.0  
**Last Updated**: 2025-01-20  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Database Architecture](#database-architecture)
6. [Integration Points](#integration-points)
7. [Protocol Specifications](#protocol-specifications)
8. [Learning System](#learning-system)
9. [File Structure](#file-structure)
10. [Extension Points](#extension-points)

---

## 🎯 System Overview

The Blender-Ollama MCP Server is a Model Context Protocol (MCP) implementation that enables natural language control of Blender 3D software through Cursor IDE. It uses a multi-agent system with specialized domain experts, local LLM (Ollama), and a comprehensive learning database.

### Key Characteristics

- **Protocol**: MCP (JSON-RPC 2.0 over stdio)
- **Architecture**: Multi-agent system with 10 specialized agents
- **AI**: Local LLM via Ollama (code generation + vision)
- **Storage**: 11 SQLite databases for learning and tracking
- **Integration**: Direct Blender control via TCP socket
- **Media**: Image/video analysis with vision models

---

## 🏗️ Architecture Diagram

### High-Level System Architecture

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
│  │  Request Router                                                  │   │
│  │  • Tool Handlers (13 tools)                                      │   │
│  │  • Resource Handlers (53 resources)                              │   │
│  │  • Prompt Templates (5 prompts)                                  │   │
│  │  • Error Handling                                                │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────┬───────────────────────┬──────────────────────┬────────────┘
             │                       │                      │
             │                       │                      │
             ▼                       ▼                      ▼
    ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
    │   AGENT      │      │     MEDIA    │      │     DATA     │
    │ COORDINATOR  │      │   HANDLER    │      │  COLLECTOR   │
    │              │      │              │      │              │
    │ Routes to    │      │ • Images     │      │ • Log Ops    │
    │ 10 Specialists│     │ • Videos     │      │ • Track Perf │
    └──────┬───────┘      └──────┬───────┘      └──────┬───────┘
           │                     │                      │
           │                     │                      │
           ▼                     ▼                      ▼
┌──────────────────────┐  ┌──────────────┐    ┌──────────────────────┐
│  SPECIALIZED AGENTS  │  │   OLLAMA     │    │   SQLITE DATABASES   │
│  (10 Specialists)    │  │  (LLM API)   │    │  (11 Databases)      │
│                      │  │              │    │                      │
│ • Modeling           │  │ • Code Gen   │    │ • blender_data.db   │
│ • Shading            │  │ • Vision     │    │ • modeling_data.db  │
│ • Animation          │  │ • Analysis   │    │ • shading_data.db   │
│ • VFX                │  │              │    │ • animation_data.db  │
│ • Motion Graphics    │  │              │    │ • vfx_data.db        │
│ • Rendering          │  │              │    │ • ... (6 more)       │
│ • Rigging            │  │              │    │                      │
│ • Sculpting          │  │              │    │                      │
│ • Camera Operator    │  │              │    │                      │
│ • Videography        │  │              │    │                      │
└──────────┬───────────┘  └──────────────┘    └──────────────────────┘
           │
           │ Generated Blender Python Code
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    BLENDER SOCKET SERVER                                │
│                    (Port 9876 - Python Addon)                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  • execute_code() - Runs Python code in Blender                │   │
│  │  • get_scene_info() - Returns scene state                       │   │
│  │  • TCP Socket Communication (JSON)                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────────┘
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

---

## 🔧 Component Details

### 1. MCP Server (`mcp_server.py`)

**Role**: Main entry point, handles all Cursor communication

**Responsibilities**:
- Receives JSON-RPC 2.0 requests from Cursor via stdio
- Routes requests to appropriate handlers (tools/resources/prompts)
- Formats responses back to Cursor
- Manages server lifecycle and initialization
- Handles errors and logging

**Key Components**:
```python
BlenderOllamaMCPServer
├── Tools (13)
│   ├── create_scene
│   ├── get_scene_info
│   ├── execute_blender_code
│   ├── query_database
│   ├── get_model_performance
│   ├── get_successful_patterns
│   ├── list_specialists
│   ├── load_reference_image
│   ├── analyze_image
│   ├── create_scene_from_image
│   ├── load_reference_video
│   ├── analyze_video
│   └── list_media_files
├── Resources (53)
│   ├── Database schemas (11 specialists × 5 types)
│   ├── Scene state
│   ├── Agent list
│   └── Cached media
└── Prompts (5)
    ├── create_modeling_scene
    ├── create_material_setup
    ├── analyze_performance
    ├── find_similar_operations
    └── create_scene_from_reference_image
```

**Size**: ~48 KB, ~1,100 lines

---

### 2. Agent Coordinator (`specialized_agents.py`)

**Role**: Routes user requests to the appropriate specialist agent

**Architecture**:
```python
AgentCoordinator
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

**Routing Algorithm**:
1. Analyzes user request for keywords
2. Matches keywords to specialist domains
3. Routes to most appropriate specialist
4. Falls back to general specialist if unclear

**Example**:
- Request: "Create a red cube"
- Analysis: "cube" → Modeling domain
- Route: `ModelingSpecialist`

**Size**: ~30 KB, ~775 lines

---

### 3. Specialized Agents (10 Domain Experts)

**Base Class**: `BaseBlenderSpecialist`

Each agent has:
- **Domain Knowledge**: Specialized prompts for their field
- **Code Generation**: Uses Ollama LLM to generate Blender Python
- **Data Collector**: Records operations to their database
- **Learning**: Improves over time from recorded patterns
- **Blender Connection**: Direct socket connection to Blender

**Agent Structure**:
```python
BaseBlenderSpecialist
├── name: str
├── ollama_url: str
├── blender_host: str
├── blender_port: int
├── primary_model: str
├── fallback_models: List[str]
├── collector: BlenderDataCollector
└── Methods:
    ├── connect_to_blender()
    ├── generate_code(description: str) -> str
    ├── execute_code(code: str) -> Dict
    ├── create_scene(description: str) -> Dict
    └── record_operation(...)
```

**Specialist Details**:

| Specialist | Domain | Database | Key Capabilities |
|------------|--------|----------|-----------------|
| **Modeling** | 3D modeling, meshes, geometry | `modeling_data.db` | Primitive shapes, modifiers, mesh operations |
| **Shading** | Materials and shaders | `shading_data.db` | Material creation, node setup, textures |
| **Animation** | Animation and keyframes | `animation_data.db` | Keyframe animation, constraints, drivers |
| **VFX** | Visual effects and simulations | `vfx_data.db` | Physics, particles, fluid simulation |
| **Motion Graphics** | Text and motion graphics | `motiongraphics_data.db` | Text objects, motion graphics, effects |
| **Rendering** | Rendering and export | `rendering_data.db` | Render settings, output formats, compositing |
| **Rigging** | Armatures and rigging | `rigging_data.db` | Bone creation, constraints, IK/FK |
| **Sculpting** | Digital sculpting | `sculpting_data.db` | Sculpting tools, brushes, detail |
| **Camera Operator** | Camera operations | `cameraoperator_data.db` | Camera setup, framing, animation |
| **Videography** | Video editing | `videography_data.db` | Video sequences, editing, effects |

---

### 4. Data Collector (`data_collector.py`)

**Role**: Records all operations for learning and analysis

**Database Structure**:
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
```

**Database Schema** (per database):
```sql
-- Operations table
CREATE TABLE operations (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    description TEXT,
    model_used TEXT,
    generated_code TEXT,
    execution_result TEXT,  -- JSON
    scene_before TEXT,      -- JSON
    scene_after TEXT,       -- JSON
    execution_time REAL,
    success INTEGER,
    error_message TEXT,
    retry_count INTEGER
);

-- Model performance table
CREATE TABLE model_performance (
    id TEXT PRIMARY KEY,
    model_name TEXT,
    total_requests INTEGER,
    successful_requests INTEGER,
    failed_requests INTEGER,
    timeout_count INTEGER,
    average_generation_time REAL,
    average_code_length REAL,
    success_rate REAL
);

-- Code patterns table
CREATE TABLE code_patterns (
    id TEXT PRIMARY KEY,
    pattern_type TEXT,
    code_snippet TEXT,
    usage_count INTEGER,
    success_rate REAL,
    context TEXT
);

-- Error patterns table
CREATE TABLE error_patterns (
    id TEXT PRIMARY KEY,
    error_type TEXT,
    error_message TEXT,
    fix_applied TEXT,
    occurrence_count INTEGER,
    context TEXT
);

-- Scene transitions table
CREATE TABLE scene_transitions (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    scene_before TEXT,  -- JSON
    scene_after TEXT,   -- JSON
    operation_type TEXT,
    objects_added TEXT, -- JSON
    objects_modified TEXT, -- JSON
    objects_removed TEXT  -- JSON
);
```

**Size**: ~19 KB, ~510 lines

---

### 5. Media Handler (`media_handler.py`)

**Role**: Processes reference images and videos

**Workflow**:
```
Media Handler
│
├── Load Image/Video
│   ├── Validates file format
│   ├── Reads file data
│   └── Encodes to base64
│
├── Cache Management
│   └── Stores in memory cache
│
├── Analyze with Ollama Vision
│   ├── Uses vision-capable models (llama3.2-vision, llava, etc.)
│   ├── Extracts scene description
│   └── Extracts material properties
│
└── Generate Scene from Analysis
    └── Creates Blender scene based on image content
```

**Supported Formats**:
- **Images**: JPG, JPEG, PNG, BMP, GIF, WebP, TIFF
- **Videos**: MP4, AVI, MOV, MKV, WebM, FLV, WMV

**Methods**:
- `load_image(image_path: str) -> Dict`
- `analyze_image(image_path: str, model: str = "llama3.2-vision") -> Dict`
- `extract_scene_description(image_path: str) -> str`
- `extract_materials(image_path: str) -> List[Dict]`
- `load_video(video_path: str) -> Dict`
- `analyze_video(video_path: str) -> Dict`
- `list_media_files(directory: str) -> List[str]`

**Size**: ~9 KB, ~259 lines

---

### 6. Blender Socket Server (Python Addon)

**Role**: Bridge between MCP server and Blender

**Communication Protocol**:
```
MCP Server → TCP Socket (localhost:9876) → Blender Addon
                                              │
                                              ▼
                                         Blender Python API
```

**Commands**:
```json
// Execute code
{
  "type": "execute_code",
  "params": {
    "code": "bpy.ops.mesh.primitive_cube_add()"
  }
}

// Get scene info
{
  "type": "get_scene_info",
  "params": {}
}
```

**Response Format**:
```json
{
  "status": "success",
  "result": {
    "objects": [...],
    "materials": [...],
    "scene_info": {...}
  }
}
```

---

### 7. Ollama LLM Integration

**Role**: Generates Blender Python code and analyzes images

**Usage**:
```
Agent → Ollama API (localhost:11434)
         │
         ├── Text Generation (code creation)
         │   └── Models: gemma3:4b, deepseek-r1:8b, llama3.2:latest
         │
         └── Vision Analysis (image/video understanding)
             └── Models: llama3.2-vision, llava, bakllava
```

**API Endpoints**:
- `/api/generate` - Text generation
- `/api/chat` - Chat completion
- `/api/embeddings` - Embeddings (future)

**Model Configuration**:
- **Primary**: `gemma3:4b` (fast, efficient)
- **Fallback**: `deepseek-r1:8b`, `llama3.2:latest`
- **Vision**: `llama3.2-vision:latest` (default), `llava`, `bakllava`

---

## 🔄 Data Flow

### Scene Creation Flow

```
[1] USER (Cursor)
    │
    │ "Create a red cube"
    ▼
[2] CURSOR IDE
    │
    │ JSON-RPC Request
    │ {
    │   "method": "tools/call",
    │   "params": {
    │     "name": "create_scene",
    │     "arguments": {
    │       "description": "Create a red cube"
    │     }
    │   }
    │ }
    ▼
[3] MCP SERVER (mcp_server.py)
    │
    │ Route to create_scene tool handler
    ▼
[4] AGENT COORDINATOR
    │
    │ Analyze: "cube" → Modeling domain
    │ Route to ModelingSpecialist
    ▼
[5] MODELING SPECIALIST
    │
    │ Build prompt:
    │ "You are a Blender modeling expert.
    │  Create a red cube..."
    │
    ├──→ [6] OLLAMA LLM
    │       │
    │       │ Generate code:
    │       │ bpy.ops.mesh.primitive_cube_add()
    │       │ cube = bpy.context.active_object
    │       │ mat = bpy.data.materials.new("Red")
    │       │ mat.diffuse_color = (1, 0, 0, 1)
    │       │ cube.data.materials.append(mat)
    │       │
    │       └──→ [5] Return code
    │
    ├──→ [7] DATA COLLECTOR
    │       │
    │       │ Log operation to modeling_data.db
    │       │ - Description
    │       │ - Generated code
    │       │ - Model used
    │       │ - Timestamp
    │       │
    │       └──→ [SQLITE] Store
    │
    └──→ [8] BLENDER SOCKET SERVER
            │
            │ Send code via TCP (port 9876)
            │ {
            │   "type": "execute_code",
            │   "params": {"code": "..."}
            │ }
            ▼
        [9] BLENDER
            │
            │ Execute Python code
            │ - Create cube mesh
            │ - Create material
            │ - Apply material
            │
            └──→ [8] Return result
                    │
                    ▼
                [3] MCP SERVER
                    │
                    │ Format response
                    ▼
                [2] CURSOR IDE
                    │
                    └──→ [1] USER
                            │
                            └──→ Display: "Cube created successfully"
```

### Image Analysis Flow

```
[1] USER
    │
    │ "Load this image and create scene"
    ▼
[2] MCP SERVER
    │
    │ Route to load_reference_image tool
    ▼
[3] MEDIA HANDLER
    │
    ├── Load image file
    ├── Validate format
    ├── Read and encode (base64)
    └── Cache in memory
    │
    ├──→ [4] OLLAMA VISION MODEL
    │       │
    │       │ Analyze image:
    │       │ - Describe objects
    │       │ - Extract colors
    │       │ - Identify layout
    │       │ - Note materials
    │       │
    │       └──→ [3] Return analysis
    │
    └──→ [5] AGENT COORDINATOR
            │
            │ Route based on analysis
            │ (e.g., "red cube" → Modeling)
            ▼
        [6] SPECIALIST
            │
            │ Generate code from analysis
            │
            └──→ [7] BLENDER
                    │
                    └──→ Scene created
```

---

## 🗄️ Database Architecture

### Database Hierarchy

```
blender_data.db (Main)
│
└── Central log of all operations
    └── Cross-domain operations

Specialist Databases (10)
│
├── modeling_data.db
│   └── Modeling-specific operations
│
├── shading_data.db
│   └── Material/shader operations
│
├── animation_data.db
│   └── Animation operations
│
├── vfx_data.db
│   └── VFX operations
│
├── motiongraphics_data.db
│   └── Motion graphics operations
│
├── rendering_data.db
│   └── Rendering operations
│
├── rigging_data.db
│   └── Rigging operations
│
├── sculpting_data.db
│   └── Sculpting operations
│
├── cameraoperator_data.db
│   └── Camera operations
│
└── videography_data.db
    └── Video editing operations
```

### Data Relationships

```
Operation
    │
    ├──→ Model Performance
    │       └──→ Tracks which models work best
    │
    ├──→ Code Pattern
    │       └──→ Extracts reusable patterns
    │
    ├──→ Error Pattern (if failed)
    │       └──→ Records errors and fixes
    │
    └──→ Scene Transition
            └──→ Tracks scene state changes
```

---

## 🔌 Integration Points

### 1. Cursor ↔ MCP Server

**Protocol**: JSON-RPC 2.0  
**Transport**: stdio (standard input/output)  
**Format**: JSON messages  
**Direction**: Bidirectional

**Request Example**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_scene",
    "arguments": {
      "description": "Create a red cube"
    }
  }
}
```

**Response Example**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Scene created successfully"
      }
    ]
  }
}
```

---

### 2. MCP Server ↔ Blender

**Protocol**: Custom JSON over TCP  
**Transport**: TCP Socket (localhost:9876)  
**Format**: JSON messages  
**Direction**: Request → Response

**Request Format**:
```json
{
  "type": "execute_code",
  "params": {
    "code": "bpy.ops.mesh.primitive_cube_add()"
  }
}
```

**Response Format**:
```json
{
  "status": "success",
  "result": {
    "output": "...",
    "error": null
  }
}
```

---

### 3. MCP Server ↔ Ollama

**Protocol**: HTTP REST API  
**Transport**: HTTP (localhost:11434)  
**Format**: JSON  
**Direction**: Request → Response

**Text Generation Request**:
```json
{
  "model": "gemma3:4b",
  "prompt": "You are a Blender expert...",
  "stream": false
}
```

**Vision Analysis Request**:
```json
{
  "model": "llama3.2-vision:latest",
  "prompt": "Describe this image...",
  "images": ["base64_encoded_image"]
}
```

---

### 4. Agents ↔ Databases

**Protocol**: SQL  
**Transport**: SQLite file access  
**Format**: SQL queries  
**Direction**: Write (operations), Read (queries)

**Write Example**:
```python
collector.record_operation(
    description="Create red cube",
    model_used="gemma3:4b",
    generated_code="...",
    success=True
)
```

**Read Example**:
```python
patterns = collector.get_successful_patterns(limit=10)
```

---

## 📐 Protocol Specifications

### MCP Protocol

**Version**: 2024-11-05  
**Base Protocol**: JSON-RPC 2.0

**Methods**:
- `initialize` - Initialize MCP connection
- `tools/list` - List available tools
- `tools/call` - Call a tool
- `resources/list` - List available resources
- `resources/read` - Read a resource
- `prompts/list` - List available prompts
- `prompts/get` - Get a prompt

**Error Codes**:
- `-32700` - Parse error
- `-32600` - Invalid Request
- `-32601` - Method not found
- `-32602` - Invalid params
- `-32603` - Internal error
- `-32000` - Server error

---

## 🧠 Learning System

### How the System Learns

#### 1. Operation Recording
```
Every Operation
    │
    ├──→ Recorded to database
    │       ├── Description
    │       ├── Generated code
    │       ├── Success/failure
    │       ├── Execution time
    │       └── Model used
    │
    └──→ Used for pattern extraction
```

#### 2. Pattern Recognition
```
Operations Database
    │
    ├──→ Extract common code patterns
    │       └──→ Store in code_patterns table
    │
    ├──→ Identify successful patterns
    │       └──→ Prioritize in future generation
    │
    └──→ Avoid failed patterns
            └──→ Learn from mistakes
```

#### 3. Error Learning
```
Failed Operations
    │
    ├──→ Record error message
    │
    ├──→ Record context
    │
    ├──→ Apply fix (if available)
    │
    └──→ Store in error_patterns table
            └──→ Use for future error handling
```

#### 4. Performance Tracking
```
Model Usage
    │
    ├──→ Track success rate per model
    │
    ├──→ Track response time
    │
    ├──→ Track code quality
    │
    └──→ Optimize model selection
            └──→ Use best model for each task
```

---

## 📁 File Structure

### Complete Directory Layout

```
F:\mcp server\
│
├── Core Implementation
│   ├── mcp_server.py              # Main MCP server (48 KB)
│   ├── specialized_agents.py      # Agent system (30 KB)
│   ├── data_collector.py          # Database system (19 KB)
│   └── media_handler.py           # Media handling (9 KB)
│
├── Startup & Testing
│   ├── start_server.py            # Production startup
│   ├── server_status.py           # Status checker
│   ├── run_all_tests.py           # Test suite
│   ├── test_blender_connection_full.py
│   ├── test_mcp_protocol.py
│   └── test_mcp.py
│
├── Configuration
│   ├── cursor_config.json
│   ├── cursor_mcp_config_ready.json
│   └── requirements.txt
│
├── Documentation
│   ├── README.md
│   ├── ARCHITECTURE.md            # This file
│   ├── ARCHITECTURE_MAP.md
│   ├── ARCHITECTURE_VISUAL.md
│   ├── SERVER_PROGRESS.md
│   ├── PRODUCTION_READY.md
│   ├── IMPLEMENTATION_COMPLETE.md
│   ├── CURSOR_TROUBLESHOOTING.md
│   ├── MEDIA_FEATURES.md
│   └── ... (other docs)
│
└── Databases (11 SQLite files)
    ├── blender_data.db
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
```

---

## 🔧 Extension Points

### Adding a New Specialist

1. **Create Specialist Class**:
```python
class NewSpecialist(BaseBlenderSpecialist):
    def __init__(self):
        super().__init__(
            name="NewSpecialist",
            primary_model="gemma3:4b"
        )
    
    def get_domain_prompt(self) -> str:
        return "You are a Blender [domain] expert..."
```

2. **Register in MCP Server**:
```python
self.coordinator.register_specialist(NewSpecialist())
```

3. **Create Database**:
```python
collector = BlenderDataCollector("newspecialist_data.db")
```

---

### Adding a New Tool

1. **Define Tool in MCP Server**:
```python
def _define_tools(self):
    return [
        # ... existing tools ...
        {
            "name": "new_tool",
            "description": "Tool description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                }
            }
        }
    ]
```

2. **Implement Handler**:
```python
async def _handle_tool_call(self, name: str, arguments: Dict):
    if name == "new_tool":
        # Implementation
        return {"result": "..."}
```

---

### Adding a New Resource

1. **Define Resource**:
```python
def _define_resources(self):
    return [
        # ... existing resources ...
        {
            "uri": "blender://new/resource",
            "name": "New Resource",
            "description": "Resource description",
            "mimeType": "application/json"
        }
    ]
```

2. **Implement Handler**:
```python
async def _handle_resource_read(self, uri: str):
    if uri == "blender://new/resource":
        # Return resource data
        return {"contents": [...]}
```

---

## 🎯 Key Design Decisions

### 1. Multi-Agent Architecture
**Why**: Different Blender domains require specialized knowledge. A single agent would be too generic.

**Benefit**: Each specialist can focus on their domain, improving code quality and accuracy.

---

### 2. Local LLM (Ollama)
**Why**: Privacy, speed, and no API costs. Works offline.

**Benefit**: Fast response times, no data leaves the machine, free to use.

---

### 3. SQLite Databases
**Why**: Lightweight, file-based, no server required. Perfect for learning data.

**Benefit**: Easy to backup, query, and analyze. No external dependencies.

---

### 4. TCP Socket for Blender
**Why**: Direct control, real-time execution, no file-based workflow.

**Benefit**: Immediate feedback, better error handling, seamless integration.

---

### 5. MCP Protocol
**Why**: Standard protocol for AI tool integration. Works with Cursor and other MCP clients.

**Benefit**: Future-proof, extensible, well-documented.

---

## 📊 Performance Characteristics

### Response Times
- **Server Startup**: < 2 seconds
- **Tool Response**: < 5 seconds (operation-dependent)
- **Blender Connection**: < 1 second
- **Database Queries**: < 1 second
- **Image Analysis**: 5-15 seconds (model-dependent)
- **Code Generation**: 2-10 seconds (model-dependent)

### Scalability
- **Concurrent Requests**: Handled sequentially (MCP stdio limitation)
- **Database Size**: SQLite handles millions of records efficiently
- **Memory Usage**: ~50-100 MB (depends on cache size)
- **CPU Usage**: Low when idle, spikes during code generation

---

## 🔒 Security Considerations

### Network Security
- **Blender Socket**: Localhost only (port 9876)
- **Ollama API**: Localhost only (port 11434)
- **No External Network**: All communication is local

### Data Security
- **Local Storage**: All data stored locally
- **No Cloud**: No data sent to external services
- **User Control**: User has full control over all data

### Code Execution
- **Sandboxed**: Code runs in Blender's Python environment
- **User Approval**: User can review code before execution (future feature)
- **Error Handling**: Comprehensive error catching prevents crashes

---

## 🚀 Future Enhancements

### Planned Features
1. **Batch Operations**: Execute multiple operations at once
2. **Scene Templates**: Pre-built scene templates
3. **Advanced Analytics**: Dashboard for performance metrics
4. **Multi-Blender Support**: Connect to multiple Blender instances
5. **Code Review**: Preview code before execution
6. **Version Control**: Track scene versions
7. **Cloud Deployment**: Optional cloud-based Ollama

---

## 📚 References

### Protocol & Integration
- [MCP Protocol Specification](https://modelcontextprotocol.io) - Model Context Protocol specification
- [Cursor MCP Server Guide](https://cursor.com/docs/cookbook/building-mcp-server) - Building MCP servers for Cursor

### Blender Documentation
- [Blender Python API](https://docs.blender.org/api/current/) - Official Blender Python API reference
- [Blender Developer Documentation](https://developer.blender.org/docs/) - Blender development handbook and architecture
- [Blender Developer Handbook](https://developer.blender.org/docs/handbook/) - Complete guide for Blender developers
- [Blender Features Documentation](https://developer.blender.org/docs/features/) - Design and implementation of Blender features
- [Blender Projects](https://projects.blender.org/) - Blender source code, issues, and development platform
- [Blender Developer Forum](https://devtalk.blender.org/) - Community forum for Blender developers
- [Blender Release Notes](https://developer.blender.org/docs/releases/) - API changes and compatibility notes

### AI & LLM
- [Ollama Documentation](https://ollama.ai/docs) - Ollama LLM server documentation

---

**This architecture enables intelligent, learning-based control of Blender through natural language commands via Cursor IDE.**

