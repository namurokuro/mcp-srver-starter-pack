#!/usr/bin/env python3
"""
Thread-Safe Execution Queue for Blender Socket Operations
Adapted from PolyMCP's approach for our socket-based architecture
"""

import queue
import threading
import time
import uuid
import json
import socket
from typing import Dict, Any, Optional, Callable
from datetime import datetime


class ThreadSafeExecutor:
    """Thread-safe execution queue for Blender socket operations"""
    
    def __init__(self, blender_host="localhost", blender_port=9876, max_queue_size=1000):
        self.execution_queue = queue.Queue(maxsize=max_queue_size)
        self.result_store = {}
        self.is_running = False
        self.blender_host = blender_host
        self.blender_port = blender_port
        self.socket = None
        self.socket_lock = threading.Lock()
        self.queue_timeout = 30.0
        self.queue_check_interval = 0.1
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        self.is_running = True
    
    def _connect_to_blender(self) -> bool:
        """Connect to Blender socket server"""
        with self.socket_lock:
            if self.socket:
                try:
                    # Test connection
                    self.socket.send(b'{"type":"ping"}')
                    return True
                except:
                    self.socket = None
            
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(30)
                self.socket.connect((self.blender_host, self.blender_port))
                return True
            except Exception as e:
                self.socket = None
                return False
    
    def _send_command(self, command: Dict) -> Dict:
        """Send command to Blender and get response"""
        if not self._connect_to_blender():
            return {"status": "error", "message": "Failed to connect to Blender"}
        
        try:
            with self.socket_lock:
                self.socket.send(json.dumps(command).encode())
                response = self.socket.recv(65536)
                return json.loads(response.decode())
        except Exception as e:
            self.socket = None  # Reset connection on error
            return {"status": "error", "message": str(e)}
    
    def _worker(self):
        """Worker thread that processes the queue"""
        while self.is_running:
            try:
                # Get task from queue (with timeout)
                try:
                    request = self.execution_queue.get(timeout=self.queue_check_interval)
                except queue.Empty:
                    continue
                
                request_id = request['id']
                operation_type = request['type']
                params = request.get('params', {})
                
                try:
                    # Execute operation
                    if operation_type == "execute_code":
                        command = {
                            "type": "execute_code",
                            "params": params
                        }
                        result = self._send_command(command)
                    elif operation_type == "get_scene_info":
                        command = {
                            "type": "get_scene_info",
                            "params": {}
                        }
                        result = self._send_command(command)
                    else:
                        result = {"status": "error", "message": f"Unknown operation type: {operation_type}"}
                    
                    # Store result
                    self.result_store[request_id] = {
                        'status': 'success',
                        'result': result,
                        'timestamp': time.time()
                    }
                    
                except Exception as e:
                    error_details = {
                        'error': str(e),
                        'operation': operation_type,
                        'params': str(params)[:200]
                    }
                    self.result_store[request_id] = {
                        'status': 'error',
                        'error': error_details,
                        'timestamp': time.time()
                    }
                
                # Mark task as done
                self.execution_queue.task_done()
                
                # Clean old results (older than 5 minutes)
                current_time = time.time()
                expired_ids = [
                    rid for rid, data in list(self.result_store.items())
                    if current_time - data['timestamp'] > 300
                ]
                for rid in expired_ids:
                    self.result_store.pop(rid, None)
                    
            except Exception as e:
                # Log error but continue
                print(f"[ThreadSafeExecutor] Worker error: {e}", file=__import__('sys').stderr)
                time.sleep(0.1)
    
    def execute_code(self, code: str) -> Dict:
        """Execute Python code in Blender (thread-safe)"""
        request_id = str(uuid.uuid4())
        
        # Add to queue
        try:
            self.execution_queue.put({
                'id': request_id,
                'type': 'execute_code',
                'params': {'code': code}
            }, timeout=1.0)
        except queue.Full:
            return {"status": "error", "message": "Execution queue is full"}
        
        # Wait for result
        start_time = time.time()
        while time.time() - start_time < self.queue_timeout:
            if request_id in self.result_store:
                result_data = self.result_store.pop(request_id)
                
                if result_data['status'] == 'success':
                    return result_data['result']
                else:
                    return {
                        "status": "error",
                        "message": result_data.get('error', {}).get('error', 'Unknown error')
                    }
            
            time.sleep(self.queue_check_interval)
        
        # Timeout
        self.result_store.pop(request_id, None)
        return {"status": "error", "message": "Operation timeout"}
    
    def get_scene_info(self) -> Dict:
        """Get scene information (thread-safe)"""
        request_id = str(uuid.uuid4())
        
        # Add to queue
        try:
            self.execution_queue.put({
                'id': request_id,
                'type': 'get_scene_info',
                'params': {}
            }, timeout=1.0)
        except queue.Full:
            return {"status": "error", "message": "Execution queue is full"}
        
        # Wait for result
        start_time = time.time()
        while time.time() - start_time < self.queue_timeout:
            if request_id in self.result_store:
                result_data = self.result_store.pop(request_id)
                
                if result_data['status'] == 'success':
                    return result_data['result']
                else:
                    return {
                        "status": "error",
                        "message": result_data.get('error', {}).get('error', 'Unknown error')
                    }
            
            time.sleep(self.queue_check_interval)
        
        # Timeout
        self.result_store.pop(request_id, None)
        return {"status": "error", "message": "Operation timeout"}
    
    def stop(self):
        """Stop the executor"""
        self.is_running = False
        if self.socket:
            with self.socket_lock:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.execution_queue.qsize()
    
    def get_pending_count(self) -> int:
        """Get number of pending operations"""
        return self.execution_queue.qsize() + len(self.result_store)


# Global executor instance
_executor_instance = None
_executor_lock = threading.Lock()


def get_executor(blender_host="localhost", blender_port=9876) -> ThreadSafeExecutor:
    """Get or create global executor instance"""
    global _executor_instance
    
    with _executor_lock:
        if _executor_instance is None:
            _executor_instance = ThreadSafeExecutor(blender_host, blender_port)
        return _executor_instance

