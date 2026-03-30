#!/usr/bin/env python3
"""
Intelligent Question Generator for Sip & Spill (Queue-Based)
Deep research ONE show at a time, pause when tokens run out, resume next day
Token-optimized: research queue + daily budgeting + auto-save
"""

import json
import os
from typing import Optional
from datetime import datetime

import requests
from anthropic import Anthropic

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DAILY_TOKEN_BUDGET = 10000  # ~$0.05/day
OUTPUT_FILE = 'data/generated_questions.json'
QUEUE_FILE = 'data/research_queue.json'
PROGRESS_FILE = 'data/research_progress.json'

# Default research queue (shows to research)
DEFAULT_QUEUE = {
  'disney': [
    'Frozen', 'Aladdin', 'The Lion King', 'Cinderella', 'Sleeping Beauty',
    'Tangled', 'Moana', 'Encanto', 'Coco', 'Raya and the Last Dragon',
    'Mulan', 'Pocahontas', 'Beauty and the Beast', 'The Little Mermaid', 'Hercules',
    'Tarzan', 'The Jungle Book', 'Pinocchio', 'Snow White', 'Rapunzel'
  ],
  'pop': [
    'Friends', 'The Office', 'Breaking Bad', 'Game of Thrones', 'The Crown',
    'Stranger Things', 'The Boys', 'Succession', 'Ted Lasso', 'Bridgerton',
    'Ozark', 'Money Heist', 'Dark', 'Peaky Blinders', 'The Mandalorian',
    'The Last of Us', 'The Bear', 'Beef', 'Anatomy of a Scandal', 'Squid Game'
  ],
  'celeb': [
    'Taylor Swift', 'Elon Musk', 'Oprah Winfrey', 'Dwayne Johnson',
    'Kylie Jenner', 'Jeff Bezos', 'Rihanna', 'LeBron James', 'Kim Kardashian',
    'Beyoncé', 'Drake', 'Ariana Grande', 'Travis Scott', 'Zendaya',
    'Ryan Reynolds', 'Margot Robbie', 'Timothée Chalamet', 'Billie Eilish', 'Harry Styles'
  ]
}


# ═══════════════════════════════════════════════════════════════
# QUEUE MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def load_queue() -> dict:
  """Load research queue or initialize with defaults"""
  if os.path.exists(QUEUE_FILE):
    try:
      with open(QUEUE_FILE, 'r') as f:
        return json.load(f)
    except:
      pass
  
  return DEFAULT_QUEUE.copy()


def load_progress() -> dict:
  """Load research progress (what's done, token usage)"""
  if os.path.exists(PROGRESS_FILE):
    try:
      with open(PROGRESS_FILE, 'r') as f:
        return json.load(f)
    except:
      pass
  
  return {
    'completed': {'disney': [], 'pop': [], 'celeb': []},
    'tokens_used_today': 0,
    'last_reset': datetime.now().isoformat(),
    'shows_researched': 0,
    'stats': {
      'disney': {'researched': 0, 'questions': 0},
      'pop': {'researched': 0, 'questions': 0},
      'celeb': {'researched': 0, 'questions': 0}
    }
  }


def save_progress(prog: dict):
  """Save research progress"""
  os.makedirs('data', exist_ok=True)
  with open(PROGRESS_FILE, 'w') as f:
    json.dump(prog, f, indent=2)


def save_queue(queue: dict):
  """Save research queue"""
  os.makedirs('data', exist_ok=True)
  with open(QUEUE_FILE, 'w') as f:
    json.dump(queue, f, indent=2)


def reset_daily_budget():
  """Reset token budget if it's a new day"""
  prog = load_progress()
  last_reset = datetime.fromisoformat(prog['last_reset'])
  today = datetime.now().date()
  last_date = last_reset.date()
  
  if today > last_date:
    prog['tokens_used_today'] = 0
    prog['last_reset'] = datetime.now().isoformat()
    save_progress(prog)
    print(f"\n📅 New day! Token budget reset to {DAILY_TOKEN_BUDGET}")
    return True
  return False


# ═══════════════════════════════════════════════════════════════
# RESEARCH ENGINE: Wikipedia + Web
# ═══════════════════════════════════════════════════════════════

def research_show(show_name: str) -> dict:
  """Deep research on a single show via Wikipedia + web"""
  print(f"\n🔍 Researching '{show_name}'...")
  
  research_data = {
    'title': show_name,
    'genre': [],
    'plot_summary': '',
    'main_characters': [],
    'notable_episodes': [],
    'awards': '',
    'creators': ''
  }
  
  # Wikipedia lookup
  wiki_data = _search_wikipedia(show_name)
  if wiki_data:
    research_data.update(wiki_data)
    print(f"  ✅ Found detailed info on Wikipedia")
    return research_data
  
  # Manual input fallback
  print("  ℹ️  Wikipedia lookup not available. Let's gather info manually for better questions:")
  research_data['plot_summary'] = input("  📝 Plot/Description (2-3 sentences): ").strip()
  research_data['main_characters'] = [c.strip() for c in input("  👥 Main characters (comma-separated): ").split(',')]
  research_data['genre'] = [g.strip() for g in input("  🎬 Genre/Type (comma-separated): ").split(',')]
  research_data['notable_episodes'] = input("  🎭 Notable episodes/moments: ").strip()
  
  return research_data


