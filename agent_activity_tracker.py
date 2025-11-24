"""
Agent Activity Tracker
Tracks all agent activities, operations, and status for viewport visualization
"""

import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum


class ActivityStatus(Enum):
    """Status of an agent activity"""
    IDLE = "idle"
    STARTING = "starting"
    THINKING = "thinking"
    GENERATING = "generating"
    EXECUTING = "executing"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class AgentActivity:
    """Represents a single agent activity"""
    agent_name: str
    activity_id: str
    status: str
    task_description: str
    start_time: float
    end_time: Optional[float] = None
    progress: float = 0.0
    current_step: str = ""
    error_message: Optional[str] = None
    result: Optional[Dict] = None
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['duration'] = (
            (self.end_time or time.time()) - self.start_time
        ) if self.end_time or self.start_time else 0
        return data


@dataclass
class AgentStatus:
    """Current status of an agent"""
    agent_name: str
    status: str
    current_activity_id: Optional[str] = None
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    last_activity_time: Optional[float] = None
    is_active: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class AgentActivityTracker:
    """Singleton tracker for all agent activities"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.activities: Dict[str, AgentActivity] = {}
        self.agent_statuses: Dict[str, AgentStatus] = {}
        self.activity_history: deque = deque(maxlen=1000)  # Keep last 1000 activities
        self.subscribers: List[callable] = []
        self.lock = threading.Lock()
        self._initialized = True
    
    def register_agent(self, agent_name: str):
        """Register an agent with the tracker"""
        with self.lock:
            if agent_name not in self.agent_statuses:
                self.agent_statuses[agent_name] = AgentStatus(
                    agent_name=agent_name,
                    status=ActivityStatus.IDLE.value,
                    is_active=False
                )
                self._notify_subscribers({
                    "type": "agent_registered",
                    "agent_name": agent_name
                })
    
    def start_activity(self, agent_name: str, task_description: str, 
                      activity_id: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> str:
        """Start tracking a new activity"""
        if activity_id is None:
            activity_id = f"{agent_name}_{int(time.time() * 1000)}"
        
        activity = AgentActivity(
            agent_name=agent_name,
            activity_id=activity_id,
            status=ActivityStatus.STARTING.value,
            task_description=task_description,
            start_time=time.time(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.activities[activity_id] = activity
            
            # Update agent status
            if agent_name not in self.agent_statuses:
                self.register_agent(agent_name)
            
            status = self.agent_statuses[agent_name]
            status.status = ActivityStatus.STARTING.value
            status.current_activity_id = activity_id
            status.is_active = True
            status.last_activity_time = time.time()
        
        self._notify_subscribers({
            "type": "activity_started",
            "activity": activity.to_dict()
        })
        
        return activity_id
    
    def update_activity(self, activity_id: str, status: Optional[str] = None,
                       progress: Optional[float] = None,
                       current_step: Optional[str] = None,
                       metadata: Optional[Dict] = None):
        """Update an activity's status"""
        with self.lock:
            if activity_id not in self.activities:
                return
            
            activity = self.activities[activity_id]
            
            if status:
                activity.status = status
                # Update agent status
                if activity.agent_name in self.agent_statuses:
                    self.agent_statuses[activity.agent_name].status = status
            
            if progress is not None:
                activity.progress = max(0.0, min(1.0, progress))
            
            if current_step:
                activity.current_step = current_step
            
            if metadata:
                if activity.metadata is None:
                    activity.metadata = {}
                activity.metadata.update(metadata)
            
            self._notify_subscribers({
                "type": "activity_updated",
                "activity": activity.to_dict()
            })
    
    def complete_activity(self, activity_id: str, success: bool = True,
                         result: Optional[Dict] = None,
                         error_message: Optional[str] = None):
        """Mark an activity as complete"""
        with self.lock:
            if activity_id not in self.activities:
                return
            
            activity = self.activities[activity_id]
            activity.end_time = time.time()
            activity.progress = 1.0
            
            if success:
                activity.status = ActivityStatus.SUCCESS.value
            else:
                activity.status = ActivityStatus.ERROR.value
                activity.error_message = error_message
            
            if result:
                activity.result = result
            
            # Update agent status
            agent_name = activity.agent_name
            if agent_name in self.agent_statuses:
                status = self.agent_statuses[agent_name]
                status.total_operations += 1
                if success:
                    status.successful_operations += 1
                    status.status = ActivityStatus.IDLE.value
                else:
                    status.failed_operations += 1
                    status.status = ActivityStatus.ERROR.value
                
                # Check if agent has other active activities
                has_other_active = any(
                    a.activity_id != activity_id and 
                    a.status not in [ActivityStatus.SUCCESS.value, ActivityStatus.ERROR.value, ActivityStatus.CANCELLED.value]
                    for a in self.activities.values()
                    if a.agent_name == agent_name
                )
                
                if not has_other_active:
                    status.is_active = False
                    status.current_activity_id = None
                    if status.status == ActivityStatus.ERROR.value:
                        # Reset to idle after error
                        status.status = ActivityStatus.IDLE.value
            
            # Move to history
            self.activity_history.append(activity.to_dict())
        
        self._notify_subscribers({
            "type": "activity_completed",
            "activity": activity.to_dict()
        })
    
    def log_message(self, agent_name: str, message: str, level: str = "INFO"):
        """Log a message for an agent"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "type": "log_message",
            "agent_name": agent_name,
            "message": message,
            "level": level,
            "timestamp": timestamp
        }
        
        with self.lock:
            # Add to most recent activity if exists
            for activity in reversed(list(self.activities.values())):
                if activity.agent_name == agent_name and activity.metadata:
                    if "logs" not in activity.metadata:
                        activity.metadata["logs"] = []
                    activity.metadata["logs"].append({
                        "message": message,
                        "level": level,
                        "timestamp": timestamp
                    })
                    break
        
        self._notify_subscribers(log_entry)
    
    def get_all_activities(self) -> List[Dict]:
        """Get all current activities"""
        with self.lock:
            return [activity.to_dict() for activity in self.activities.values()]
    
    def get_agent_activities(self, agent_name: str) -> List[Dict]:
        """Get activities for a specific agent"""
        with self.lock:
            return [
                activity.to_dict()
                for activity in self.activities.values()
                if activity.agent_name == agent_name
            ]
    
    def get_all_agent_statuses(self) -> List[Dict]:
        """Get status of all agents"""
        with self.lock:
            return [status.to_dict() for status in self.agent_statuses.values()]
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict]:
        """Get status of a specific agent"""
        with self.lock:
            if agent_name in self.agent_statuses:
                return self.agent_statuses[agent_name].to_dict()
            return None
    
    def get_activity_history(self, limit: int = 100) -> List[Dict]:
        """Get recent activity history"""
        with self.lock:
            return list(self.activity_history)[-limit:]
    
    def get_dashboard_data(self) -> Dict:
        """Get all data for dashboard"""
        with self.lock:
            return {
                "activities": [activity.to_dict() for activity in self.activities.values()],
                "agent_statuses": [status.to_dict() for status in self.agent_statuses.values()],
                "recent_history": list(self.activity_history)[-50:],
                "timestamp": time.time()
            }
    
    def subscribe(self, callback: callable):
        """Subscribe to activity updates"""
        with self.lock:
            if callback not in self.subscribers:
                self.subscribers.append(callback)
    
    def unsubscribe(self, callback: callable):
        """Unsubscribe from activity updates"""
        with self.lock:
            if callback in self.subscribers:
                self.subscribers.remove(callback)
    
    def _notify_subscribers(self, data: Dict):
        """Notify all subscribers of an update"""
        for callback in self.subscribers:
            try:
                callback(data)
            except Exception as e:
                print(f"Error notifying subscriber: {e}", flush=True)
    
    def clear_completed_activities(self, older_than_seconds: int = 3600):
        """Clear completed activities older than specified time"""
        current_time = time.time()
        with self.lock:
            to_remove = [
                activity_id
                for activity_id, activity in self.activities.items()
                if activity.end_time and (current_time - activity.end_time) > older_than_seconds
            ]
            for activity_id in to_remove:
                del self.activities[activity_id]


# Global singleton instance
tracker = AgentActivityTracker()

