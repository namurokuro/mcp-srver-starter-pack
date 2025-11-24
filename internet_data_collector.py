#!/usr/bin/env python3
"""
Internet Data Collector for Blender Learning System
Collects knowledge from:
- Blender documentation
- Tutorials and guides
- Code examples
- API references
- Community forums
- GitHub repositories
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import time
import hashlib
from urllib.parse import urljoin, urlparse
import sys

class InternetDataCollector:
    """Collects Blender knowledge from internet sources"""
    
    def __init__(self, db_path: str = "blender_data.db"):
        self.db_path = db_path
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables for internet-collected data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Internet knowledge table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS internet_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT NOT NULL,
                source_type TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                code_examples TEXT,
                tags TEXT,
                collected_at TEXT NOT NULL,
                content_hash TEXT UNIQUE,
                relevance_score REAL DEFAULT 0.0,
                verified INTEGER DEFAULT 0
            )
        """)
        
        # API examples table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_examples (
                api_call TEXT NOT NULL,
                example_code TEXT NOT NULL,
                source_url TEXT,
                description TEXT,
                parameters TEXT,
                return_type TEXT,
                collected_at TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                PRIMARY KEY (api_call, example_code)
            )
        """)
        
        # Tutorial patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tutorial_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                title TEXT,
                description TEXT,
                code_template TEXT,
                source_url TEXT,
                collected_at TEXT NOT NULL,
                success_count INTEGER DEFAULT 0,
                tags TEXT
            )
        """)
        
        # Best practices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS best_practices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                practice TEXT NOT NULL,
                description TEXT,
                code_example TEXT,
                source_url TEXT,
                collected_at TEXT NOT NULL,
                verified_count INTEGER DEFAULT 0,
                tags TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def collect_blender_docs(self, base_url: str = "https://docs.blender.org/api/current/") -> List[Dict]:
        """Collect from Blender official API documentation"""
        print(f"📚 Collecting from Blender API docs: {base_url}")
        collected = []
        
        try:
            # Main API reference pages
            api_pages = [
                "bpy.ops.html",
                "bpy.types.html",
                "bpy.data.html",
                "bpy.context.html",
                "mathutils.html"
            ]
            
            for page in api_pages:
                url = urljoin(base_url, page)
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        data = self._parse_doc_page(url, response.text)
                        if data:
                            collected.append(data)
                            self._store_knowledge(data)
                            print(f"  ✅ Collected: {page}")
                            time.sleep(1)  # Be polite
                except Exception as e:
                    print(f"  ⚠️  Error collecting {page}: {e}")
            
        except Exception as e:
            print(f"❌ Error collecting Blender API docs: {e}")
        
        return collected
    
    def collect_blender_manual(self, base_url: str = "https://docs.blender.org/manual/en/latest/", 
                              sections: List[str] = None) -> List[Dict]:
        """Collect from Blender User Manual"""
        print(f"📖 Collecting from Blender Manual: {base_url}")
        collected = []
        
        if sections is None:
            # Key sections for learning
            sections = [
                "getting_started/configuration/index.html",
                "modeling/index.html",
                "sculpting_paint/index.html",
                "animation/index.html",
                "physics/index.html",
                "rendering/index.html",
                "compositing/index.html",
                "scripting/index.html",
                "addons/index.html"
            ]
        
        try:
            for section in sections:
                url = urljoin(base_url, section)
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        data = self._parse_manual_page(url, response.text)
                        if data:
                            collected.append(data)
                            self._store_knowledge(data)
                            print(f"  ✅ Collected: {section}")
                        
                        # Also collect linked pages from this section
                        linked_pages = self._extract_manual_links(response.text, base_url)
                        for link in linked_pages[:5]:  # Limit to 5 per section
                            try:
                                link_response = self.session.get(link, timeout=10)
                                if link_response.status_code == 200:
                                    link_data = self._parse_manual_page(link, link_response.text)
                                    if link_data:
                                        collected.append(link_data)
                                        self._store_knowledge(link_data)
                                        print(f"    ✅ Collected linked page")
                                time.sleep(0.5)
                            except Exception as e:
                                pass  # Skip failed links
                        
                        time.sleep(1)  # Be polite
                except Exception as e:
                    print(f"  ⚠️  Error collecting {section}: {e}")
            
        except Exception as e:
            print(f"❌ Error collecting Blender Manual: {e}")
        
        return collected
    
    def _parse_manual_page(self, url: str, html: str) -> Optional[Dict]:
        """Parse Blender manual page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = title_elem.text.strip() if title_elem else url.split('/')[-1]
            
            # Remove navigation and footer
            for elem in soup.find_all(['nav', 'footer', 'header', 'script', 'style']):
                elem.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                content = main_content.get_text(separator='\n', strip=True)
            else:
                content = soup.get_text(separator='\n', strip=True)
            
            # Limit content size
            content = content[:10000]  # First 10KB
            
            # Extract code examples
            code_blocks = soup.find_all(['pre', 'code', 'div'], class_=re.compile(r'code|example|highlight'))
            code_examples = []
            for code in code_blocks:
                code_text = code.get_text()
                if 'bpy' in code_text or 'import' in code_text or len(code_text) > 20:
                    code_examples.append(code_text[:500])  # Limit code size
            
            # Extract key terms and concepts
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
            key_concepts = [h.get_text().strip() for h in headings[:10]]
            
            content_hash = hashlib.md5((url + content[:1000]).encode()).hexdigest()
            
            # Determine tags based on URL
            tags = []
            if 'configuration' in url:
                tags.append('configuration')
            if 'modeling' in url:
                tags.append('modeling')
            if 'animation' in url:
                tags.append('animation')
            if 'scripting' in url:
                tags.append('scripting')
            if 'rendering' in url:
                tags.append('rendering')
            tags.append('manual')
            tags.append('documentation')
            
            return {
                "source_url": url,
                "source_type": "blender_manual",
                "title": title,
                "content": content,
                "code_examples": json.dumps(code_examples),
                "tags": ",".join(tags),
                "collected_at": datetime.now().isoformat(),
                "content_hash": content_hash,
                "relevance_score": 0.9,  # Manual is highly relevant
                "verified": 1  # Official documentation
            }
        except Exception as e:
            print(f"  ⚠️  Error parsing manual page: {e}")
            return None
    
    def _extract_manual_links(self, html: str, base_url: str) -> List[str]:
        """Extract relevant links from manual page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # Convert relative to absolute
                if href.startswith('/'):
                    href = urljoin(base_url, href)
                elif not href.startswith('http'):
                    href = urljoin(base_url, href)
                
                # Only include manual pages
                if 'docs.blender.org/manual' in href and href not in links:
                    links.append(href)
            
            return links[:20]  # Limit to 20 links
        except:
            return []
    
    def collect_github_examples(self, repo_url: str, search_terms: List[str] = None) -> List[Dict]:
        """Collect code examples from GitHub repositories"""
        print(f"🔍 Collecting from GitHub: {repo_url}")
        collected = []
        
        if search_terms is None:
            search_terms = ["blender", "python", "bpy", "addon"]
        
        # GitHub API search
        try:
            for term in search_terms:
                api_url = f"https://api.github.com/search/code"
                params = {
                    "q": f"{term} language:python",
                    "sort": "stars",
                    "order": "desc",
                    "per_page": 10
                }
                
                try:
                    response = self.session.get(api_url, params=params, timeout=10)
                    if response.status_code == 200:
                        results = response.json().get("items", [])
                        for item in results:
                            code_data = self._extract_github_code(item)
                            if code_data:
                                collected.append(code_data)
                                self._store_knowledge(code_data)
                        print(f"  ✅ Found {len(results)} examples for '{term}'")
                    time.sleep(2)  # GitHub rate limit
                except Exception as e:
                    print(f"  ⚠️  Error searching '{term}': {e}")
        
        except Exception as e:
            print(f"❌ Error collecting from GitHub: {e}")
        
        return collected
    
    def collect_stackoverflow(self, tags: List[str] = None, max_pages: int = 5) -> List[Dict]:
        """Collect from Stack Overflow"""
        print("💬 Collecting from Stack Overflow...")
        collected = []
        
        if tags is None:
            tags = ["blender", "blender-python", "bpy"]
        
        try:
            for tag in tags:
                for page in range(1, max_pages + 1):
                    api_url = "https://api.stackexchange.com/2.3/questions"
                    params = {
                        "order": "desc",
                        "sort": "votes",
                        "tagged": tag,
                        "site": "stackoverflow",
                        "page": page,
                        "pagesize": 50,
                        "filter": "withbody"
                    }
                    
                    try:
                        response = self.session.get(api_url, params=params, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            questions = data.get("items", [])
                            
                            for q in questions:
                                so_data = self._parse_stackoverflow_question(q)
                                if so_data:
                                    collected.append(so_data)
                                    self._store_knowledge(so_data)
                            
                            print(f"  ✅ Collected {len(questions)} questions for '{tag}' (page {page})")
                            
                            if not data.get("has_more", False):
                                break
                            
                            time.sleep(1)  # Rate limit
                    except Exception as e:
                        print(f"  ⚠️  Error on page {page}: {e}")
        
        except Exception as e:
            print(f"❌ Error collecting from Stack Overflow: {e}")
        
        return collected
    
    def collect_youtube_tutorials(self, search_query: str, max_results: int = 10) -> List[Dict]:
        """Collect tutorial information from YouTube (metadata only)"""
        print(f"🎥 Collecting YouTube tutorials: {search_query}")
        collected = []
        
        # Note: YouTube API requires API key
        # This is a placeholder for when API key is available
        # For now, we can collect from YouTube URLs if provided
        
        print("  ⚠️  YouTube API requires key - skipping for now")
        return collected
    
    def collect_blender_artists(self, search_terms: List[str] = None) -> List[Dict]:
        """Collect from Blender Artists forum"""
        print("🎨 Collecting from Blender Artists forum...")
        collected = []
        
        if search_terms is None:
            search_terms = ["python", "scripting", "addon"]
        
        base_url = "https://blenderartists.org"
        
        # Note: Would need to scrape or use API if available
        print("  ⚠️  Forum scraping requires careful implementation")
        return collected
    
    def _parse_doc_page(self, url: str, html: str) -> Optional[Dict]:
        """Parse Blender documentation page"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract title
            title = soup.find('title')
            title_text = title.text if title else url
            
            # Extract code examples
            code_blocks = soup.find_all(['pre', 'code'])
            code_examples = []
            for code in code_blocks:
                code_text = code.get_text()
                if 'bpy' in code_text or 'import bpy' in code_text:
                    code_examples.append(code_text)
            
            # Extract main content
            content = soup.get_text()[:5000]  # Limit content
            
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            return {
                "source_url": url,
                "source_type": "blender_docs",
                "title": title_text,
                "content": content,
                "code_examples": json.dumps(code_examples),
                "tags": "documentation,api,reference",
                "collected_at": datetime.now().isoformat(),
                "content_hash": content_hash,
                "relevance_score": 1.0,
                "verified": 1
            }
        except Exception as e:
            print(f"  ⚠️  Error parsing doc page: {e}")
            return None
    
    def _extract_github_code(self, item: Dict) -> Optional[Dict]:
        """Extract code from GitHub search result"""
        try:
            file_url = item.get("html_url", "")
            repo_name = item.get("repository", {}).get("full_name", "")
            
            # Get file content
            raw_url = file_url.replace("/blob/", "/raw/")
            response = self.session.get(raw_url, timeout=10)
            
            if response.status_code == 200:
                code = response.text
                
                # Extract Blender-specific code
                if 'bpy' in code or 'import bpy' in code:
                    # Extract function/class definitions
                    functions = re.findall(r'def\s+(\w+).*?:', code)
                    classes = re.findall(r'class\s+(\w+).*?:', code)
                    
                    return {
                        "source_url": file_url,
                        "source_type": "github",
                        "title": f"{repo_name} - {item.get('name', '')}",
                        "content": code[:2000],  # First 2000 chars
                        "code_examples": json.dumps([code]),
                        "tags": f"github,{repo_name}",
                        "collected_at": datetime.now().isoformat(),
                        "content_hash": hashlib.md5(code.encode()).hexdigest(),
                        "relevance_score": 0.8,
                        "verified": 0
                    }
        except Exception as e:
            print(f"  ⚠️  Error extracting GitHub code: {e}")
        
        return None
    
    def _parse_stackoverflow_question(self, question: Dict) -> Optional[Dict]:
        """Parse Stack Overflow question"""
        try:
            title = question.get("title", "")
            body = question.get("body", "")
            question_id = question.get("question_id", 0)
            score = question.get("score", 0)
            tags = ",".join(question.get("tags", []))
            
            # Extract code blocks
            code_blocks = re.findall(r'<code>(.*?)</code>', body, re.DOTALL)
            python_code = [code for code in code_blocks if 'bpy' in code or 'import' in code]
            
            if python_code or 'blender' in title.lower():
                url = f"https://stackoverflow.com/questions/{question_id}"
                
                return {
                    "source_url": url,
                    "source_type": "stackoverflow",
                    "title": title,
                    "content": body[:3000],  # Limit content
                    "code_examples": json.dumps(python_code),
                    "tags": tags,
                    "collected_at": datetime.now().isoformat(),
                    "content_hash": hashlib.md5((title + body).encode()).hexdigest(),
                    "relevance_score": min(score / 10.0, 1.0),  # Normalize score
                    "verified": 1 if score > 5 else 0
                }
        except Exception as e:
            print(f"  ⚠️  Error parsing SO question: {e}")
        
        return None
    
    def _store_knowledge(self, data: Dict):
        """Store collected knowledge in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO internet_knowledge 
                (source_url, source_type, title, content, code_examples, tags, 
                 collected_at, content_hash, relevance_score, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get("source_url"),
                data.get("source_type"),
                data.get("title"),
                data.get("content"),
                data.get("code_examples"),
                data.get("tags"),
                data.get("collected_at"),
                data.get("content_hash"),
                data.get("relevance_score", 0.0),
                data.get("verified", 0)
            ))
            
            conn.commit()
        except sqlite3.IntegrityError:
            # Duplicate content_hash, skip
            pass
        except Exception as e:
            print(f"  ⚠️  Error storing knowledge: {e}")
        finally:
            conn.close()
    
    def extract_api_examples(self) -> List[Dict]:
        """Extract API usage examples from collected knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT code_examples, source_url FROM internet_knowledge
            WHERE code_examples IS NOT NULL AND code_examples != '[]'
        """)
        
        api_examples = []
        for row in cursor.fetchall():
            code_examples_json, source_url = row
            try:
                examples = json.loads(code_examples_json)
                for code in examples:
                    # Extract API calls
                    api_calls = re.findall(r'bpy\.(ops|data|types|context)\.\w+', code)
                    for api_call in api_calls:
                        api_examples.append({
                            "api_call": api_call,
                            "example_code": code[:1000],
                            "source_url": source_url,
                            "collected_at": datetime.now().isoformat()
                        })
            except:
                pass
        
        conn.close()
        return api_examples
    
    def search_knowledge(self, query: str, limit: int = 10) -> List[Dict]:
        """Search collected internet knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT source_url, source_type, title, content, code_examples, 
                   tags, relevance_score, verified
            FROM internet_knowledge
            WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
            ORDER BY relevance_score DESC, verified DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "source_url": row[0],
                "source_type": row[1],
                "title": row[2],
                "content": row[3][:500],  # Preview
                "code_examples": json.loads(row[4]) if row[4] else [],
                "tags": row[5],
                "relevance_score": row[6],
                "verified": row[7]
            })
        
        conn.close()
        return results


def main():
    """Main collection function"""
    print("=" * 70)
    print("INTERNET DATA COLLECTOR FOR BLENDER LEARNING")
    print("=" * 70)
    print()
    
    collector = InternetDataCollector()
    
    # Collect from different sources
    print("Starting data collection...\n")
    
    # 1. Blender API Documentation
    collector.collect_blender_docs()
    print()
    
    # 2. Blender User Manual
    collector.collect_blender_manual()
    print()
    
    # 3. GitHub Examples
    collector.collect_github_examples("https://github.com")
    print()
    
    # 4. Stack Overflow
    collector.collect_stackoverflow(max_pages=3)
    print()
    
    # Summary
    conn = sqlite3.connect(collector.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM internet_knowledge")
    total = cursor.fetchone()[0]
    conn.close()
    
    print("=" * 70)
    print(f"✅ Collection complete! Total knowledge items: {total}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Collection interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

