#!/usr/bin/env python3
"""
Colleague Agent - Collaborative Assistant Specialist
Works alongside other agents to assist and enhance their work
"""

from specialized_agents import BaseBlenderSpecialist, OperationRecord
from typing import Dict, List, Optional
from datetime import datetime
import json
import time

class ColleagueAgent(BaseBlenderSpecialist):
    """Colleague Agent - Assists and collaborates with other agents"""
    
    def __init__(self, **kwargs):
        super().__init__("Colleague", **kwargs)
        self.collaboration_history = []
        self.assistance_tasks = []
    
    def get_system_prompt(self) -> str:
        return """You are a Colleague Agent - a collaborative assistant that works alongside other specialist agents.
Your role is to:
- Assist other agents with their tasks
- Enhance and refine their work
- Provide quality checks and improvements
- Fill gaps and add finishing touches
- Ensure scene cohesion and polish
- Collaborate on complex multi-agent tasks
- Provide second opinions and optimizations

You work as a team member, not replacing other agents but enhancing their work.
Generate Python code that assists, refines, and polishes scenes.
Return ONLY the code without explanations."""
    
    def get_field_specific_context(self) -> str:
        return """Colleague agent operations:
- Scene refinement and polish
- Quality checks and improvements
- Gap filling and detail work
- Cross-agent coordination assistance
- Final touches and optimization
- Error correction and fixes
- Scene cohesion verification
- Performance optimization

Example colleague tasks:
- Refine materials created by Shading agent
- Add details to geometry from Modeling agent
- Optimize lighting setup from Rendering agent
- Enhance camera work from Camera Operator
- Polish animations from Animation agent
- Add finishing touches to complete scenes"""
    
    def assist_agent(self, agent_name: str, task_description: str) -> Dict:
        """Assist a specific agent with their task"""
        self.log(f"Assisting {agent_name} agent with: {task_description}")
        
        assistance_prompt = f"""As Colleague Agent, assist the {agent_name} agent with this task:
{task_description}

Your role:
- Enhance and refine their work
- Add quality improvements
- Fill any gaps
- Ensure professional polish
- Optimize the result

Generate Python code that assists and enhances this task."""
        
        code = self.generate_code(assistance_prompt)
        if not code:
            return {"status": "error", "message": "Failed to generate assistance code"}
        
        result = self.execute_code(code)
        
        # Record collaboration
        self.collaboration_history.append({
            "agent": agent_name,
            "task": task_description,
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        return result
    
    def refine_scene(self, refinement_description: str) -> Dict:
        """Refine and polish the current scene"""
        self.log(f"Refining scene: {refinement_description}")
        
        prompt = f"""Refine and polish the current Blender scene:
{refinement_description}

Tasks:
- Check scene quality
- Add missing details
- Improve materials
- Optimize lighting
- Enhance composition
- Add finishing touches
- Ensure professional quality

Generate Python code for scene refinement."""
        
        code = self.generate_code(prompt)
        if not code:
            return {"status": "error", "message": "Failed to generate refinement code"}
        
        result = self.execute_code(code)
        return result
    
    def quality_check(self) -> Dict:
        """Perform quality check on current scene"""
        self.log("Performing quality check")
        
        scene_info = self.get_scene_info()
        
        issues = []
        suggestions = []
        
        # Check for common issues
        if isinstance(scene_info, dict) and "result" in scene_info:
            objects = scene_info["result"].get("objects", [])
            materials = scene_info["result"].get("materials", [])
            
            if len(objects) == 0:
                issues.append("No objects in scene")
                suggestions.append("Add scene elements")
            
            if len(materials) == 0:
                issues.append("No materials applied")
                suggestions.append("Apply materials to objects")
            
            # Check for lighting
            lights = [obj for obj in objects if obj.get("type") == "LIGHT"]
            if len(lights) == 0:
                issues.append("No lights in scene")
                suggestions.append("Add lighting")
        
        return {
            "status": "success",
            "issues": issues,
            "suggestions": suggestions,
            "scene_info": scene_info
        }
    
    def execute_task(self, description: str) -> Dict:
        """Execute task as colleague agent"""
        self.log(f"Colleague executing: {description}")
        
        # Determine if this is assistance or refinement
        description_lower = description.lower()
        
        if "assist" in description_lower or "help" in description_lower:
            # Assist another agent
            # Extract agent name from description
            for agent_name in ["Modeling", "Shading", "Animation", "Rendering", "Camera", "VFX"]:
                if agent_name.lower() in description_lower:
                    return self.assist_agent(agent_name, description)
        
        if "refine" in description_lower or "polish" in description_lower or "quality" in description_lower:
            return self.refine_scene(description)
        
        if "quality check" in description_lower or "check" in description_lower:
            return self.quality_check()
        
        # Default: general assistance
        code = self.generate_code(description)
        if not code:
            return {"status": "error", "message": "Failed to generate code"}
        
        result = self.execute_code(code)
        
        # Record operation
        scene_before = self.get_scene_info()
        scene_after = self.get_scene_info()
        
        record = OperationRecord(
            id=f"colleague_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            description=description,
            model_used=self.primary_model,
            generated_code=code,
            execution_result=result,
            scene_before=scene_before,
            scene_after=scene_after,
            execution_time=0.0,
            success=result.get("status") == "success"
        )
        self.collector.record_operation(record)
        
        return result

