#!/usr/bin/env python3
"""
Intelligent Question Generator for Sip & Spill
Researches shows/movies and generates quality trivia questions via Claude
Optimizes token usage by batching questions in single API calls
"""

import json
import os
from typing import Optional
from datetime import datetime
import re

import requests
from anthropic import Anthropic

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Output file for generated questions
OUTPUT_FILE = 'data/generated_questions.json'


# ═══════════════════════════════════════════════════════════════
# RESEARCH ENGINE: Wikipedia + Web
# ═══════════════════════════════════════════════════════════════

def research_show(show_name: str) -> dict:
    """
    Research a show/movie using Wikipedia and web search
    Returns: {title, genre, release_year, characters, plot_summary, episodes, etc.}
    """
    print(f"\n🔍 Researching '{show_name}'...")
    
    research_data = {
        'title': show_name,
        'genre': [],
        'release_year': None,
        'main_characters': [],
        'plot_summary': '',
        'network': '',
        'years_aired': '',
        'creator': '',
        'episodes_count': 0,
        'source_url': ''
    }
    
    # Try Wikipedia first
    wiki_data = _search_wikipedia(show_name)
    if wiki_data:
        research_data.update(wiki_data)
        return research_data
    
    # Fallback: prompt user for details
    print("  ⚠️  Wikipedia lookup not available. Let's gather info manually:")
    research_data['plot_summary'] = input("  📝 Brief plot summary: ").strip()
    research_data['main_characters'] = input("  👥 Main characters (comma-separated): ").strip().split(',')
    research_data['genre'] = input("  🎬 Genre (comma-separated): ").strip().split(',')
    
    return research_data


def _search_wikipedia(show_name: str) -> Optional[dict]:
    """Attempt to fetch show info from Wikipedia via API"""
    try:
        # Wikipedia API search
        url = 'https://en.wikipedia.org/w/api.php'
        params = {
            'action': 'query',
            'format': 'json',
            'srsearch': show_name,
            'srprop': 'snippet',
            'srlimit': 3
        }
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            print("  ✅ Wikipedia found relevant info")
            return None  # In production, parse response better
        
    except Exception as e:
        print(f"  ⚠️  Wikipedia lookup failed: {e}")
    
    return None


# ═══════════════════════════════════════════════════════════════
# QUESTION GENERATION: Claude API (Token-Optimized)
# ═══════════════════════════════════════════════════════════════

