import sqlite3
import os
from datetime import datetime, timedelta
from flask import g, current_app

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seven_ascension.db")

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
    cursor.execute("PRAGMA journal_mode=WAL;")
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

def seed_initial_data(conn):
    cursor = conn.cursor()
    
    # Check if demo user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ("PlayerOne",))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        return

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    # 1. Insert Demo User "PlayerOne"
    # Starting stats: Level 6, Phase 2, Balanced XP
    cursor.execute("""
        INSERT INTO users (
            username, total_xp, level, ascension_phase, archetype_title,
            mind_xp, health_xp, career_xp, wealth_xp, aether_gold,
            current_streak, longest_streak, streak_shields, focus_minutes_total,
            last_active_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "PlayerOne",
        1600,
        6,
        2,
        "Grand Architect",
        420,
        380,
        450,
        350,
        175,
        5,
        7,
        2,
        125,
        yesterday.isoformat()
    ))
    user_id = cursor.lastrowid

    # 2. Insert 2 Active Campaigns
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
        "Design and deploy production-grade distributed intelligence engines.",
        "Technical mastery, architectural resilience, high cognitive output.",
        "Entropy, Void of Fragmented Logic",
        "Primordial Lord of Technical Debt",
        600,
        320,
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
        "Iron Will: The Titan Conditioning",
        "Forge neuromuscular strength, metabolic flexibility, and physical endurance.",
        "Daily physical conditioning, zone 2 cardio, clean nutrition.",
        "Acedia, The Sloth Colossus",
        "Warden of Stagnation",
        500,
        410,
        campaign2_target,
        "active"
    ))
    campaign2_id = cursor.lastrowid

    # 3. Insert 6 Daily Quests for Today
    today_str = today.isoformat()
    sample_quests = [
        (
            campaign1_id, user_id,
            "Design Deep Residual Neural Architecture Diagram",
            "MIND", "A", 150, 65, 150, 0, today_str, None
        ),
        (
            campaign2_id, user_id,
            "Deadlift 3x5 at 80% 1RM & Mobility Sequence",
            "HEALTH", "B", 100, 40, 100, 0, today_str, None
        ),
        (
            campaign1_id, user_id,
            "Refactor Blueprint Routing Architecture",
            "CAREER", "C", 65, 25, 65, 0, today_str, None
        ),
        (
            None, user_id,
            "Audit Index Fund Allocation & Rebalance Portfolio",
            "WEALTH", "C", 65, 25, 65, 0, today_str, None
        ),
        (
            campaign1_id, user_id,
            "Execute 50-minute Crucible Deep Focus Module",
            "MIND", "B", 100, 40, 100, 0, today_str, None
        ),
        (
            campaign2_id, user_id,
            "Cold Shower Protocol & 10-Minute Box Breathing",
            "HEALTH", "D", 40, 15, 40, 1, today_str, datetime.now().isoformat()
        ),
    ]

    for q in sample_quests:
        cursor.execute("""
            INSERT INTO daily_quests (
                campaign_id, user_id, task_name, attribute_type, difficulty_rank,
                xp_value, gold_value, boss_damage, is_completed, quest_date, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q)

    # 4. Insert 7 Historical Journal Logs (Days -6 to Today)
    historical_logs = [
        (
            user_id,
            "Commenced the architecture blueprint for the distributed graph pipeline. Felt solid momentum in the morning, though afternoon context-switching slowed deployment.",
            "The arcane currents flow favorably, Adept. Beware the siren song of reactive multitasking—anchor your focus in the deep crucible.",
            65,
            "#deepwork,#architecture,#flowstate",
            "Context switching during afternoon standups",
            50,
            (today - timedelta(days=6)).strftime("%Y-%m-%d 20:15:00")
        ),
        (
            user_id,
            "Crushed high-intensity kettlebell conditioning and finished 2 key modules. Struggled slightly with late-night screen blue light causing insomnia.",
            "Your physical vessel hardens against the Void. Guard your nocturnal gateway with equal vigilance; rest is the foundation of astral power.",
            72,
            "#fitness,#conditioning,#discipline",
            "Late night screen exposure",
            50,
            (today - timedelta(days=5)).strftime("%Y-%m-%d 21:30:00")
        ),
        (
            user_id,
            "Felt mental friction today. Procrastinated on data schema migration due to ambiguous requirements. Eventually rallied for a 25min focus session.",
            "Ambiguity is the shroud worn by Entropy. Slice through fog with granular micro-vows. A single clean strike dissolves hesitation.",
            -15,
            "#friction,#procrastination,#schema",
            "Ambiguous technical requirements",
            50,
            (today - timedelta(days=4)).strftime("%Y-%m-%d 22:05:00")
        ),
        (
            user_id,
            "Breakthrough day. Refactored the core state machine and solved the recursive database locking issue. Energy was vibrant throughout.",
            "Triumphant insight! The weave of logic answers your command. The Campaign Boss trembles as your architecture solidifies.",
            88,
            "#breakthrough,#clean_code,#state_machine",
            "None",
            50,
            (today - timedelta(days=3)).strftime("%Y-%m-%d 19:45:00")
        ),
        (
            user_id,
            "Managed personal finances, paid tax reserves, and completed morning mobility drills. Steady and measured progress.",
            "Order across all pillars is the mark of true sovereignty. Gold flows where discipline reigns supreme.",
            60,
            "#wealth,#mobility,#order",
            "Minor fatigue from week buildup",
            50,
            (today - timedelta(days=2)).strftime("%Y-%m-%d 20:50:00")
        ),
        (
            user_id,
            "Deep focus dungeon: executed two 50-minute Crucible sessions back-to-back. The neural pipeline test suite passed with 100% coverage.",
            "You have entered the transcendent flow. The Citadel rises stone by stone beneath your disciplined hands.",
            82,
            "#crucible,#deepwork,#unit_tests",
            "None",
            50,
            yesterday.strftime("%Y-%m-%d 21:10:00")
        ),
        (
            user_id,
            "Dawn session began with clarity. Logged morning cold protocol and prepared daily quests. Ready to confront the Campaign Boss.",
            "The morning sun illuminates your path of Ascension. Maintain the sacred streak and let no distraction breach your perimeter.",
            75,
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

    # 5. Insert 5 Reliquary Items
    items = [
        (
            user_id,
            "Chronos Aegis (Streak Freeze Shield)",
            "Forged from temporal quartz. Automatically prevents streak loss if an entire calendar day passes without quest activity.",
            "SYSTEM_ARTIFACT",
            120,
            "shield",
            1
        ),
        (
            user_id,
            "Nectar of Awakening (Specialty Cold Brew)",
            "Redeemable for a single-origin artisan pour-over or nitro cold brew without productivity guilt.",
            "IRL_REWARD",
            45,
            "coffee",
            3
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
            0
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
    ]

    for it in items:
        cursor.execute("""
            INSERT INTO reliquary_items (
                user_id, item_name, item_description, item_type,
                gold_cost, icon_name, times_purchased
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, it)

    # 6. Insert initial focus sessions for historical velocity chart
    focus_history = [
        (user_id, campaign1_id, "MIND", 50, 160, 180, (today - timedelta(days=6)).strftime("%Y-%m-%d 10:00:00")),
        (user_id, campaign2_id, "HEALTH", 25, 70, 80, (today - timedelta(days=4)).strftime("%Y-%m-%d 16:30:00")),
        (user_id, campaign1_id, "MIND", 50, 160, 180, yesterday.strftime("%Y-%m-%d 14:00:00")),
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
