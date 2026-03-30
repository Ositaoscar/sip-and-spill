# Intelligent Question Generator for Sip & Spill (Queue-Based)

> Smart trivia generation ONE show at a time, pause when tokens run out, resume tomorrow
> Daily token budgeting for sustainable, cost-efficient question research

## Overview

**New queue-based workflow:**
1. **Research queue** — 20 shows per category (Disney, Pop, Celebrity) to research
2. **One show at a time** — Deep research ONE show, generate 5 smart questions
3. **Token budgeting** — $0.05/day budget (~500 tokens per show)
4. **Auto-save progress** — Resume next day where you left off
5. **Smart distractors** — Claude creates believable wrong answers (not obvious)

**Why this approach?**
- ✅ Token-sustainable (spread cost across days, not one big API call)
- ✅ Deep research (each show gets full attention, better questions)
- ✅ Progress tracking (see what's done, what's pending)
- ✅ Pause anytime (no pressure to finish today)
- ✅ App-ready (questions gradually fill database, scalable design)

---

## Setup (3 minutes)

### 1. Install Dependencies
```bash
cd /Users/mambohq/Documents/odin_os/sip-and-spill
pip install anthropic requests
```

### 2. Get Anthropic API Key
- Go to [console.anthropic.com](https://console.anthropic.com)
- Create free account, then API keys section
- Copy your key (looks like `sk-ant-...`)

### 3. Set API Key
```bash
# Copy template
cp .env.example .env

# Edit .env and paste your key
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Run Generator
```bash
python generate_questions.py
```

---

## Usage Workflow

### First Run: Interactive Dashboard
```
📊 RESEARCH DASHBOARD
💰 TOKEN BUDGET TODAY
   Used: 0 / 10000
   Remaining: 10000 tokens (~5 shows)

📂 CATEGORY PROGRESS
   DISNEY     ⏳ 0/20      0 questions generated
   POP        ⏳ 0/20      0 questions generated
   CELEB      ⏳ 0/20      0 questions generated

🎯 NEXT SHOW TO RESEARCH
   DISNEY     → Frozen
   POP        → Friends
   CELEB      → Taylor Swift

Options:
  1️⃣  Research next show in queue
  2️⃣  Add custom show to research
  3️⃣  View all questions (review)
  4️⃣  Pause (save & exit)
```

### Example: Research One Show

**Choose option 1:**
```
🔍 Researching 'Frozen'...
  ✅ Found detailed info on Wikipedia

🤖 Generating 5 questions with Claude...
  ✅ Generated 5 questions (1823 tokens)
  ✅ Saved 5 questions from Frozen
```

**What happened:**
- Researched Frozen using Wikipedia API
- Asked Claude to generate 5 smart questions in ONE call
- Cost: ~1823 tokens (~$0.01)
- Saved to `data/generated_questions.json`
- Progress auto-saved

### Continue or Pause
```
💰 TOKEN BUDGET TODAY
   Used: 1823 / 10000
   Remaining: 8177 tokens (~4 more shows)

Options:
  1️⃣  Research next show... (→ continue)
  4️⃣  Pause (save & exit)  (→ resume tomorrow)
```

---

## Daily Token Budget Explained

**Today's Limit:** 10,000 tokens (~$0.05)

**Per Show Cost:**
- Deep research prompt + 5 questions = ~1500-1800 tokens
- Cost: ~$0.01 per show
- Per-day limit: 5-6 shows ✓ sustainable

**Tomorrow:** Budget resets automatically to 10,000 tokens

```
Day 1: Research 5 shows (Frozen, Aladdin, Lion King, Cinderella, Tangled)
       Token budget: 10000 used, 0 remaining → PAUSE

Day 2: Sleep! Budget resets overnight
       Token budget: 0 used, 10000 remaining → Resume!
```

---

## Files Created & Updated

```
data/
  research_queue.json       ← Shows to research (auto-created)
  research_progress.json    ← Progress tracking (auto-saved)
  generated_questions.json  ← Final question bank (game loads from here)

generate_questions.py      ← The CLI tool (RUN THIS)
.env                       ← Your API key (created from .env.example)
QUESTION_GENERATOR.md      ← This file
```

---

## Generated Question Format

Each question looks like:
```json
{
  "q": "In Frozen, what is the name of Elsa's sister?",
  "options": ["Anna", "Emma", "Elena"],
  "answer": 0,
  "fact": "Anna and Elsa are voiced by Kristen Bell and Idina Menzel respectively.",
  "show": "Frozen",
  "added_date": "2024-03-30T15:30:00"
}
```

**Key features:**
- ✅ Correct answer always at index 0
- ✅ 3 options (harder than 4)
- ✅ Plausible distractors that aren't obvious
- ✅ Fun facts (educational hook)
- ✅ Tracked by show name

---

## Viewing & Managing Questions

### View All Questions
```
Option 3: View all questions

📊 Questions by Category:
  DISNEY: 50 questions from 10 shows
    → Frozen, Aladdin, Lion King, Cinderella, Tangled...
  POP: 25 questions from 5 shows
    → Friends, The Office...
  CELEB: 15 questions from 3 shows
    → Taylor Swift...
```

### Add Custom Show to Queue
```
Option 2: Add custom show

📺 Show/Movie name: Breaking Bad
📁 Category (disney/pop/celeb): pop

✅ Added Breaking Bad to pop queue
```

---

## Game Auto-Integration

The game automatically:
1. Loads `data/generated_questions.json` on startup
2. Uses custom questions if available
3. Falls back to hardcoded bank if no custom questions
4. Shows console message: `✅ Loaded custom-generated questions`

**To use generated questions:**
- Generate 5-10 shows worth of questions (50+ questions)
- Hard refresh game (`Cmd+Shift+R` Mac, `Ctrl+Shift+R` Windows)
- Game now uses smart, deep-researched questions!

---

## FAQ

### Q: Do I need to pay?
**A:** Only if you use the generator. Cost is~$0.01 per show. Game works free without it.

### Q: Can I pause mid-research?
**A:** YES! Choose option 4 at any time. Progress is saved. Resume tomorrow.

### Q: What if I run out of tokens?
**A:** Generator auto-pauses when you hit 10,000 tokens. Budget resets next day.

### Q: How do I customize difficulty?
**A:** Edit the prompt in generate_questions.py (line ~145). Change "challenging" to "easy/medium/hard" or add requirements like "include episode numbers."

### Q: Can I add shows not in the default queue?
**A:** YES! Choose option 2 and add custom shows. They'll be researched in order.

### Q: Do generated questions replace the hardcoded ones?
**A:** No, they SUPPLEMENT. Hardcoded bank is still there as fallback. You're adding smart questions ON TOP.

### Q: How many questions should I generate?
**A:** Recommended:
- Disney: 30-40 questions (6-8 shows)
- Pop: 30-40 questions (6-8 shows)
- Celebrity: 25-30 questions (5-6 shows)
- Total: 100+ questions for a robust bank

---

## Token Math

```
Cost per show: 1500 tokens = $0.01
Daily budget: 10,000 tokens = $0.05

Day 1: Generate 5 shows = $0.05
Day 2: Generate 5 shows = $0.05
Day 3-4-5: Generate 15 more shows = $0.15
Total: 25 premium shows = $0.25 (includes deep Wikipedia research)

Contrast:
- Manual editing: free but hours of work
- External API: $1+ per 50 questions
- This approach: $0.25 per 50 smart questions ✓ Best value
```

---

## Next Steps

1. ✅ Install dependencies: `pip install anthropic requests`
2. ✅ Set API key in `.env`
3. ✅ Run: `python generate_questions.py`
4. ✅ Research 5-10 shows over several days
5. ✅ Hard refresh game to see custom questions

---

## Questions?

Check:
- `generate_questions.py` code comments
- `data/research_progress.json` to see real-time progress
- Game console (F12) for load status

**Created by GitHub Copilot**  
Sustainable, queue-based, deep-research trivia generation 🎯
