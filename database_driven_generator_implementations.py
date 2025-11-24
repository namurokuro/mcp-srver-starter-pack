#!/usr/bin/env python3
"""
Database-Driven Generator Implementations
All possible ways to integrate image/video generators with the database system
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Database paths
DATABASE_DIR = Path("databases")
OUTPUT_DIR = Path("output/generated")

@dataclass
class GeneratorImplementation:
    """Represents a generator implementation pattern"""
    name: str
    description: str
    database_source: str
    generator_type: str  # "image" or "video"
    use_case: str
    code_template: str
    integration_points: List[str]
    example_prompts: List[str]

class DatabaseDrivenGenerator:
    """Main class for database-driven generator implementations"""
    
    def __init__(self):
        self.db_path = DATABASE_DIR
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_operations_from_db(self, db_name: str, limit: int = 50) -> List[Dict]:
        """Get operations from a specific database"""
        db_path = self.db_path / db_name
        if not db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if operations table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operations'")
            if not cursor.fetchone():
                conn.close()
                return []
            
            cursor.execute(f"""
                SELECT id, description, generated_code, success, model_used, timestamp
                FROM operations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            operations = []
            for row in cursor.fetchall():
                operations.append({
                    "id": row[0],
                    "description": row[1],
                    "code": row[2],
                    "success": bool(row[3]),
                    "model": row[4],
                    "timestamp": row[5]
                })
            
            conn.close()
            return operations
        except Exception as e:
            print(f"Error reading {db_name}: {e}")
            return []
    
    def get_patterns_from_db(self, db_name: str, limit: int = 20) -> List[Dict]:
        """Get successful patterns from database"""
        db_path = self.db_path / db_name
        if not db_path.exists():
            return []
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='code_patterns'")
            if not cursor.fetchone():
                conn.close()
                return []
            
            cursor.execute(f"""
                SELECT description_pattern, code_template, success_count, failure_count
                FROM code_patterns
                WHERE success_count > failure_count
                ORDER BY success_count DESC
                LIMIT ?
            """, (limit,))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    "description": row[0],
                    "code_template": row[1],
                    "success_count": row[2],
                    "failure_count": row[3]
                })
            
            conn.close()
            return patterns
        except Exception as e:
            print(f"Error reading patterns from {db_name}: {e}")
            return []
    
    def create_prompt_from_operation(self, operation: Dict) -> str:
        """Create image generation prompt from operation description"""
        description = operation.get("description", "")
        
        # Enhance prompt based on operation type
        if "model" in description.lower() or "mesh" in description.lower():
            return f"3D model reference: {description}, professional Blender modeling, high detail, clean topology"
        elif "shade" in description.lower() or "material" in description.lower():
            return f"Material reference: {description}, realistic textures, PBR materials, Blender shading"
        elif "animate" in description.lower() or "keyframe" in description.lower():
            return f"Animation reference: {description}, motion study, keyframe poses, Blender animation"
        elif "render" in description.lower() or "light" in description.lower():
            return f"Lighting reference: {description}, professional lighting setup, cinematic, Blender rendering"
        else:
            return f"Blender scene reference: {description}, 3D art, professional quality"
    
    def create_prompt_from_pattern(self, pattern: Dict) -> str:
        """Create image generation prompt from successful pattern"""
        description = pattern.get("description", "")
        success_rate = pattern.get("success_count", 0) / (pattern.get("success_count", 0) + pattern.get("failure_count", 1))
        
        # High success rate patterns get more detailed prompts
        if success_rate > 0.8:
            return f"Proven technique reference: {description}, highly successful workflow, professional Blender technique"
        else:
            return f"Technique reference: {description}, Blender workflow"
    
    # ========== IMPLEMENTATION 1: Operation-Based Reference Generation ==========
    
    def implementation_1_operation_references(self, db_name: str) -> GeneratorImplementation:
        """Generate reference images for database operations"""
        operations = self.get_operations_from_db(db_name, limit=10)
        
        prompts = [self.create_prompt_from_operation(op) for op in operations]
        
        return GeneratorImplementation(
            name="Operation-Based Reference Generation",
            description=f"Generate reference images for {len(operations)} operations from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Create visual references for operations before execution",
            code_template=f'''def generate_references_for_operations(db_name="{db_name}"):
    """Generate reference images for all operations in database"""
    from image_generator_client import ImageGeneratorClient
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    
    generator = DatabaseDrivenGenerator()
    operations = generator.get_operations_from_db(db_name)
    client = ImageGeneratorClient()
    
    references = []
    for op in operations:
        prompt = generator.create_prompt_from_operation(op)
        result = client.generate_image_stable_diffusion(prompt)
        if result.get("success"):
            references.append({{
                "operation_id": op["id"],
                "image_path": result["image_path"],
                "prompt": prompt
            }})
    
    return references''',
            integration_points=[
                "Before operation execution - preview what will be created",
                "After operation failure - generate alternative reference",
                "For learning - visualize successful operations",
                "For documentation - create visual examples"
            ],
            example_prompts=prompts[:5]
        )
    
    # ========== IMPLEMENTATION 2: Pattern-Based Generation ==========
    
    def implementation_2_pattern_based(self, db_name: str) -> GeneratorImplementation:
        """Generate images based on successful code patterns"""
        patterns = self.get_patterns_from_db(db_name, limit=10)
        
        prompts = [self.create_prompt_from_pattern(p) for p in patterns]
        
        return GeneratorImplementation(
            name="Pattern-Based Reference Generation",
            description=f"Generate reference images for {len(patterns)} successful patterns from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Visualize proven techniques and workflows",
            code_template=f'''def generate_pattern_references(db_name="{db_name}"):
    """Generate reference images for successful patterns"""
    from image_generator_client import ImageGeneratorClient
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    
    generator = DatabaseDrivenGenerator()
    patterns = generator.get_patterns_from_db(db_name)
    client = ImageGeneratorClient()
    
    references = []
    for pattern in patterns:
        prompt = generator.create_prompt_from_pattern(pattern)
        result = client.generate_image_stable_diffusion(prompt)
        if result.get("success"):
            references.append({{
                "pattern_description": pattern["description"],
                "success_rate": pattern["success_count"] / (pattern["success_count"] + pattern["failure_count"]),
                "image_path": result["image_path"]
            }})
    
    return references''',
            integration_points=[
                "Pattern library - visual examples of successful techniques",
                "Learning system - show what works",
                "Quick reference - visual pattern guide",
                "Documentation - pattern visualization"
            ],
            example_prompts=prompts[:5]
        )
    
    # ========== IMPLEMENTATION 3: Scene Visualization ==========
    
    def implementation_3_scene_visualization(self, db_name: str) -> GeneratorImplementation:
        """Generate scene previews from operation descriptions"""
        operations = self.get_operations_from_db(db_name, limit=20)
        
        # Filter for scene-related operations
        scene_ops = [
            op for op in operations 
            if any(keyword in op.get("description", "").lower() 
                   for keyword in ["scene", "create", "add", "build", "setup"])
        ]
        
        prompts = [self.create_prompt_from_operation(op) for op in scene_ops]
        
        return GeneratorImplementation(
            name="Scene Visualization",
            description=f"Generate scene previews for {len(scene_ops)} scene operations from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Preview scenes before creating them in Blender",
            code_template=f'''def visualize_scenes_from_db(db_name="{db_name}"):
    """Generate scene previews from database operations"""
    from image_generator_client import ImageGeneratorClient
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    
    generator = DatabaseDrivenGenerator()
    operations = generator.get_operations_from_db(db_name)
    
    # Filter scene operations
    scene_ops = [op for op in operations 
                 if any(k in op["description"].lower() 
                        for k in ["scene", "create", "add", "build"])]
    
    client = ImageGeneratorClient()
    previews = []
    for op in scene_ops:
        prompt = generator.create_prompt_from_operation(op)
        result = client.generate_image_stable_diffusion(
            prompt, width=1024, height=1024, steps=30
        )
        if result.get("success"):
            previews.append({{
                "operation_id": op["id"],
                "preview_path": result["image_path"],
                "description": op["description"]
            }})
    
    return previews''',
            integration_points=[
                "Pre-creation preview - see scene before building",
                "Concept validation - verify idea before execution",
                "Client approval - show preview before work",
                "Planning - visualize complex scenes"
            ],
            example_prompts=prompts[:5]
        )
    
    # ========== IMPLEMENTATION 4: Error Recovery References ==========
    
    def implementation_4_error_recovery(self, db_name: str) -> GeneratorImplementation:
        """Generate alternative references when operations fail"""
        operations = self.get_operations_from_db(db_name, limit=50)
        
        # Filter failed operations
        failed_ops = [op for op in operations if not op.get("success", True)]
        
        prompts = [self.create_prompt_from_operation(op) for op in failed_ops]
        
        return GeneratorImplementation(
            name="Error Recovery Reference Generation",
            description=f"Generate alternative references for {len(failed_ops)} failed operations from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Generate alternative approaches when operations fail",
            code_template=f'''def generate_error_recovery_references(db_name="{db_name}"):
    """Generate alternative references for failed operations"""
    from image_generator_client import ImageGeneratorClient
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    
    generator = DatabaseDrivenGenerator()
    operations = generator.get_operations_from_db(db_name)
    
    failed_ops = [op for op in operations if not op.get("success", True)]
    client = ImageGeneratorClient()
    
    alternatives = []
    for op in failed_ops:
        # Create alternative prompt
        original_desc = op["description"]
        alternative_prompt = f"Alternative approach: {{original_desc}}, different technique, Blender workflow"
        
        result = client.generate_image_stable_diffusion(alternative_prompt)
        if result.get("success"):
            alternatives.append({{
                "failed_operation_id": op["id"],
                "alternative_image": result["image_path"],
                "suggestion": "Try this alternative approach"
            }})
    
    return alternatives''',
            integration_points=[
                "Error recovery - suggest alternatives when operations fail",
                "Learning from mistakes - visualize what didn't work",
                "Alternative approaches - explore different techniques",
                "Troubleshooting - visual debugging aid"
            ],
            example_prompts=prompts[:5] if prompts else []
        )
    
    # ========== IMPLEMENTATION 5: Model Performance Visualization ==========
    
    def implementation_5_model_performance(self, db_name: str) -> GeneratorImplementation:
        """Generate visualizations showing which models work best for what"""
        return GeneratorImplementation(
            name="Model Performance Visualization",
            description=f"Visualize model performance patterns from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Understand which models work best for different tasks",
            code_template=f'''def visualize_model_performance(db_name="{db_name}"):
    """Generate visual references showing model performance"""
    import sqlite3
    from image_generator_client import ImageGeneratorClient
    from pathlib import Path
    
    db_path = Path("databases") / db_name
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get model performance data
    cursor.execute("SELECT model_used, COUNT(*) as count, SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successes FROM operations GROUP BY model_used")
    
    models = cursor.fetchall()
    conn.close()
    
    client = ImageGeneratorClient()
    visualizations = []
    
    for model, count, successes in models:
        success_rate = successes / count if count > 0 else 0
        prompt = f"Visualization: {{model}} model performance, {{success_rate*100:.0f}}% success rate, Blender operations"
        
        result = client.generate_image_stable_diffusion(prompt)
        if result.get("success"):
            visualizations.append({{
                "model": model,
                "performance_image": result["image_path"],
                "success_rate": success_rate
            }})
    
    return visualizations''',
            integration_points=[
                "Model selection - visual guide to best models",
                "Performance analysis - understand model strengths",
                "Optimization - identify best model for task",
                "Documentation - model comparison visuals"
            ],
            example_prompts=[
                "Model performance visualization: llama3.2, high success rate, Blender operations",
                "Model comparison: different models for different tasks"
            ]
        )
    
    # ========== IMPLEMENTATION 6: Workflow Sequence Generation ==========
    
    def implementation_6_workflow_sequence(self, db_name: str) -> GeneratorImplementation:
        """Generate image sequences showing workflow steps"""
        operations = self.get_operations_from_db(db_name, limit=10)
        
        return GeneratorImplementation(
            name="Workflow Sequence Visualization",
            description=f"Generate step-by-step image sequences for workflows from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Visualize multi-step workflows as image sequences",
            code_template=f'''def generate_workflow_sequence(db_name="{db_name}", workflow_steps=None):
    """Generate image sequence for a workflow"""
    from image_generator_client import ImageGeneratorClient
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    
    generator = DatabaseDrivenGenerator()
    operations = generator.get_operations_from_db(db_name)
    
    if workflow_steps is None:
        # Use recent operations as workflow
        workflow_steps = operations[:5]
    
    client = ImageGeneratorClient()
    sequence = []
    
    for i, step in enumerate(workflow_steps, 1):
        prompt = f"Step {{i}} of workflow: {{step['description']}}, Blender tutorial step, clear instructions"
        result = client.generate_image_stable_diffusion(prompt, width=1024, height=1024)
        
        if result.get("success"):
            sequence.append({{
                "step_number": i,
                "image_path": result["image_path"],
                "description": step["description"]
            }})
    
    return sequence''',
            integration_points=[
                "Tutorial creation - visual step-by-step guides",
                "Workflow documentation - image-based tutorials",
                "Learning materials - visual workflow sequences",
                "Client presentations - show process visually"
            ],
            example_prompts=[
                f"Step {i} of workflow: {op['description']}" 
                for i, op in enumerate(operations[:5], 1)
            ]
        )
    
    # ========== IMPLEMENTATION 7: Video Generation from Sequences ==========
    
    def implementation_7_video_from_sequences(self, db_name: str) -> GeneratorImplementation:
        """Generate videos from operation sequences"""
        return GeneratorImplementation(
            name="Video Generation from Operation Sequences",
            description=f"Generate videos showing operation sequences from {db_name}",
            database_source=db_name,
            generator_type="video",
            use_case="Create reference videos from successful operation sequences",
            code_template=f'''def generate_video_from_sequence(db_name="{db_name}"):
    """Generate video from operation sequence"""
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    # Note: Requires Stable Video Diffusion or similar
    
    generator = DatabaseDrivenGenerator()
    operations = generator.get_operations_from_db(db_name, limit=5)
    
    # Generate keyframe images
    keyframes = []
    for op in operations:
        prompt = generator.create_prompt_from_operation(op)
        # Generate image (would use image generator)
        # Then convert to video frame
    
    # Use Stable Video Diffusion to create video from frames
    # video_result = stable_video_diffusion.generate_from_images(keyframes)
    
    return video_result''',
            integration_points=[
                "Reference videos - animated references",
                "Tutorial videos - automated tutorial creation",
                "Motion studies - animated workflow visualization",
                "Presentation videos - dynamic workflow demos"
            ],
            example_prompts=[
                "Video sequence: Blender workflow, step-by-step animation"
            ]
        )
    
    # ========== IMPLEMENTATION 8: Context-Aware Generation ==========
    
    def implementation_8_context_aware(self, db_name: str) -> GeneratorImplementation:
        """Generate images with context from database"""
        return GeneratorImplementation(
            name="Context-Aware Reference Generation",
            description=f"Generate references using full database context from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Generate references that consider all database knowledge",
            code_template=f'''def generate_context_aware_reference(db_name="{db_name}", operation_description: str):
    """Generate reference using full database context"""
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    from image_generator_client import ImageGeneratorClient
    
    generator = DatabaseDrivenGenerator()
    
    # Get related operations
    operations = generator.get_operations_from_db(db_name, limit=20)
    
    # Get successful patterns
    patterns = generator.get_patterns_from_db(db_name, limit=10)
    
    # Build context-aware prompt
    context = f"Based on {{len(operations)}} operations and {{len(patterns)}} patterns: "
    context += operation_description
    context += ", using proven techniques from database, Blender workflow"
    
    client = ImageGeneratorClient()
    result = client.generate_image_stable_diffusion(context, width=1024, height=1024, steps=30)
    
    return result''',
            integration_points=[
                "Intelligent generation - use all available knowledge",
                "Best practices - incorporate learned patterns",
                "Optimized references - leverage database insights",
                "Smart defaults - use proven approaches"
            ],
            example_prompts=[
                "Context-aware reference: using database knowledge, proven techniques"
            ]
        )
    
    # ========== IMPLEMENTATION 9: Batch Generation for Database ==========
    
    def implementation_9_batch_generation(self, db_name: str) -> GeneratorImplementation:
        """Batch generate references for entire database"""
        operations = self.get_operations_from_db(db_name, limit=100)
        
        return GeneratorImplementation(
            name="Batch Reference Generation",
            description=f"Batch generate references for {len(operations)} operations from {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Generate reference library for entire database",
            code_template=f'''def batch_generate_database_references(db_name="{db_name}"):
    """Batch generate references for all operations in database"""
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    from image_generator_client import ImageGeneratorClient
    import json
    from pathlib import Path
    
    generator = DatabaseDrivenGenerator()
    operations = generator.get_operations_from_db(db_name, limit=1000)
    client = ImageGeneratorClient()
    
    results = []
    for i, op in enumerate(operations, 1):
        print(f"Generating {{i}}/{{len(operations)}}: {{op['description'][:50]}}...")
        
        prompt = generator.create_prompt_from_operation(op)
        result = client.generate_image_stable_diffusion(prompt)
        
        if result.get("success"):
            results.append({{
                "operation_id": op["id"],
                "image_path": result["image_path"],
                "prompt": prompt,
                "description": op["description"]
            }})
    
    # Save batch results
    output_file = Path("output/generated") / f"{{db_name}}_references.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results''',
            integration_points=[
                "Reference library - comprehensive visual database",
                "Offline generation - pre-generate all references",
                "Documentation - complete visual documentation",
                "Learning resource - full visual knowledge base"
            ],
            example_prompts=[f"Batch generation for {len(operations)} operations"]
        )
    
    # ========== IMPLEMENTATION 10: Interactive Generation ==========
    
    def implementation_10_interactive(self, db_name: str) -> GeneratorImplementation:
        """Interactive generation with database feedback loop"""
        return GeneratorImplementation(
            name="Interactive Database-Driven Generation",
            description=f"Interactive generation with feedback loop using {db_name}",
            database_source=db_name,
            generator_type="image",
            use_case="Iterative generation with database learning",
            code_template=f'''def interactive_generation_with_feedback(db_name="{db_name}", initial_prompt: str):
    """Interactive generation with database feedback"""
    from database_driven_generator_implementations import DatabaseDrivenGenerator
    from image_generator_client import ImageGeneratorClient
    
    generator = DatabaseDrivenGenerator()
    client = ImageGeneratorClient()
    
    # Generate initial image
    result = client.generate_image_stable_diffusion(initial_prompt)
    
    if result.get("success"):
        # Store in database for future reference
        # This creates a feedback loop
        
        # Get similar operations from database
        similar_ops = generator.get_operations_from_db(db_name, limit=5)
        
        # Refine prompt based on similar successful operations
        refined_prompt = f"{{initial_prompt}}, similar to successful operations: {{similar_ops[0]['description']}}"
        
        # Generate refined version
        refined_result = client.generate_image_stable_diffusion(refined_prompt)
        
        return {{
            "initial": result,
            "refined": refined_result,
            "similar_operations": similar_ops
        }}
    
    return result''',
            integration_points=[
                "Iterative refinement - improve with feedback",
                "Learning system - database learns from generations",
                "Adaptive generation - adjust based on history",
                "Continuous improvement - better over time"
            ],
            example_prompts=[
                "Interactive generation with database feedback loop"
            ]
        )

