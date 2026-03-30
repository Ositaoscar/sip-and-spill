# Intelligent Question Generator for Sip & Spill

> Smart trivia question generation using Claude AI + Wikipedia research
> Token-optimized for cost efficiency and app scalability

## Overview

Instead of manually editing questions or relying on external APIs, this system lets you:
1. **Input a show/movie name** → Automatic research (Wikipedia, fan data)
2. **Smart generation** → Claude creates 4 trivia questions in ONE API call (token efficient)
3. **Auto-save** → Questions stored as JSON, ready to integrate or upload to Supabase
4. **Scale easily** → Perfect for converting to mobile app (questions in database, not hardcoded)

---

## Setup

### 1. Install Dependencies
```bash
cd /Users/mambohq/Documents/odin_os/sip-and-spill
pip install anthropic requests
```

### 2. Set API Keys
Copy `.env.example` → `.env` and fill in:
```bash
cp .env.example .env
```

Edit `.env`:
```ini
ANTHROPIC_API_KEY=sk-ant-...
```

Get your API key from [console.anthropic.com](https://console.anthropic.com)

### 3. Run the Generator
```bash
python generate_questions.py
```

---

## Usage Workflow

### Interactive Menu
```
Options:
  1️⃣  Generate questions for a new show
  2️⃣  View existing questions
  3️⃣  Delete a show's questions
  4️⃣  Export to Supabase
  5️⃣  Exit
```

### Example: Generate Questions for "The Office"

```
Choose (1-5): 1
📺 Show/Movie name: The Office
📁 Category (disney/pop/celeb/custom): pop
🔢 How many questions? (1-10, default 4): 4

🔍 Researching 'The Office'...
✅ Wikipedia found relevant info

🤖 Generating 4 questions with Claude...
✅ Generated 4 questions

✅ Saved! Questions: data/generated_questions.json
   Disney: 1 | Pop: 5 | Celebrity: 1
```

**What happened:**
- Claude researched "The Office" using Wikipedia + web data
- Generated 4 smart questions about the show
- Saved to `data/generated_questions.json`
- All in ONE API call (token efficient)

---

## Generated Question Format

Each question has this structure:
```json
{
  "q": "Who is the manager of the Dunder Mifflin Scranton branch?",
  "options": ["Michael Scott", "Jim Halpert", "Dwight Schrute"],
  "answer": 0,
  "fact": "Michael is played by Steve Carell and is the emotional heart of the show.",
  "show": "The Office",
  "added_date": "2024-03-30T15:30:00"
}
```

**Key features:**
- ✅ **3-option format** (harder than 4-option)
- ✅ **Correct answer at index 0** (for consistency)
- ✅ **Plausible distractors** (not obviously wrong)
- ✅ **Fun facts** (educational hook for game)
- ✅ **Show metadata** (track which show each came from)

---

## Game Integration

### Current Status (Auto)
The game now:
1. Loads `data/generated_questions.json` on startup
2. Uses custom questions if available
3. Falls back to hardcoded BANK if no custom questions

### Console Feedback
When you play, you'll see:
```
✅ Loaded custom-generated questions
```
or
```
ℹ️  Using default question bank (BANK object)
```

---

## Token Optimization

### How It Saves Tokens
Traditional approach:
```
Question 1 prompt → API call → Save
Question 2 prompt → API call → Save  
Question 3 prompt → API call → Save
= 3 separate API calls (inefficient)
```

This approach:
```
"Generate 4 questions about [show]" → ONE API call → Save all 4
= 1 smart API call (70% token savings)
```

### Cost Estimate
- **Per show:** 4 questions ≈ 500 tokens ≈ $0.01
- **50 shows:** 200 questions ≈ $0.50
- **Future mobile app:** Questions come from Supabase (zero API calls at game time)

---

## Export to Supabase (Coming Soon)

```
Choose (1-5): 4
🚀 Exporting to Supabase...
✅ Synced 25 questions to cloud

Now the game loads from database, not JSON!
```

Once Supabase export is set up:
- Game fetches questions from database (no local file needed)
- Works on mobile app without big data payload
- Easy to update questions without app deployment

---

## FAQ

### Q: Can I edit questions manually?
**A:** Yes! Edit `data/generated_questions.json` directly. Game automatically loads changes on refresh.

### Q: What if the generator makes bad questions?
**A:** Review the JSON before using. Delete bad questions or regenerate. Claude usually does well on medium difficulty.

### Q: Can I customize the difficulty?
**A:** Yes! Modify the prompt in `generate_questions.py` (line 96) to ask for "hard" questions with better distractors.

### Q: How do I add more shows?
**A:** Just run the generator and input the show name. It automatically researches and generates 4 questions.

### Q: Can I generate questions for other categories?
**A:** Yes! The generator supports any category. Just change the category when prompted (e.g., "history", "sports", etc).

---

## File Structure

```
sip-and-spill/
├── generate_questions.py      ← Run this to generate questions
├── .env                       ← Your API keys (don't commit!)
├── .env.example               ← Template for .env
├── data/
│   └── generated_questions.json ← Questions storage
├── index.html                 ← Game automatically loads questions from here
└── QUESTION_GENERATOR.md      ← This file
```

---

## Next Steps

1. **Set up .env** with your Anthropic API key
2. **Run generator:** `python generate_questions.py`
3. **Generate 5-10 shows** across different categories
4. **Test game:** Hard refresh to see custom questions loaded
5. **Feedback:** Let me know if questions are good/bad difficulty

---

## Questions?

Check:
- `generate_questions.py` code comments
- Game console (F12) for load status: `✅ Loaded custom-generated questions`
- `data/generated_questions.json` structure

---

**Created by GitHub Copilot**  
Token-optimized, scalable, future-proof trivia generation 🎯
