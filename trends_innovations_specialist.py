#!/usr/bin/env python3
"""
Trends & Innovations Specialist
Monitors web trends and provides development proposals
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import sys
import time
import requests
from data_collector import BlenderDataCollector
from pathlib import Path


class TrendsInnovationsSpecialist:
    """
    Specialist that monitors trends and innovations in:
    - Blender development
    - AI/LLM technologies
    - 3D graphics industry
    - Video editing and video types
    - Fashion industry
    - Furniture design
    - MCP protocol
    - Related technologies
    
    Provides development proposals based on trends relevant to the project
    """
    
    def __init__(self, ollama_url="http://localhost:11434"):
        self.name = "TrendsInnovations"
        self.ollama_url = ollama_url
        self.collector = BlenderDataCollector("trends_innovations_data.db")
        self.insights_cache = {}
        self.last_update = None
        self.current_project_context = None
        self.project_history = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{self.name}] [{level}] {message}", file=sys.stderr)
        sys.stderr.flush()
    
    def analyze_trends(self, topics: List[str]) -> Dict:
        """
        Analyze trends for given topics
        Uses Ollama to analyze and synthesize information
        """
        self.log(f"Analyzing trends for: {', '.join(topics)}")
        
        # Build analysis prompt
        topics_str = ", ".join(topics)
        prompt = f"""Analyze current trends and innovations in the following areas:
{topics_str}

