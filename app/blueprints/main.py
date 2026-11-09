from flask import Blueprint, render_template, jsonify, request, g
from datetime import datetime, date, timedelta
from app.database import get_db, seed_initial_data
from app.services.game_engine import (
    calculate_level_info,
    calculate_sub_level_info,
    get_ascension_phase,
    calculate_archetype_title,
    get_streak_multiplier,
    get_current_date
)

main_bp = Blueprint('main', __name__)

def get_current_user_id():
    db = get_db()
    user = db.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1").fetchone()
    if user:
        return user['id']
    # If no user exists, run full rich sample data seeding
    return seed_initial_data(db, force=True)

@main_bp.route('/')
@main_bp.route('/api')
@main_bp.route('/api/')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/api/demo/seed', methods=['POST'])
def seed_demo_realm():
    db = get_db()
    data = request.get_json(silent=True) or {}
    force = bool(data.get('force', True))
    user_id = seed_initial_data(db, force=force)
    return jsonify({
        "success": True,
        "message": "Sanctuary replenished with rich sample cultivation data!",
        "user_id": user_id
    })

@main_bp.route('/api/hud', methods=['GET'])
def get_hud():
    db = get_db()
    user_id = get_current_user_id()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    total_xp = user['total_xp']
    level_info = calculate_level_info(total_xp)

    # Sub-levels for 4 pillars
    pillar_info = {
        'MIND': calculate_sub_level_info(user['mind_xp']),
        'HEALTH': calculate_sub_level_info(user['health_xp']),
        'CAREER': calculate_sub_level_info(user['career_xp']),
        'WEALTH': calculate_sub_level_info(user['wealth_xp']),
    }

    # Dynamic archetype calculation
    archetype = calculate_archetype_title(
        user['mind_xp'], user['health_xp'], user['career_xp'], user['wealth_xp']
    )
    if archetype != user['archetype_title']:
        db.execute("UPDATE users SET archetype_title = ? WHERE id = ?", (archetype, user_id))
        db.commit()

    streak_mult = get_streak_multiplier(user['current_streak'])

    # Active Campaigns
    campaigns_rows = db.execute("""
        SELECT * FROM campaigns 
        WHERE user_id = ? AND status = 'active'
        ORDER BY id DESC
    """, (user_id,)).fetchall()
    
    campaigns = []
    for c in campaigns_rows:
        hp_pct = round((c['boss_current_hp'] / c['boss_max_hp']) * 100, 1) if c['boss_max_hp'] > 0 else 0.0
        campaigns.append({
            'id': c['id'],
            'title': c['title'],
            'description': c['description'],
            'boss_name': c['boss_name'],
            'boss_title': c['boss_title'],
            'boss_max_hp': c['boss_max_hp'],
            'boss_current_hp': c['boss_current_hp'],
            'boss_hp_pct': hp_pct,
            'target_date': c['target_date'],
            'status': c['status']
        })

    # Today's Quests (or all incomplete + today's completed)
    today_str = get_current_date(request)
    quests_rows = db.execute("""
        SELECT q.*, c.title as campaign_title, c.boss_name
        FROM daily_quests q
        LEFT JOIN campaigns c ON q.campaign_id = c.id
        WHERE q.user_id = ? AND (q.quest_date = ? OR q.is_completed = 0)
        ORDER BY q.is_completed ASC, q.id DESC
    """, (user_id, today_str)).fetchall()
    
    quests = [dict(q) for q in quests_rows]

    # Recent Grimoire Logs
    logs_rows = db.execute("""
        SELECT * FROM adventure_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (user_id,)).fetchall()
    recent_logs = [dict(l) for l in logs_rows]

    # Reliquary Items
    items_rows = db.execute("""
        SELECT * FROM reliquary_items
        WHERE user_id = ?
        ORDER BY item_type ASC, gold_cost ASC
    """, (user_id,)).fetchall()
    reliquary_items = [dict(i) for i in items_rows]

    # Oracle Telemetry (14-day velocity chart data)
    today = date.fromisoformat(today_str)
    dates_14d = [(today - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    
    # Calculate daily XP from focus sessions and completed quests
    xp_by_date = {d: 0 for d in dates_14d}
    sentiment_by_date = {d: 0 for d in dates_14d}
    sentiment_count = {d: 0 for d in dates_14d}

    # Quests XP by completion date
    completed_q = db.execute("""
        SELECT substr(completed_at, 1, 10) as c_date, SUM(xp_value) as sum_xp
        FROM daily_quests
        WHERE user_id = ? AND is_completed = 1 AND completed_at IS NOT NULL
        GROUP BY c_date
    """, (user_id,)).fetchall()
    for row in completed_q:
        if row['c_date'] in xp_by_date:
            xp_by_date[row['c_date']] += (row['sum_xp'] or 0)

    # Focus XP by completion date
    completed_f = db.execute("""
        SELECT substr(completed_at, 1, 10) as c_date, SUM(xp_earned) as sum_xp
        FROM focus_sessions
        WHERE user_id = ?
        GROUP BY c_date
    """, (user_id,)).fetchall()
    for row in completed_f:
        if row['c_date'] in xp_by_date:
            xp_by_date[row['c_date']] += (row['sum_xp'] or 0)

    # Logs sentiment by date
    logs_all = db.execute("""
        SELECT substr(created_at, 1, 10) as l_date, sentiment_score
        FROM adventure_logs
        WHERE user_id = ?
    """, (user_id,)).fetchall()
    for row in logs_all:
        ld = row['l_date']
        if ld in sentiment_by_date:
            sentiment_by_date[ld] += row['sentiment_score']
            sentiment_count[ld] += 1

    final_sentiment = []
    for d in dates_14d:
        if sentiment_count[d] > 0:
            final_sentiment.append(round(sentiment_by_date[d] / sentiment_count[d]))
        else:
            final_sentiment.append(0)

    # Blocker extraction for tag cloud
    blocker_counts = {}
    for l in recent_logs:
        raw_b = l.get('detected_blockers', '')
        if raw_b and raw_b != 'None':
            for item in raw_b.split(';'):
                item_clean = item.strip()
                if item_clean and item_clean.lower() != 'none':
                    blocker_counts[item_clean] = blocker_counts.get(item_clean, 0) + 1

    user_dict = dict(user)
    user_dict['archetype_title'] = archetype

    payload = {
        'user': user_dict,
        'level_info': level_info,
        'pillar_info': pillar_info,
        'streak_multiplier': streak_mult,
        'campaigns': campaigns,
        'quests': quests,
        'recent_logs': recent_logs,
        'reliquary_items': reliquary_items,
        'oracle': {
            'radar': {
                'labels': ['MIND', 'HEALTH', 'CAREER', 'WEALTH'],
                'values': [user['mind_xp'], user['health_xp'], user['career_xp'], user['wealth_xp']],
                'levels': [pillar_info['MIND']['sub_level'], pillar_info['HEALTH']['sub_level'], pillar_info['CAREER']['sub_level'], pillar_info['WEALTH']['sub_level']]
            },
            'velocity_14d': {
                'dates': [d[5:] for d in dates_14d], # MM-DD
                'xp': [xp_by_date[d] for d in dates_14d],
                'sentiment': final_sentiment
            },
            'top_blockers': [{'tag': k, 'count': v} for k, v in sorted(blocker_counts.items(), key=lambda x: x[1], reverse=True)[:6]]
        }
    }
    return jsonify(payload)
