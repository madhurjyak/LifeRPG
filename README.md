# The Seven-Phase Ascension — AI-Powered Life RPG

> A production-grade, AI-powered Life RPG and gamified productivity web application built with a serene, light Wuxia / Daoist Cultivation aesthetic.

![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Flask 3.x](https://img.shields.io/badge/flask-3.x-green.svg)
![SQLite WAL](https://img.shields.io/badge/sqlite-WAL%20mode-orange.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

---

## The Seven Phases of Ascension

1. **Phase I — The Vow**: Swear a macro goal and target date. The AI Game Master splinters the vow into 5–6 actionable daily deeds across 4 pillars (*Spirit/Mind, Physique/Health, Dao/Career, Fortune/Wealth*) and manifests a thematic Tribulation Boss.
2. **Phase II — The Grind**: Daily quest matrix with difficulty ranks (`E` to `S`), attribute tags, streak multipliers, and instant damage channeling to the active Tribulation.
3. **Phase III — The Crucible**: Meditation focus chamber with customizable Pomodoro intervals (25m, 50m, 90m) and ambient Zen breathing guidance.
4. **Phase IV — The Grimoire**: Daily Daoist chronicle and reflection journal with automated sentiment scoring, friction blocker detection, and AI Game Master wisdom notes.
5. **Phase V — The Ascension**: Non-linear leveling formulas, 7 Ascension Realm Tiers (Dormant Initiate to Transcendent Ascendant), and dynamic class archetypes (e.g. *Astral Savant*, *Grand Architect*, *Psionic Juggernaut*).
6. **Phase VI — The Reliquary**: Aether Gold / Spirit Stones marketplace for custom IRL rewards and *Chronos Aegis* streak preservation shields.
7. **Phase VII — The Oracle**: Telemetry dashboard featuring a 4-Pillar Harmonic Radar Chart, 14-Day Velocity & Mind Harmony Dual-Axis Line Chart, Blocker Frequency tags, and one-click weekly prophecy divination.

---

## System Architecture

- **Backend**: Python 3.11+, Flask 3.x (Modular Blueprints & Application Factory), SQLite3 (WAL mode + Foreign Keys), Pydantic schemas.
- **AI Engine**: Google GenAI SDK (`gemini-2.5-flash`) paired with a deterministic offline heuristic generator that runs 100% offline without API keys.
- **Frontend**: HTML5, Tailwind CSS, Alpine.js, Chart.js, Canvas-Confetti, Lucide Icons.
- **Audio**: Web Audio API procedural sound synthesizer (resonant singing bowl chimes, temple wooden fish, pure jade pings, and bronze gong fanfares).

---

## Quickstart

### 1. Clone & Setup
```bash
git clone https://github.com/madhurjyak/LifeRPG.git
cd LifeRPG
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix:
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your Gemini API key to `.env`:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Launch the Application
```bash
python run.py
```
Open **http://127.0.0.1:5000** in your browser.

---

## Running Verification & Simulation

Run the automated endpoint test suite:
```bash
pytest tests/test_api.py -v
```

Execute the 100-Day agentic progression simulation:
```bash
python tests/simulate_100_days.py
```

---

## License
MIT License.
