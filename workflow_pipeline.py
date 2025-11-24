#!/usr/bin/env python3
"""
Blender Generator Evolving and Teaching AI Assistant
Main Workflow Pipeline Orchestrator

This system creates a complete pipeline:
1. User explains idea → Main agent discusses to understand
2. Agent researches (internet + database) for tutorials/addons
3. Agent creates plan with plugin/addon recommendations
4. User chooses approach
5. Agent delegates tasks to specialists
6. After completion, asks user to save techniques to database
"""

import json
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import sqlite3

# Import existing components
try:
    from youtube_scraper import YouTubeScraper
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

try:
    from image_generator_client import ImageGeneratorClient
    IMAGE_GENERATOR_AVAILABLE = True
except ImportError:
    IMAGE_GENERATOR_AVAILABLE = False

@dataclass
class UserRequest:
    """User's initial request"""
    idea: str
    has_tutorial_link: bool = False
    tutorial_url: Optional[str] = None
    has_reference_images: bool = False
    reference_images: List[str] = None
    has_reference_videos: bool = False
    reference_videos: List[str] = None
    has_own_footage: bool = False
    footage_path: Optional[str] = None
    wants_to_generate: bool = False
    wants_to_learn: bool = False
    wants_to_edit: bool = False
    
    def __post_init__(self):
        if self.reference_images is None:
            self.reference_images = []
        if self.reference_videos is None:
            self.reference_videos = []

@dataclass
class ResearchResult:
    """Research findings"""
    tutorials: List[Dict] = None
    addons: List[Dict] = None
    plugins: List[Dict] = None
    database_patterns: List[Dict] = None
    similar_projects: List[Dict] = None
    
    def __post_init__(self):
        if self.tutorials is None:
            self.tutorials = []
        if self.addons is None:
            self.addons = []
        if self.plugins is None:
            self.plugins = []
        if self.database_patterns is None:
            self.database_patterns = []
        if self.similar_projects is None:
            self.similar_projects = []

@dataclass
class RecommendedResource:
    """Recommended plugin/addon/resource"""
    name: str
    type: str  # "addon", "plugin", "tutorial", "technique"
    cost: str  # "free", "paid", "subscription"
    description: str
    url: Optional[str] = None
    why_recommended: str = ""
    required: bool = False

@dataclass
class ProjectPlan:
    """Complete project plan"""
    project_id: str
    user_request: UserRequest
    research: ResearchResult
    recommended_resources: List[RecommendedResource]
    workflow_steps: List[Dict]
    estimated_time: Optional[str] = None
    complexity: str = "medium"  # "simple", "medium", "complex"
    specialist_assignments: Dict[str, List[str]] = None  # specialist -> tasks
    
    def __post_init__(self):
        if self.specialist_assignments is None:
            self.specialist_assignments = {}

@dataclass
class ProjectResult:
    """Final project result"""
    project_id: str
    success: bool
    output_files: List[str]
    techniques_used: List[Dict]
    resources_used: List[Dict]
    user_feedback: Optional[str] = None
    save_to_database: bool = False

