# The Seven-Phase Ascension (Life RPG)

> **A Production-Grade, AI-Powered Life RPG & Gamified Productivity Platform**  
> *Cultivation Edition: Calm Light Wuxia Aesthetics, Non-Linear RPG Mathematics, and AI Telemetry.*

---

## 🌟 Overview

**The Seven-Phase Ascension** transforms real-world goals, deep-work focus sessions, and habit tracking into a unified Daoist cultivation journey. Declare macro vows, splinter them into actionable deeds, enter secluded focus chambers, and dispel inner tribulation beasts across four core pillars: **Spirit (Mind)**, **Physique (Health)**, **Dao (Career)**, and **Fortune (Wealth)**.

---

## ⛩️ The Seven Phases of Ascension

1. **Phase I — The Vow**: Swear a macro goal and target date. The AI Game Master splinters the vow into 5–6 daily deeds and spawns a thematic **Tribulation Beast** with calculated HP.
2. **Phase II — The Grind (Daily Deeds)**: Practice deeds with difficulty ranks ($E$ to $S$), streak multipliers, and instant Tribulation strikes that award Qi & Spirit Stones.
3. **Phase III — The Crucible (Meditation Pavilion)**: Customizable Pomodoro timer (25m / 50m / 90m) with gentle breathing circle animation, delivering critical strikes to the active Tribulation.
4. **Phase IV — The Grimoire (Daoist Chronicle)**: Contemplation journal analyzed for sentiment score ($-100$ to $+100$), auto-tags, and habit blockers with personalized mentor reflections.
5. **Phase V — The Ascension**: Dynamic leveling math ($\lfloor 100 \times (L - 1)^{1.5} \rfloor$) and 7 Realm Tiers with dynamic Archetypes (*Astral Savant*, *Titan Vanguard*, *Grand Architect*, *Sovereign Alchemist*, and hybrid titles).
6. **Phase VI — The Reliquary (Pavilion of Relics)**: Spend Spirit Stones on custom mortal rewards or **Chronos Preservation Talismans** (Streak Freeze Shields).
7. **Phase VII — The Oracle (Celestial Astrolabe)**: 4-Pillar Harmonic Radar, 14-day Qi & Mind-State velocity charts, blocker tag frequency cloud, and strategic weekly AI decrees.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, Flask 3.x (Modular Blueprints & Application Factory), SQLite3 (WAL mode, Foreign Keys enforced), Pydantic.
- **AI Engine**: Google GenAI SDK (`gemini-2.5-flash`) via `.env` (`GEMINI_API_KEY`) + 100% deterministic offline fallback.
- **Frontend**: HTML5, Jinja2, Tailwind CSS, Alpine.js, Chart.js, Canvas-Confetti, Lucide Icons.
- **Audio**: Web Audio API procedural acoustics (Tibetan singing bowls, wooden fish *muyu*, jade chimes, bronze temple gong).

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional: Add your `GEMINI_API_KEY` for live LLM generation; works 100% offline via deterministic heuristics without an API key).*

### 3. Run the Application
```bash
python run.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🧪 Testing & Verification

Run the automated endpoint and database test suite:
```bash
pytest tests/test_api.py -v
```

Execute the 100-day progression simulation:
```bash
python tests/simulate_100_days.py
```

---

## 📜 License
MIT

