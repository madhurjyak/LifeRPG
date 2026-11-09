import os
import re
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from app.models import (
    CampaignSplinterResponse,
    JournalAnalysisResponse,
    OracleProphecyResponse,
    GeneratedQuest
)
from app.services.game_engine import DIFFICULTY_REWARDS

load_dotenv()

def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except Exception:
        return None

# ====================================================================
# DETERMINISTIC HEURISTIC GAME MASTER (100% OFFLINE CAPABLE)
# ====================================================================

def _heuristic_campaign(goal_title: str, description: str, difficulty_focus: str) -> CampaignSplinterResponse:
    text = (goal_title + " " + (description or "")).lower()

    if any(k in text for k in ["code", "tech", "app", "ai", "software", "system", "exam", "engineer", "data"]):
        boss_name = "Nihilus, Weaver of Latency"
        boss_title = "Primordial Lord of Fragmented Architecture"
        boss_hp = 600
        lore = f"From the dark corridors of technical entropy emerges {boss_name}. To defeat this entity, you must transmute chaotic code into immutable architectures."
        quests = [
            GeneratedQuest(task_name="Architect Core Interface & Flow Specification", attribute_type="MIND", difficulty_rank="A", xp_value=150, gold_value=65, boss_damage=150),
            GeneratedQuest(task_name="Implement & Verify High-Fidelity Module Logic", attribute_type="CAREER", difficulty_rank="B", xp_value=100, gold_value=40, boss_damage=100),
            GeneratedQuest(task_name="45-Minute Postural Reset & Zone 2 Cardio", attribute_type="HEALTH", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Optimize Asset Allocation & Track Project Budget", attribute_type="WEALTH", difficulty_rank="D", xp_value=40, gold_value=15, boss_damage=40),
            GeneratedQuest(task_name="Synthesize Architecture Notes in Adventure Grimoire", attribute_type="MIND", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Eliminate Critical Tech Friction Point", attribute_type="CAREER", difficulty_rank="B", xp_value=100, gold_value=40, boss_damage=100)
        ]
    elif any(k in text for k in ["fit", "gym", "run", "lift", "health", "muscle", "diet", "fast", "sleep", "weight"]):
        boss_name = "Acedia, The Sloth Colossus"
        boss_title = "Warden of Metabolic Stagnation"
        boss_hp = 550
        lore = f"The colossal manifestation of physical inertia, {boss_name}, seeks to encase your vessel in stone. Break the petrification with relentless kinetic discipline."
        quests = [
            GeneratedQuest(task_name="Execute Heavy Compound Lift Protocol", attribute_type="HEALTH", difficulty_rank="A", xp_value=150, gold_value=65, boss_damage=150),
            GeneratedQuest(task_name="Log Macronutrient Balance & Hydration Target", attribute_type="HEALTH", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Deep Physiological Study / Form Analysis", attribute_type="MIND", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Streamline Weekly Equipment & Recovery Budget", attribute_type="WEALTH", difficulty_rank="D", xp_value=40, gold_value=15, boss_damage=40),
            GeneratedQuest(task_name="Cold Plunge or Contrast Shower Protocol", attribute_type="HEALTH", difficulty_rank="B", xp_value=100, gold_value=40, boss_damage=100),
            GeneratedQuest(task_name="Pre-Sleep Mobility & Box Breathing Routine", attribute_type="HEALTH", difficulty_rank="D", xp_value=40, gold_value=15, boss_damage=40)
        ]
    elif any(k in text for k in ["money", "finance", "wealth", "revenue", "sale", "fund", "invest", "crypto", "business"]):
        boss_name = "Mammon, Shade of Market Volatility"
        boss_title = "Specter of Speculative Ruin"
        boss_hp = 580
        lore = f"{boss_name} whispers mirages of instant gratification and paralysis. Master the forge of compounding capital to dispel its illusion."
        quests = [
            GeneratedQuest(task_name="Audit Primary Cash Flow & Burn Rate", attribute_type="WEALTH", difficulty_rank="A", xp_value=150, gold_value=65, boss_damage=150),
            GeneratedQuest(task_name="Deploy High-Value Pipeline Acquisition Outreach", attribute_type="CAREER", difficulty_rank="B", xp_value=100, gold_value=40, boss_damage=100),
            GeneratedQuest(task_name="Deep Market Research / Macro Economic Synthesis", attribute_type="MIND", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="High-Intensity Focus Conditioning to Sharpen Stress Resilience", attribute_type="HEALTH", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Rebalance Long-Term Index Asset Holdings", attribute_type="WEALTH", difficulty_rank="B", xp_value=100, gold_value=40, boss_damage=100),
            GeneratedQuest(task_name="Review & Eliminate Recurring Subscription Waste", attribute_type="WEALTH", difficulty_rank="D", xp_value=40, gold_value=15, boss_damage=40)
        ]
    else:
        boss_name = "Entropy, Void of Fragmented Will"
        boss_title = "The Primordial Unmaker of Intent"
        boss_hp = 500
        lore = f"{boss_name} gathers in the silent spaces where vows falter. Forge your daily rituals into weapons of pure resolve."
        quests = [
            GeneratedQuest(task_name=f"Master Core Pillar of '{goal_title[:30]}'", attribute_type="MIND", difficulty_rank="A", xp_value=150, gold_value=65, boss_damage=150),
            GeneratedQuest(task_name="Execute 50-Minute Crucible Deep Focus Sprint", attribute_type="CAREER", difficulty_rank="B", xp_value=100, gold_value=40, boss_damage=100),
            GeneratedQuest(task_name="Kinetic Vigor: 30-Minute Bodyweight Conditioning", attribute_type="HEALTH", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Review Weekly Capital & Resource Reserves", attribute_type="WEALTH", difficulty_rank="D", xp_value=40, gold_value=15, boss_damage=40),
            GeneratedQuest(task_name="Synthesize Reflection in the Grimoire", attribute_type="MIND", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65),
            GeneratedQuest(task_name="Eliminate Daily Procrastination Vector", attribute_type="CAREER", difficulty_rank="C", xp_value=65, gold_value=25, boss_damage=65)
        ]

    # Adjust rewards based on difficulty table
    for q in quests:
        r = DIFFICULTY_REWARDS.get(q.difficulty_rank, DIFFICULTY_REWARDS['C'])
        q.xp_value = r['xp']
        q.gold_value = r['gold']
        q.boss_damage = r['boss_damage']

    return CampaignSplinterResponse(
        boss_name=boss_name,
        boss_title=boss_title,
        boss_hp=boss_hp,
        narrative_premise=lore,
        quests=quests
    )

def _heuristic_journal(journal_text: str, recent_quests_summary: str, user_state: dict) -> JournalAnalysisResponse:
    text = journal_text.lower()
    
    positives = ["crushed", "breakthrough", "clarity", "energized", "great", "strong", "proud", "consistent", "focused", "completed", "progress", "flow", "triumph", "solid", "win"]
    negatives = ["friction", "procrastinated", "tired", "failed", "distracted", "exhausted", "late", "fog", "stress", "sluggish", "blocked", "burnout", "anxiety", "struggled", "behind"]

    pos_count = sum(1 for word in positives if word in text)
    neg_count = sum(1 for word in negatives if word in text)

    raw_sentiment = (pos_count - neg_count) * 25
    sentiment_score = max(-100, min(100, raw_sentiment if raw_sentiment != 0 else 30))

    # Detected blockers
    blockers = []
    if any(k in text for k in ["tired", "exhaust", "sleep", "insomnia"]):
        blockers.append("Sleep deficit or energy depletion")
    if any(k in text for k in ["procrastinat", "hesitat", "avoid"]):
        blockers.append("Execution hesitation and cognitive friction")
    if any(k in text for k in ["distract", "phone", "scroll", "interrupt"]):
        blockers.append("Attention fragmentation from external stimuli")
    if any(k in text for k in ["confus", "ambigu", "unclear"]):
        blockers.append("Ambiguous task scope or unclear next steps")
    if not blockers:
        blockers.append("No active friction detected; forward momentum intact")
    
    detected_blockers = "; ".join(blockers)

    # Tags
    tags = ["#ascension", "#grimoire"]
    if any(k in text for k in ["code", "tech", "build", "study", "read", "learn"]):
        tags.append("#mind")
    if any(k in text for k in ["gym", "run", "lift", "cardio", "sleep", "walk"]):
        tags.append("#health")
    if any(k in text for k in ["work", "career", "client", "project", "deploy"]):
        tags.append("#career")
    if any(k in text for k in ["invest", "money", "save", "budget", "crypto"]):
        tags.append("#wealth")
    if sentiment_score >= 50:
        tags.append("#flowstate")
    elif sentiment_score < 0:
        tags.append("#crucible_trial")

    auto_tags = ",".join(tags[:5])

    # Narrative notes
    archetype = user_state.get('archetype_title', 'Adept')
    level = user_state.get('level', 1)

    if sentiment_score >= 50:
        notes = f"The arcane ether hums with your triumph, {archetype}. At Level {level}, your focus has struck a resounding blow against the Void. Consolidate these gains and let your momentum carry you toward the next Ascension threshold."
    elif sentiment_score < 0:
        notes = f"Take heed, {archetype}. Friction is not failure—it is the resistance that forges celestial steel. Acknowledge the blocker: '{detected_blockers.split(';')[0]}'. Regroup in the Crucible, adjust your guard, and advance with disciplined micro-steps."
    else:
        notes = f"A day of steady craftsmanship recorded in the eternal annals, {archetype}. Every measured action reinforces your foundation. Guard your evening recovery and prepare for tomorrow's dawn."

    return JournalAnalysisResponse(
        sentiment_score=sentiment_score,
        auto_tags=auto_tags,
        detected_blockers=detected_blockers,
        ai_gamemaster_notes=notes
    )

def _heuristic_oracle(user_metrics: dict, logs_summary: str, attribute_distribution: dict) -> OracleProphecyResponse:
    # Find weakest pillar
    attrs = {
        'MIND': attribute_distribution.get('MIND', 0),
        'HEALTH': attribute_distribution.get('HEALTH', 0),
        'CAREER': attribute_distribution.get('CAREER', 0),
        'WEALTH': attribute_distribution.get('WEALTH', 0)
    }
    sorted_attrs = sorted(attrs.items(), key=lambda x: x[1])
    weakest_pillar, weakest_xp = sorted_attrs[0]
    strongest_pillar, strongest_xp = sorted_attrs[-1]

    streak = user_metrics.get('current_streak', 0)
    
    # Burnout risk estimation
    if streak >= 14 and attrs.get('HEALTH', 0) < attrs.get('MIND', 0) * 0.4:
        burnout = 'HIGH'
    elif streak >= 7 and weakest_xp < strongest_xp * 0.3:
        burnout = 'MODERATE'
    else:
        burnout = 'LOW'

    title = f"The Oracle's Decree: Alignment of the {weakest_pillar.capitalize()} Gateway"

    narrative = (
        f"The celestial telemetry reveals commanding mastery in your {strongest_pillar} pillar ({strongest_xp} XP), "
        f"yet the astral matrix suffers harmonic imbalance. Your current {streak}-day momentum is formidable, "
        f"but sustained elevation to higher Ascension Phases demands equilibrium across all four realms of existence."
    )

    pillar_advice = {
        'MIND': "Your cognitive reserves require deliberate nourishment. Incorporate 30 minutes of deep non-screen synthesis or philosophical contemplation.",
        'HEALTH': "The physical vessel bears the strain of your high-velocity ambition. Prioritize circadian alignment, zone 2 aerobic recovery, and contrast therapy.",
        'CAREER': "Your theoretical knowledge outpaces tangible manifestation. Commit to publishing or deploying a tangible, immutable artifact this cycle.",
        'WEALTH': "Neglect of the earthly treasury limits long-term sovereignty. Audit overhead leaks, optimize asset allocation, and establish automated compounding."
    }
    weak_advice = pillar_advice.get(weakest_pillar, "Rebalance your daily rituals to fortify your least exercised attribute.")

    # Recommended quests
    rec_quests = [
        GeneratedQuest(
            task_name=f"Fortify the Gateway: Dedicated {weakest_pillar.capitalize()} Alignment Ritual",
            attribute_type=weakest_pillar,
            difficulty_rank="B",
            xp_value=100,
            gold_value=40,
            boss_damage=100
        ),
        GeneratedQuest(
            task_name="Crucible Calibration: 50-Minute Sovereign Focus Session",
            attribute_type="MIND" if weakest_pillar != "MIND" else "HEALTH",
            difficulty_rank="A",
            xp_value=150,
            gold_value=65,
            boss_damage=150
        )
    ]

    return OracleProphecyResponse(
        prophecy_title=title,
        narrative_assessment=narrative,
        weakest_pillar_advice=weak_advice,
        burnout_risk_level=burnout,
        recommended_quests=rec_quests
    )

# ====================================================================
# PUBLIC AI SERVICE FACADE (WITH INSTANT GRACEFUL FALLBACK)
# ====================================================================

class AIGameMasterService:
    @staticmethod
    def generate_campaign_and_quests(goal_title: str, description: str = "", difficulty_focus: str = "BALANCED") -> CampaignSplinterResponse:
        client = get_genai_client()
        if not client:
            return _heuristic_campaign(goal_title, description, difficulty_focus)

        try:
            prompt = f"""
You are the Omniscient AI Game Master of 'The Seven-Phase Ascension' Life RPG.
A user has sworn a macro vow:
Goal Title: "{goal_title}"
Description: "{description}"
Focus: "{difficulty_focus}"

Create an epic thematic RPG Boss and splinter this macro goal into 5 to 6 actionable Daily Quests.
Distribute the quests across the 4 attributes: MIND, HEALTH, CAREER, WEALTH.
Assign difficulty ranks from: 'E', 'D', 'C', 'B', 'A', 'S'.
Return pure valid JSON matching this schema:
{{
  "boss_name": "string (e.g., 'Nihilus, Weaver of Latency')",
  "boss_title": "string (e.g., 'Primordial Lord of Fragmented Code')",
  "boss_hp": integer (between 450 and 700),
  "narrative_premise": "string (atmospheric 2-sentence lore context)",
  "quests": [
    {{
      "task_name": "string (actionable and concise)",
      "attribute_type": "MIND" | "HEALTH" | "CAREER" | "WEALTH",
      "difficulty_rank": "E" | "D" | "C" | "B" | "A" | "S",
      "xp_value": integer,
      "gold_value": integer,
      "boss_damage": integer
    }}
  ]
}}
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            data = json.loads(response.text)
            
            # Fill in standardized reward math
            for q in data.get('quests', []):
                diff = q.get('difficulty_rank', 'C').upper()
                rewards = DIFFICULTY_REWARDS.get(diff, DIFFICULTY_REWARDS['C'])
                q['xp_value'] = rewards['xp']
                q['gold_value'] = rewards['gold']
                q['boss_damage'] = rewards['boss_damage']

            return CampaignSplinterResponse(**data)
        except Exception:
            # Deterministic fallback guaranteed to never fail
            return _heuristic_campaign(goal_title, description, difficulty_focus)

    @staticmethod
    def analyze_journal_entry(journal_text: str, recent_quests_summary: str = "", user_state: Optional[Dict[str, Any]] = None) -> JournalAnalysisResponse:
        user_state = user_state or {}
        client = get_genai_client()
        if not client:
            return _heuristic_journal(journal_text, recent_quests_summary, user_state)

        try:
            prompt = f"""
You are the AI Game Master of 'The Seven-Phase Ascension'.
Analyze the following user journal entry:
"{journal_text}"

User State: Level {user_state.get('level', 1)}, Archetype: {user_state.get('archetype_title', 'Novice Seeker')}.
Recent Activity: {recent_quests_summary}

Respond in pure valid JSON matching this schema:
{{
  "sentiment_score": integer (-100 to 100),
  "auto_tags": "comma-separated hashtags like #deepwork,#focus,#burnout",
  "detected_blockers": "concise summary of friction points or 'None'",
  "ai_gamemaster_notes": "atmospheric 2-3 sentence second-person RPG narration acknowledging triumphs/struggles and imparting tactical wisdom"
}}
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            data = json.loads(response.text)
            return JournalAnalysisResponse(**data)
        except Exception:
            return _heuristic_journal(journal_text, recent_quests_summary, user_state)

    @staticmethod
    def generate_oracle_prophecy(user_metrics: Dict[str, Any], logs_summary: str = "", attribute_distribution: Optional[Dict[str, Any]] = None) -> OracleProphecyResponse:
        attribute_distribution = attribute_distribution or {'MIND': 100, 'HEALTH': 100, 'CAREER': 100, 'WEALTH': 100}
        client = get_genai_client()
        if not client:
            return _heuristic_oracle(user_metrics, logs_summary, attribute_distribution)

        try:
            prompt = f"""
You are The Oracle of 'The Seven-Phase Ascension'.
Analyze this user's 14-day telemetry and attribute distribution:
Metrics: {json.dumps(user_metrics)}
Attribute XP Distribution: {json.dumps(attribute_distribution)}
Recent Logs Summary: {logs_summary}

Generate a weekly strategic prophecy in pure JSON matching this schema:
{{
  "prophecy_title": "string (e.g., 'Decree of the Unshakable Will')",
  "narrative_assessment": "string (strategic overview of momentum, velocity, and risks)",
  "weakest_pillar_advice": "string (actionable advice to balance their weakest attribute)",
  "burnout_risk_level": "LOW" | "MODERATE" | "HIGH",
  "recommended_quests": [
    {{
      "task_name": "string",
      "attribute_type": "MIND" | "HEALTH" | "CAREER" | "WEALTH",
      "difficulty_rank": "C" | "B" | "A",
      "xp_value": integer,
      "gold_value": integer,
      "boss_damage": integer
    }}
  ]
}}
"""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            data = json.loads(response.text)
            for q in data.get('recommended_quests', []):
                diff = q.get('difficulty_rank', 'C').upper()
                rewards = DIFFICULTY_REWARDS.get(diff, DIFFICULTY_REWARDS['C'])
                q['xp_value'] = rewards['xp']
                q['gold_value'] = rewards['gold']
                q['boss_damage'] = rewards['boss_damage']

            return OracleProphecyResponse(**data)
        except Exception:
            return _heuristic_oracle(user_metrics, logs_summary, attribute_distribution)

