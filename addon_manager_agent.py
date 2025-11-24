"""
Addon Manager Agent - Scrapes installed Blender addons and builds control protocols
"""

import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from specialized_agents import BaseBlenderSpecialist, OperationRecord
from data_collector import BlenderDataCollector


class AddonManagerSpecialist(BaseBlenderSpecialist):
    """Specialist for managing Blender addons - scraping and control protocols"""
    
    def __init__(self, **kwargs):
        super().__init__("AddonManager", **kwargs)
        self.addons_db_path = "addons_data.db"
        self._init_addons_database()
        self.addons_cache = {}
        self.control_protocols = {}
    
    def _init_addons_database(self):
        """Initialize database for storing addon information"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        # Addons table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS addons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT UNIQUE NOT NULL,
                name TEXT,
                description TEXT,
                author TEXT,
                version TEXT,
                enabled INTEGER DEFAULT 0,
                location TEXT,
                category TEXT,
                first_scraped TEXT,
                last_updated TEXT,
                metadata TEXT
            )
        """)
        
        # Control protocols table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS control_protocols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addon_module TEXT NOT NULL,
                protocol_name TEXT NOT NULL,
                protocol_type TEXT NOT NULL,
                code_template TEXT NOT NULL,
                parameters TEXT,
                description TEXT,
                created_at TEXT,
                last_used TEXT,
                usage_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                FOREIGN KEY (addon_module) REFERENCES addons(module)
            )
        """)
        
        # Addon operations log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS addon_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addon_module TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                operation_data TEXT,
                timestamp TEXT,
                success INTEGER DEFAULT 0,
                error_message TEXT,
                FOREIGN KEY (addon_module) REFERENCES addons(module)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_system_prompt(self) -> str:
        return """You are a Blender Addon Manager expert specializing in:
- Scraping and cataloging installed Blender addons
- Extracting addon metadata (name, version, author, description)
- Building control protocols for addon management
- Enabling/disabling addons programmatically
- Configuring addon preferences
- Managing addon dependencies
- Creating addon operation templates
- Monitoring addon status and changes

Generate Python code for addon management operations.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Common addon management operations:
- bpy.context.preferences.addons - Access installed addons
- addon = bpy.context.preferences.addons.get('addon_module')
- addon.module - Addon module name
- addon.name - Addon display name
- bpy.ops.preferences.addon_enable(module='addon_module')
- bpy.ops.preferences.addon_disable(module='addon_module')
- bpy.ops.preferences.addon_install(filepath='path/to/addon.py')
- bpy.ops.preferences.addon_refresh()
- addon.preferences - Access addon preferences
- bpy.utils.addon_utils.module_bl_info(module) - Get addon info

Addon scraping:
- Iterate through bpy.context.preferences.addons
- Extract module, name, description, author, version
- Check enabled status
- Get addon location and category
- Store metadata in database

Control protocol building:
- Create enable/disable protocols
- Build configuration protocols
- Create operation templates
- Generate code for common addon operations"""
    
    def scrape_addons(self) -> Dict:
        """Scrape all installed addons from Blender"""
        self.log("Scraping installed addons...")
        
        code = """
import bpy
import json
import importlib

addons_data = []

# Get all installed addons
for module_name in bpy.context.preferences.addons.keys():
    addon = bpy.context.preferences.addons[module_name]
    
    # Get addon info
    addon_info = {
        "module": module_name,
        "name": getattr(addon, 'name', module_name),
        "enabled": True,
        "location": getattr(addon, 'filepath', ''),
        "description": "",
        "author": "",
        "version": "",
        "category": ""
    }
    
    # Try to get bl_info from the addon module
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'bl_info'):
            bl_info = module.bl_info
            addon_info.update({
                "name": bl_info.get('name', addon_info['name']),
                "description": bl_info.get('description', ''),
                "author": bl_info.get('author', ''),
                "version": str(bl_info.get('version', ())),
                "category": bl_info.get('category', ''),
            })
    except Exception:
        pass  # If we can't import, just use basic info
    
    addons_data.append(addon_info)

