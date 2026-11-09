import os
import sys
import sqlite3
import random
from datetime import date, timedelta

# Add parent directory to path so imports work cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database import init_db
from app.services.game_engine import (
    calculate_level_info,
    xp_for_level,
    get_ascension_phase
)

def run_100_day_simulation():
    print("====================================================================")
    print("STARTING 100-DAY ASCENSION SIMULATION & AGENTIC VERIFICATION SUITE")
    print("====================================================================")

    sim_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sim_100_days.db'))
    if os.path.exists(sim_db_path):
        os.remove(sim_db_path)
    for ext in ['-wal', '-shm']:
        if os.path.exists(sim_db_path + ext):
            try:
                os.remove(sim_db_path + ext)
            except OSError:
                pass

    app = create_app({
        'TESTING': True,
        'DATABASE': sim_db_path,
        'SECRET_KEY': 'sim-secret'
    })

    with app.app_context():
        init_db(db_path=sim_db_path, seed=True)

    client = app.test_client()

    start_date = date(2026, 1, 1)
    bosses_defeated = 0
    shields_used_count = 0
    quests_completed_count = 0
    focus_sessions_count = 0
    journal_entries_count = 0
    shop_purchases_count = 0

    campaign_vows = [
        ("Conquer the Distributed Systems Realm", "Master partition tolerance and consensus algorithms.", "MIND"),
        ("The Titan Hypertrophy & Kinetic Conditioning", "Forge neuromuscular strength and metabolic flexibility.", "HEALTH"),
        ("Architect Sovereign Capital Engine", "Establish high savings compounding and index distribution.", "WEALTH"),
    ]
    vow_idx = 0

    # Days with missed activity to verify Chronos Aegis shields and decay
    missed_days = {14, 28, 45, 62, 78, 92}

    print("[*] Beginning 100-Day loop with realistic human behavioral variance...")

    for day_num in range(1, 101):
        sim_date = start_date + timedelta(days=day_num - 1)
        sim_date_str = sim_date.isoformat()
        headers = {'X-Simulation-Date': sim_date_str}

        # 1. Check for missed rest day
        if day_num in missed_days:
            # User rests today; no quests logged
            continue

        # 2. Active Day: Fetch HUD
        hud_res = client.get('/api/hud', headers=headers)
        assert hud_res.status_code == 200, f"Failed HUD on day {day_num}"
        hud = hud_res.get_json()
        user = hud['user']

        # Ensure gold is never negative
        assert user['aether_gold'] >= 0, f"Day {day_num}: Gold is negative ({user['aether_gold']})"

        # 3. Check campaigns. If no active campaign and vows remain, swear a new macro vow
        active_campaigns = hud['campaigns']
        if len(active_campaigns) == 0 and vow_idx < len(campaign_vows):
            goal, desc, focus = campaign_vows[vow_idx]
            vow_idx += 1
            vow_res = client.post('/api/campaign', headers=headers, json={
                "goal_title": goal,
                "description": desc,
                "difficulty_focus": focus,
                "target_date": (sim_date + timedelta(days=30)).isoformat()
            })
            assert vow_res.status_code == 201, f"Failed campaign creation on day {day_num}"
            hud = client.get('/api/hud', headers=headers).get_json()
            active_campaigns = hud['campaigns']

        # 4. Quest completion (1 quest per active day)
        uncompleted_quests = [q for q in hud['quests'] if not q['is_completed']]
        
        # If low on uncompleted quests, inscribe a quest for today
        if not uncompleted_quests:
            target_c_id = active_campaigns[0]['id'] if active_campaigns else None
            client.post('/api/quests', headers=headers, json={
                "task_name": f"Day {day_num} Ritual: Tactical Mastery",
                "attribute_type": random.choice(["MIND", "HEALTH", "CAREER", "WEALTH"]),
                "difficulty_rank": random.choice(["D", "C", "B"]),
                "campaign_id": target_c_id
            })
            hud = client.get('/api/hud', headers=headers).get_json()
            uncompleted_quests = [q for q in hud['quests'] if not q['is_completed']]

        # Complete 1 quest
        target_q = uncompleted_quests[0]
        cq_res = client.post(f"/api/complete_quest/{target_q['id']}", headers=headers)
        assert cq_res.status_code == 200, f"Day {day_num}: complete_quest failed"
        cq_data = cq_res.get_json()
        quests_completed_count += 1

        if cq_data.get('shield_used'):
            shields_used_count += 1
            print(f"  [+] Day {day_num}: CHRONOS AEGIS TRIGGERED! Streak preserved at {cq_data.get('streak')} days.")

        if cq_data.get('boss_defeated'):
            bosses_defeated += 1
            print(f"  [!] Day {day_num}: BOSS DEFEATED! ({cq_data.get('defeated_boss_name')}) — Total Defeats: {bosses_defeated}")

        # 5. Focus Session in Crucible: Every 5-6 days
        if day_num % 5 == 0:
            active_c_id = active_campaigns[0]['id'] if active_campaigns else None
            f_res = client.post('/api/crucible/complete', headers=headers, json={
                "duration_minutes": 25,
                "attribute_type": random.choice(["MIND", "CAREER"]),
                "campaign_id": active_c_id
            })
            assert f_res.status_code == 200, f"Day {day_num}: Crucible failed"
            f_data = f_res.get_json()
            focus_sessions_count += 1
            if f_data.get('boss_defeated'):
                bosses_defeated += 1
                print(f"  [!] Day {day_num}: BOSS DEFEATED via Crucible! — Total Defeats: {bosses_defeated}")

        # 6. Grimoire Journal Reflection: Every 6 days
        if day_num % 6 == 0:
            j_res = client.post('/api/journal', headers=headers, json={
                "journal_content": f"Day {day_num} chronicle: Maintained mental clarity through afternoon deep block. Solid progress on the active campaign."
            })
            assert j_res.status_code == 201, f"Day {day_num}: Grimoire failed"
            journal_entries_count += 1

        # 7. Reliquary Economy: Keep shields stocked when gold is healthy
        hud = client.get('/api/hud', headers=headers).get_json()
        current_gold = hud['user']['aether_gold']
        current_shields = hud['user']['streak_shields']

        if current_gold >= 200 and current_shields < 2:
            shield_item = next((i for i in hud['reliquary_items'] if i['item_type'] == 'SYSTEM_ARTIFACT' or 'shield' in i['item_name'].lower()), None)
            if shield_item and current_gold >= shield_item['gold_cost']:
                buy_res = client.post(f"/api/reliquary/buy/{shield_item['id']}", headers=headers)
                assert buy_res.status_code == 200
                shop_purchases_count += 1

        # Periodic Log
        if day_num % 20 == 0:
            hud = client.get('/api/hud', headers=headers).get_json()
            u = hud['user']
            print(f"  [-] Day {day_num:3d}: Level {u['level']:2d} | Phase {u['ascension_phase']} ({hud['level_info']['ascension_title']}) | XP: {u['total_xp']:5d} | Gold: {u['aether_gold']:4d} | Bosses Slain: {bosses_defeated}")

    # ====================================================================
    # FINAL DAY 100 VERIFICATION & ASSERTIONS
    # ====================================================================
    final_hud = client.get('/api/hud', headers={'X-Simulation-Date': (start_date + timedelta(days=99)).isoformat()}).get_json()
    final_user = final_hud['user']
    final_level = final_user['level']
    final_phase = final_user['ascension_phase']
    final_gold = final_user['aether_gold']
    final_xp = final_user['total_xp']

    print("====================================================================")
    print("DAY 100 SIMULATION RESULTS:")
    print(f"  • Final Level:               {final_level}")
    print(f"  • Final Total XP:            {final_xp:,}")
    print(f"  • Final Ascension Phase:     {final_phase} ({final_hud['level_info']['ascension_title']})")
    print(f"  • Final Archetype:           {final_user['archetype_title']}")
    print(f"  • Final Aether Gold:         {final_gold}")
    print(f"  • Campaign Bosses Defeated:  {bosses_defeated}")
    print(f"  • Quests Completed:          {quests_completed_count}")
    print(f"  • Focus Sessions:            {focus_sessions_count}")
    print(f"  • Journal Entries:           {journal_entries_count}")
    print(f"  • Chronos Shields Consumed:  {shields_used_count}")
    print(f"  • Marketplace Purchases:     {shop_purchases_count}")
    print("====================================================================")

    # 1. Level between 22 and 35
    assert 22 <= final_level <= 35, f"Simulation failure: Final level {final_level} is not between 22 and 35"
    print("  [PASS] Level between 22 and 35 assertion verified.")

    # 2. Unlocks at least Ascension Phase IV (Phase >= 4)
    assert final_phase >= 4, f"Simulation failure: Final Ascension Phase {final_phase} is less than Phase IV (4)"
    print("  [PASS] Ascension Phase IV or higher assertion verified.")

    # 3. Defeats at least 3 Campaign Bosses
    assert bosses_defeated >= 3, f"Simulation failure: Defeated {bosses_defeated} bosses, expected at least 3"
    print("  [PASS] At least 3 Campaign Bosses defeated assertion verified.")

    # 4. Maintains a non-negative Gold balance
    assert final_gold >= 0, f"Simulation failure: Negative Gold balance ({final_gold})"
    print("  [PASS] Non-negative Gold balance assertion verified.")

    print("\n>>> ALL 100-DAY AGENTIC SIMULATION ASSERTIONS PASSED WITH ZERO LOCKS OR EXCEPTIONS! <<<")

    # Clean up test simulation DB
    if os.path.exists(sim_db_path):
        os.remove(sim_db_path)
    for ext in ['-wal', '-shm']:
        if os.path.exists(sim_db_path + ext):
            try:
                os.remove(sim_db_path + ext)
            except OSError:
                pass

if __name__ == '__main__':
    run_100_day_simulation()
