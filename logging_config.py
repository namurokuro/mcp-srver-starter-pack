"""
Structured JSON Logging Configuration for MCP Server
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "mcp-server",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add thread/process info if available
        if record.threadName:
            log_entry["thread"] = record.threadName
        if record.processName:
            log_entry["process"] = record.processName
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            log_entry["exception_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        
        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add context if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'tool_name'):
            log_entry["tool_name"] = record.tool_name
        
        return json.dumps(log_entry, ensure_ascii=False)

class MCPLogger:
    """MCP Server Logger with structured logging"""
    
    def __init__(self, name: str = "mcp_server", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler with JSON formatter
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler for persistent logs (optional)
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(
            log_dir / f"mcp-server-{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional extra fields"""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional extra fields"""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self.logger.error(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional extra fields"""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self.logger.warning(message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional extra fields"""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self.logger.debug(message, extra=extra)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self.logger.exception(message, extra=extra)
    
    def log_request(self, method: str, request_id: str = None, **kwargs):
        """Log MCP request"""
        extra = {
            "request_id": request_id,
            "method": method,
            "extra_fields": kwargs
        }
        self.logger.info(f"MCP Request: {method}", extra=extra)
    
    def log_tool_call(self, tool_name: str, request_id: str = None, **kwargs):
        """Log tool execution"""
        extra = {
            "request_id": request_id,
            "tool_name": tool_name,
            "extra_fields": kwargs
        }
        self.logger.info(f"Tool Call: {tool_name}", extra=extra)

# Global logger instance
_logger_instance = None

def get_logger(name: str = "mcp_server", log_level: str = None) -> MCPLogger:
    """Get or create logger instance"""
    global _logger_instance
    if _logger_instance is None:
        log_level = log_level or "INFO"
        _logger_instance = MCPLogger(name, log_level)
    return _logger_instance

# Convenience functions
def setup_logging(log_level: str = "INFO"):
    """Setup logging for the application"""
    return get_logger("mcp_server", log_level)

def log_info(message: str, **kwargs):
    """Log info message"""
    get_logger().info(message, **kwargs)

def log_error(message: str, **kwargs):
    """Log error message"""
    get_logger().error(message, **kwargs)

def log_warning(message: str, **kwargs):
    """Log warning message"""
    get_logger().warning(message, **kwargs)

def log_debug(message: str, **kwargs):
    """Log debug message"""
    get_logger().debug(message, **kwargs)

