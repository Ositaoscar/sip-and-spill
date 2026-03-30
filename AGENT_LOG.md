# Agent Log — Sip & Spill Development Handoff

> Document for agents: what's done, what's broken, what needs fixing

---

## 📊 Current Status

| Component | Status | Priority | Notes |
|-----------|--------|----------|-------|
| Game UI | ✅ Working | — | All screens render, animations smooth |
| Question Loading | ✅ Working | — | Loads from JSON, falls back to BANK |
| Multiplayer (Online) | ⚠️ Partial | Medium | Supabase connected but needs testing |
| Local Play | ✅ Working | — | No API needed, fully functional |
| Question Generator | ✅ Ready | — | Queue-based, daily token budget |
| Dashboard Graphics | ❌ Missing | Low | No fancy UI, functional only |

---

## 🔴 Known Issues

### Issue 1: Supabase Connection Unreliable
- **File:** `index.html` [lines 220-260]
- **Problem:** Real-time subscriptions fail intermittently (unreliable WebSocket)
- **Current Fix:** Polling fallback (checks every 1s for multiplayer updates)
- **Status:** Works but not elegant
- **Agent Task:** Consider switching to:
  - HTTP polling only (no WebSocket)
  - Supabase alternative (Firebase?)
  - Local storage + manual refresh

### Issue 2: Disney Show Questions (Legacy)
- **File:** `index.html` [lines 290-331]
- **Problem:** Hardcoded show generator creates mediocre questions
- **Status:** Works but will be replaced by Claude-generated ones
- **Agent Task:** Can be LEFT AS-IS (fallback). When user generates 20+ Disney questions via tool, game will prefer them.

### Issue 3: Question Distractors (Too Easy)
- **File:** `data/generated_questions.json` (the placeholder data)
- **Problem:** Default BANK questions have obvious wrong answers
- **Vector:** Generate 50+ smart questions using queue tool (in progress)
- **Agent Task:** Monitor generation progress, ensure 5+ questions per show

---

## 🟡 Needs Attention (Not Bugs)

### Feature 1: Supabase Export
- **File:** `generate_questions.py` [line ~400, search for "Export to Supabase"]
- **Status:** Stubbed out (prints "Feature coming soon")
- **What's needed:**
  - Connect to Supabase
  - Upload `generated_questions.json` to database table
  - Game then loads from DB instead of JSON (required for mobile app)
- **Priority:** HIGH (needs to happen before app conversion)
- **Agent Task:** Implement Supabase upload + DB schema creation

### Feature 2: Mobile App Conversion
- **Status:** Not started
- **Files needed:**
  - Move game to React Native or Flutter
  - Switch data source from JSON to Supabase
  - Add offline support
- **Priority:** MEDIUM (after question generation stabilizes)
- **Agent Task:** Plan architecture (not implement yet)

### Feature 3: Leaderboard / Score Tracking
- **File:** Game has no score persistence across sessions
- **Status:** Not started
- **Priority:** LOW (nice-to-have)
- **Agent Task:** Add Supabase table + UI to display top scores

---

## 🟢 Ready to Edit / Enhance

### Section 1: Game Difficulty Curves
- **File:** `index.html` [lines 675-710: pick() function]
- **Current behavior:** Streak-based drinks (1st wrong = 2 drinks, 2nd = 4, etc.)
- **Agent task:** Can EASILY modify:
  - Change multiplier (2x → 3x → 4x)
  - Add time bonuses (faster answer = more points)
  - Add combo streak (consecutive right answers)
- **Effort:** LOW (just edit multipliers in `pick()` function)

### Section 2: UI Theming
- **File:** `index.html` [lines 12-14: `:root` CSS variables]
- **Current colors:** Dark theme (black bg, pink/purple gradients)
- **Agent task:** Can instantly theme by editing:
  ```css
  :root{
    --bg:#0e0818;        ← Background color
    --pink:#f472b6;      ← Primary accent
    --purple:#a78bfa;    ← Secondary accent
    --gold:#fbbf24;      ← Fact box color
    --green:#34d399      ← Success color
  }
  ```
- **Effort:** TRIVIAL (just change hex codes)

### Section 3: Question Categories
- **File:** `index.html` [lines 160-167]
- **Current:** Disney / Pop Culture / Celebrity tiles
- **Agent task:** Can add new categories:
  - Add tile in HTML (copy existing `<div class="cat-tile">`)
  - Add subcategories in SUBCATS object [line 283]
  - Add questions to BANK object [line 345]
- **Effort:** LOW-MEDIUM

### Section 4: Game Win Condition
- **File:** `index.html` [line 580: check for `pts[G.cur]>=10`]
- **Current:** First to 10 points wins
- **Agent task:** Change win condition:
  - Edit `10` to `15` for longer games
  - Or add difficulty levels