class MainCoordinatorAgent:
    """Main agent that coordinates the entire workflow"""
    
    def __init__(self, ollama_url: str = "http://ollama:11434"):
        self.ollama_url = ollama_url
        self.youtube_scraper = YouTubeScraper() if YOUTUBE_AVAILABLE else None
        self.image_generator = ImageGeneratorClient() if IMAGE_GENERATOR_AVAILABLE else None
        self.db_dir = Path("databases")
        self.projects_dir = Path("blender_projects")
        self.projects_dir.mkdir(exist_ok=True)
        
    def understand_user_request(self, user_input: str, context: Dict = None) -> UserRequest:
        """
        Phase 1: Understand user's request through conversation
        
        This is where the main agent discusses with the user to fully understand
        what they want to create.
        """
        print("="*70)
        print("PHASE 1: UNDERSTANDING USER REQUEST")
        print("="*70)
        print()
        
        # Parse user input to extract information
        request = UserRequest(idea=user_input)
        
        # Check for tutorial links
        if "youtube.com" in user_input or "youtu.be" in user_input:
            request.has_tutorial_link = True
            # Extract URL
            import re
            url_match = re.search(r'(https?://[^\s]+)', user_input)
            if url_match:
                request.tutorial_url = url_match.group(1)
                request.wants_to_learn = True
        
        # Check for reference mentions
        if any(word in user_input.lower() for word in ["reference", "image", "picture", "photo"]):
            request.has_reference_images = True
        
        if any(word in user_input.lower() for word in ["video", "footage", "clip"]):
            request.has_reference_videos = True
        
        # Check intent
        if any(word in user_input.lower() for word in ["generate", "create", "make"]):
            request.wants_to_generate = True
        
        if any(word in user_input.lower() for word in ["edit", "modify", "change"]):
            request.wants_to_edit = True
        
        print(f"User Idea: {request.idea}")
        print(f"Has Tutorial Link: {request.has_tutorial_link}")
        if request.tutorial_url:
            print(f"Tutorial URL: {request.tutorial_url}")
        print(f"Wants to Generate: {request.wants_to_generate}")
        print(f"Wants to Learn: {request.wants_to_learn}")
        print(f"Wants to Edit: {request.wants_to_edit}")
        print()
        
        return request
    
    def research_resources(self, user_request: UserRequest) -> ResearchResult:
        """
        Phase 2: Research tutorials, addons, plugins, and database patterns
        
        Searches:
        - Internet for tutorials
        - Database for similar patterns
        - Addon/plugin repositories
        """
        print("="*70)
        print("PHASE 2: RESEARCHING RESOURCES")
        print("="*70)
        print()
        
        research = ResearchResult()
        
        # 1. Search database for similar patterns
        print("Searching database for similar patterns...")
        research.database_patterns = self._search_database(user_request.idea)
        print(f"Found {len(research.database_patterns)} similar patterns in database")
        
        # 2. If tutorial link provided, scrape it
        if user_request.has_tutorial_link and self.youtube_scraper:
            print(f"Scraping tutorial: {user_request.tutorial_url}")
            try:
                tutorial_data = self.youtube_scraper.get_video_info(
                    user_request.tutorial_url, 
                    include_transcript=True
                )
                if tutorial_data.get('success'):
                    research.tutorials.append({
                        'url': user_request.tutorial_url,
                        'title': tutorial_data.get('title'),
                        'description': tutorial_data.get('description'),
                        'data': tutorial_data
                    })
                    print(f"Tutorial scraped: {tutorial_data.get('title')}")
            except Exception as e:
                print(f"Error scraping tutorial: {e}")
        
        # 3. Search for relevant addons/plugins
        print("Searching for relevant addons and plugins...")
        research.addons = self._search_addons(user_request.idea)
        research.plugins = self._search_plugins(user_request.idea)
        print(f"Found {len(research.addons)} addons and {len(research.plugins)} plugins")
        
        # 4. Search for similar projects in database
        research.similar_projects = self._search_similar_projects(user_request.idea)
        print(f"Found {len(research.similar_projects)} similar projects")
        
        print()
        return research
    
    def create_project_plan(
        self, 
        user_request: UserRequest, 
        research: ResearchResult
    ) -> ProjectPlan:
        """
        Phase 3: Create comprehensive project plan with recommendations
        
        Includes:
        - Recommended addons/plugins (free and paid)
        - Workflow steps
        - Specialist assignments
        """
        print("="*70)
        print("PHASE 3: CREATING PROJECT PLAN")
        print("="*70)
        print()
        
        project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze research and create recommendations
        recommended_resources = []
        
        # Recommend addons based on research
        for addon in research.addons[:5]:  # Top 5
            recommended_resources.append(RecommendedResource(
                name=addon.get('name', 'Unknown'),
                type="addon",
                cost=addon.get('cost', 'unknown'),
                description=addon.get('description', ''),
                url=addon.get('url'),
                why_recommended=f"Relevant for: {user_request.idea[:50]}...",
                required=addon.get('required', False)
            ))
        
        # Recommend plugins
        for plugin in research.plugins[:5]:
            recommended_resources.append(RecommendedResource(
                name=plugin.get('name', 'Unknown'),
                type="plugin",
                cost=plugin.get('cost', 'unknown'),
                description=plugin.get('description', ''),
                url=plugin.get('url'),
                why_recommended=f"Useful for project requirements",
                required=plugin.get('required', False)
            ))
        
        # Create workflow steps based on user request and research
        workflow_steps = self._create_workflow_steps(user_request, research)
        
        # Assign tasks to specialists
        specialist_assignments = self._assign_to_specialists(user_request, workflow_steps)
        
        # Determine complexity
        complexity = self._determine_complexity(user_request, workflow_steps)
        
        plan = ProjectPlan(
            project_id=project_id,
            user_request=user_request,
            research=research,
            recommended_resources=recommended_resources,
            workflow_steps=workflow_steps,
            complexity=complexity,
            specialist_assignments=specialist_assignments
        )
        
        print(f"Project ID: {plan.project_id}")
        print(f"Complexity: {plan.complexity}")
        print(f"Recommended Resources: {len(plan.recommended_resources)}")
        print(f"Workflow Steps: {len(plan.workflow_steps)}")
        print(f"Specialists Assigned: {len(plan.specialist_assignments)}")
        print()
        
        return plan
    
    def execute_project(self, plan: ProjectPlan) -> ProjectResult:
        """
        Phase 4: Execute project by delegating to specialists
        """
        print("="*70)
        print("PHASE 4: EXECUTING PROJECT")
        print("="*70)
        print()
        
        project_dir = self.projects_dir / plan.project_id
        project_dir.mkdir(exist_ok=True)
        
        # Save plan
        plan_file = project_dir / "project_plan.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(plan), f, indent=2, default=str)
        
        # Execute workflow steps
        output_files = []
        techniques_used = []
        resources_used = []
        
        for i, step in enumerate(plan.workflow_steps, 1):
            print(f"Executing step {i}/{len(plan.workflow_steps)}: {step.get('name', 'Unknown')}")
            
            # Here would be actual execution via specialist agents
            # For now, we'll simulate
            step_result = {
                'step': i,
                'name': step.get('name'),
                'status': 'completed',
                'output': f"output_{i}.blend"
            }
            output_files.append(step_result['output'])
            techniques_used.append(step.get('technique', {}))
            resources_used.append(step.get('resources', []))
        
        result = ProjectResult(
            project_id=plan.project_id,
            success=True,
            output_files=output_files,
            techniques_used=techniques_used,
            resources_used=resources_used
        )
        
        # Save result
        result_file = project_dir / "project_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        print(f"Project completed: {plan.project_id}")
        print(f"Output files: {len(output_files)}")
        print()
        
        return result
    
    def ask_to_save_to_database(self, result: ProjectResult) -> bool:
        """
        Phase 5: Ask user if techniques/resources should be saved to database
        """
        print("="*70)
        print("PHASE 5: LEARNING & DATABASE UPDATE")
        print("="*70)
        print()
        
        print("Project completed successfully!")
        print()
        print("Would you like to save the techniques and resources used to the database?")
        print("This will help the system learn and improve for future projects.")
        print()
        print("Techniques used:")
        for i, technique in enumerate(result.techniques_used, 1):
            print(f"  {i}. {technique.get('name', 'Unknown')}")
        print()
        print("Resources used:")
        for i, resource in enumerate(result.resources_used, 1):
            print(f"  {i}. {resource}")
        print()
        
        # In real implementation, this would be interactive
        # For now, return True to indicate user wants to save
        save_to_db = True  # Would be user input
        
        if save_to_db:
            self._save_to_database(result)
            print("Techniques and resources saved to database!")
        else:
            print("Techniques and resources not saved.")
        
        print()
        return save_to_db
    
    # Helper methods
    
    def _search_database(self, query: str) -> List[Dict]:
        """Search all databases for similar patterns"""
        patterns = []
        
        for db_file in self.db_dir.glob("*.db"):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Search operations table
                cursor.execute("""
                    SELECT description, generated_code, success, model_used
                    FROM operations
                    WHERE description LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT 5
                """, (f"%{query}%",))
                
                for row in cursor.fetchall():
                    patterns.append({
                        'database': db_file.name,
                        'description': row[0],
                        'code': row[1],
                        'success': bool(row[2]),
                        'model': row[3]
                    })
                
                conn.close()
            except Exception as e:
                print(f"Error searching {db_file.name}: {e}")
        
        return patterns
    
    def _search_addons(self, query: str) -> List[Dict]:
        """Search for relevant Blender addons"""
        # This would search actual addon repositories
        # For now, return mock data based on query
        addons = []
        
        keywords = query.lower()
        
        if "model" in keywords:
            addons.append({
                'name': 'Hard Ops',
                'cost': 'paid',
                'description': 'Advanced modeling tools',
                'url': 'https://blendermarket.com/products/hardops',
                'required': False
            })
        
        if "material" in keywords or "shader" in keywords:
            addons.append({
                'name': 'Material Library',
                'cost': 'free',
                'description': 'Material presets library',
                'url': 'https://blender.org',
                'required': False
            })
        
        if "animation" in keywords:
            addons.append({
                'name': 'Animation Nodes',
                'cost': 'free',
                'description': 'Node-based animation system',
                'url': 'https://github.com',
                'required': False
            })
        
        return addons
    
    def _search_plugins(self, query: str) -> List[Dict]:
        """Search for relevant plugins"""
        # Similar to addons
        return []
    
    def _search_similar_projects(self, query: str) -> List[Dict]:
        """Search for similar completed projects"""
        projects = []
        
        # Search project directories
        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                plan_file = project_dir / "project_plan.json"
                if plan_file.exists():
                    try:
                        with open(plan_file, 'r') as f:
                            plan_data = json.load(f)
                            if query.lower() in plan_data.get('user_request', {}).get('idea', '').lower():
                                projects.append({
                                    'project_id': project_dir.name,
                                    'idea': plan_data.get('user_request', {}).get('idea')
                                })
                    except:
                        pass
        
        return projects
    
    def _create_workflow_steps(
        self, 
        user_request: UserRequest, 
        research: ResearchResult
    ) -> List[Dict]:
        """Create workflow steps based on request and research"""
        steps = []
        
        # Base workflow
        if user_request.wants_to_generate:
            steps.append({
                'name': 'Generate reference images',
                'specialist': 'image_generator',
                'technique': {'name': 'AI Image Generation', 'type': 'generation'},
                'resources': ['Stable Diffusion', 'FLUX']
            })
        
        if user_request.has_tutorial_link:
            steps.append({
                'name': 'Analyze tutorial workflow',
                'specialist': 'tutorial_analyzer',
                'technique': {'name': 'Tutorial Analysis', 'type': 'learning'},
                'resources': ['YouTube Scraper']
            })
        
        steps.append({
            'name': 'Create Blender scene',
            'specialist': 'modeling',
            'technique': {'name': 'Scene Creation', 'type': 'modeling'},
            'resources': ['Blender']
        })
        
        if user_request.wants_to_edit:
            steps.append({
                'name': 'Edit footage',
                'specialist': 'videography',
                'technique': {'name': 'Video Editing', 'type': 'editing'},
                'resources': ['Blender VSE']
            })
        
        return steps
    
    def _assign_to_specialists(
        self, 
        user_request: UserRequest, 
        workflow_steps: List[Dict]
    ) -> Dict[str, List[str]]:
        """Assign tasks to specialist agents"""
        assignments = {}
        
        for step in workflow_steps:
            specialist = step.get('specialist', 'general')
            if specialist not in assignments:
                assignments[specialist] = []
            assignments[specialist].append(step.get('name'))
        
        return assignments
    
    def _determine_complexity(
        self, 
        user_request: UserRequest, 
        workflow_steps: List[Dict]
    ) -> str:
        """Determine project complexity"""
        num_steps = len(workflow_steps)
        num_specialists = len(set(step.get('specialist') for step in workflow_steps))
        
        if num_steps <= 3 and num_specialists <= 2:
            return "simple"
        elif num_steps <= 6 and num_specialists <= 4:
            return "medium"
        else:
            return "complex"
    
    def _save_to_database(self, result: ProjectResult):
        """Save techniques and resources to database"""
        # Determine which database to use based on techniques
        for technique in result.techniques_used:
            tech_type = technique.get('type', 'general')
            
            # Map to database
            db_mapping = {
                'modeling': 'modeling_data.db',
                'shading': 'shading_data.db',
                'animation': 'animation_data.db',
                'vfx': 'vfx_data.db',
                'rendering': 'rendering_data.db',
                'generation': 'vfx_data.db'  # AI generation goes to VFX
            }
            
            db_name = db_mapping.get(tech_type, 'general_data.db')
            db_path = self.db_dir / db_name
            
            # Create database if it doesn't exist
            if not db_path.exists():
                self._create_database(db_path)
            
            # Save technique
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO operations 
                    (description, generated_code, success, model_used, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    technique.get('name', 'Unknown'),
                    json.dumps(technique),
                    1,  # success
                    'workflow_pipeline',
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error saving to database: {e}")
    
    def _create_database(self, db_path: Path):
        """Create database with operations table"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                generated_code TEXT,
                success INTEGER,
                model_used TEXT,
                timestamp TEXT
            )
        """)
        
        conn.commit()
        conn.close()

