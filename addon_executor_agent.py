"""
Addon Executor Agent - Runs addon operations and maintains database of installed addons
"""

import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from specialized_agents import BaseBlenderSpecialist, OperationRecord
from data_collector import BlenderDataCollector


class AddonExecutorSpecialist(BaseBlenderSpecialist):
    """Specialist for executing addon operations and maintaining addon database"""
    
    def __init__(self, **kwargs):
        super().__init__("AddonExecutor", **kwargs)
        self.addons_db_path = "addons_executor.db"
        self._init_addons_database()
        self.addon_cache = {}
        self.operation_history = []
    
    def _init_addons_database(self):
        """Initialize comprehensive database for installed addons"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        # Installed addons table with comprehensive info
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS installed_addons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                display_name TEXT,
                description TEXT,
                author TEXT,
                version TEXT,
                category TEXT,
                location TEXT,
                enabled INTEGER DEFAULT 0,
                installed_date TEXT,
                last_used TEXT,
                usage_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                bl_info TEXT,
                preferences TEXT,
                dependencies TEXT,
                requirements TEXT,
                documentation_url TEXT,
                support_url TEXT,
                license TEXT,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        # Addon operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS addon_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addon_module TEXT NOT NULL,
                operation_name TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                parameters TEXT,
                result TEXT,
                execution_time REAL,
                success INTEGER DEFAULT 0,
                error_message TEXT,
                timestamp TEXT,
                context TEXT,
                FOREIGN KEY (addon_module) REFERENCES installed_addons(module)
            )
        """)
        
        # Addon operators table (tracks available operators from addons)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS addon_operators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addon_module TEXT NOT NULL,
                operator_id TEXT NOT NULL,
                operator_name TEXT,
                operator_description TEXT,
                operator_category TEXT,
                parameters TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used TEXT,
                FOREIGN KEY (addon_module) REFERENCES installed_addons(module),
                UNIQUE(addon_module, operator_id)
            )
        """)
        
        # Addon preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS addon_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addon_module TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                preference_value TEXT,
                preference_type TEXT,
                description TEXT,
                last_modified TEXT,
                FOREIGN KEY (addon_module) REFERENCES installed_addons(module),
                UNIQUE(addon_module, preference_key)
            )
        """)
        
        # Addon execution history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addon_module TEXT NOT NULL,
                operation TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                execution_time REAL,
                success INTEGER DEFAULT 0,
                error_details TEXT,
                timestamp TEXT,
                session_id TEXT,
                FOREIGN KEY (addon_module) REFERENCES installed_addons(module)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_addon_module ON installed_addons(module)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_operations_addon ON addon_operations(addon_module)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_operations_timestamp ON addon_operations(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON execution_history(timestamp)")
        
        conn.commit()
        conn.close()
        self.log("Addon executor database initialized")
    
    def get_system_prompt(self) -> str:
        return """You are a Blender Addon Executor expert specializing in:
- Running and executing addon operations
- Managing addon databases
- Tracking addon usage and performance
- Executing addon operators and functions
- Managing addon preferences
- Monitoring addon behavior
- Logging addon operations
- Handling addon errors and exceptions

Generate Python code for addon execution operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common addon execution operations:
- bpy.ops.addon_operator.execute() - Execute addon operator
- bpy.context.preferences.addons['module'].preferences - Access preferences
- bpy.ops.wm.addon_enable(module='module') - Enable addon
- bpy.ops.wm.addon_disable(module='module') - Disable addon
- bpy.utils.addon_utils.module_bl_info(module) - Get addon info
- bpy.ops - Access all operators including addon operators
- addon = bpy.context.preferences.addons.get('module')
- addon.preferences.property_name - Access preference property

Addon execution:
- Find and execute addon operators
- Run addon functions
- Access addon preferences
- Monitor addon operations
- Track addon performance
- Handle addon errors"""
    
    def scan_and_store_addons(self) -> Dict:
        """Scan Blender for all installed addons and store in database"""
        self.log("Scanning and storing installed addons...")
        
        code = """
import bpy
import json
import importlib
from datetime import datetime

addons_list = []

# Get all installed addons
for module_name in bpy.context.preferences.addons.keys():
    addon = bpy.context.preferences.addons[module_name]
    
    addon_data = {
        "module": module_name,
        "name": getattr(addon, 'name', module_name),
        "display_name": getattr(addon, 'name', module_name),
        "enabled": True,
        "location": getattr(addon, 'filepath', ''),
        "description": "",
        "author": "",
        "version": "",
        "category": "",
        "bl_info": {},
        "preferences": {},
        "dependencies": [],
        "requirements": [],
        "tags": []
    }
    
    # Try to get bl_info
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'bl_info'):
            bl_info = module.bl_info
            addon_data.update({
                "display_name": bl_info.get('name', addon_data['name']),
                "description": bl_info.get('description', ''),
                "author": bl_info.get('author', ''),
                "version": str(bl_info.get('version', ())),
                "category": bl_info.get('category', ''),
                "location": bl_info.get('location', addon_data['location']),
            })
            addon_data["bl_info"] = dict(bl_info)
            
            # Extract dependencies and requirements
            if 'dependencies' in bl_info:
                addon_data["dependencies"] = bl_info.get('dependencies', [])
            if 'requirements' in bl_info:
                addon_data["requirements"] = bl_info.get('requirements', [])
    except Exception as e:
        addon_data["error"] = str(e)
    
    # Try to get preferences
    try:
        if hasattr(addon, 'preferences'):
            prefs = addon.preferences
            prefs_dict = {}
            for prop in dir(prefs):
                if not prop.startswith('_'):
                    try:
                        value = getattr(prefs, prop)
                        if not callable(value):
                            prefs_dict[prop] = str(value)
                    except:
                        pass
            addon_data["preferences"] = prefs_dict
    except Exception as e:
        pass
    
    addons_list.append(addon_data)

result = {
    "status": "success",
    "addons": addons_list,
    "total_count": len(addons_list),
    "timestamp": datetime.now().isoformat()
}

print(json.dumps(result))
"""
        
        result = self.execute_code(code)
        
        if result.get("status") == "success":
            try:
                output = result.get("output", "")
                import re
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    stored_count = self._store_addons_in_db(data.get("addons", []))
                    return {
                        "status": "success",
                        "addons_scanned": len(data.get("addons", [])),
                        "addons_stored": stored_count,
                        "message": f"Scanned and stored {stored_count} addons"
                    }
            except Exception as e:
                self.log(f"Error parsing addon data: {e}", "ERROR")
        
        return {"status": "error", "message": "Failed to scan addons"}
    
    def _store_addons_in_db(self, addons: List[Dict]) -> int:
        """Store addons in database"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        stored = 0
        
        for addon in addons:
            module = addon.get("module", "")
            if not module:
                continue
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO installed_addons
                    (module, name, display_name, description, author, version, category,
                     location, enabled, installed_date, last_used, usage_count,
                     success_count, error_count, bl_info, preferences, dependencies,
                     requirements, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    module,
                    addon.get("name", ""),
                    addon.get("display_name", ""),
                    addon.get("description", ""),
                    addon.get("author", ""),
                    addon.get("version", ""),
                    addon.get("category", ""),
                    addon.get("location", ""),
                    1 if addon.get("enabled", False) else 0,
                    datetime.now().isoformat(),
                    None,
                    0,
                    0,
                    0,
                    json.dumps(addon.get("bl_info", {})),
                    json.dumps(addon.get("preferences", {})),
                    json.dumps(addon.get("dependencies", [])),
                    json.dumps(addon.get("requirements", [])),
                    json.dumps(addon.get("tags", [])),
                    json.dumps(addon)
                ))
                stored += 1
            except Exception as e:
                self.log(f"Error storing addon {module}: {e}", "ERROR")
        
        conn.commit()
        conn.close()
        return stored
    
    def discover_addon_operators(self, addon_module: Optional[str] = None) -> Dict:
        """Discover operators available from addons"""
        self.log(f"Discovering operators for addon: {addon_module or 'all'}")
        
        code = """
import bpy
import json

operators_list = []

# Get all operators
all_operators = dir(bpy.ops)

# Filter addon operators (usually in specific categories)
for op_path in all_operators:
    try:
        # Try to get operator info
        op_category = op_path.split('.')[0] if '.' in op_path else ''
        op_name = op_path.split('.')[-1] if '.' in op_path else op_path
        
        # Try to execute operator info
        try:
            op = getattr(bpy.ops, op_path)
            if hasattr(op, 'get_rna_type'):
                rna = op.get_rna_type()
                op_info = {
                    "operator_id": op_path,
                    "operator_name": op_name,
                    "category": op_category,
                    "description": getattr(rna, 'description', ''),
                }
                operators_list.append(op_info)
        except:
            pass
    except:
        pass

result = {
    "status": "success",
    "operators": operators_list,
    "total_count": len(operators_list)
}

print(json.dumps(result))
"""
        
        result = self.execute_code(code)
        
        if result.get("status") == "success":
            try:
                output = result.get("output", "")
                import re
                json_match = re.search(r'\{.*\}', output, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    stored = self._store_operators(data.get("operators", []), addon_module)
                    return {
                        "status": "success",
                        "operators_found": len(data.get("operators", [])),
                        "operators_stored": stored,
                        "message": f"Discovered and stored {stored} operators"
                    }
            except Exception as e:
                self.log(f"Error parsing operators: {e}", "ERROR")
        
        return {"status": "error", "message": "Failed to discover operators"}
    
    def _store_operators(self, operators: List[Dict], addon_module: Optional[str] = None):
        """Store operators in database"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        stored = 0
        
        for op in operators:
            op_id = op.get("operator_id", "")
            if not op_id:
                continue
            
            # Try to determine addon module from operator path
            module = addon_module
            if not module:
                # Extract from operator category or path
                category = op.get("category", "")
                # This is a simplified approach - could be improved
                module = category if category else "unknown"
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO addon_operators
                    (addon_module, operator_id, operator_name, operator_description,
                     operator_category, parameters, usage_count, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    module,
                    op_id,
                    op.get("operator_name", ""),
                    op.get("description", ""),
                    op.get("category", ""),
                    json.dumps(op.get("parameters", {})),
                    0,
                    None
                ))
                stored += 1
            except Exception as e:
                self.log(f"Error storing operator {op_id}: {e}", "ERROR")
        
        conn.commit()
        conn.close()
        return stored
    
    def execute_addon_operator(self, operator_id: str, parameters: Optional[Dict] = None) -> Dict:
        """Execute an addon operator"""
        self.log(f"Executing operator: {operator_id}")
        
        start_time = time.time()
        params = parameters or {}
        
        # Build code to execute operator
        code = f"""
import bpy
import json

operator_id = "{operator_id}"
params = {json.dumps(params)}

try:
    # Get operator
    op_path = operator_id.split('.')
    op = bpy.ops
    for part in op_path:
        op = getattr(op, part)
    
    # Execute with parameters
    result = op(**params)
    
    execution_result = {{
        "status": "success",
        "operator_id": operator_id,
        "result": str(result),
        "message": "Operator executed successfully"
    }}
except Exception as e:
    execution_result = {{
        "status": "error",
        "operator_id": operator_id,
        "error": str(e),
        "message": f"Failed to execute operator: {{str(e)}}"
    }}

print(json.dumps(execution_result))
"""
        
        result = self.execute_code(code)
        execution_time = time.time() - start_time
        
        # Store operation in database
        self._log_operation(operator_id, "execute", params, result, execution_time)
        
        # Update operator usage stats
        self._update_operator_stats(operator_id, result.get("status") == "success")
        
        return {
            "status": result.get("status", "error"),
            "operator_id": operator_id,
            "execution_time": execution_time,
            "result": result,
            "message": result.get("message", "")
        }
    
    def _log_operation(self, addon_module: str, operation_name: str, 
                      parameters: Dict, result: Dict, execution_time: float):
        """Log addon operation to database"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO addon_operations
            (addon_module, operation_name, operation_type, parameters, result,
             execution_time, success, error_message, timestamp, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            addon_module,
            operation_name,
            "operator_execution",
            json.dumps(parameters),
            json.dumps(result),
            execution_time,
            1 if result.get("status") == "success" else 0,
            result.get("error", ""),
            datetime.now().isoformat(),
            json.dumps({"session": "default"})
        ))
        
        conn.commit()
        conn.close()
    
    def _update_operator_stats(self, operator_id: str, success: bool):
        """Update operator usage statistics"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        # Extract module from operator_id
        module = operator_id.split('.')[0] if '.' in operator_id else "unknown"
        
        cursor.execute("""
            UPDATE addon_operators
            SET usage_count = usage_count + 1,
                last_used = ?
            WHERE operator_id = ?
        """, (datetime.now().isoformat(), operator_id))
        
        # Update addon stats
        cursor.execute("""
            UPDATE installed_addons
            SET usage_count = usage_count + 1,
                last_used = ?,
                success_count = success_count + ?,
                error_count = error_count + ?
            WHERE module = ?
        """, (datetime.now().isoformat(), 1 if success else 0, 0 if success else 1, module))
        
        conn.commit()
        conn.close()
    
    def get_installed_addons(self, enabled_only: bool = False) -> Dict:
        """Get list of installed addons from database"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        if enabled_only:
            cursor.execute("""
                SELECT module, name, display_name, enabled, version, category,
                       usage_count, last_used
                FROM installed_addons
                WHERE enabled = 1
                ORDER BY name
            """)
        else:
            cursor.execute("""
                SELECT module, name, display_name, enabled, version, category,
                       usage_count, last_used
                FROM installed_addons
                ORDER BY name
            """)
        
        addons = []
        for row in cursor.fetchall():
            addons.append({
                "module": row[0],
                "name": row[1],
                "display_name": row[2],
                "enabled": bool(row[3]),
                "version": row[4],
                "category": row[5],
                "usage_count": row[6],
                "last_used": row[7]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "addons": addons,
            "count": len(addons),
            "enabled_count": sum(1 for a in addons if a["enabled"])
        }
    
    def get_addon_info(self, addon_module: str) -> Dict:
        """Get detailed information about a specific addon"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM installed_addons WHERE module = ?
        """, (addon_module,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {"status": "error", "message": f"Addon '{addon_module}' not found"}
        
        return {
            "status": "success",
            "module": row[1],
            "name": row[2],
            "display_name": row[3],
            "description": row[4],
            "author": row[5],
            "version": row[6],
            "category": row[7],
            "location": row[8],
            "enabled": bool(row[9]),
            "installed_date": row[10],
            "last_used": row[11],
            "usage_count": row[12],
            "success_count": row[13],
            "error_count": row[14],
            "bl_info": json.loads(row[15] or "{}"),
            "preferences": json.loads(row[16] or "{}"),
            "dependencies": json.loads(row[17] or "[]"),
            "requirements": json.loads(row[18] or "[]")
        }
    
    def get_operation_history(self, addon_module: Optional[str] = None, limit: int = 50) -> Dict:
        """Get operation history"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        if addon_module:
            cursor.execute("""
                SELECT * FROM addon_operations
                WHERE addon_module = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (addon_module, limit))
        else:
            cursor.execute("""
                SELECT * FROM addon_operations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        operations = []
        for row in cursor.fetchall():
            operations.append({
                "id": row[0],
                "addon_module": row[1],
                "operation_name": row[2],
                "operation_type": row[3],
                "parameters": json.loads(row[4] or "{}"),
                "result": json.loads(row[5] or "{}"),
                "execution_time": row[6],
                "success": bool(row[7]),
                "error_message": row[8],
                "timestamp": row[9]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "operations": operations,
            "count": len(operations)
        }
    
    def execute_task(self, description: str) -> Dict:
        """Execute addon executor task"""
        self.log(f"AddonExecutor executing: {description}")
        
        description_lower = description.lower()
        
        # Scan and store addons
        if any(keyword in description_lower for keyword in 
               ['scan addons', 'store addons', 'update addon database', 'refresh addon database']):
            return self.scan_and_store_addons()
        
        # Discover operators
        if any(keyword in description_lower for keyword in 
               ['discover operators', 'find operators', 'list operators', 'scan operators']):
            addon_module = self._extract_addon_module(description)
            return self.discover_addon_operators(addon_module)
        
        # Get installed addons
        if any(keyword in description_lower for keyword in 
               ['list installed addons', 'get installed addons', 'show addons', 'installed addons']):
            enabled_only = 'enabled' in description_lower
            return self.get_installed_addons(enabled_only)
        
        # Get addon info
        if any(keyword in description_lower for keyword in 
               ['addon info', 'addon details', 'info about addon']):
            addon_module = self._extract_addon_module(description)
            if addon_module:
                return self.get_addon_info(addon_module)
            return {"status": "error", "message": "Addon module not specified"}
        
        # Execute operator
        if any(keyword in description_lower for keyword in 
               ['execute operator', 'run operator', 'call operator', 'run addon']):
            operator_id = self._extract_operator_id(description)
            if operator_id:
                params = self._extract_parameters(description)
                return self.execute_addon_operator(operator_id, params)
            return {"status": "error", "message": "Operator ID not specified"}
        
        # Get operation history
        if any(keyword in description_lower for keyword in 
               ['operation history', 'execution history', 'history', 'log']):
            addon_module = self._extract_addon_module(description)
            limit = self._extract_limit(description, default=50)
            return self.get_operation_history(addon_module, limit)
        
        # Default: scan and store addons
        return self.scan_and_store_addons()
    
    def _extract_addon_module(self, description: str) -> Optional[str]:
        """Extract addon module name from description"""
        import re
        # Try quoted strings
        quoted = re.findall(r'["\']([^"\']+)["\']', description)
        if quoted:
            return quoted[0]
        
        # Try after keywords
        words = description.split()
        for i, word in enumerate(words):
            if word.lower() in ['addon', 'module'] and i + 1 < len(words):
                return words[i + 1]
        
        return None
    
    def _extract_operator_id(self, description: str) -> Optional[str]:
        """Extract operator ID from description"""
        import re
        # Look for patterns like "operator_name" or "category.operator"
        quoted = re.findall(r'["\']([^"\']+)["\']', description)
        if quoted:
            return quoted[0]
        
        # Try to find operator pattern
        op_match = re.search(r'(\w+\.\w+)', description)
        if op_match:
            return op_match.group(1)
        
        return None
    
    def _extract_parameters(self, description: str) -> Dict:
        """Extract parameters from description (simplified)"""
        # This is a simplified extraction - could be enhanced with NLP
        params = {}
        # Look for key=value patterns
        import re
        kv_pairs = re.findall(r'(\w+)=([^\s,]+)', description)
        for key, value in kv_pairs:
            # Try to convert to appropriate type
            try:
                if value.lower() in ['true', 'false']:
                    params[key] = value.lower() == 'true'
                elif value.replace('.', '').isdigit():
                    params[key] = float(value) if '.' in value else int(value)
                else:
                    params[key] = value
            except:
                params[key] = value
        
        return params
    
    def _extract_limit(self, description: str, default: int = 50) -> int:
        """Extract limit number from description"""
        import re
        numbers = re.findall(r'\d+', description)
        if numbers:
            return int(numbers[0])
        return default



