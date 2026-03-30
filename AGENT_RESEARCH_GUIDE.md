# Agent Research Instructions

> How to direct your agent to autonomously research shows and update progress

---

## Quick Start (For You)

**To direct agent to research 5 shows:**
```
Agent, run:
python research_batch.py auto 5
```

**To research specific shows:**
```
Agent, research these:
python research_batch.py shows "Breaking Bad" "pop" "Friends" "pop" "Stranger Things" "pop"
```

**To check progress:**
```
Agent, check status:
python research_batch.py status
```

---

## Agent Instructions (What to Do)

### Mode 1: Auto Research (Next Unfinished Shows)

**Command:**
```bash
python research_batch.py auto 5
```

**What happens:**
1. Checks daily token budget (max 10,000 tokens/day)
2. Finds next 5 unresearched shows in queue
3. For each show:
   - Deep researches it (Wikipedia)
   - Generates 5 smart questions via Claude
   - Auto-saves to `data/generated_questions.json`
   - Updates `data/research_progress.json`
4. Returns JSON summary with results

**Example output:**
```json
{
  "status": "success",
  "shows_researched": 5,
  "questions_generated": 25,
  "tokens_used": 8500,
  "shows": [
    {
      "name": "Frozen",
      "category": "disney",
      "questions": 5,
      "tokens": 1750
    },
    {
      "name": "Aladdin",
      "category": "disney",
      "questions": 5,
      "tokens": 1680
    },
    ...
  ],
  "token_budget_remaining": 1500
}
```

---

### Mode 2: Research Specific Shows

**Command format:**
```bash
python research_batch.py shows SHOW_NAME CATEGORY SHOW_NAME CATEGORY ...
```

**Example:**
```bash
python research_batch.py shows "Breaking Bad" "pop" "The Office" "pop" "Oprah Winfrey" "celeb"
```

**What happens:**
1. Takes specified shows
2. Researches each one in order
3. Stops if token budget exhausted
4. Updates all files automatically
5. Returns JSON summary

---

### Mode 3: Check Current Status

**Command:**
```bash
python research_batch.py status
```

**Output:**
```json
{
  "tokens_used_today": 8500,
  "tokens_remaining": 1500,
  "total_questions": 47,
  "by_category": {
    "disney": 25,
    "pop": 22,
    "celeb": 0,
    "custom": 0
  },
  "shows_researched": 5,
  "progress": {
    "disney": "5/20",
    "pop": "4/20",
    "celeb": "0/20"
  }
}
```

---

## For User: How to Direct Agent

### Scenario 1: "Research until budget is exhausted"
```
Agent:
cd /Users/mambohq/Documents/odin_os/sip-and-spill
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python research_batch.py auto 10

Then tell me the summary (questions_generated, tokens_used).
```

### Scenario 2: "Research these specific shows"
```
Agent:
cd /Users/mambohq/Documents/odin_os/sip-and-spill
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python research_batch.py shows "Game of Thrones" "pop" "The Crown" "pop" "Stranger Things" "pop"

Report back when done.
```

### Scenario 3: "Check what's been researched"
```
Agent:
cd /Users/mambohq/Documents/odin_os/sip-and-spill
export ANTHROPIC_API_KEY=sk-ant-your-key-here
python research_batch.py status

Show me the status JSON.
```

---

## Agent Capabilities

✅ **Autonomous:** No user interaction needed  
✅ **Token-aware:** Stops when budget exhausted  
✅ **Progress-tracked:** Saves after each show  
✅ **JSON output:** Easy for you to read results  
✅ **File-safe:** Only appends, never deletes existing questions  
✅ **Resumable:** Run again tomorrow when budget resets  

---

## Files Modified During Research

| File | Changes |
|------|---------|
| `data/generated_questions.json` | New questions appended |
| `data/research_progress.json` | Progress updated (tokens, shows researched) |
| `data/research_queue.json` | Tracks which shows are done |
| `data/research_batch.py` | Script that agent runs |

---

## Error Handling

If something fails:
- **API error?** Agent will report in "error" field of JSON
- **Budget exceeded?** Script stops gracefully (status: "budget_limit_reached")
- **Invalid show?** Script logs error and moves to next
- **Invalid API key?** Will exit with error message before running

---

## Cost Breakdown

- Per show: ~1500 tokens (~$0.01)
- Daily budget: 10,000 tokens ($0.05)
- Per day: Can research 6-7 shows
- Per week: ~40 shows = $0.35

---

## Example: Research 40 Shows Over 1 Week

**Monday:** `python research_batch.py auto 6` → 6 disney shows
**Tuesday:** `python research_batch.py auto 7` → 5 more disney + 2 pop
**Wednesday:** `python research_batch.py auto 6` → 6 pop shows
**Thursday:** `python research_batch.py auto 5` → 5 pop shows
**Friday:** `python research_batch.py auto 6` → 6 celeb shows
**Saturday:** `python research_batch.py auto 6` → 6 celeb shows
**Sunday:** `python research_batch.py auto 5` → 5 celeb shows (if under budget)

**Total:** ~42 shows researched = 210 questions = $0.35

---

## How Agent Should Report Back

```
✅ RESEARCH COMPLETE

Shows Researched: 5
Questions Generated: 25
Tokens Used: 8500 / 10000
Token Budget Remaining: 1500

Questions by Category:
  Disney: 25 (Frozen, Aladdin, Lion King, Cinderella, Tangled)
  Pop: 22 (Friends, Office, Breaking Bad, Game of Thrones, Stranger Things)
  Celebrity: 0

Status: 5/20 Disney done, 4/20 Pop done, 0/20 Celebrity done

Next Steps: Tomorrow research 5-6 more shows (budget will reset)
```

---

**NOTE:** User provides API key via `export ANTHROPIC_API_KEY=...` before agent runs. Agent uses it for all Claude API calls.