def generate_all_implementations() -> Dict[str, List[GeneratorImplementation]]:
    """Generate all possible implementations for all databases"""
    
    databases = [
        "modeling_data.db",
        "shading_data.db",
        "animation_data.db",
        "vfx_data.db",
        "motiongraphics_data.db",
        "rendering_data.db",
        "rigging_data.db",
        "sculpting_data.db",
        "cameraoperator_data.db",
        "videography_data.db"
    ]
    
    generator = DatabaseDrivenGenerator()
    all_implementations = {}
    
    for db_name in databases:
        db_path = DATABASE_DIR / db_name
        if not db_path.exists():
            continue
        
        implementations = []
        
        # Generate all implementation types
        implementations.append(generator.implementation_1_operation_references(db_name))
        implementations.append(generator.implementation_2_pattern_based(db_name))
        implementations.append(generator.implementation_3_scene_visualization(db_name))
        implementations.append(generator.implementation_4_error_recovery(db_name))
        implementations.append(generator.implementation_5_model_performance(db_name))
        implementations.append(generator.implementation_6_workflow_sequence(db_name))
        implementations.append(generator.implementation_7_video_from_sequences(db_name))
        implementations.append(generator.implementation_8_context_aware(db_name))
        implementations.append(generator.implementation_9_batch_generation(db_name))
        implementations.append(generator.implementation_10_interactive(db_name))
        
        all_implementations[db_name] = implementations
    
    return all_implementations

