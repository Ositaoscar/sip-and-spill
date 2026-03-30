#!/usr/bin/env python3
"""
Agent-Friendly Research Batch Mode
Run autonomously to research shows and update progress
No user interaction needed - designed for agent automation
"""

import json
import os
import sys
from typing import Optional
from datetime import datetime

import requests
from anthropic import Anthropic

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DAILY_TOKEN_BUDGET = 10000
OUTPUT_FILE = 'data/generated_questions.json'
QUEUE_FILE = 'data/research_queue.json'
PROGRESS_FILE = 'data/research_progress.json'


# ═══════════════════════════════════════════════════════════════
# LOAD/SAVE UTILITIES
# ═══════════════════════════════════════════════════════════════

def load_queue() -> dict:
  if os.path.exists(QUEUE_FILE):
    try:
      with open(QUEUE_FILE, 'r') as f:
        return json.load(f)
    except:
      pass
  return {'disney': [], 'pop': [], 'celeb': []}


def load_progress() -> dict:
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
  os.makedirs('data', exist_ok=True)
  with open(PROGRESS_FILE, 'w') as f:
    json.dump(prog, f, indent=2)


def save_queue(queue: dict):
  os.makedirs('data', exist_ok=True)
  with open(QUEUE_FILE, 'w') as f:
    json.dump(queue, f, indent=2)


def load_questions_db() -> dict:
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
  os.makedirs('data', exist_ok=True)
  total = sum(len(qdb[cat]) for cat in ['disney', 'pop', 'celeb', 'custom'])
  qdb['metadata']['last_updated'] = datetime.now().isoformat()
  qdb['metadata']['total_questions'] = total
  for cat in ['disney', 'pop', 'celeb', 'custom']:
    qdb['metadata']['categories'][cat] = len(qdb[cat])
  with open(OUTPUT_FILE, 'w') as f:
    json.dump(qdb, f, indent=2)


def reset_daily_budget():
  prog = load_progress()
  last_reset = datetime.fromisoformat(prog['last_reset'])
  today = datetime.now().date()
  last_date = last_reset.date()
  if today > last_date:
    prog['tokens_used_today'] = 0
    prog['last_reset'] = datetime.now().isoformat()
    save_progress(prog)
    return True
  return False


# ═══════════════════════════════════════════════════════════════
# RESEARCH & GENERATION
# ═══════════════════════════════════════════════════════════════

def research_show(show_name: str) -> dict:
  """Silent research mode - gathers basic info"""
  research_data = {
    'title': show_name,
    'genre': [],
    'plot_summary': show_name + ' is a show/movie',
    'main_characters': [show_name],
    'notable_episodes': '',
    'awards': '',
    'creators': ''
  }
  
  # Try Wikipedia
  try:
    url = 'https://en.wikipedia.org/w/api.php'
    params = {'action': 'query', 'format': 'json', 'srsearch': show_name, 'srlimit': 1}
    resp = requests.get(url, params=params, timeout=5)
    if resp.status_code == 200:
      return research_data
  except:
    pass
  
  return research_data


def generate_show_questions(show_data: dict, num_questions: int = 5, category: str = 'pop') -> tuple:
  """Generate questions via Claude API"""
  client = Anthropic()
  
  context = f"""
TITLE: {show_data['title']}
CATEGORY: {category.upper()}

GENRE: {', '.join(show_data['genre'])}
CHARACTERS: {', '.join(show_data['main_characters'][:5])}
PLOT: {show_data['plot_summary']}
NOTABLE: {show_data.get('notable_episodes', '')}
CREATORS: {show_data.get('creators', '')}
AWARDS: {show_data.get('awards', '')}

Create {num_questions} CHALLENGING trivia questions.
Mix easy/medium/hard difficulty.
3 options per question, answer at index 0.
Plausible distractors (believable wrong answers).
"""
  
  prompt = f"""Generate {num_questions} trivia questions about "{show_data['title']}".

{context}

OUTPUT ONLY: JSON array, no explanation.
[
  {{"q": "Question?", "options": ["Correct", "Wrong", "Wrong"], "answer": 0, "fact": "Fact."}},
  ...
]"""

  try:
    response = client.messages.create(
      model='claude-3-5-sonnet-20241022',
      max_tokens=2000,
      messages=[{'role': 'user', 'content': prompt}]
    )
    
    tokens_used = response.usage.input_tokens + response.usage.output_tokens
    response_text = response.content[0].text
    questions = json.loads(response_text)
    
    return questions, tokens_used
    
  except Exception as e:
    return [], 0


def add_show_to_db(category: str, show_name: str, questions: list, qdb: dict):
  for q in questions:
    q['show'] = show_name
    q['added_date'] = datetime.now().isoformat()
    qdb[category].append(q)
  save_questions_db(qdb)


# ═══════════════════════════════════════════════════════════════
# BATCH RESEARCH (AGENT-FRIENDLY)
# ═══════════════════════════════════════════════════════════════