def _search_wikipedia(show_name: str) -> Optional[dict]:
  """Attempt Wikipedia API lookup"""
  try:
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
      'action': 'query',
      'format': 'json',
      'srsearch': show_name,
      'srprop': 'snippet',
      'srlimit': 1
    }
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
      return None  # In production, parse response for detailed info
  except:
    pass
  return None


# ═══════════════════════════════════════════════════════════════
# QUESTION GENERATION: Claude API (Deep Research Mode)
# ═══════════════════════════════════════════════════════════════

def generate_show_questions(
  show_data: dict,
  num_questions: int = 5,
  category: str = 'pop'
) -> tuple:
  """
  Deep research generation: 5-6 smart questions per show
  Returns: (questions_list, tokens_used)
  """
  client = Anthropic()
  
  context = _build_deep_context(show_data, category)
  
  prompt = f"""You are a trivia expert creating challenging questions about "{show_data['title']}".

RESEARCH CONTEXT:
{context}

REQUIREMENTS:
1. Generate {num_questions} UNIQUE, CHALLENGING trivia questions
2. 3 options per question ONLY
3. Correct answer at index 0 (first option)
4. Plausible distractors (related but WRONG—not obvious)
5. Include interesting facts users would learn from the show
6. Vary difficulty: some require deep fandom knowledge, some are medium

FORMAT: Output ONLY valid JSON array, no explanation:
[
  {{"q": "Question?", "options": ["Correct", "Wrong but believable", "Wrong but believable"], "answer": 0, "fact": "Interesting trivia fact."}},
  ...
]

Generate {num_questions} questions now:"""

  try:
    response = client.messages.create(
      model='claude-3-5-sonnet-20241022',
      max_tokens=2000,
      messages=[{'role': 'user', 'content': prompt}]
    )
    
    # Extract tokens used
    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    
    # Parse JSON
    response_text = response.content[0].text
    questions = json.loads(response_text)
    
    print(f"  ✅ Generated {len(questions)} questions ({tokens_used} tokens)")
    return questions, tokens_used
    
  except json.JSONDecodeError:
    print(f"  ❌ Failed to parse JSON response")
    return [], 0
  except Exception as e:
    print(f"  ❌ API error: {e}")
    return [], 0


def _build_deep_context(show_data: dict, category: str) -> str:
  """Build rich research context for Claude"""
  context = f"""
TITLE: {show_data['title']}
CATEGORY: {category.upper()}

GENRE: {', '.join(show_data['genre'])}
CHARACTERS: {', '.join(show_data['main_characters'][:10])}
PLOT: {show_data['plot_summary']}
NOTABLE: {show_data.get('notable_episodes', 'N/A')}
CREATORS: {show_data.get('creators', 'N/A')}
AWARDS: {show_data.get('awards', 'N/A')}

Create questions that test DEEP knowledge, not trivial facts.
Mix easy/medium/hard. Make distractors believable.
"""
  return context


# ═══════════════════════════════════════════════════════════════
# SAVE QUESTIONS
# ═══════════════════════════════════════════════════════════════

def load_questions_db() -> dict:
  """Load existing questions database"""
  if os.path.exists(OUTPUT_FILE):
    try:
      with open(OUTPUT_FILE, 'r') as f:
        return json.load(f)
    except:
      pass
  
  return {
    'disney': [], 'pop': [], 'celeb': [], 'custom': [],
    'metadata': {
      'last_updated': None,
      'total_questions': 0,
      'categories': {'disney': 0, 'pop': 0, 'celeb': 0, 'custom': 0}
    }
  }


def save_questions_db(qdb: dict):
  """Save questions to database"""
  os.makedirs('data', exist_ok=True)
  
  # Update metadata
  total = sum(len(qdb[cat]) for cat in ['disney', 'pop', 'celeb', 'custom'])
  qdb['metadata']['last_updated'] = datetime.now().isoformat()
  qdb['metadata']['total_questions'] = total
  for cat in ['disney', 'pop', 'celeb', 'custom']:
    qdb['metadata']['categories'][cat] = len(qdb[cat])
  
  with open(OUTPUT_FILE, 'w') as f:
    json.dump(qdb, f, indent=2)


def add_show_to_db(category: str, show_name: str, questions: list, qdb: dict):
  """Add generated questions for a show to database"""
  for q in questions:
    q['show'] = show_name
    q['added_date'] = datetime.now().isoformat()
    qdb[category].append(q)
  
  save_questions_db(qdb)


# ═══════════════════════════════════════════════════════════════
# DASHBOARD & PROGRESS
# ═══════════════════════════════════════════════════════════════