def create_implementation_report():
    """Create comprehensive implementation report"""
    
    print("="*70)
    print("GENERATING ALL DATABASE-DRIVEN GENERATOR IMPLEMENTATIONS")
    print("="*70)
    print()
    
    all_implementations = generate_all_implementations()
    
    # Convert to JSON-serializable format
    report = {}
    for db_name, implementations in all_implementations.items():
        report[db_name] = []
        for impl in implementations:
            report[db_name].append({
                "name": impl.name,
                "description": impl.description,
                "database_source": impl.database_source,
                "generator_type": impl.generator_type,
                "use_case": impl.use_case,
                "code_template": impl.code_template,
                "integration_points": impl.integration_points,
                "example_prompts": impl.example_prompts
            })
    
    # Save JSON report
    json_file = Path("temp_tutorial_data/all_generator_implementations.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Create human-readable report
    report_text = []
    report_text.append("="*70)
    report_text.append("ALL POSSIBLE GENERATOR IMPLEMENTATIONS")
    report_text.append("="*70)
    report_text.append("")
    
    total_implementations = sum(len(impls) for impls in all_implementations.values())
    report_text.append(f"Total Databases: {len(all_implementations)}")
    report_text.append(f"Total Implementations: {total_implementations}")
    report_text.append("")
    
    for db_name, implementations in all_implementations.items():
        report_text.append(f"\n{'='*70}")
        report_text.append(f"DATABASE: {db_name}")
        report_text.append(f"{'='*70}")
        report_text.append("")
        
        for i, impl in enumerate(implementations, 1):
            report_text.append(f"\n[{i}] {impl.name}")
            report_text.append("-"*70)
            report_text.append(f"Description: {impl.description}")
            report_text.append(f"Type: {impl.generator_type}")
            report_text.append(f"Use Case: {impl.use_case}")
            report_text.append("")
            report_text.append("Integration Points:")
            for point in impl.integration_points:
                report_text.append(f"  • {point}")
            report_text.append("")
            report_text.append("Example Prompts:")
            for prompt in impl.example_prompts[:3]:
                report_text.append(f"  - {prompt[:80]}...")
            report_text.append("")
    
    report_text.append("\n" + "="*70)
    report_text.append("END OF REPORT")
    report_text.append("="*70)
    
    txt_file = Path("temp_tutorial_data/all_generator_implementations_report.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_text))
    
    print(f"[OK] Generated {total_implementations} implementations")
    print(f"[OK] JSON report: {json_file}")
    print(f"[OK] Text report: {txt_file}")
    print()
    print("\n".join(report_text))
    
    return report

if __name__ == "__main__":
    try:
        create_implementation_report()
    except Exception as e:
        print(f"\n[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()

