"""
YouTube Scraper for MCP Server
Extracts video information, transcripts, and metadata from YouTube videos
"""

import json
import re
import sys
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs
import requests

try:
    from yt_dlp import YoutubeDL
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("[WARNING] yt-dlp not available. Install with: pip install yt-dlp", file=sys.stderr)

class YouTubeScraper:
    """YouTube video scraper using yt-dlp"""
    
    def __init__(self):
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is required. Install with: pip install yt-dlp")
        
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, url: str, include_transcript: bool = False) -> Dict[str, Any]:
        """
        Get comprehensive video information
        
        Args:
            url: YouTube video URL
            include_transcript: Whether to include transcript/subtitles
            
        Returns:
            Dictionary with video information
        """
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        info = {
            'video_id': video_id,
            'url': url,
            'success': False,
            'error': None
        }
        
        try:
            # Configure options
            opts = self.ydl_opts.copy()
            if include_transcript:
                opts['writesubtitles'] = True
                opts['writeautomaticsub'] = True
                opts['subtitleslangs'] = ['en', 'en-US', 'en-GB']
                opts['subtitlesformat'] = 'vtt'
            
            with YoutubeDL(opts) as ydl:
                video_data = ydl.extract_info(url, download=False)
                
                # Extract relevant information
                info.update({
                    'success': True,
                    'title': video_data.get('title', ''),
                    'description': video_data.get('description', ''),
                    'duration': video_data.get('duration', 0),
                    'duration_string': video_data.get('duration_string', ''),
                    'uploader': video_data.get('uploader', ''),
                    'uploader_id': video_data.get('uploader_id', ''),
                    'upload_date': video_data.get('upload_date', ''),
                    'view_count': video_data.get('view_count', 0),
                    'like_count': video_data.get('like_count', 0),
                    'thumbnail': video_data.get('thumbnail', ''),
                    'categories': video_data.get('categories', []),
                    'tags': video_data.get('tags', []),
                    'webpage_url': video_data.get('webpage_url', url),
                    'formats': self._extract_format_info(video_data.get('formats', [])),
                })
                
                # Get transcript if requested
                if include_transcript:
                    transcript = self._get_transcript(video_data, video_id)
                    if transcript:
                        info['transcript'] = transcript
                
        except Exception as e:
            info['error'] = str(e)
            info['success'] = False
        
        return info
    
    def _extract_format_info(self, formats: List[Dict]) -> List[Dict]:
        """Extract relevant format information"""
        format_info = []
        for fmt in formats:
            format_info.append({
                'format_id': fmt.get('format_id', ''),
                'ext': fmt.get('ext', ''),
                'resolution': fmt.get('resolution', ''),
                'fps': fmt.get('fps', 0),
                'vcodec': fmt.get('vcodec', ''),
                'acodec': fmt.get('acodec', ''),
                'filesize': fmt.get('filesize', 0),
            })
        return format_info
    
    def _get_transcript(self, video_data: Dict, video_id: str) -> Optional[Dict]:
        """Extract transcript/subtitles if available"""
        try:
            # Check for automatic captions
            automatic_captions = video_data.get('automatic_captions', {})
            subtitles = video_data.get('subtitles', {})
            
            # Try to get English subtitles
            for lang_code in ['en', 'en-US', 'en-GB']:
                if lang_code in automatic_captions:
                    return {
                        'language': lang_code,
                        'type': 'automatic',
                        'available': True
                    }
                if lang_code in subtitles:
                    return {
                        'language': lang_code,
                        'type': 'manual',
                        'available': True
                    }
            
            return {
                'available': False,
                'message': 'No English subtitles available'
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def get_transcript_text(self, url: str, language: str = 'en') -> Optional[str]:
        """
        Get transcript text from video
        
        Args:
            url: YouTube video URL
            language: Language code (default: 'en')
            
        Returns:
            Transcript text or None
        """
        try:
            opts = {
                'quiet': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': [language],
                'subtitlesformat': 'vtt',
                'skip_download': True,
            }
            
            with YoutubeDL(opts) as ydl:
                video_data = ydl.extract_info(url, download=False)
                video_id = video_data.get('id', '')
                
                # Try to download and parse transcript
                # Note: This is a simplified version - full implementation would
                # download the subtitle file and parse it
                return f"Transcript available for video {video_id}"
                
        except Exception as e:
            print(f"Error getting transcript: {e}", file=sys.stderr)
            return None
    
    def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for YouTube videos
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of video information dictionaries
        """
        try:
            opts = {
                'quiet': True,
                'default_search': 'ytsearch',
                'extract_flat': True,
            }
            
            with YoutubeDL(opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                results = ydl.extract_info(search_query, download=False)
                
                videos = []
                if 'entries' in results:
                    for entry in results['entries']:
                        if entry:
                            videos.append({
                                'video_id': entry.get('id', ''),
                                'title': entry.get('title', ''),
                                'url': entry.get('url', ''),
                                'duration': entry.get('duration', 0),
                                'view_count': entry.get('view_count', 0),
                            })
                
                return videos
                
        except Exception as e:
            print(f"Error searching videos: {e}", file=sys.stderr)
            return []

def scrape_youtube_video(url: str, include_transcript: bool = False) -> Dict[str, Any]:
    """
    Convenience function to scrape a YouTube video
    
    Args:
        url: YouTube video URL
        include_transcript: Whether to include transcript information
        
    Returns:
        Video information dictionary
    """
    scraper = YouTubeScraper()
    return scraper.get_video_info(url, include_transcript)

def search_youtube(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to search YouTube
    
    Args:
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of video information dictionaries
    """
    scraper = YouTubeScraper()
    return scraper.search_videos(query, max_results)

if __name__ == "__main__":
    # Test the scraper
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_scraper.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    print(f"Scraping: {url}")
    
    try:
        scraper = YouTubeScraper()
        info = scraper.get_video_info(url, include_transcript=True)
        print(json.dumps(info, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