def show_dashboard(queue: dict, prog: dict, qdb: dict):
  """Show research progress and next steps"""
  print("\n" + "="*70)
  print("  📊 RESEARCH DASHBOARD")
  print("="*70)
  
  # Token status
  tokens_left = DAILY_TOKEN_BUDGET - prog['tokens_used_today']
  print(f"\n💰 TOKEN BUDGET TODAY")
  print(f"   Used: {prog['tokens_used_today']} / {DAILY_TOKEN_BUDGET}")
  print(f"   Remaining: {tokens_left} tokens (~{tokens_left//2000} shows)")
  
  # Category progress
  print(f"\n📂 CATEGORY PROGRESS")
  for cat in ['disney', 'pop', 'celeb']:
    done = len(prog['completed'][cat])
    total = len(queue[cat])
    questions = len(qdb[cat])
    pct = (done/total*100) if total > 0 else 0
    status = "✅" if done == total else f"⏳ {done}/{total}"
    print(f"   {cat.upper():8} {status:15} {questions:3} questions generated")
  
  # Next show to research
  print(f"\n🎯 NEXT SHOW TO RESEARCH")
  for cat in ['disney', 'pop', 'celeb']:
    pending = [s for s in queue[cat] if s not in prog['completed'][cat]]
    if pending:
      print(f"   {cat.upper():8} → {pending[0]}")
  
  print("\n" + "="*70)


# ═══════════════════════════════════════════════════════════════
# INTERACTIVE WORKFLOW
# ═══════════════════════════════════════════════════════════════

def interactive_research():
  """Main research loop: one show at a time"""
  print("\n" + "="*70)
  print("  🍹 Sip & Spill — Intelligent Question Generator")
  print("  Queue-Based: Research one show, save, pause anytime")
  print("="*70)
  
  reset_daily_budget()
  
  queue = load_queue()
  prog = load_progress()
  qdb = load_questions_db()
  
  while True:
    show_dashboard(queue, prog, qdb)
    
    print("\nOptions:")
    print("  1️⃣  Research next show in queue")
    print("  2️⃣  Add custom show to research")
    print("  3️⃣  View all questions (review)")
    print("  4️⃣  Pause (save & exit)")
    
    choice = input("\nChoose (1-4): ").strip()
    
    if choice == '1':
      # Find next unresearched show across all categories
      next_show = None
      next_cat = None
      
      for cat in ['disney', 'pop', 'celeb']:
        pending = [s for s in queue[cat] if s not in prog['completed'][cat]]
        if pending:
          next_show = pending[0]
          next_cat = cat
          break
      
      if not next_show:
        print("\n✅ All shows researched! Great job!")
        break
      
      # Check token budget
      tokens_left = DAILY_TOKEN_BUDGET - prog['tokens_used_today']
      if tokens_left < 1500:
        print(f"\n⚠️  Token budget low ({tokens_left} left). Pausing for today.")
        print(f"   Resume tomorrow to continue.")
        break
      
      # Research the show
      show_data = research_show(next_show)
      questions, tokens_used = generate_show_questions(show_data, num_questions=5, category=next_cat)
      
      if questions:
        add_show_to_db(next_cat, next_show, questions, qdb)
        prog['completed'][next_cat].append(next_show)
        prog['tokens_used_today'] += tokens_used
        prog['shows_researched'] += 1
        prog['stats'][next_cat]['researched'] += 1
        prog['stats'][next_cat]['questions'] += len(questions)
        save_progress(prog)
        print(f"  ✅ Saved {len(questions)} questions from {next_show}")
    
    elif choice == '2':
      show_name = input("\n📺 Show/Movie name: ").strip()
      category = input("📁 Category (disney/pop/celeb): ").strip().lower()
      if category not in ['disney', 'pop', 'celeb']:
        category = 'celeb'
      
      if category not in queue:
        queue[category] = []
      
      if show_name not in queue[category]:
        queue[category].append(show_name)
        save_queue(queue)
        print(f"  ✅ Added {show_name} to {category} queue")
      else:
        print(f"  ℹ️  {show_name} already in queue")
    
    elif choice == '3':
      print("\n📊 Questions by Category:")
      for cat in ['disney', 'pop', 'celeb', 'custom']:
        count = len(qdb[cat])
        if count > 0:
          shows = set(q.get('show', 'Unknown') for q in qdb[cat])
          print(f"  {cat.upper()}: {count} questions from {len(shows)} shows")
          print(f"    → {', '.join(list(shows)[:5])}{'...' if len(shows) > 5 else ''}")
    
    elif choice == '4':
      print("\n👋 Pausing research. Progress saved!")
      print(f"   Resume tomorrow to continue (token budget resets daily)")
      save_progress(prog)
      save_queue(queue)
      break


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
  if not ANTHROPIC_API_KEY:
    print("❌ ANTHROPIC_API_KEY not set. Add to .env file")
    exit(1)
  
  interactive_research()
