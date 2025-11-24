# data_collector.py - Data Collection System for Blender-Ollama Agent
"""
Collects and stores data about:
- Blender operations and their success rates
- Code generation patterns from different models
- Error patterns and solutions
- Scene states and transitions
- Model performance metrics
"""

import json
import sqlite3
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class OperationRecord:
    """Record of a Blender operation"""
    id: str
    timestamp: str
    description: str
    model_used: str
    generated_code: str
    execution_result: Dict
    scene_before: Dict
    scene_after: Dict
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class ModelPerformance:
    """Performance metrics for a model"""
    model_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    timeout_count: int
    average_generation_time: float
    average_code_length: float
    success_rate: float


@dataclass
class CodePattern:
    """Pattern of successful code generation"""
    pattern_hash: str
    description_pattern: str
    code_template: str
    success_count: int
    failure_count: int
    models_used: List[str]


class BlenderDataCollector:
    """
    Collects and stores data about Blender operations for building
    a knowledge base and improving the agent.
    """
    
    def __init__(self, db_path: str = "blender_data.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                description TEXT NOT NULL,
                model_used TEXT NOT NULL,
                generated_code TEXT NOT NULL,
                execution_result TEXT NOT NULL,
                scene_before TEXT NOT NULL,
                scene_after TEXT NOT NULL,
                execution_time REAL NOT NULL,
                success INTEGER NOT NULL,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0
            )
        """)
        
        # Model performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                model_name TEXT PRIMARY KEY,
                total_requests INTEGER DEFAULT 0,
                successful_requests INTEGER DEFAULT 0,
                failed_requests INTEGER DEFAULT 0,
                timeout_count INTEGER DEFAULT 0,
                total_generation_time REAL DEFAULT 0,
                total_code_length INTEGER DEFAULT 0,
                last_updated TEXT NOT NULL
            )
        """)
        
        # Code patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_patterns (
                pattern_hash TEXT PRIMARY KEY,
                description_pattern TEXT NOT NULL,
                code_template TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                models_used TEXT NOT NULL,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)
        
        # Error patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_message TEXT NOT NULL,
                error_type TEXT,
                operation_description TEXT,
                model_used TEXT,
                generated_code TEXT,
                solution TEXT,
                frequency INTEGER DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL
            )
        """)
        
        # Scene transitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scene_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                operation_description TEXT NOT NULL,
                code_used TEXT NOT NULL,
                success INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        # Blender API reference table (from documentation)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blender_api_reference (
                api_call TEXT PRIMARY KEY,
                description TEXT,
                parameters TEXT,
                return_type TEXT,
                version_added TEXT,
                version_deprecated TEXT,
                examples TEXT,
                category TEXT
            )
        """)
        
        self.conn.commit()
    
    def record_operation(self, record: OperationRecord):
        """Record a Blender operation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO operations VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            record.id,
            record.timestamp,
            record.description,
            record.model_used,
            record.generated_code,
            json.dumps(record.execution_result),
            json.dumps(record.scene_before),
            json.dumps(record.scene_after),
            record.execution_time,
            1 if record.success else 0,
            record.error_message,
            record.retry_count
        ))
        
        # Update model performance
        self._update_model_performance(record.model_used, record.success, record.execution_time, len(record.generated_code))
        
        # Extract and store code pattern
        self._extract_code_pattern(record)
        
        # Store error if failed
        if not record.success and record.error_message:
            self._record_error_pattern(record)
        
        # Store scene transition
        self._record_scene_transition(record)
        
        self.conn.commit()
    
    def _update_model_performance(self, model_name: str, success: bool, 
                                 execution_time: float, code_length: int):
        """Update model performance metrics"""
        cursor = self.conn.cursor()
        
        # Get current stats
        cursor.execute("SELECT * FROM model_performance WHERE model_name = ?", (model_name,))
        row = cursor.fetchone()
        
        if row:
            total_req, success_req, failed_req, timeout, total_time, total_len, _ = row[1:]
            total_req += 1
            if success:
                success_req += 1
            else:
                failed_req += 1
            total_time += execution_time
            total_len += code_length
            
            cursor.execute("""
                UPDATE model_performance SET
                    total_requests = ?,
                    successful_requests = ?,
                    failed_requests = ?,
                    total_generation_time = ?,
                    total_code_length = ?,
                    last_updated = ?
                WHERE model_name = ?
            """, (total_req, success_req, failed_req, total_time, total_len, 
                  datetime.now().isoformat(), model_name))
        else:
            cursor.execute("""
                INSERT INTO model_performance VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (model_name, 1, 1 if success else 0, 0 if success else 1, 
                  0, execution_time, code_length, datetime.now().isoformat()))
    
    def _extract_code_pattern(self, record: OperationRecord):
        """Extract and store code patterns from successful operations"""
        if not record.success:
            return
        
        # Create a pattern hash from code structure (simplified)
        code_lines = record.generated_code.split('\n')
        # Remove comments and normalize
        code_structure = [line.strip() for line in code_lines 
                         if line.strip() and not line.strip().startswith('#')]
        pattern_str = '\n'.join(code_structure[:10])  # First 10 lines as pattern
        
        pattern_hash = hashlib.md5(pattern_str.encode()).hexdigest()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM code_patterns WHERE pattern_hash = ?", (pattern_hash,))
        row = cursor.fetchone()
        
        if row:
            success_count, failure_count, models_used = row[3], row[4], json.loads(row[5])
            success_count += 1
            if record.model_used not in models_used:
                models_used.append(record.model_used)
            
            cursor.execute("""
                UPDATE code_patterns SET
                    success_count = ?,
                    models_used = ?,
                    last_seen = ?
                WHERE pattern_hash = ?
            """, (success_count, json.dumps(models_used), 
                  datetime.now().isoformat(), pattern_hash))
        else:
            cursor.execute("""
                INSERT INTO code_patterns VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pattern_hash, record.description, pattern_str, 1, 0,
                  json.dumps([record.model_used]), datetime.now().isoformat(),
                  datetime.now().isoformat()))
    
    def _record_error_pattern(self, record: OperationRecord):
        """Record error patterns for analysis"""
        cursor = self.conn.cursor()
        
        # Check if similar error exists
        error_type = self._classify_error(record.error_message)
        cursor.execute("""
            SELECT id, frequency FROM error_patterns 
            WHERE error_message = ? AND error_type = ?
            LIMIT 1
        """, (record.error_message, error_type))
        
        row = cursor.fetchone()
        if row:
            error_id, frequency = row
            cursor.execute("""
                UPDATE error_patterns SET
                    frequency = ?,
                    last_seen = ?
                WHERE id = ?
            """, (frequency + 1, datetime.now().isoformat(), error_id))
        else:
            cursor.execute("""
                INSERT INTO error_patterns 
                (error_message, error_type, operation_description, model_used, 
                 generated_code, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (record.error_message, error_type, record.description,
                  record.model_used, record.generated_code,
                  datetime.now().isoformat(), datetime.now().isoformat()))
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type"""
        error_lower = error_message.lower()
        if "timeout" in error_lower:
            return "timeout"
        elif "syntax" in error_lower or "parse" in error_lower:
            return "syntax_error"
        elif "attribute" in error_lower or "has no attribute" in error_lower:
            return "attribute_error"
        elif "type" in error_lower and "error" in error_lower:
            return "type_error"
        elif "connection" in error_lower or "connect" in error_lower:
            return "connection_error"
        else:
            return "unknown"
    
    def _record_scene_transition(self, record: OperationRecord):
        """Record scene state transitions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO scene_transitions 
            (from_state, to_state, operation_description, code_used, success, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            json.dumps(record.scene_before),
            json.dumps(record.scene_after),
            record.description,
            record.generated_code,
            1 if record.success else 0,
            record.timestamp
        ))
    
    def get_model_performance(self, model_name: Optional[str] = None) -> List[ModelPerformance]:
        """Get performance metrics for models"""
        cursor = self.conn.cursor()
        
        if model_name:
            cursor.execute("SELECT * FROM model_performance WHERE model_name = ?", (model_name,))
            rows = [cursor.fetchone()]
        else:
            cursor.execute("SELECT * FROM model_performance")
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            if row:
                model_name, total_req, success_req, failed_req, timeout, total_time, total_len, _ = row
                avg_time = total_time / total_req if total_req > 0 else 0
                avg_len = total_len / total_req if total_req > 0 else 0
                success_rate = success_req / total_req if total_req > 0 else 0
                
                results.append(ModelPerformance(
                    model_name=model_name,
                    total_requests=total_req,
                    successful_requests=success_req,
                    failed_requests=failed_req,
                    timeout_count=timeout or 0,
                    average_generation_time=avg_time,
                    average_code_length=avg_len,
                    success_rate=success_rate
                ))
        
        return results
    
    def get_successful_patterns(self, limit: int = 10) -> List[CodePattern]:
        """Get most successful code patterns"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM code_patterns 
            ORDER BY success_count DESC, failure_count ASC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        results = []
        for row in rows:
            pattern_hash, desc_pattern, code_template, success_count, failure_count, models_used, _, _ = row
            results.append(CodePattern(
                pattern_hash=pattern_hash,
                description_pattern=desc_pattern,
                code_template=code_template,
                success_count=success_count,
                failure_count=failure_count,
                models_used=json.loads(models_used)
            ))
        
        return results
    
    def get_common_errors(self, limit: int = 10) -> List[Dict]:
        """Get most common errors"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT error_message, error_type, frequency, solution
            FROM error_patterns
            ORDER BY frequency DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [
            {
                "error_message": row[0],
                "error_type": row[1],
                "frequency": row[2],
                "solution": row[3]
            }
            for row in rows
        ]
    
    def add_blender_api_reference(self, api_calls: List[Dict]):
        """Add Blender API reference data from documentation"""
        cursor = self.conn.cursor()
        for api_call in api_calls:
            cursor.execute("""
                INSERT OR REPLACE INTO blender_api_reference VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api_call.get("api_call"),
                api_call.get("description"),
                json.dumps(api_call.get("parameters", {})),
                api_call.get("return_type"),
                api_call.get("version_added"),
                api_call.get("version_deprecated"),
                json.dumps(api_call.get("examples", [])),
                api_call.get("category")
            ))
        self.conn.commit()
    
    def search_similar_operations(self, description: str, limit: int = 5) -> List[Dict]:
        """Find similar successful operations"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT description, generated_code, execution_result, success
            FROM operations
            WHERE description LIKE ? AND success = 1
            ORDER BY timestamp DESC
            LIMIT ?
        """, (f"%{description}%", limit))
        
        rows = cursor.fetchall()
        return [
            {
                "description": row[0],
                "code": row[1],
                "result": json.loads(row[2]),
                "success": bool(row[3])
            }
            for row in rows
        ]
    
    def export_data(self, output_path: str):
        """Export all data to JSON for analysis"""
        data = {
            "model_performance": [asdict(mp) for mp in self.get_model_performance()],
            "successful_patterns": [asdict(cp) for cp in self.get_successful_patterns(20)],
            "common_errors": self.get_common_errors(20),
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage and testing
if __name__ == "__main__":
    collector = BlenderDataCollector()
    
    # Example: Record a test operation
    test_record = OperationRecord(
        id="test_001",
        timestamp=datetime.now().isoformat(),
        description="Create a cube",
        model_used="gemma3:4b",
        generated_code="import bpy\nbpy.ops.mesh.primitive_cube_add(location=(0,0,0))",
        execution_result={"status": "success", "result": {"executed": True}},
        scene_before={"object_count": 0},
        scene_after={"object_count": 1},
        execution_time=0.5,
        success=True
    )
    
    collector.record_operation(test_record)
    
    # Get performance stats
    print("Model Performance:")
    for perf in collector.get_model_performance():
        print(f"  {perf.model_name}: {perf.success_rate:.2%} success rate")
    
    # Export data
    collector.export_data("blender_data_export.json")
    print("\nData exported to blender_data_export.json")
    
    collector.close()