result = {
    "status": "success",
    "addons": addons_data,
    "total_count": len(addons_data),
    "enabled_count": len(addons_data)
}

print(json.dumps(result))
"""
        
        result = self.execute_code(code)
        
        if result.get("status") == "success":
            # Parse the result
            try:
                output = result.get("output", "")
                if output:
                    # Try to extract JSON from output
                    import re
                    json_match = re.search(r'\{.*\}', output, re.DOTALL)
                    if json_match:
                        addons_data = json.loads(json_match.group())
                        self._store_addons(addons_data.get("addons", []))
                        return {
                            "status": "success",
                            "addons": addons_data.get("addons", []),
                            "total_count": addons_data.get("total_count", 0),
                            "enabled_count": addons_data.get("enabled_count", 0),
                            "message": f"Scraped {addons_data.get('total_count', 0)} addons"
                        }
            except Exception as e:
                self.log(f"Error parsing addon data: {e}", "ERROR")
        
        # Fallback: try simpler scraping
        return self._scrape_addons_simple()
    
    def _scrape_addons_simple(self) -> Dict:
        """Simpler addon scraping method"""
        code = """
import bpy
import json

addons_list = []
for module_name in bpy.context.preferences.addons.keys():
    addon = bpy.context.preferences.addons[module_name]
    addon_data = {
        "module": module_name,
        "name": getattr(addon, 'name', module_name),
        "enabled": True,
    }
    addons_list.append(addon_data)

