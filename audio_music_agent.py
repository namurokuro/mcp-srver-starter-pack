#!/usr/bin/env python3
"""
Audio/Music Agent - Генерира музика и аудио за Blender видеа
Интегрира се с AI музикални генератори (Suno AI, Udio, etc.)
"""

import requests
import json
import time
from typing import Dict, Optional, List
from pathlib import Path


class AudioMusicAgent:
    """Agent за генериране на музика и аудио"""
    
    def __init__(self):
        self.name = "AudioMusic"
        self.music_library = Path("music_library")
        self.music_library.mkdir(exist_ok=True)
        self.generated_tracks = []
    
    def generate_music_with_suno(self, prompt: str, duration: int = 30) -> Dict:
        """
        Генерира музика с Suno AI
        Note: Това изисква Suno API ключ или web scraping
        """
        # TODO: Implement Suno AI integration
        # За сега връщаме инструкции
        return {
            "status": "info",
            "message": "Suno AI integration needed",
            "instructions": {
                "manual": "Go to suno.ai and generate music with prompt",
                "prompt": prompt,
                "duration": duration,
                "download": "Download generated track and save to music_library/"
            }
        }
    
    def generate_music_with_udio(self, prompt: str, duration: int = 60) -> Dict:
        """
        Генерира музика с Udio
        Note: Това изисква Udio API ключ
        """
        # TODO: Implement Udio integration
        return {
            "status": "info",
            "message": "Udio integration needed",
            "instructions": {
                "manual": "Go to udio.com and generate music",
                "prompt": prompt,
                "duration": duration
            }
        }
    
    def suggest_music_for_scene(self, scene_description: str) -> Dict:
        """Предлага подходяща музика за сцена"""
        description_lower = scene_description.lower()
        
        # Определяне на стил базирано на описание
        if any(word in description_lower for word in ["explosion", "action", "dramatic", "intense"]):
            style = "dramatic cinematic music, intense, epic, 30 seconds"
        elif any(word in description_lower for word in ["calm", "peaceful", "serene", "ocean", "bedroom"]):
            style = "ambient atmospheric music, calm, peaceful, 60 seconds"
        elif any(word in description_lower for word in ["modern", "futuristic", "tech", "ai"]):
            style = "electronic tech music, modern, futuristic, 30 seconds"
        elif any(word in description_lower for word in ["transformation", "before", "after", "reveal"]):
            style = "upbeat electronic music, energetic, build-up to drop, 30 seconds"
        else:
            style = "cinematic background music, versatile, 45 seconds"
        
        return {
            "status": "success",
            "suggested_style": style,
            "prompt": f"{style}, TikTok style, high quality",
            "recommended_generators": ["Suno AI", "Udio", "Mubert"],
            "duration": 30 if "30 seconds" in style else 60
        }
    
    def create_music_prompt(self, video_type: str, mood: str, duration: int = 30) -> str:
        """Създава оптимизиран prompt за музика"""
        prompts = {
            "before_after": f"Upbeat electronic music, energetic, modern, {duration} seconds, TikTok style, build-up to satisfying drop",
            "tutorial": f"Clean professional music, not distracting, educational vibe, {duration} seconds, background-friendly",
            "time_lapse": f"Ambient atmospheric music, smooth, flowing, {duration} seconds, background-friendly, calming",
            "behind_scenes": f"Tech electronic music, futuristic, modern, {duration} seconds, AI-themed, energetic",
            "transformation": f"Inspirational cinematic music, uplifting, progressive, {duration} seconds, positive vibes",
            "cinematic": f"Cinematic orchestral music, dramatic, emotional, {duration} seconds, high quality",
            "funny": f"Playful upbeat music, fun, lighthearted, {duration} seconds, TikTok style",
            "dramatic": f"Dramatic cinematic music, intense, epic, {duration} seconds, high quality"
        }
        
        base_prompt = prompts.get(video_type, f"{mood} music, {duration} seconds, TikTok style")
        return f"{base_prompt}, high quality, no vocals (instrumental)"
    
    def get_music_recommendations(self, scene_type: str) -> List[Dict]:
        """Връща препоръки за музика"""
        recommendations = {
            "bedroom": {
                "style": "ambient atmospheric music, calm, peaceful",
                "generators": ["Suno AI", "Udio", "Mubert"],
                "duration": 60,
                "mood": "serene, relaxing"
            },
            "explosion": {
                "style": "dramatic cinematic music, intense, epic",
                "generators": ["Suno AI", "AIVA"],
                "duration": 30,
                "mood": "intense, dramatic"
            },
            "tutorial": {
                "style": "clean professional music, background-friendly",
                "generators": ["Mubert", "Stable Audio"],
                "duration": 60,
                "mood": "professional, educational"
            }
        }
        
        return [recommendations.get(scene_type, {
            "style": "versatile cinematic music",
            "generators": ["Suno AI"],
            "duration": 45,
            "mood": "neutral"
        })]
    
    def save_music_info(self, track_name: str, prompt: str, generator: str, file_path: str):
        """Запазва информация за генерираната музика"""
        track_info = {
            "name": track_name,
            "prompt": prompt,
            "generator": generator,
            "file_path": file_path,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.generated_tracks.append(track_info)
        
        # Запазване в JSON файл
        library_file = self.music_library / "music_library.json"
        if library_file.exists():
            with open(library_file, 'r', encoding='utf-8') as f:
                library = json.load(f)
        else:
            library = []
        
        library.append(track_info)
        
        with open(library_file, 'w', encoding='utf-8') as f:
            json.dump(library, f, indent=2, ensure_ascii=False)
    
    def list_generated_tracks(self) -> List[Dict]:
        """Връща списък с генерирани тракове"""
        library_file = self.music_library / "music_library.json"
        if library_file.exists():
            with open(library_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


def main():
    """Test the audio music agent"""
    agent = AudioMusicAgent()
    
    # Test scene suggestion
    result = agent.suggest_music_for_scene("modern bedroom with ocean view")
    print("Suggested music:", result)
    
    # Test prompt creation
    prompt = agent.create_music_prompt("before_after", "energetic", 30)
    print("\nGenerated prompt:", prompt)
    
    # Test recommendations
    recs = agent.get_music_recommendations("bedroom")
    print("\nRecommendations:", recs)


if __name__ == "__main__":
    main()