- **Effort:** TRIVIAL

---

## 📋 Checklist for Next Agent

### Before Starting Work:
- [ ] Read this log (you are here ✅)
- [ ] Check latest GitHub commit: `git log --oneline -5`
- [ ] Test game locally: hard refresh, play one round
- [ ] Verify Supabase connection: check browser console (F12)

### If Working on Questions (Agent-Driven):
- [ ] Set `ANTHROPIC_API_KEY` first: `export ANTHROPIC_API_KEY=sk-ant-...`
- [ ] Use batch research script: `python research_batch.py auto 5`
- [ ] Or specify shows: `python research_batch.py shows "Breaking Bad" "pop" "Friends" "pop"`
- [ ] Check progress: `python research_batch.py status`
- [ ] Daily budget: $0.05 (10,000 tokens) — resets tomorrow
- [ ] Game auto-loads from `data/generated_questions.json` on restart

**Latest files:**
- `research_batch.py` — Agent runs this (all autonomous, no interaction)
- `AGENT_RESEARCH_GUIDE.md` — How to direct agent research

### If Working on Supabase:
- [ ] Check credentials in `.env.example`
- [ ] Supabase URL: `https://bbnuvufsmzhsfoconhcn.supabase.co`
- [ ] Need RLS policies for multiplayer (game isolation by room code)
- [ ] Questions table schema: [id, category, show, q, options[], answer_idx, fact]

### If Working on UI/UX:
- [ ] Edit CSS: `index.html` lines 12-14 (colors)
- [ ] Edit HTML: `index.html` lines 100-210 (layouts)
- [ ] Test on mobile: 375px width (iPhone SE) and 812px (iPhone X)

---

## 🔗 Key Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| `index.html` | Main game (all UI + logic) | 1-850 |
| `generate_questions.py` | Question generator (CLI tool) | 1-400 |
| `data/generated_questions.json` | Question bank (JSON) | 1-50+ |
| `QUESTION_GENERATOR.md` | How to use generator | — |
| `.env` / `.env.example` | API keys | — |
| `AGENT_LOG.md` | This file | — |

---

## 💬 Recent Context (Last 10 Commits)

```
7d242c6 docs: Update guide for queue-based generator
ec9aa9d refactor: Queue-based question generator with daily token budgeting
b9f3b60 feat: Add intelligent question generator with Claude AI support
de82aef fix: Remove extra closing brace causing syntax error at line 430
10f12b7 fix: Resolve initialization errors (jesse plot, SUBCATS ordering)
7081a86 refactor: Enhanced Supabase logging and debug output
6a2c497 feat: Hybrid difficulty system (3-option + streak multiplier)
da223d4 feat: Expand Pop & Celebrity question banks to 25 questions
...
```

---

## 🎯 Immediate Next Steps (For User or Next Agent)

1. **Generate Questions** (User action)
   - Set: `export ANTHROPIC_API_KEY=sk-ant-...`
   - Run: `python generate_questions.py`
   - Research 5-10 shows to build smart question bank
   - Takes 5-10 minutes per show, spread across days

2. **Test Questions** (User action)
   - Hard refresh game: `Cmd+Shift+R`
   - Check console: should see `✅ Loaded custom-generated questions`
   - Play game, verify difficulty level

3. **Fix Supabase** (Agent task — if multiplayer needed)
   - Implement export in `generate_questions.py`
   - Create questions table schema
   - Test multiplayer across devices

4. **Enhance UI** (Agent task — nice-to-have)
   - Add leaderboard screen
   - Add difficulty selector
   - Add sound effects

---

## 🚀 Version History

| Version | Date | Major Changes |
|---------|------|--------------|
| 1.0 | Mar 28 | Initial game + local play |
| 1.1 | Mar 29 | Supabase integration + multiplayer |
| 1.2 | Mar 29 | Question expansion (25 per category) |
| 1.3 | Mar 29 | Hybrid difficulty (3-option + streak) |
| 1.4 | Mar 30 | **Queue-based generator + daily budgeting** ← Current |
| 1.5 | TBD | Supabase export + mobile app |

---

## 📞 Questions to Answer For Agent

**Before editing, ask yourself:**
1. Is this a UI change or game logic change?
2. Does this affect multiplayer functionality?
3. Will this require API calls (Supabase, Claude, etc.)?
4. Does this need extensive testing?
5. What files need to be modified?

**Document your changes:**
- Update this log when done
- Commit with clear message: `feat/fix/refactor: [description]`
- Test before pushing to GitHub

---

**Last updated:** 2026-03-30  
**Current agent:** Next developer  
**Status:** Stable, ready for enhancement