result = {
    "status": "success",
    "addons": addons_list,
    "total_count": len(addons_list)
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
                    self._store_addons(data.get("addons", []))
                    return data
            except Exception as e:
                self.log(f"Error in simple scraping: {e}", "ERROR")
        
        return {"status": "error", "message": "Failed to scrape addons"}
    
    def _store_addons(self, addons: List[Dict]):
        """Store scraped addons in database"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        for addon in addons:
            module = addon.get("module", "")
            if not module:
                continue
            
            cursor.execute("""
                INSERT OR REPLACE INTO addons 
                (module, name, description, author, version, enabled, location, category, 
                 first_scraped, last_updated, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                module,
                addon.get("name", ""),
                addon.get("description", ""),
                addon.get("author", ""),
                str(addon.get("version", "")),
                1 if addon.get("enabled", False) else 0,
                addon.get("location", ""),
                addon.get("category", ""),
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                json.dumps(addon)
            ))
        
        conn.commit()
        conn.close()
        self.log(f"Stored {len(addons)} addons in database")
    
    def build_control_protocols(self, addon_module: Optional[str] = None) -> Dict:
        """Build control protocols for addons"""
        self.log("Building control protocols...")
        
        # Get addons from database
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        if addon_module:
            cursor.execute("SELECT * FROM addons WHERE module = ?", (addon_module,))
        else:
            cursor.execute("SELECT * FROM addons")
        
        addons = cursor.fetchall()
        conn.close()
        
        protocols_created = []
        
        for addon_row in addons:
            module = addon_row[1]  # module is at index 1
            name = addon_row[2]  # name is at index 2
            
            # Build basic control protocols
            protocols = self._create_basic_protocols(module, name)
            
            for protocol in protocols:
                self._store_protocol(module, protocol)
                protocols_created.append(protocol)
        
        return {
            "status": "success",
            "protocols_created": len(protocols_created),
            "protocols": protocols_created,
            "message": f"Created {len(protocols_created)} control protocols"
        }
    
    def _create_basic_protocols(self, module: str, name: str) -> List[Dict]:
        """Create basic control protocols for an addon"""
        protocols = []
        
        # Enable protocol
        enable_protocol = {
            "protocol_name": "enable",
            "protocol_type": "enable",
            "code_template": f"""
import bpy
import json
try:
    bpy.ops.preferences.addon_enable(module='{module}')
    result = {{"status": "success", "message": "Addon '{name}' enabled"}}
except Exception as e:
    result = {{"status": "error", "message": str(e)}}
print(json.dumps(result))
""",
            "parameters": json.dumps({"module": module}),
            "description": f"Enable addon {name}",
            "created_at": datetime.now().isoformat()
        }
        protocols.append(enable_protocol)
        
        # Disable protocol
        disable_protocol = {
            "protocol_name": "disable",
            "protocol_type": "disable",
            "code_template": f"""
import bpy
import json
try:
    bpy.ops.preferences.addon_disable(module='{module}')
    result = {{"status": "success", "message": "Addon '{name}' disabled"}}
except Exception as e:
    result = {{"status": "error", "message": str(e)}}
print(json.dumps(result))
""",
            "parameters": json.dumps({"module": module}),
            "description": f"Disable addon {name}",
            "created_at": datetime.now().isoformat()
        }
        protocols.append(disable_protocol)
        
        # Get status protocol
        status_protocol = {
            "protocol_name": "get_status",
            "protocol_type": "query",
            "code_template": f"""
import bpy
import json
try:
    addon = bpy.context.preferences.addons.get('{module}')
    if addon:
        result = {{
            "status": "success",
            "module": "{module}",
            "name": "{name}",
            "enabled": True
        }}
    else:
        result = {{
            "status": "success",
            "module": "{module}",
            "enabled": False
        }}
except Exception as e:
    result = {{"status": "error", "message": str(e)}}
print(json.dumps(result))
""",
            "parameters": json.dumps({"module": module}),
            "description": f"Get status of addon {name}",
            "created_at": datetime.now().isoformat()
        }
        protocols.append(status_protocol)
        
        # Refresh protocol
        refresh_protocol = {
            "protocol_name": "refresh",
            "protocol_type": "refresh",
            "code_template": f"""
import bpy
import json
try:
    bpy.ops.preferences.addon_refresh()
    result = {{"status": "success", "message": "Addons refreshed"}}
except Exception as e:
    result = {{"status": "error", "message": str(e)}}
print(json.dumps(result))
""",
            "parameters": json.dumps({}),
            "description": "Refresh addon list",
            "created_at": datetime.now().isoformat()
        }
        protocols.append(refresh_protocol)
        
        return protocols
    
    def _store_protocol(self, addon_module: str, protocol: Dict):
        """Store a control protocol in database"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO control_protocols
            (addon_module, protocol_name, protocol_type, code_template, parameters, 
             description, created_at, last_used, usage_count, success_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            addon_module,
            protocol["protocol_name"],
            protocol["protocol_type"],
            protocol["code_template"],
            protocol.get("parameters", "{}"),
            protocol.get("description", ""),
            protocol.get("created_at", datetime.now().isoformat()),
            None,
            0,
            0
        ))
        
        conn.commit()
        conn.close()
    
    def execute_protocol(self, addon_module: str, protocol_name: str, params: Optional[Dict] = None) -> Dict:
        """Execute a control protocol for an addon"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT code_template, parameters FROM control_protocols
            WHERE addon_module = ? AND protocol_name = ?
        """, (addon_module, protocol_name))
        
        protocol = cursor.fetchone()
        conn.close()
        
        if not protocol:
            return {
                "status": "error",
                "message": f"Protocol '{protocol_name}' not found for addon '{addon_module}'"
            }
        
        code_template = protocol[0]
        stored_params = json.loads(protocol[1] or "{}")
        
        # Merge parameters
        if params:
            stored_params.update(params)
        
        # Replace parameters in code template
        code = code_template
        for key, value in stored_params.items():
            code = code.replace(f"{{{key}}}", str(value))
        
        # Execute the protocol
        result = self.execute_code(code)
        
        # Update protocol usage stats
        self._update_protocol_stats(addon_module, protocol_name, result.get("status") == "success")
        
        return result
    
    def _update_protocol_stats(self, addon_module: str, protocol_name: str, success: bool):
        """Update protocol usage statistics"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE control_protocols
            SET last_used = ?, usage_count = usage_count + 1,
                success_count = success_count + ?
            WHERE addon_module = ? AND protocol_name = ?
        """, (datetime.now().isoformat(), 1 if success else 0, addon_module, protocol_name))
        
        conn.commit()
        conn.close()
    
    def get_addons_list(self) -> Dict:
        """Get list of all scraped addons"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT module, name, enabled, description, author, version, category
            FROM addons
            ORDER BY name
        """)
        
        addons = []
        for row in cursor.fetchall():
            addons.append({
                "module": row[0],
                "name": row[1],
                "enabled": bool(row[2]),
                "description": row[2],
                "author": row[4],
                "version": row[5],
                "category": row[6]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "addons": addons,
            "count": len(addons)
        }
    
    def get_protocols(self, addon_module: Optional[str] = None) -> Dict:
        """Get control protocols"""
        conn = sqlite3.connect(self.addons_db_path)
        cursor = conn.cursor()
        
        if addon_module:
            cursor.execute("""
                SELECT addon_module, protocol_name, protocol_type, description, 
                       usage_count, success_count
                FROM control_protocols
                WHERE addon_module = ?
                ORDER BY protocol_name
            """, (addon_module,))
        else:
            cursor.execute("""
                SELECT addon_module, protocol_name, protocol_type, description,
                       usage_count, success_count
                FROM control_protocols
                ORDER BY addon_module, protocol_name
            """)
        
        protocols = []
        for row in cursor.fetchall():
            protocols.append({
                "addon_module": row[0],
                "protocol_name": row[1],
                "protocol_type": row[2],
                "description": row[3],
                "usage_count": row[4],
                "success_count": row[5]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "protocols": protocols,
            "count": len(protocols)
        }
    
    def execute_task(self, description: str) -> Dict:
        """Execute addon management task"""
        self.log(f"AddonManager executing: {description}")
        
        description_lower = description.lower()
        
        # Scrape addons
        if any(keyword in description_lower for keyword in 
               ['scrape', 'scan', 'list addons', 'get addons', 'find addons']):
            return self.scrape_addons()
        
        # Build protocols
        if any(keyword in description_lower for keyword in 
               ['build protocol', 'create protocol', 'generate protocol', 'control protocol']):
            # Try to extract addon module from description
            addon_module = None
            words = description.split()
            for i, word in enumerate(words):
                if word.lower() in ['for', 'addon', 'module'] and i + 1 < len(words):
                    addon_module = words[i + 1]
                    break
            return self.build_control_protocols(addon_module)
        
        # Get addons list
        if any(keyword in description_lower for keyword in 
               ['show addons', 'list', 'get list', 'all addons']):
            return self.get_addons_list()
        
        # Get protocols
        if any(keyword in description_lower for keyword in 
               ['show protocols', 'list protocols', 'get protocols']):
            addon_module = None
            words = description.split()
            for i, word in enumerate(words):
                if word.lower() in ['for', 'addon', 'module'] and i + 1 < len(words):
                    addon_module = words[i + 1]
                    break
            return self.get_protocols(addon_module)
        
        # Enable addon
        if 'enable' in description_lower and 'addon' in description_lower:
            # Extract addon module
            addon_module = self._extract_addon_module(description)
            if addon_module:
                return self.execute_protocol(addon_module, "enable")
        
        # Disable addon
        if 'disable' in description_lower and 'addon' in description_lower:
            addon_module = self._extract_addon_module(description)
            if addon_module:
                return self.execute_protocol(addon_module, "disable")
        
        # Default: scrape and build protocols
        scrape_result = self.scrape_addons()
        if scrape_result.get("status") == "success":
            protocol_result = self.build_control_protocols()
            return {
                "status": "success",
                "scraping": scrape_result,
                "protocols": protocol_result,
                "message": "Scraped addons and built control protocols"
            }
        
        return scrape_result
    
    def _extract_addon_module(self, description: str) -> Optional[str]:
        """Extract addon module name from description"""
        # Try to find quoted strings
        import re
        quoted = re.findall(r'["\']([^"\']+)["\']', description)
        if quoted:
            return quoted[0]
        
        # Try to find after keywords
        words = description.split()
        for i, word in enumerate(words):
            if word.lower() in ['addon', 'module'] and i + 1 < len(words):
                return words[i + 1]
        
        return None