Provide:
1. Current trends (what's happening now)
2. Emerging technologies (what's coming)
3. Industry developments (market changes)
4. Technical innovations (new capabilities)
5. Development opportunities (what to build)

Format as JSON with sections for each topic."""
        
        try:
            payload = {
                "model": "llama3.2:latest",  # Use larger model for analysis
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                self.log("Trend analysis completed")
                return {"status": "success", "analysis": result}
            else:
                return {"status": "error", "message": f"API error: {response.status_code}"}
                
        except Exception as e:
            self.log(f"Error analyzing trends: {e}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    def generate_proposals(self, analysis: str, focus_area: str = "general") -> Dict:
        """
        Generate development proposals based on trend analysis
        """
        self.log(f"Generating proposals for: {focus_area}")
        
        # Build context-aware prompt
        project_context_str = ""
        if self.current_project_context:
            project_type = self.current_project_context.get("type", "")
            project_desc = self.current_project_context.get("description", "")
            project_context_str = f"\n\nCurrent Project Context:\n- Project Type: {project_type}\n- Description: {project_desc}\n\nPrioritize proposals that are relevant to this specific project."
        
        prompt = f"""Based on this trend analysis:
{analysis}

Generate specific development proposals for a Blender-Ollama MCP Server system.
Focus area: {focus_area}
{project_context_str}

Consider how these trends relate to:
- 3D content creation (Blender)
- Video production and editing
- Fashion visualization and design
- Furniture and interior design
- TikTok and Instagram content creation
- Gaming and game development
- AI-assisted workflows
- Multi-industry applications

For each proposal, provide:
1. Title
2. Description
3. Benefits (how it helps the project - be specific to current project if context provided)
4. Implementation complexity (Low/Medium/High)
5. Priority (Low/Medium/High) - prioritize based on project relevance
6. Estimated impact
7. Relevant industries (Blender, Video, Fashion, Furniture, TikTok, Instagram, Gaming, etc.)
8. Project relevance (how relevant to current project if context provided)

Format as JSON array of proposals."""
        
        try:
            payload = {
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,  # Higher for creativity
                    "num_predict": 2000
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                self.log("Proposals generated")
                return {"status": "success", "proposals": result}
            else:
                return {"status": "error", "message": f"API error: {response.status_code}"}
                
        except Exception as e:
            self.log(f"Error generating proposals: {e}", "ERROR")
            return {"status": "error", "message": str(e)}
    
    def monitor_blender_trends(self) -> Dict:
        """
        Monitor Blender-specific trends
        """
        topics = [
            "Blender 3D software development",
            "Blender Python API updates",
            "Blender features and releases",
            "Blender community trends",
            "3D graphics industry trends"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_ai_trends(self) -> Dict:
        """
        Monitor AI/LLM trends relevant to the system
        """
        topics = [
            "Large Language Models (LLMs)",
            "Ollama and local AI",
            "Model Context Protocol (MCP)",
            "AI code generation",
            "Multi-agent systems"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_tech_trends(self) -> Dict:
        """
        Monitor general technology trends
        """
        topics = [
            "3D graphics technology",
            "Procedural generation",
            "Real-time rendering",
            "AI-assisted workflows",
            "Developer tools and IDEs"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_video_trends(self) -> Dict:
        """
        Monitor video editing and video format trends
        """
        topics = [
            "Video editing software and tools",
            "Video formats and codecs (MP4, H.264, H.265, AV1, etc.)",
            "Video editing trends and techniques",
            "Video production workflows",
            "Video effects and transitions",
            "Video streaming and delivery",
            "Video compression technologies",
            "Video editing AI tools",
            "Motion graphics trends",
            "Color grading trends"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_fashion_trends(self) -> Dict:
        """
        Monitor fashion industry trends relevant to 3D and visualization
        """
        topics = [
            "Fashion design trends",
            "3D fashion visualization",
            "Virtual fashion and digital clothing",
            "Fashion technology and innovation",
            "Fashion photography and rendering",
            "Textile and material trends",
            "Fashion e-commerce visualization",
            "AR/VR in fashion",
            "Sustainable fashion technology",
            "Fashion design software"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_furniture_trends(self) -> Dict:
        """
        Monitor furniture design and interior design trends
        """
        topics = [
            "Furniture design trends",
            "3D furniture visualization",
            "Interior design software",
            "Furniture manufacturing technology",
            "Sustainable furniture design",
            "Furniture e-commerce visualization",
            "AR/VR furniture placement",
            "Furniture rendering and visualization",
            "Smart furniture technology",
            "Custom furniture design"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_tiktok_trends(self) -> Dict:
        """
        Monitor TikTok trends relevant to 3D content creation
        """
        topics = [
            "TikTok video trends and formats",
            "TikTok content creation trends",
            "TikTok video effects and transitions",
            "TikTok vertical video formats (9:16)",
            "TikTok 3D content and AR filters",
            "TikTok video editing techniques",
            "TikTok viral content patterns",
            "TikTok music and audio trends",
            "TikTok hashtag and challenge trends",
            "TikTok creator tools and software",
            "TikTok video optimization",
            "TikTok algorithm and engagement trends"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_instagram_trends(self) -> Dict:
        """
        Monitor Instagram trends relevant to 3D content creation
        """
        topics = [
            "Instagram content trends and formats",
            "Instagram Reels trends and features",
            "Instagram Stories trends",
            "Instagram video formats and aspect ratios",
            "Instagram 3D content and AR filters",
            "Instagram video editing trends",
            "Instagram visual aesthetics and trends",
            "Instagram engagement strategies",
            "Instagram hashtag trends",
            "Instagram creator tools and software",
            "Instagram algorithm updates",
            "Instagram shopping and e-commerce trends",
            "Instagram carousel and multi-image trends"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_gaming_trends(self) -> Dict:
        """
        Monitor gaming industry trends relevant to 3D content creation
        """
        topics = [
            "Game development trends",
            "3D game asset creation",
            "Game engine trends (Unity, Unreal, Godot)",
            "Procedural game content generation",
            "Game character design trends",
            "Game environment design trends",
            "Game animation trends",
            "Game VFX and particle effects",
            "Game rendering techniques",
            "Mobile game development trends",
            "Indie game development trends",
            "Game asset marketplaces",
            "Game modding and user-generated content",
            "Virtual reality (VR) gaming trends",
            "Augmented reality (AR) gaming trends",
            "Game streaming and content creation",
            "Game monetization trends",
            "Game UI/UX design trends"
        ]
        
        return self.analyze_trends(topics)
    
    def monitor_project_specific_trends(self, custom_topics: List[str]) -> Dict:
        """
        Monitor custom project-specific trends
        """
        return self.analyze_trends(custom_topics)
    
    def set_project_context(self, project_type: str, project_description: Optional[str] = None):
        """
        Set the current project context to adapt trend monitoring
        
        Args:
            project_type: Type of project (e.g., "fashion", "gaming", "video", "furniture", "tiktok", "instagram", "custom")
            project_description: Optional description of the project
        """
        self.current_project_context = {
            "type": project_type,
            "description": project_description,
            "timestamp": datetime.now().isoformat()
        }
        self.log(f"Project context set: {project_type}")
        
        # Store in history
        self.project_history.append(self.current_project_context.copy())
        
        # Keep only last 50 projects
        if len(self.project_history) > 50:
            self.project_history = self.project_history[-50:]
    
    def get_project_relevant_trends(self) -> Dict:
        """
        Get trends relevant to the current project context
        Automatically selects focus areas based on project type
        """
        if not self.current_project_context:
            # No project context - return general trends
            return self.get_development_proposals("general")
        
        project_type = self.current_project_context.get("type", "general")
        project_desc = self.current_project_context.get("description", "")
        
        self.log(f"Getting project-relevant trends for: {project_type}")
        
        # Map project types to focus areas
        project_focus_map = {
            "fashion": "fashion",
            "furniture": "furniture",
            "video": "video",
            "tiktok": "tiktok",
            "instagram": "instagram",
            "gaming": "gaming",
            "game": "gaming",
            "blender": "blender",
            "3d": "blender",
            "modeling": "blender"
        }
        
        # Determine focus area from project type
        focus_area = project_focus_map.get(project_type.lower(), "general")
        
        # If custom project, extract topics from description
        if project_type.lower() == "custom" and project_desc:
            # Extract custom topics from description
            custom_topics = self._extract_topics_from_description(project_desc)
            return self.get_development_proposals("custom", custom_topics)
        
        return self.get_development_proposals(focus_area)
    
    def _extract_topics_from_description(self, description: str) -> List[str]:
        """
        Extract relevant topics from project description
        Uses LLM to identify key topics
        """
        prompt = f"""From this project description, extract 5-10 key topics for trend monitoring:
{description}

Return a JSON array of topic strings, each describing a trend area to monitor.
Example: ["Architectural visualization", "Building design", "Real estate technology"]
"""
        
        try:
            payload = {
                "model": "llama3.2:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                # Try to parse JSON array
                try:
                    # Extract JSON from response
                    import re
                    json_match = re.search(r'\[.*\]', result, re.DOTALL)
                    if json_match:
                        topics = json.loads(json_match.group())
                        return topics if isinstance(topics, list) else [str(t) for t in topics]
                except:
                    pass
                
                # Fallback: split by lines and clean
                topics = [line.strip() for line in result.split('\n') if line.strip() and not line.strip().startswith('#')]
                return topics[:10]  # Limit to 10 topics
                
        except Exception as e:
            self.log(f"Error extracting topics: {e}", "ERROR")
        
        # Default topics if extraction fails
        return [description]
    
    def get_development_proposals(self, focus_area: str = "general", custom_topics: Optional[List[str]] = None, use_project_context: bool = True) -> Dict:
        """
        Get comprehensive development proposals
        Combines trend analysis with proposal generation
        
        Args:
            focus_area: "general", "blender", "ai", "tech", "video", "fashion", "furniture", "tiktok", "instagram", "gaming", or "custom"
            custom_topics: List of custom topics (required if focus_area is "custom")
            use_project_context: If True and project context exists, adapts proposals to current project
        """
        # If project context exists and use_project_context is True, adapt focus
        if use_project_context and self.current_project_context:
            project_type = self.current_project_context.get("type", "").lower()
            project_desc = self.current_project_context.get("description", "")
            
            # Override focus_area if it's "general" and we have project context
            if focus_area == "general" and project_type:
                project_focus_map = {
                    "fashion": "fashion",
                    "furniture": "furniture",
                    "video": "video",
                    "tiktok": "tiktok",
                    "instagram": "instagram",
                    "gaming": "gaming",
                    "game": "gaming",
                    "blender": "blender",
                    "3d": "blender",
                    "modeling": "blender"
                }
                
                if project_type in project_focus_map:
                    focus_area = project_focus_map[project_type]
                    self.log(f"Adapted focus area to {focus_area} based on project context")
                elif project_type == "custom" and project_desc:
                    custom_topics = self._extract_topics_from_description(project_desc)
                    focus_area = "custom"
        
        self.log(f"Getting development proposals for: {focus_area}")
        
        # Analyze trends based on focus area
        if focus_area == "blender":
            trends_result = self.monitor_blender_trends()
        elif focus_area == "ai":
            trends_result = self.monitor_ai_trends()
        elif focus_area == "tech":
            trends_result = self.monitor_tech_trends()
        elif focus_area == "video":
            trends_result = self.monitor_video_trends()
        elif focus_area == "fashion":
            trends_result = self.monitor_fashion_trends()
        elif focus_area == "furniture":
            trends_result = self.monitor_furniture_trends()
        elif focus_area == "tiktok":
            trends_result = self.monitor_tiktok_trends()
        elif focus_area == "instagram":
            trends_result = self.monitor_instagram_trends()
        elif focus_area == "gaming":
            trends_result = self.monitor_gaming_trends()
        elif focus_area == "custom":
            if not custom_topics:
                return {"status": "error", "message": "custom_topics required for custom focus area"}
            trends_result = self.monitor_project_specific_trends(custom_topics)
        else:
            # General - combine all major areas
            blender_trends = self.monitor_blender_trends()
            ai_trends = self.monitor_ai_trends()
            tech_trends = self.monitor_tech_trends()
            video_trends = self.monitor_video_trends()
            fashion_trends = self.monitor_fashion_trends()
            furniture_trends = self.monitor_furniture_trends()
            tiktok_trends = self.monitor_tiktok_trends()
            instagram_trends = self.monitor_instagram_trends()
            gaming_trends = self.monitor_gaming_trends()
            
            trends_result = {
                "status": "success",
                "analysis": f"Blender Trends:\n{blender_trends.get('analysis', '')}\n\n"
                          f"AI Trends:\n{ai_trends.get('analysis', '')}\n\n"
                          f"Tech Trends:\n{tech_trends.get('analysis', '')}\n\n"
                          f"Video Trends:\n{video_trends.get('analysis', '')}\n\n"
                          f"Fashion Trends:\n{fashion_trends.get('analysis', '')}\n\n"
                          f"Furniture Trends:\n{furniture_trends.get('analysis', '')}\n\n"
                          f"TikTok Trends:\n{tiktok_trends.get('analysis', '')}\n\n"
                          f"Instagram Trends:\n{instagram_trends.get('analysis', '')}\n\n"
                          f"Gaming Trends:\n{gaming_trends.get('analysis', '')}"
            }
        
        if trends_result.get("status") != "success":
            return trends_result
        
        # Generate proposals
        proposals_result = self.generate_proposals(
            trends_result.get("analysis", ""),
            focus_area
        )
        
        if proposals_result.get("status") != "success":
            return proposals_result
        
        # Store insight
        insight = {
            "timestamp": datetime.now().isoformat(),
            "focus_area": focus_area,
            "trends_analysis": trends_result.get("analysis", ""),
            "proposals": proposals_result.get("proposals", ""),
            "source": "trends_analysis"
        }
        
        # Store in database (using operations table)
        from data_collector import OperationRecord
        record = OperationRecord(
            id=f"trends_{int(time.time())}",
            timestamp=datetime.now().isoformat(),
            description=f"Trend analysis and proposals for {focus_area}",
            model_used="llama3.2:latest",
            generated_code=json.dumps(insight, indent=2),
            execution_result={"status": "success", "insight": insight},
            scene_before={},
            scene_after={},
            execution_time=0.0,
            success=True
        )
        self.collector.record_operation(record)
        
        return {
            "status": "success",
            "trends_analysis": trends_result.get("analysis", ""),
            "proposals": proposals_result.get("proposals", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recent_insights(self, limit: int = 10) -> List[Dict]:
        """
        Get recent trend insights from database
        """
        try:
            conn = self.collector.conn
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT description, generated_code, timestamp, success
                FROM operations
                WHERE description LIKE '%Trend analysis%'
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            insights = []
            for row in rows:
                try:
                    code_data = json.loads(row[1])
                    insights.append({
                        "description": row[0],
                        "insight": code_data,
                        "timestamp": row[2],
                        "success": bool(row[3])
                    })
                except:
                    pass
            
            return insights
            
        except Exception as e:
            self.log(f"Error getting insights: {e}", "ERROR")
            return []
    
    def cleanup(self):
        """Clean up resources"""
        if self.collector:
            self.collector.close()


# Example usage
if __name__ == "__main__":
    specialist = TrendsInnovationsSpecialist()
    
    print("="*70)
    print("TRENDS & INNOVATIONS SPECIALIST")
    print("="*70)
    print()
    
    # Get general proposals
    print("Getting development proposals...")
    result = specialist.get_development_proposals("general")
    
    if result.get("status") == "success":
        print("\nTrends Analysis:")
        print(result.get("trends_analysis", "")[:500] + "...")
        print("\nProposals:")
        print(result.get("proposals", "")[:500] + "...")
    else:
        print(f"Error: {result.get('message')}")
    
    # Get recent insights
    print("\n" + "="*70)
    print("Recent Insights:")
    print("="*70)
    insights = specialist.get_recent_insights(5)
    for insight in insights:
        print(f"\n{insight['timestamp']}: {insight['description']}")
    
    specialist.cleanup()

