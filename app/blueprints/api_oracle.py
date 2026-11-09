from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database import get_db
from app.services.ai_gamemaster import AIGameMasterService
from app.blueprints.main import get_current_user_id

oracle_bp = Blueprint('oracle', __name__)

@oracle_bp.route('/api/oracle/prophecy', methods=['POST'])
def generate_prophecy():
    data = request.get_json(silent=True) or {}
    inject_quests = data.get('inject_quests', True)

    user_id = get_current_user_id()
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Summarize recent logs
    recent_logs = db.execute("""
        SELECT journal_content, sentiment_score, detected_blockers
        FROM adventure_logs
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,)).fetchall()

    logs_summary = " | ".join([
        f"Sentiment {l['sentiment_score']}: {l['journal_content'][:100]}... [Blockers: {l['detected_blockers']}]"
        for l in recent_logs
    ]) or "No recent journal reflections recorded."

    metrics = {
        'total_xp': user['total_xp'],
        'level': user['level'],
        'current_streak': user['current_streak'],
        'longest_streak': user['longest_streak'],
        'focus_minutes_total': user['focus_minutes_total'],
        'streak_shields': user['streak_shields'],
        'aether_gold': user['aether_gold']
    }

    attrs = {
        'MIND': user['mind_xp'],
        'HEALTH': user['health_xp'],
        'CAREER': user['career_xp'],
        'WEALTH': user['wealth_xp']
    }

    prophecy = AIGameMasterService.generate_oracle_prophecy(
        user_metrics=metrics,
        logs_summary=logs_summary,
        attribute_distribution=attrs
    )

    today_str = datetime.now().date().isoformat()
    injected_count = 0

    if inject_quests and prophecy.recommended_quests:
        cursor = db.cursor()
        for q in prophecy.recommended_quests:
            cursor.execute("""
                INSERT INTO daily_quests (
                    campaign_id, user_id, task_name, attribute_type, difficulty_rank,
                    xp_value, gold_value, boss_damage, is_completed, quest_date
                ) VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, 0, ?)
            """, (
                user_id,
                f"[Oracle Decree] {q.task_name}",
                q.attribute_type,
                q.difficulty_rank,
                q.xp_value,
                q.gold_value,
                q.boss_damage,
                today_str
            ))
            injected_count += 1
        db.commit()

    return jsonify({
        "success": True,
        "message": "The Oracle has spoken from the cosmic depths.",
        "prophecy": {
            "prophecy_title": prophecy.prophecy_title,
            "narrative_assessment": prophecy.narrative_assessment,
            "weakest_pillar_advice": prophecy.weakest_pillar_advice,
            "burnout_risk_level": prophecy.burnout_risk_level,
            "recommended_quests": [q.model_dump() for q in prophecy.recommended_quests]
        },
        "injected_quests_count": injected_count
    })

