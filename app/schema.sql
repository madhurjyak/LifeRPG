-- The Seven-Phase Ascension Relational Database Schema
-- SQLite3 with WAL mode and Foreign Keys enforced

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    ascension_phase INTEGER DEFAULT 1,
    archetype_title TEXT DEFAULT 'Novice Seeker',
    mind_xp INTEGER DEFAULT 0,
    health_xp INTEGER DEFAULT 0,
    career_xp INTEGER DEFAULT 0,
    wealth_xp INTEGER DEFAULT 0,
    aether_gold INTEGER DEFAULT 100,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    streak_shields INTEGER DEFAULT 1,
    focus_minutes_total INTEGER DEFAULT 0,
    last_active_date TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    ai_context TEXT,
    boss_name TEXT NOT NULL,
    boss_title TEXT NOT NULL,
    boss_max_hp INTEGER NOT NULL DEFAULT 500,
    boss_current_hp INTEGER NOT NULL DEFAULT 500,
    target_date TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'conquered', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    user_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    attribute_type TEXT NOT NULL CHECK(attribute_type IN ('MIND', 'HEALTH', 'CAREER', 'WEALTH')),
    difficulty_rank TEXT NOT NULL DEFAULT 'C' CHECK(difficulty_rank IN ('E', 'D', 'C', 'B', 'A', 'S')),
    xp_value INTEGER NOT NULL,
    gold_value INTEGER NOT NULL DEFAULT 15,
    boss_damage INTEGER NOT NULL DEFAULT 50,
    is_completed INTEGER DEFAULT 0,
    quest_date TEXT NOT NULL,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS adventure_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    journal_content TEXT NOT NULL,
    ai_gamemaster_notes TEXT NOT NULL,
    sentiment_score INTEGER NOT NULL,
    auto_tags TEXT NOT NULL,
    detected_blockers TEXT DEFAULT '',
    xp_awarded INTEGER DEFAULT 50,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reliquary_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    item_description TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK(item_type IN ('IRL_REWARD', 'SYSTEM_ARTIFACT')),
    gold_cost INTEGER NOT NULL,
    icon_name TEXT DEFAULT 'sparkles',
    times_purchased INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    campaign_id INTEGER,
    attribute_type TEXT NOT NULL DEFAULT 'MIND' CHECK(attribute_type IN ('MIND', 'HEALTH', 'CAREER', 'WEALTH')),
    duration_minutes INTEGER NOT NULL,
    xp_earned INTEGER NOT NULL,
    boss_damage_dealt INTEGER NOT NULL,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

-- Optimization indexes
CREATE INDEX IF NOT EXISTS idx_quests_user_date ON daily_quests(user_id, quest_date);
CREATE INDEX IF NOT EXISTS idx_campaigns_user_status ON campaigns(user_id, status);
CREATE INDEX IF NOT EXISTS idx_logs_user ON adventure_logs(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_focus_user ON focus_sessions(user_id, completed_at);