def research_batch_auto(num_shows: int = 5) -> dict:
  """
  Autonomously research next N unfinished shows.
  Returns summary dict for agent to log.
  """
  os.makedirs('data', exist_ok=True)
  reset_daily_budget()
  
  queue = load_queue()
  prog = load_progress()
  qdb = load_questions_db()
  
  summary = {
    'status': 'success',
    'shows_researched': 0,
    'questions_generated': 0,
    'tokens_used': 0,
    'shows': [],
    'error': None,
    'token_budget_remaining': DAILY_TOKEN_BUDGET - prog['tokens_used_today']
  }
  
  for _ in range(num_shows):
    # Find next unresearched show
    next_show = None
    next_cat = None
    
    for cat in ['disney', 'pop', 'celeb']:
      pending = [s for s in queue[cat] if s not in prog['completed'][cat]]
      if pending:
        next_show = pending[0]
        next_cat = cat
        break
    
    if not next_show:
      summary['status'] = 'completed_all'
      break
    
    # Check token budget
    tokens_left = DAILY_TOKEN_BUDGET - prog['tokens_used_today']
    if tokens_left < 1500:
      summary['status'] = 'budget_limit_reached'
      break
    
    # Research & generate
    try:
      show_data = research_show(next_show)
      questions, tokens_used = generate_show_questions(show_data, num_questions=5, category=next_cat)
      
      if questions and tokens_used > 0:
        add_show_to_db(next_cat, next_show, questions, qdb)
        prog['completed'][next_cat].append(next_show)
        prog['tokens_used_today'] += tokens_used
        prog['shows_researched'] += 1
        prog['stats'][next_cat]['researched'] += 1
        prog['stats'][next_cat]['questions'] += len(questions)
        save_progress(prog)
        
        summary['shows_researched'] += 1
        summary['questions_generated'] += len(questions)
        summary['tokens_used'] += tokens_used
        summary['shows'].append({
          'name': next_show,
          'category': next_cat,
          'questions': len(questions),
          'tokens': tokens_used
        })
      else:
        summary['error'] = f"Failed to generate questions for {next_show}"
        break
    
    except Exception as e:
      summary['error'] = f"Error researching {next_show}: {str(e)}"
      break
  
  summary['token_budget_remaining'] = DAILY_TOKEN_BUDGET - prog['tokens_used_today']
  return summary


def research_batch_specific(shows: list) -> dict:
  """
  Research specific shows provided by agent.
  Format: [('show_name', 'category'), ...]
  """
  os.makedirs('data', exist_ok=True)
  reset_daily_budget()
  
  prog = load_progress()
  qdb = load_questions_db()
  
  summary = {
    'status': 'success',
    'shows_researched': 0,
    'questions_generated': 0,
    'tokens_used': 0,
    'shows': [],
    'error': None
  }
  
  for show_name, category in shows:
    # Check token budget
    tokens_left = DAILY_TOKEN_BUDGET - prog['tokens_used_today']
    if tokens_left < 1500:
      summary['status'] = 'budget_limit_reached'
      break
    
    # Research & generate
    try:
      show_data = research_show(show_name)
      questions, tokens_used = generate_show_questions(show_data, num_questions=5, category=category)
      
      if questions and tokens_used > 0:
        add_show_to_db(category, show_name, questions, qdb)
        prog['tokens_used_today'] += tokens_used
        prog['shows_researched'] += 1
        save_progress(prog)
        
        summary['shows_researched'] += 1
        summary['questions_generated'] += len(questions)
        summary['tokens_used'] += tokens_used
        summary['shows'].append({
          'name': show_name,
          'category': category,
          'questions': len(questions),
          'tokens': tokens_used
        })
      else:
        summary['error'] = f"Failed to generate questions for {show_name}"
        break
    
    except Exception as e:
      summary['error'] = f"Error researching {show_name}: {str(e)}"
      break
  
  summary['token_budget_remaining'] = DAILY_TOKEN_BUDGET - prog['tokens_used_today']
  return summary


def get_status() -> dict:
  """Get current research status"""
  prog = load_progress()
  qdb = load_questions_db()
  queue = load_queue()
  
  return {
    'tokens_used_today': prog['tokens_used_today'],
    'tokens_remaining': DAILY_TOKEN_BUDGET - prog['tokens_used_today'],
    'total_questions': qdb['metadata']['total_questions'],
    'by_category': qdb['metadata']['categories'],
    'shows_researched': prog['shows_researched'],
    'progress': {
      'disney': f"{len(prog['completed']['disney'])}/{len(queue['disney'])}",
      'pop': f"{len(prog['completed']['pop'])}/{len(queue['pop'])}",
      'celeb': f"{len(prog['completed']['celeb'])}/{len(queue['celeb'])}"
    }
  }


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
  if not ANTHROPIC_API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not set")
    sys.exit(1)
  
  if len(sys.argv) < 2:
    print("Usage: python research_batch.py <auto|shows|status>")
    print("  auto N    — Research next N unfinished shows (default 5)")
    print("  shows S1 C1 S2 C2 ... — Research specific shows (pairs of show_name,category)")
    print("  status    — Show current progress")
    sys.exit(1)
  
  cmd = sys.argv[1]
  
  if cmd == 'auto':
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    result = research_batch_auto(num)
    print(json.dumps(result, indent=2))
  
  elif cmd == 'shows':
    # Parse pairs: "Breaking Bad" "pop" "Friends" "pop"
    shows = []
    for i in range(2, len(sys.argv), 2):
      if i+1 < len(sys.argv):
        shows.append((sys.argv[i], sys.argv[i+1]))
    result = research_batch_specific(shows)
    print(json.dumps(result, indent=2))
  
  elif cmd == 'status':
    result = get_status()
    print(json.dumps(result, indent=2))
  
  else:
    print(f"Unknown command: {cmd}")
    sys.exit(1)
