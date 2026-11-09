from flask import Blueprint, request, jsonify
from app.database import get_db
from app.models import ReliquaryItemCreateRequest
from app.blueprints.main import get_current_user_id

reliquary_bp = Blueprint('reliquary', __name__)

@reliquary_bp.route('/api/reliquary/buy/<int:item_id>', methods=['POST'])
def buy_item(item_id):
    user_id = get_current_user_id()
    db = get_db()

    item = db.execute("SELECT * FROM reliquary_items WHERE id = ? AND user_id = ?", (item_id, user_id)).fetchone()
    if not item:
        return jsonify({"error": "Reliquary item not found"}), 404

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user['aether_gold'] < item['gold_cost']:
        return jsonify({
            "error": f"Insufficient Aether Gold. You possess {user['aether_gold']} Gold, but {item['item_name']} requires {item['gold_cost']} Gold."
        }), 400

    new_gold = user['aether_gold'] - item['gold_cost']
    new_shields = user['streak_shields']

    # If it's a shield or system artifact
    is_shield = (item['item_type'] == 'SYSTEM_ARTIFACT') or ("shield" in item['item_name'].lower()) or ("chronos aegis" in item['item_name'].lower())
    if is_shield:
        new_shields += 1

    db.execute("UPDATE reliquary_items SET times_purchased = times_purchased + 1 WHERE id = ?", (item_id,))
    db.execute("UPDATE users SET aether_gold = ?, streak_shields = ? WHERE id = ?", (new_gold, new_shields, user_id))
    db.commit()

    msg = f"Acquired '{item['item_name']}'!"
    if is_shield:
        msg += f" Streak shields increased to {new_shields}."

    return jsonify({
        "success": True,
        "message": msg,
        "item": {
            "id": item['id'],
            "item_name": item['item_name'],
            "item_type": item['item_type'],
            "times_purchased": item['times_purchased'] + 1
        },
        "remaining_gold": new_gold,
        "streak_shields": new_shields
    })

@reliquary_bp.route('/api/reliquary/create', methods=['POST'])
def create_custom_reward():
    try:
        data = request.get_json(force=True) or {}
        req = ReliquaryItemCreateRequest(**data)
    except Exception as e:
        return jsonify({"error": f"Invalid item specification: {str(e)}"}), 400

    user_id = get_current_user_id()
    db = get_db()

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO reliquary_items (
            user_id, item_name, item_description, item_type,
            gold_cost, icon_name, times_purchased
        ) VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (
        user_id,
        req.item_name,
        req.item_description,
        req.item_type,
        req.gold_cost,
        req.icon_name
    ))
    item_id = cursor.lastrowid
    db.commit()

    return jsonify({
        "success": True,
        "message": f"Custom relic '{req.item_name}' forged in the Reliquary.",
        "item": {
            "id": item_id,
            "item_name": req.item_name,
            "item_description": req.item_description,
            "item_type": req.item_type,
            "gold_cost": req.gold_cost,
            "icon_name": req.icon_name,
            "times_purchased": 0
        }
    }), 201

@reliquary_bp.route('/api/reliquary/items', methods=['GET'])
def list_items():
    user_id = get_current_user_id()
    db = get_db()
    items = db.execute("SELECT * FROM reliquary_items WHERE user_id = ? ORDER BY gold_cost ASC", (user_id,)).fetchall()
    return jsonify({"items": [dict(i) for i in items]})

