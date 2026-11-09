import os
import pytest
import tempfile
from app import create_app
from app.database import init_db
from app.services.game_engine import (
    xp_for_level,
    calculate_level_info,
    calculate_sub_level_info,
    calculate_archetype_title,
    update_streak_for_activity,
    get_ascension_phase
)

@pytest.fixture
def client():
    # Use a clean temporary SQLite database for test suite
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret'
    })

    with app.app_context():
        init_db(db_path=db_path, seed=True)

    with app.test_client() as test_client:
        yield test_client

    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)
    # Also clean up WAL and SHM if present
    for ext in ['-wal', '-shm']:
        if os.path.exists(db_path + ext):
            try:
                os.remove(db_path + ext)
            except OSError:
                pass

# ====================================================================
# 1. RPG MATHEMATICS & GAME ENGINE UNIT TESTS
# ====================================================================

def test_xp_formula_and_level_calculation():
    # Level 1 is 0 XP
    assert xp_for_level(1) == 0
    # Level 2: 100 * (1 ** 1.5) = 100 XP
    assert xp_for_level(2) == 100
    # Level 5: 100 * (4 ** 1.5) = 800 XP
    assert xp_for_level(5) == 800
    # Level 10: 100 * (9 ** 1.5) = 2700 XP
    assert xp_for_level(10) == 2700

    info_lvl1 = calculate_level_info(0)
    assert info_lvl1['level'] == 1
    assert info_lvl1['ascension_phase'] == 1

    info_lvl5 = calculate_level_info(850)
    assert info_lvl5['level'] == 5
    assert info_lvl5['ascension_phase'] == 2

    info_lvl20 = calculate_level_info(8500)
    assert info_lvl20['level'] >= 20
    assert info_lvl20['ascension_phase'] == 4 # Phase IV: Astral Vanguard

def test_ascension_phase_tiers():
    assert get_ascension_phase(1)['phase_number'] == 1
    assert get_ascension_phase(4)['phase_number'] == 1
    assert get_ascension_phase(5)['phase_number'] == 2
    assert get_ascension_phase(9)['phase_number'] == 2
    assert get_ascension_phase(10)['phase_number'] == 3
    assert get_ascension_phase(16)['phase_number'] == 3
    assert get_ascension_phase(17)['phase_number'] == 4
    assert get_ascension_phase(24)['phase_number'] == 4
    assert get_ascension_phase(25)['phase_number'] == 5
    assert get_ascension_phase(34)['phase_number'] == 5
    assert get_ascension_phase(35)['phase_number'] == 6
    assert get_ascension_phase(49)['phase_number'] == 6
    assert get_ascension_phase(50)['phase_number'] == 7

def test_archetype_titles():
    # Pure titles
    assert calculate_archetype_title(500, 100, 100, 100) == "Astral Savant"
    assert calculate_archetype_title(100, 500, 100, 100) == "Titan Vanguard"
    assert calculate_archetype_title(100, 100, 500, 100) == "Grand Architect"
    assert calculate_archetype_title(100, 100, 100, 500) == "Sovereign Alchemist"
    
    # Hybrid titles (within 10% difference)
    # MIND (500) & CAREER (480) -> difference is 20/500 = 4% <= 10%
    assert calculate_archetype_title(500, 50, 480, 50) == "Arcane Architect"
    # HEALTH (500) & CAREER (490) -> Iron Forgemaster
    assert calculate_archetype_title(50, 500, 490, 50) == "Iron Forgemaster"
    # CAREER (500) & WEALTH (475) -> Empire Magnate
    assert calculate_archetype_title(50, 50, 500, 475) == "Empire Magnate"

def test_streak_and_shield_logic():
    # Day 1 start
    streak, longest, shields, used, _ = update_streak_for_activity(0, 0, 1, None, "2026-11-01")
    assert streak == 1
    assert longest == 1

    # Consecutive next day
    streak, longest, shields, used, _ = update_streak_for_activity(1, 1, 1, "2026-11-01", "2026-11-02")
    assert streak == 2
    assert longest == 2
    assert not used

    # Missed day WITH shield: 2026-11-02 to 2026-11-04 (gap of 2 days)
    streak, longest, shields, used, msg = update_streak_for_activity(2, 2, 1, "2026-11-02", "2026-11-04")
    assert used is True
    assert shields == 0
    assert streak == 3 # Streak preserved and incremented!
    assert "Chronos Aegis" in msg

    # Missed day WITHOUT shield: 2026-11-04 to 2026-11-07 (gap of 3 days, 0 shields left)
    streak, longest, shields, used, _ = update_streak_for_activity(3, 3, 0, "2026-11-04", "2026-11-07")
    assert used is False
    assert streak == 1 # Reset to 1
    assert longest == 3

