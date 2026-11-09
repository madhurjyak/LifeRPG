from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database import get_db
from app.models import QuestCreateRequest, CrucibleCompleteRequest
from app.services.game_engine import (
    DIFFICULTY_REWARDS,
    calculate_quest_rewards,
    calculate_crucible_rewards,
    calculate_level_info,
    calculate_archetype_title,
    update_streak_for_activity,
    get_current_date
)
from app.blueprints.main import get_current_user_id

quests_bp = Blueprint('quests', __name__)

@quests_bp.route('/api/quests', methods=['POST'])
def create_quest():
    try:
        data = request.get_json(force=True) or {}
        req = QuestCreateRequest(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid quest data: {str(e)}"}), 400

    user_id = get_current_user_id()
    db = get_db()
    today_str = get_current_date(request)

    rewards = DIFFICULTY_REWARDS.get(req.difficulty_rank.upper(), DIFFICULTY_REWARDS['C'])

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO daily_quests (
            campaign_id, user_id, task_name, attribute_type, difficulty_rank,
            xp_value, gold_value, boss_damage, is_completed, quest_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    """, (
        req.campaign_id,
        user_id,
        req.task_name,
        req.attribute_type,
        req.difficulty_rank,
        rewards['xp'],
        rewards['gold'],
        rewards['boss_damage'],
        today_str
    ))
    quest_id = cursor.lastrowid
    db.commit()

    return jsonify({
        "success": True,
        "quest": {
            "id": quest_id,
            "campaign_id": req.campaign_id,
            "task_name": req.task_name,
            "attribute_type": req.attribute_type,
            "difficulty_rank": req.difficulty_rank,
            "xp_value": rewards['xp'],
            "gold_value": rewards['gold'],
            "boss_damage": rewards['boss_damage'],
            "is_completed": 0,
            "quest_date": today_str
        }
    }), 201

@quests_bp.route('/api/complete_quest/<int:quest_id>', methods=['POST'])
def complete_quest(quest_id):
    user_id = get_current_user_id()
    db = get_db()

    quest = db.execute("SELECT * FROM daily_quests WHERE id = ? AND user_id = ?", (quest_id, user_id)).fetchone()
    if not quest:
        return jsonify({"error": "Quest not found"}), 404

    if quest['is_completed'] == 1:
        return jsonify({
            "success": True,
            "message": "Quest was already marked complete.",
            "already_completed": True
        })

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    today_str = get_current_date(request)

    # Calculate base and streak-multiplied rewards
    rewards = calculate_quest_rewards(quest['difficulty_rank'], user['current_streak'])
    earned_xp = rewards['final_xp']
    earned_gold = rewards['gold']
    boss_dmg = rewards['boss_damage']

    # Update streak
    new_streak, new_longest, new_shields, shield_used, streak_msg = update_streak_for_activity(
        user['current_streak'],
        user['longest_streak'],
        user['streak_shields'],
        user['last_active_date'],
        today_str
    )

    # Process Boss Damage
    target_campaign_id = quest['campaign_id']
    if not target_campaign_id:
        # Pick the oldest active campaign
        act_c = db.execute(
            "SELECT id FROM campaigns WHERE user_id = ? AND status = 'active' ORDER BY id ASC LIMIT 1",
            (user_id,)
        ).fetchone()
        if act_c:
            target_campaign_id = act_c['id']

    boss_defeated = False
    defeated_boss_name = None
    if target_campaign_id:
        campaign = db.execute("SELECT * FROM campaigns WHERE id = ? AND user_id = ?", (target_campaign_id, user_id)).fetchone()
        if campaign and campaign['status'] == 'active':
            new_boss_hp = max(0, campaign['boss_current_hp'] - boss_dmg)
            if new_boss_hp == 0 and campaign['boss_current_hp'] > 0:
                boss_defeated = True
                defeated_boss_name = campaign['boss_name']
                # Defeat bonus: +500 XP, +200 Gold
                earned_xp += 500
                earned_gold += 200
                db.execute("UPDATE campaigns SET boss_current_hp = 0, status = 'conquered' WHERE id = ?", (target_campaign_id,))
            else:
                db.execute("UPDATE campaigns SET boss_current_hp = ? WHERE id = ?", (new_boss_hp, target_campaign_id))

    # Attribute XP allocation
    attr_type = quest['attribute_type']
    new_mind_xp = user['mind_xp'] + (earned_xp if attr_type == 'MIND' else 0)
    new_health_xp = user['health_xp'] + (earned_xp if attr_type == 'HEALTH' else 0)
    new_career_xp = user['career_xp'] + (earned_xp if attr_type == 'CAREER' else 0)
    new_wealth_xp = user['wealth_xp'] + (earned_xp if attr_type == 'WEALTH' else 0)

    new_total_xp = user['total_xp'] + earned_xp
    new_gold = user['aether_gold'] + earned_gold

    # Level, Ascension Phase & Archetype
    lvl_info = calculate_level_info(new_total_xp)
    leveled_up = lvl_info['level'] > user['level']
    phase_advanced = lvl_info['ascension_phase'] > user['ascension_phase']
    new_archetype = calculate_archetype_title(new_mind_xp, new_health_xp, new_career_xp, new_wealth_xp)

    # Update quest
    now_iso = datetime.now().isoformat()
    db.execute("UPDATE daily_quests SET is_completed = 1, completed_at = ? WHERE id = ?", (now_iso, quest_id))

    # Update user
    db.execute("""
        UPDATE users SET
            total_xp = ?, level = ?, ascension_phase = ?, archetype_title = ?,
            mind_xp = ?, health_xp = ?, career_xp = ?, wealth_xp = ?,
            aether_gold = ?, current_streak = ?, longest_streak = ?,
            streak_shields = ?, last_active_date = ?
        WHERE id = ?
    """, (
        new_total_xp,
        lvl_info['level'],
        lvl_info['ascension_phase'],
        new_archetype,
        new_mind_xp,
        new_health_xp,
        new_career_xp,
        new_wealth_xp,
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
        "quest_id": quest_id,
        "xp_gained": earned_xp,
        "gold_gained": earned_gold,
        "boss_damage_dealt": boss_dmg,
        "streak": new_streak,
        "shield_used": shield_used,
        "streak_message": streak_msg,
        "leveled_up": leveled_up,
        "new_level": lvl_info['level'],
        "phase_advanced": phase_advanced,
        "new_phase": lvl_info['ascension_phase'],
        "boss_defeated": boss_defeated,
        "defeated_boss_name": defeated_boss_name,
        "user": {
            "total_xp": new_total_xp,
            "level": lvl_info['level'],
            "ascension_phase": lvl_info['ascension_phase'],
            "archetype_title": new_archetype,
            "aether_gold": new_gold,
            "current_streak": new_streak,
            "streak_shields": new_shields
        }
    })

@quests_bp.route('/api/crucible/complete', methods=['POST'])
def complete_crucible():
    try:
        data = request.get_json(force=True) or {}
        req = CrucibleCompleteRequest(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid Crucible session: {str(e)}"}), 400

    user_id = get_current_user_id()
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    today_str = get_current_date(request)

    rewards = calculate_crucible_rewards(req.duration_minutes, user['current_streak'])
    earned_xp = rewards['final_xp']
    earned_gold = rewards['gold']
    boss_dmg = rewards['boss_damage']

    # Update streak
    new_streak, new_longest, new_shields, shield_used, streak_msg = update_streak_for_activity(
        user['current_streak'],
        user['longest_streak'],
        user['streak_shields'],
        user['last_active_date'],
        today_str
    )

    # Boss strike
    target_campaign_id = req.campaign_id
    if not target_campaign_id:
        act_c = db.execute(
            "SELECT id FROM campaigns WHERE user_id = ? AND status = 'active' ORDER BY id ASC LIMIT 1",
            (user_id,)
        ).fetchone()
        if act_c:
            target_campaign_id = act_c['id']

    boss_defeated = False
    defeated_boss_name = None
    if target_campaign_id:
        campaign = db.execute("SELECT * FROM campaigns WHERE id = ? AND user_id = ?", (target_campaign_id, user_id)).fetchone()
        if campaign and campaign['status'] == 'active':
            new_boss_hp = max(0, campaign['boss_current_hp'] - boss_dmg)
            if new_boss_hp == 0 and campaign['boss_current_hp'] > 0:
                boss_defeated = True
                defeated_boss_name = campaign['boss_name']
                earned_xp += 500
                earned_gold += 200
                db.execute("UPDATE campaigns SET boss_current_hp = 0, status = 'conquered' WHERE id = ?", (target_campaign_id,))
            else:
                db.execute("UPDATE campaigns SET boss_current_hp = ? WHERE id = ?", (new_boss_hp, target_campaign_id))

    # Focus gives primary XP to chosen attribute (MIND or CAREER)
    attr_type = req.attribute_type
    new_mind_xp = user['mind_xp'] + (earned_xp if attr_type == 'MIND' else 0)
    new_health_xp = user['health_xp'] + (earned_xp if attr_type == 'HEALTH' else 0)
    new_career_xp = user['career_xp'] + (earned_xp if attr_type == 'CAREER' else 0)
    new_wealth_xp = user['wealth_xp'] + (earned_xp if attr_type == 'WEALTH' else 0)

    new_total_xp = user['total_xp'] + earned_xp
    new_gold = user['aether_gold'] + earned_gold
    new_focus_min = user['focus_minutes_total'] + req.duration_minutes

    lvl_info = calculate_level_info(new_total_xp)
    leveled_up = lvl_info['level'] > user['level']
    phase_advanced = lvl_info['ascension_phase'] > user['ascension_phase']
    new_archetype = calculate_archetype_title(new_mind_xp, new_health_xp, new_career_xp, new_wealth_xp)

    now_iso = datetime.now().isoformat()
    db.execute("""
        INSERT INTO focus_sessions (
            user_id, campaign_id, attribute_type, duration_minutes,
            xp_earned, boss_damage_dealt, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        target_campaign_id,
        attr_type,
        req.duration_minutes,
        earned_xp,
        boss_dmg,
        now_iso
    ))

    db.execute("""
        UPDATE users SET
            total_xp = ?, level = ?, ascension_phase = ?, archetype_title = ?,
            mind_xp = ?, health_xp = ?, career_xp = ?, wealth_xp = ?,
            aether_gold = ?, current_streak = ?, longest_streak = ?,
            streak_shields = ?, focus_minutes_total = ?, last_active_date = ?
        WHERE id = ?
    """, (
        new_total_xp,
        lvl_info['level'],
        lvl_info['ascension_phase'],
        new_archetype,
        new_mind_xp,
        new_health_xp,
        new_career_xp,
        new_wealth_xp,
        new_gold,
        new_streak,
        new_longest,
        new_shields,
        new_focus_min,
        today_str,
        user_id
    ))
    db.commit()

    return jsonify({
        "success": True,
        "message": f"Crucible Focus Chamber survived! {req.duration_minutes} minutes logged.",
        "duration_minutes": req.duration_minutes,
        "xp_gained": earned_xp,
        "gold_gained": earned_gold,
        "boss_damage_dealt": boss_dmg,
        "streak": new_streak,
        "shield_used": shield_used,
        "streak_message": streak_msg,
        "leveled_up": leveled_up,
        "new_level": lvl_info['level'],
        "phase_advanced": phase_advanced,
        "new_phase": lvl_info['ascension_phase'],
        "boss_defeated": boss_defeated,
        "defeated_boss_name": defeated_boss_name,
        "user": {
            "total_xp": new_total_xp,
            "level": lvl_info['level'],
            "ascension_phase": lvl_info['ascension_phase'],
            "archetype_title": new_archetype,
            "aether_gold": new_gold,
            "focus_minutes_total": new_focus_min,
            "current_streak": new_streak
        }
    })