def run_complete_workflow(user_input: str):
    """Run the complete workflow pipeline"""
    coordinator = MainCoordinatorAgent()
    
    # Phase 1: Understand
    user_request = coordinator.understand_user_request(user_input)
    
    # Phase 2: Research
    research = coordinator.research_resources(user_request)
    
    # Phase 3: Plan
    plan = coordinator.create_project_plan(user_request, research)
    
    # Display plan for user approval
    print("="*70)
    print("PROJECT PLAN - USER APPROVAL REQUIRED")
    print("="*70)
    print()
    print(f"Project: {plan.project_id}")
    print(f"Complexity: {plan.complexity}")
    print()
    print("Recommended Resources:")
    for resource in plan.recommended_resources:
        cost_icon = "💰" if resource.cost == "paid" else "🆓"
        print(f"  {cost_icon} {resource.name} ({resource.cost})")
        print(f"     {resource.description}")
        print(f"     Why: {resource.why_recommended}")
        print()
    
    print("Workflow Steps:")
    for i, step in enumerate(plan.workflow_steps, 1):
        print(f"  {i}. {step.get('name')} → {step.get('specialist')}")
    print()
    
    # In real implementation, wait for user approval
    user_approved = True  # Would be user input
    
    if user_approved:
        # Phase 4: Execute
        result = coordinator.execute_project(plan)
        
        # Phase 5: Learn
        coordinator.ask_to_save_to_database(result)
        
        return result
    else:
        print("Project cancelled by user.")
        return None

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = "I want to create a 3D bedroom scene with AI-generated reference images"
    
    run_complete_workflow(user_input)