# ====================================================================
# 2. REST API INTEGRATION TESTS
# ====================================================================

def test_dashboard_renders(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"The Seven-Phase Ascension" in res.data

def test_api_hud(client):
    res = client.get('/api/hud')
    assert res.status_code == 200
    data = res.get_json()
    assert 'user' in data
    assert 'level_info' in data
    assert 'pillar_info' in data
    assert 'campaigns' in data
    assert 'quests' in data
    assert 'recent_logs' in data
    assert 'reliquary_items' in data
    assert 'oracle' in data
    assert data['user']['username'] == "PlayerOne"
    assert len(data['campaigns']) >= 2
    assert len(data['quests']) >= 6

def test_api_campaign_creation(client):
    res = client.post('/api/campaign', json={
        "goal_title": "Pass AWS Solutions Architect Professional Exam",
        "description": "Master distributed VPC peering, DynamoDB global tables, and IAM policies.",
        "difficulty_focus": "MIND",
        "target_date": "2026-12-31"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert 'campaign' in data
    assert data['campaign']['boss_name'] is not None
    assert data['campaign']['boss_max_hp'] >= 450
    assert len(data['quests']) >= 5

def test_api_quest_completion(client):
    hud = client.get('/api/hud').get_json()
    uncompleted = [q for q in hud['quests'] if not q['is_completed']]
    assert len(uncompleted) > 0
    target_quest = uncompleted[0]

    initial_xp = hud['user']['total_xp']
    initial_gold = hud['user']['aether_gold']

    res = client.post(f"/api/complete_quest/{target_quest['id']}")
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['xp_gained'] > 0
    assert data['gold_gained'] > 0
    assert data['boss_damage_dealt'] > 0
    assert data['user']['total_xp'] > initial_xp
    assert data['user']['aether_gold'] > initial_gold

    # Verify idempotency
    res2 = client.post(f"/api/complete_quest/{target_quest['id']}")
    assert res2.status_code == 200
    assert res2.get_json()['already_completed'] is True

def test_api_crucible_completion(client):
    hud = client.get('/api/hud').get_json()
    campaign_id = hud['campaigns'][0]['id']
    initial_focus = hud['user']['focus_minutes_total']

    res = client.post('/api/crucible/complete', json={
        "duration_minutes": 50,
        "attribute_type": "MIND",
        "campaign_id": campaign_id
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['duration_minutes'] == 50
    assert data['xp_gained'] >= 160
    assert data['boss_damage_dealt'] >= 180
    assert data['user']['focus_minutes_total'] == initial_focus + 50

def test_api_journal_submission(client):
    res = client.post('/api/journal', json={
        "journal_content": "Crushed 2 full modules today with zero distractions. Encountered slight friction with API rate limits but solved it via caching."
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['xp_awarded'] == 50
    assert 'log' in data
    assert 'ai_gamemaster_notes' in data['log']
    assert -100 <= data['log']['sentiment_score'] <= 100
    assert len(data['log']['auto_tags']) > 0

def test_api_reliquary_item_flow(client):
    # 1. Create custom item
    create_res = client.post('/api/reliquary/create', json={
        "item_name": "Specialty Nitro Cold Brew",
        "item_description": "Single-origin Ethiopian roast after completing 3 daily quests.",
        "gold_cost": 30,
        "icon_name": "coffee",
        "item_type": "IRL_REWARD"
    })
    assert create_res.status_code == 201
    new_item = create_res.get_json()['item']
    item_id = new_item['id']

    # 2. Buy custom item
    buy_res = client.post(f"/api/reliquary/buy/{item_id}")
    assert buy_res.status_code == 200
    buy_data = buy_res.get_json()
    assert buy_data['success'] is True
    assert buy_data['item']['times_purchased'] == 1

    # 3. Buy Chronos Aegis Shield and check shields increment
    hud = client.get('/api/hud').get_json()
    shield_item = next(i for i in hud['reliquary_items'] if i['item_type'] == 'SYSTEM_ARTIFACT' or 'shield' in i['item_name'].lower())
    init_shields = hud['user']['streak_shields']

    # Ensure user has enough gold
    client.post('/api/crucible/complete', json={"duration_minutes": 90, "attribute_type": "MIND"})
    
    shield_buy_res = client.post(f"/api/reliquary/buy/{shield_item['id']}")
    assert shield_buy_res.status_code == 200
    assert shield_buy_res.get_json()['streak_shields'] == init_shields + 1

def test_api_oracle_prophecy(client):
    res = client.post('/api/oracle/prophecy', json={"inject_quests": True})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'prophecy' in data
    assert 'prophecy_title' in data['prophecy']
    assert data['prophecy']['burnout_risk_level'] in ('LOW', 'MODERATE', 'HIGH')
    assert data['injected_quests_count'] >= 1

