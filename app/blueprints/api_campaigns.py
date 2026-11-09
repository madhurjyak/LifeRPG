from flask import Blueprint, request, jsonify
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models import CampaignCreateRequest
from app.services.ai_gamemaster import AIGameMasterService
from app.services.game_engine import get_current_date
from app.blueprints.main import get_current_user_id

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/api/campaign', methods=['POST'])
def create_campaign():
    try:
        data = request.get_json(force=True) or {}
        req = CampaignCreateRequest(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid campaign data: {str(e)}"}), 400

    user_id = get_current_user_id()
    db = get_db()

    # Generate Boss and Splinter Quests via AI / Deterministic Fallback
    splinter = AIGameMasterService.generate_campaign_and_quests(
        goal_title=req.goal_title,
        description=req.description or "",
        difficulty_focus=req.difficulty_focus or "BALANCED"
    )

    target_date = req.target_date
    if not target_date:
        target_date = (datetime.now().date() + timedelta(days=30)).isoformat()

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO campaigns (
            user_id, title, description, ai_context,
            boss_name, boss_title, boss_max_hp, boss_current_hp,
            target_date, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, (
        user_id,
        req.goal_title,
        req.description or splinter.narrative_premise,
        splinter.narrative_premise,
        splinter.boss_name,
        splinter.boss_title,
        splinter.boss_hp,
        splinter.boss_hp,
        target_date
    ))
    campaign_id = cursor.lastrowid

    today_str = get_current_date(request)
    inserted_quests = []

    for q in splinter.quests:
        cursor.execute("""
            INSERT INTO daily_quests (
                campaign_id, user_id, task_name, attribute_type, difficulty_rank,
                xp_value, gold_value, boss_damage, is_completed, quest_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
        """, (
            campaign_id,
            user_id,
            q.task_name,
            q.attribute_type,
            q.difficulty_rank,
            q.xp_value,
            q.gold_value,
            q.boss_damage,
            today_str
        ))
        inserted_quests.append({
            'id': cursor.lastrowid,
            'campaign_id': campaign_id,
            'task_name': q.task_name,
            'attribute_type': q.attribute_type,
            'difficulty_rank': q.difficulty_rank,
            'xp_value': q.xp_value,
            'gold_value': q.gold_value,
            'boss_damage': q.boss_damage,
            'is_completed': 0,
            'quest_date': today_str
        })

    db.commit()

    return jsonify({
        "success": True,
        "message": f"Campaign forged! Boss '{splinter.boss_name}' has manifested.",
        "campaign": {
            "id": campaign_id,
            "title": req.goal_title,
            "boss_name": splinter.boss_name,
            "boss_title": splinter.boss_title,
            "boss_max_hp": splinter.boss_hp,
            "boss_current_hp": splinter.boss_hp,
            "target_date": target_date,
            "narrative_premise": splinter.narrative_premise
        },
        "quests": inserted_quests
    }), 201

@campaigns_bp.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    user_id = get_current_user_id()
    db = get_db()
    rows = db.execute("SELECT * FROM campaigns WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return jsonify({"campaigns": [dict(r) for r in rows]})
