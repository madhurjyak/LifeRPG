import sqlite3
import os
from datetime import datetime, timedelta
from flask import g, current_app

def get_default_db_path():
    # In Vercel serverless functions, the root filesystem is read-only.
    # Writable storage is mounted at /tmp.
    if os.getenv("VERCEL"):
        return "/tmp/seven_ascension.db"
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "seven_ascension.db")

DEFAULT_DB_PATH = get_default_db_path()

def get_db_path():
    if current_app:
        return current_app.config.get("DATABASE", DEFAULT_DB_PATH)
    return DEFAULT_DB_PATH

def get_db(custom_path=None):
    path = custom_path or get_db_path()
    if current_app:
        if "db" not in g:
            g.db = sqlite3.connect(path, timeout=30.0, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row
            _configure_sqlite(g.db)
        return g.db
    else:
        conn = sqlite3.connect(path, timeout=30.0, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        _configure_sqlite(conn)
        return conn

def _configure_sqlite(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.OperationalError:
        pass
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute("PRAGMA busy_timeout=10000;")
    cursor.close()

def close_db(e=None):
    if current_app and "db" in g:
        db = g.pop("db", None)
        if db is not None:
            db.close()

def init_db(db_path=None, seed=True):
    path = db_path or get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    
    conn = sqlite3.connect(path, timeout=30.0)
    _configure_sqlite(conn)
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    if seed:
        seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn, force=False):
    cursor = conn.cursor()
    
    # Check if demo user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ("PlayerOne",))
    existing_user = cursor.fetchone()
    
    if existing_user and not force:
        user_id = existing_user[0] if isinstance(existing_user, tuple) else existing_user["id"]
        # If user already has active campaigns, keep existing state
        cursor.execute("SELECT count(*) FROM campaigns WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.close()
            return user_id

    if existing_user and force:
        user_id = existing_user[0] if isinstance(existing_user, tuple) else existing_user["id"]
        cursor.execute("DELETE FROM daily_quests WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM campaigns WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM adventure_logs WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM reliquary_items WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM focus_sessions WHERE user_id = ?", (user_id,))
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        existing_user = None

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # 1. Insert Demo User "PlayerOne"
    # Starting stats: Level 8, Phase 2, Balanced XP across all 4 pillars
    cursor.execute("""
        INSERT INTO users (
            username, total_xp, level, ascension_phase, archetype_title,
            mind_xp, health_xp, career_xp, wealth_xp, aether_gold,
            current_streak, longest_streak, streak_shields, focus_minutes_total,
            last_active_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "PlayerOne",
        2850,
        8,
        2,
        "Grand Architect",
        850,
        720,
        880,
        400,
        340,
        7,
        14,
        2,
        275,
        yesterday.isoformat()
    ))
    user_id = cursor.lastrowid

    # 2. Insert 4 Active Campaigns (One for each Core Pillar)
    campaign1_target = (today + timedelta(days=30)).isoformat()
    cursor.execute("""
        INSERT INTO campaigns (
            user_id, title, description, ai_context,
            boss_name, boss_title, boss_max_hp, boss_current_hp,
            target_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "Master the Neural Citadel (AI System Architect)",
        "Design, benchmark, and deploy production-grade distributed intelligence engines.",
        "Technical mastery, architectural resilience, high cognitive output.",
        "Entropy, Void of Fragmented Logic",
        "Primordial Lord of Technical Debt",
        800,
        340,
        campaign1_target,
        "active"
    ))
    campaign1_id = cursor.lastrowid

    campaign2_target = (today + timedelta(days=45)).isoformat()
    cursor.execute("""
        INSERT INTO campaigns (
            user_id, title, description, ai_context,
            boss_name, boss_title, boss_max_hp, boss_current_hp,
            target_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "Titan Physique & Metabolic Transmutation",
        "Forge neuromuscular strength, 3x weekly compound lifts, and metabolic flexibility.",
        "Daily physical conditioning, zone 2 cardio, clean nutrition.",
        "Acedia, The Sloth Colossus",
        "Warden of Physical Stagnation",
        650,
        260,
        campaign2_target,
        "active"
    ))
    campaign2_id = cursor.lastrowid

    campaign3_target = (today + timedelta(days=60)).isoformat()
    cursor.execute("""
        INSERT INTO campaigns (
            user_id, title, description, ai_context,
            boss_name, boss_title, boss_max_hp, boss_current_hp,
            target_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "Ascend to Principal Staff Engineer",
        "Author foundational RFCs, align cross-functional domains, and guide engineering adepts.",
        "Strategic engineering leadership, architectural clarity, mentorship.",
        "Impostor Phantom, Lord of Self-Doubt",
        "Specter of the Hall of Echoes",
        700,
        480,
        campaign3_target,
        "active"
    ))
    campaign3_id = cursor.lastrowid

    campaign4_target = (today + timedelta(days=90)).isoformat()
    cursor.execute("""
        INSERT INTO campaigns (
            user_id, title, description, ai_context,
            boss_name, boss_title, boss_max_hp, boss_current_hp,
            target_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        "The Sovereign Treasury (Asset Freedom)",
        "Automate disciplined investment contributions, minimize drag, and secure runway.",
        "Financial sovereignty, disciplined capital allocation, wealth multiplication.",
        "Mammon's Mirage, Drake of Hollow Consumption",
        "Tempter of Impulsive Expenditures",
        500,
        190,
        campaign4_target,
        "active"
    ))
    campaign4_id = cursor.lastrowid

    # 3. Insert Daily Quests:
    # A mix of active deeds ready for interaction + today's completed + historical
    today_str = today.isoformat()
    sample_quests = [
        # Incomplete Deeds for Today (ready to click and experience gameplay mechanics)
        (
            campaign1_id, user_id,
            "Design Vector Index Partitioning Architecture",
            "MIND", "A", 150, 65, 150, 0, today_str, None
        ),
        (
            campaign2_id, user_id,
            "Heavy Barbell Squats 4x6 & Hip Mobility Flow",
            "HEALTH", "B", 100, 40, 100, 0, today_str, None
        ),
        (
            campaign3_id, user_id,
            "Author Architecture Decision Record (ADR) for Event Stream",
            "CAREER", "B", 100, 40, 100, 0, today_str, None
        ),
        (
            campaign4_id, user_id,
            "Review Monthly Investment Contributions & Rebalance Index Funds",
            "WEALTH", "C", 65, 25, 65, 0, today_str, None
        ),
        (
            campaign1_id, user_id,
            "Deploy Microservice Cluster with Zero-Downtime Migration",
            "MIND", "S", 250, 100, 250, 0, today_str, None
        ),
        (
            campaign2_id, user_id,
            "10-Minute Box Breathing & Cold Hydrotherapy Protocol",
            "HEALTH", "D", 40, 15, 40, 0, today_str, None
        ),
        (
            campaign3_id, user_id,
            "Lead High-Leverage Strategic Architecture Sync with Senior Adepts",
            "CAREER", "A", 150, 65, 150, 0, today_str, None
        ),
        # Completed Today
        (
            campaign3_id, user_id,
            "Code Review 3 Pull Requests with Architectural Mentorship",
            "CAREER", "C", 65, 25, 65, 1, today_str, (datetime.now() - timedelta(hours=3)).isoformat()
        ),
        (
            campaign1_id, user_id,
            "Deep Work Meditation: 50-Minute Crucible Focus Module",
            "MIND", "B", 100, 40, 100, 1, today_str, (datetime.now() - timedelta(hours=5)).isoformat()
        ),
        (
            campaign2_id, user_id,
            "Morning Mobility Sequence & 2L Electrolyte Hydration",
            "HEALTH", "E", 25, 10, 25, 1, today_str, (datetime.now() - timedelta(hours=6)).isoformat()
        ),
        # Completed Yesterday (maintains streak)
        (
            campaign2_id, user_id,
            "Deadlift 3x5 at 80% 1RM & Mobility Sequence",
            "HEALTH", "B", 100, 40, 100, 1, yesterday.isoformat(), yesterday.strftime("%Y-%m-%d 18:30:00")
        ),
        (
            campaign1_id, user_id,
            "Refactor Blueprint Routing Architecture",
            "MIND", "C", 65, 25, 65, 1, yesterday.isoformat(), yesterday.strftime("%Y-%m-%d 14:15:00")
        ),
        (
            campaign4_id, user_id,
            "Audit Index Fund Allocation & Tax-Loss Harvesting",
            "WEALTH", "C", 65, 25, 65, 1, yesterday.isoformat(), yesterday.strftime("%Y-%m-%d 11:00:00")
        ),
    ]

    for q in sample_quests:
        cursor.execute("""
            INSERT INTO daily_quests (
                campaign_id, user_id, task_name, attribute_type, difficulty_rank,
                xp_value, gold_value, boss_damage, is_completed, quest_date, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q)

    # 4. Insert 8 Historical Journal Logs (Days -7 to Today)
    historical_logs = [
        (
            user_id,
            "Commenced the architecture blueprint for the distributed graph pipeline. Felt solid momentum in the morning, though afternoon context-switching slowed deployment.",
            "The arcane currents flow favorably, Adept. Beware the siren song of reactive multitasking—anchor your focus in the deep crucible.",
            65,
            "#deepwork,#architecture,#flowstate",
            "Context switching during afternoon standups",
            50,
            (today - timedelta(days=7)).strftime("%Y-%m-%d 20:15:00")
        ),
        (
            user_id,
            "Crushed high-intensity kettlebell conditioning and finished 2 key modules. Struggled slightly with late-night screen blue light causing insomnia.",
            "Your physical vessel hardens against the Void. Guard your nocturnal gateway with equal vigilance; rest is the foundation of astral power.",
            72,
            "#fitness,#conditioning,#discipline",
            "Late night screen exposure",
            50,
            (today - timedelta(days=6)).strftime("%Y-%m-%d 21:30:00")
        ),
        (
            user_id,
            "Felt mental friction today. Procrastinated on data schema migration due to ambiguous requirements. Eventually rallied for a 25min focus session.",
            "Ambiguity is the shroud worn by Entropy. Slice through fog with granular micro-vows. A single clean strike dissolves hesitation.",
            -20,
            "#friction,#procrastination,#schema",
            "Ambiguous technical requirements",
            50,
            (today - timedelta(days=5)).strftime("%Y-%m-%d 22:05:00")
        ),
        (
            user_id,
            "Breakthrough day. Refactored the core state machine and solved the recursive database locking issue. Energy was vibrant throughout.",
            "Triumphant insight! The weave of logic answers your command. The Campaign Boss trembles as your architecture solidifies.",
            88,
            "#breakthrough,#clean_code,#state_machine",
            "None",
            50,
            (today - timedelta(days=4)).strftime("%Y-%m-%d 19:45:00")
        ),
        (
            user_id,
            "Managed personal finances, paid tax reserves, and completed morning mobility drills. Steady and measured progress across the sovereign treasury.",
            "Order across all pillars is the mark of true sovereignty. Gold flows where discipline reigns supreme.",
            68,
            "#wealth,#mobility,#order",
            "Minor fatigue from week buildup",
            50,
            (today - timedelta(days=3)).strftime("%Y-%m-%d 20:50:00")
        ),
        (
            user_id,
            "Deep focus dungeon: executed two 50-minute Crucible sessions back-to-back. The neural pipeline test suite passed with 100% coverage.",
            "You have entered the transcendent flow. The Citadel rises stone by stone beneath your disciplined hands.",
            85,
            "#crucible,#deepwork,#unit_tests",
            "None",
            50,
            (today - timedelta(days=2)).strftime("%Y-%m-%d 21:10:00")
        ),
        (
            user_id,
            "Heavy squat session completed and drafted ADR for event streaming pipeline. The tribulation bosses are steadily taking damage.",
            "The twin pillars of somatic power and mental clarity ascend in harmony. Victory draws nigh.",
            75,
            "#conditioning,#architecture,#momentum",
            "None",
            50,
            yesterday.strftime("%Y-%m-%d 20:30:00")
        ),
        (
            user_id,
            "Dawn session began with clarity. Logged morning cold protocol and prepared daily vows across Mind and Physique. Ready to strike the Campaign Boss.",
            "The morning sun illuminates your path of Ascension. Maintain the sacred streak and let no distraction breach your perimeter.",
            78,
            "#morning_routine,#readiness,#ascension",
            "None",
            50,
            today.strftime("%Y-%m-%d 08:30:00")
        ),
    ]

    for log in historical_logs:
        cursor.execute("""
            INSERT INTO adventure_logs (
                user_id, journal_content, ai_gamemaster_notes, sentiment_score,
                auto_tags, detected_blockers, xp_awarded, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, log)

    # 5. Insert 8 Reliquary Items
    items = [
        (
            user_id,
            "Chronos Aegis (Streak Freeze Shield)",
            "Forged from temporal quartz. Automatically prevents streak loss if an entire calendar day passes without quest activity.",
            "SYSTEM_ARTIFACT",
            120,
            "shield",
            2
        ),
        (
            user_id,
            "Aether Elixir (Focus Incense & Tea)",
            "A ceremonial blend of high-mountain oolong and grounding agarwood incense for deep seclusion sessions.",
            "IRL_REWARD",
            60,
            "flame",
            1
        ),
        (
            user_id,
            "Nectar of Awakening (Specialty Cold Brew)",
            "Redeemable for a single-origin artisan pour-over or nitro cold brew without productivity guilt.",
            "IRL_REWARD",
            45,
            "coffee",
            4
        ),
        (
            user_id,
            "Forbidden Archives (1hr Unrestricted Gaming)",
            "A one-hour guilt-free deep dive into your favorite RPG or immersive virtual realm.",
            "IRL_REWARD",
            90,
            "gamepad-2",
            2
        ),
        (
            user_id,
            "Sanctuary Retreat (Sauna & Contrast Therapy)",
            "A restorative session of thermal contrast, infrared sauna, and nervous system replenishment.",
            "IRL_REWARD",
            250,
            "sparkles",
            1
        ),
        (
            user_id,
            "Tome of Masteries (Physical Hardcover Book)",
            "Purchase a physical masterpiece book on systems design, philosophy, or epic sci-fi.",
            "IRL_REWARD",
            180,
            "book-open",
            1
        ),
        (
            user_id,
            "Arcane Keycaps (Custom Mechanical Artisan Cap)",
            "An anodized aluminum artisan keycap embodying arcane mastery on your primary keyboard.",
            "IRL_REWARD",
            300,
            "cpu",
            0
        ),
        (
            user_id,
            "Celestial Feast (Chef's Tasting Celebration)",
            "Celebrate slaying a Tier IV Boss with a celebratory multi-course dinner with companions.",
            "IRL_REWARD",
            500,
            "utensils",
            0
        ),
    ]

    for it in items:
        cursor.execute("""
            INSERT INTO reliquary_items (
                user_id, item_name, item_description, item_type,
                gold_cost, icon_name, times_purchased
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, it)

    # 6. Insert Historical Focus Sessions across the past 12 days
    focus_history = [
        (user_id, campaign1_id, "MIND", 50, 160, 180, (today - timedelta(days=12)).strftime("%Y-%m-%d 10:00:00")),
        (user_id, campaign2_id, "HEALTH", 25, 70, 80, (today - timedelta(days=10)).strftime("%Y-%m-%d 16:30:00")),
        (user_id, campaign3_id, "CAREER", 50, 160, 180, (today - timedelta(days=8)).strftime("%Y-%m-%d 11:15:00")),
        (user_id, campaign1_id, "MIND", 50, 160, 180, (today - timedelta(days=6)).strftime("%Y-%m-%d 09:45:00")),
        (user_id, campaign2_id, "HEALTH", 25, 70, 80, (today - timedelta(days=5)).strftime("%Y-%m-%d 17:00:00")),
        (user_id, campaign1_id, "MIND", 90, 280, 320, (today - timedelta(days=3)).strftime("%Y-%m-%d 14:00:00")),
        (user_id, campaign3_id, "CAREER", 50, 160, 180, (today - timedelta(days=2)).strftime("%Y-%m-%d 10:30:00")),
        (user_id, campaign1_id, "MIND", 50, 160, 180, yesterday.strftime("%Y-%m-%d 14:00:00")),
        (user_id, campaign1_id, "MIND", 50, 160, 180, today.strftime("%Y-%m-%d 09:30:00")),
    ]
    for fs in focus_history:
        cursor.execute("""
            INSERT INTO focus_sessions (
                user_id, campaign_id, attribute_type, duration_minutes,
                xp_earned, boss_damage_dealt, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, fs)

    conn.commit()
    cursor.close()
    return user_id