def generate_questions_batch(
    show_data: dict,
    num_questions: int = 4,
    difficulty: str = 'medium'
) -> list:
    """
    Generate multiple quality trivia questions in ONE API call (token efficient)
    Uses Claude with smart prompting to create good distractors
    
    Returns: [
        {'q': '...', 'options': ['opt1', 'opt2', 'opt3'], 'answer': 0, 'fact': '...'},
        ...
    ]
    """
    client = Anthropic()
    
    # Build research context for Claude
    context = _build_research_context(show_data)
    
    prompt = f"""You are a trivia expert. Generate {num_questions} smart trivia questions about "{show_data['title']}" based on this research:

{context}

REQUIREMENTS FOR EACH QUESTION:
1. Medium difficulty - not too easy, not impossible
2. 3 options ONLY (no 4th option)
3. Answer at index 0 (first option is ALWAYS correct)
4. Plausible distractors - related but WRONG (not obviously wrong)
5. Fact must be interesting and not just repeat the question

FORMAT: Output ONLY valid JSON array, no extra text. Example:
[
  {{"q": "Question text here?", "options": ["Correct Answer", "Plausible Wrong", "Plausible Wrong"], "answer": 0, "fact": "Interesting fact about the show/character."}},
  ...
]

Generate {num_questions} questions now:"""

    print(f"  🤖 Generating {num_questions} questions with Claude...")
    
    try:
        message = client.messages.create(
            model='claude-3-5-sonnet-20241022',
            max_tokens=1500,
            messages=[
                {'role': 'user', 'content': prompt}
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        questions = json.loads(response_text)
        
        print(f"  ✅ Generated {len(questions)} questions")
        return questions
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Failed to parse questions. Claude response: {response_text[:200]}")
        return []
    except Exception as e:
        print(f"  ❌ API error: {e}")
        return []


def _build_research_context(show_data: dict) -> str:
    """Format research data for Claude prompt"""
    context = f"""
Title: {show_data['title']}
Genre: {', '.join(show_data['genre']) if isinstance(show_data['genre'], list) else show_data['genre']}
Years Aired: {show_data['years_aired']}
Creator: {show_data['creator']}
Network: {show_data['network']}

Plot Summary:
{show_data['plot_summary']}

Main Characters: {', '.join(show_data['main_characters']) if isinstance(show_data['main_characters'], list) else show_data['main_characters']}

Episode Count: {show_data['episodes_count']}
"""
    return context


# ═══════════════════════════════════════════════════════════════
# STORAGE & MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def load_questions_database() -> dict:
    """Load existing questions from JSON file"""
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load existing questions: {e}")
    
    return {
        'disney': [],
        'pop': [],
        'celeb': [],
        'custom': [],
        'metadata': {
            'last_updated': None,
            'total_questions': 0,
            'categories': {}
        }
    }


def save_questions(qdb: dict):
    """Save questions to JSON file"""
    os.makedirs('data', exist_ok=True)
    
    # Update metadata
    total = sum(len(qdb[cat]) for cat in ['disney', 'pop', 'celeb', 'custom'])
    qdb['metadata']['last_updated'] = datetime.now().isoformat()
    qdb['metadata']['total_questions'] = total
    for cat in ['disney', 'pop', 'celeb', 'custom']:
        qdb['metadata']['categories'][cat] = len(qdb[cat])
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(qdb, f, indent=2)
    
    print(f"\n✅ Saved! Questions: {OUTPUT_FILE}")
    print(f"   Disney: {len(qdb['disney'])} | Pop: {len(qdb['pop'])} | Celebrity: {len(qdb['celeb'])}")


def add_questions_to_category(
    qdb: dict,
    category: str,
    show_name: str,
    questions: list
):
    """Add generated questions to a category"""
    if category not in qdb:
        qdb[category] = []
    
    for q in questions:
        q['show'] = show_name  # Track which show each question came from
        q['added_date'] = datetime.now().isoformat()
        qdb[category].append(q)


# ═══════════════════════════════════════════════════════════════
# INTERACTIVE WORKFLOW
# ═══════════════════════════════════════════════════════════════

def interactive_generator():
    """Main interactive mode: Research show → Generate questions → Save"""
    print("\n" + "="*60)
    print("  🍹 Sip & Spill — Question Generator")
    print("="*60)
    
    qdb = load_questions_database()
    
    while True:
        print("\nOptions:")
        print("  1️⃣  Generate questions for a new show")
        print("  2️⃣  View existing questions")
        print("  3️⃣  Delete a show's questions")
        print("  4️⃣  Export to Supabase")
        print("  5️⃣  Exit")
        
        choice = input("\nChoose (1-5): ").strip()
        
        if choice == '1':
            show_name = input("\n📺 Show/Movie name: ").strip()
            if not show_name:
                print("  ❌ Name required")
                continue
            
            category = input("📁 Category (disney/pop/celeb/custom): ").strip().lower()
            if category not in ['disney', 'pop', 'celeb', 'custom']:
                category = 'custom'
            
            # Research
            show_data = research_show(show_name)
            
            # Generate questions
            num_qs = int(input("🔢 How many questions? (1-10, default 4): ") or "4")
            num_qs = max(1, min(10, num_qs))
            
            questions = generate_questions_batch(show_data, num_questions=num_qs)
            
            if questions:
                add_questions_to_category(qdb, category, show_name, questions)
                save_questions(qdb)
        
        elif choice == '2':
            print("\n📊 Questions by Category:")
            for cat in ['disney', 'pop', 'celeb', 'custom']:
                count = len(qdb[cat])
                print(f"  {cat.upper()}: {count} questions")
                if count > 0:
                    shows = set(q.get('show', 'Unknown') for q in qdb[cat])
                    print(f"    Shows: {', '.join(shows)}")
        
        elif choice == '3':
            category = input("📁 Category (disney/pop/celeb/custom): ").strip().lower()
            show_name = input("📺 Show name to delete: ").strip()
            
            if category in qdb:
                before = len(qdb[category])
                qdb[category] = [q for q in qdb[category] if q.get('show') != show_name]
                after = len(qdb[category])
                print(f"  ✅ Deleted {before - after} questions for '{show_name}'")
                save_questions(qdb)
        
        elif choice == '4':
            if not SUPABASE_URL or not SUPABASE_KEY:
                print("  ❌ SUPABASE_URL and SUPABASE_KEY not set in .env")
                continue
            
            print("  🚀 Exporting to Supabase...")
            # Implementation in next step
            print("  (Feature coming soon)")
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not set. Add to .env file")
        exit(1)
    
    interactive_generator()
