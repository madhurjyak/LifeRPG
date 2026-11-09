from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database import get_db
from app.models import JournalCreateRequest
from app.services.ai_gamemaster import AIGameMasterService
from app.services.game_engine import (
    calculate_level_info,
    calculate_archetype_title,
    update_streak_for_activity,
    get_current_date
)
from app.blueprints.main import get_current_user_id

grimoire_bp = Blueprint('grimoire', __name__)

@grimoire_bp.route('/api/journal', methods=['POST'])
def submit_journal():
    try:
        data = request.get_json(force=True) or {}
        req = JournalCreateRequest(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid journal entry: {str(e)}"}), 400

    user_id = get_current_user_id()
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    today_str = get_current_date(request)

    # Recent quest summary for GM context
    recent_q = db.execute("""
        SELECT task_name, is_completed FROM daily_quests 
        WHERE user_id = ? AND quest_date = ?
    """, (user_id, today_str)).fetchall()
    q_summary = "; ".join([f"{q['task_name']} ({'Done' if q['is_completed'] else 'Pending'})" for q in recent_q]) or "No active quests logged today"

    # Analyze via AI / deterministic fallback
    analysis = AIGameMasterService.analyze_journal_entry(
        journal_text=req.journal_content,
        recent_quests_summary=q_summary,
        user_state=dict(user)
    )

    xp_reward = 50
    gold_reward = 20

    # Streak update
    new_streak, new_longest, new_shields, shield_used, streak_msg = update_streak_for_activity(
        user['current_streak'],
        user['longest_streak'],
        user['streak_shields'],
        user['last_active_date'],
        today_str
    )

    new_total_xp = user['total_xp'] + xp_reward
    new_mind_xp = user['mind_xp'] + 30
    new_career_xp = user['career_xp'] + 20
    new_gold = user['aether_gold'] + gold_reward

    lvl_info = calculate_level_info(new_total_xp)
    leveled_up = lvl_info['level'] > user['level']
    phase_advanced = lvl_info['ascension_phase'] > user['ascension_phase']
    new_archetype = calculate_archetype_title(new_mind_xp, user['health_xp'], new_career_xp, user['wealth_xp'])

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO adventure_logs (
            user_id, journal_content, ai_gamemaster_notes, sentiment_score,
            auto_tags, detected_blockers, xp_awarded, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        req.journal_content,
        analysis.ai_gamemaster_notes,
        analysis.sentiment_score,
        analysis.auto_tags,
        analysis.detected_blockers,
        xp_reward,
        now_iso
    ))
    log_id = cursor.lastrowid

    db.execute("""
        UPDATE users SET
            total_xp = ?, level = ?, ascension_phase = ?, archetype_title = ?,
            mind_xp = ?, career_xp = ?, aether_gold = ?,
            current_streak = ?, longest_streak = ?, streak_shields = ?,
            last_active_date = ?
        WHERE id = ?
    """, (
        new_total_xp,
        lvl_info['level'],
        lvl_info['ascension_phase'],
        new_archetype,
        new_mind_xp,
        new_career_xp,
        new_gold,
        new_streak,
        new_longest,
        new_shields,
        today_str,
        user_id
    ))
    db.commit()

    return jsonify({
        "success": True,
        "message": "Grimoire entry consecrated with the Game Master's blessing.",
        "log": {
            "id": log_id,
            "journal_content": req.journal_content,
            "ai_gamemaster_notes": analysis.ai_gamemaster_notes,
            "sentiment_score": analysis.sentiment_score,
            "auto_tags": analysis.auto_tags,
            "detected_blockers": analysis.detected_blockers,
            "xp_awarded": xp_reward,
            "created_at": now_iso
        },
        "xp_awarded": xp_reward,
        "gold_awarded": gold_reward,
        "streak": new_streak,
        "shield_used": shield_used,
        "streak_message": streak_msg,
        "leveled_up": leveled_up,
        "new_level": lvl_info['level'],
        "phase_advanced": phase_advanced,
        "new_phase": lvl_info['ascension_phase']
    }), 201

@grimoire_bp.route('/api/journal/history', methods=['GET'])
def get_journal_history():
    user_id = get_current_user_id()
    db = get_db()
    logs = db.execute("SELECT * FROM adventure_logs WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    return jsonify({"logs": [dict(l) for l in logs]})
