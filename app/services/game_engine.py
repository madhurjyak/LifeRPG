from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional

def get_current_date(req=None) -> str:
    """Returns ISO date string, respecting optional X-Simulation-Date header."""
    if req and hasattr(req, 'headers'):
        sim_date = req.headers.get('X-Simulation-Date')
        if sim_date:
            return sim_date
    return datetime.now().date().isoformat()

DIFFICULTY_REWARDS = {
    'E': {'xp': 25, 'gold': 10, 'boss_damage': 25},
    'D': {'xp': 40, 'gold': 15, 'boss_damage': 40},
    'C': {'xp': 65, 'gold': 25, 'boss_damage': 65},
    'B': {'xp': 100, 'gold': 40, 'boss_damage': 100},
    'A': {'xp': 150, 'gold': 65, 'boss_damage': 150},
    'S': {'xp': 250, 'gold': 100, 'boss_damage': 250},
}

ASCENSION_PHASES = [
    (1, 4, 1, "Phase I: The Dormant Initiate", "Dormant Initiate", "I"),
    (5, 9, 2, "Phase II: The Awakened Seeker", "Awakened Seeker", "II"),
    (10, 16, 3, "Phase III: The Crucible Adept", "Crucible Adept", "III"),
    (17, 24, 4, "Phase IV: The Astral Vanguard", "Astral Vanguard", "IV"),
    (25, 34, 5, "Phase V: The Grand Sovereign", "Grand Sovereign", "V"),
    (35, 49, 6, "Phase VI: The Eternal Paragon", "Eternal Paragon", "VI"),
    (50, 999999, 7, "Phase VII: The Transcendent Ascendant", "Transcendent Ascendant", "VII"),
]

def xp_for_level(lvl: int) -> int:
    """Total XP required to reach Level L: int(100 * ((L - 1) ** 1.5))"""
    if lvl <= 1:
        return 0
    return int(100 * ((lvl - 1) ** 1.5))

def calculate_level_info(total_xp: int) -> Dict[str, Any]:
    """Dynamically compute level, XP progress, and thresholds from total_xp."""
    if total_xp < 0:
        total_xp = 0
    
    lvl = 1
    while xp_for_level(lvl + 1) <= total_xp:
        lvl += 1

    base_xp = xp_for_level(lvl)
    next_level_xp = xp_for_level(lvl + 1)
    current_level_xp = total_xp - base_xp
    xp_needed_for_next = next_level_xp - base_xp
    
    if xp_needed_for_next > 0:
        level_progress_pct = round((current_level_xp / xp_needed_for_next) * 100, 1)
    else:
        level_progress_pct = 100.0

    ascension_info = get_ascension_phase(lvl)

    return {
        'level': lvl,
        'total_xp': total_xp,
        'base_xp': base_xp,
        'current_level_xp': current_level_xp,
        'next_level_xp': next_level_xp,
        'xp_to_next_level': max(0, next_level_xp - total_xp),
        'level_progress_pct': min(100.0, max(0.0, level_progress_pct)),
        'ascension_phase': ascension_info['phase_number'],
        'ascension_title': ascension_info['phase_title'],
        'ascension_roman': ascension_info['roman_numeral'],
    }

def xp_for_sub_level(sub_lvl: int) -> int:
    """Sub-level XP threshold formula: int(50 * ((sub_L - 1) ** 1.4))"""
    if sub_lvl <= 1:
        return 0
    return int(50 * ((sub_lvl - 1) ** 1.4))

def calculate_sub_level_info(attr_xp: int) -> Dict[str, Any]:
    """Compute attribute sub-level and progress."""
    if attr_xp < 0:
        attr_xp = 0
        
    sub_l = 1
    while xp_for_sub_level(sub_l + 1) <= attr_xp:
        sub_l += 1

    base_xp = xp_for_sub_level(sub_l)
    next_xp = xp_for_sub_level(sub_l + 1)
    current_xp = attr_xp - base_xp
    xp_needed = next_xp - base_xp
    progress_pct = round((current_xp / xp_needed) * 100, 1) if xp_needed > 0 else 100.0

    return {
        'sub_level': sub_l,
        'attr_xp': attr_xp,
        'current_xp': current_xp,
        'next_level_xp': next_xp,
        'xp_to_next': max(0, next_xp - attr_xp),
        'progress_pct': min(100.0, max(0.0, progress_pct)),
    }

def get_ascension_phase(level: int) -> Dict[str, Any]:
    """Maps player level to one of the 7 Ascension Phases."""
    for min_lvl, max_lvl, phase_num, title, short_title, roman in ASCENSION_PHASES:
        if min_lvl <= level <= max_lvl:
            return {
                'phase_number': phase_num,
                'phase_title': title,
                'short_title': short_title,
                'roman_numeral': roman,
                'min_level': min_lvl,
                'max_level': max_lvl
            }
    # Fallback for beyond max
    return {
        'phase_number': 7,
        'phase_title': "Phase VII: The Transcendent Ascendant",
        'short_title': "Transcendent Ascendant",
        'roman_numeral': "VII",
        'min_level': 50,
        'max_level': 999999
    }

def calculate_archetype_title(mind_xp: int, health_xp: int, career_xp: int, wealth_xp: int) -> str:
    """Calculates dynamic Archetype Title based on highest attribute XP or hybrid pairing."""
    pillars = [
        ('MIND', mind_xp),
        ('HEALTH', health_xp),
        ('CAREER', career_xp),
        ('WEALTH', wealth_xp)
    ]
    # Sort descending by XP
    pillars.sort(key=lambda x: x[1], reverse=True)
    
    top_attr, top_val = pillars[0]
    second_attr, second_val = pillars[1]

    if top_val == 0:
        return "Novice Seeker"

    # Hybrid check: within 10% of each other
    if top_val > 0 and ((top_val - second_val) / top_val) <= 0.10:
        pair = frozenset([top_attr, second_attr])
        hybrid_map = {
            frozenset(['MIND', 'CAREER']): "Arcane Architect",
            frozenset(['MIND', 'HEALTH']): "Psionic Juggernaut",
            frozenset(['MIND', 'WEALTH']): "Mystic Merchant",
            frozenset(['HEALTH', 'CAREER']): "Iron Forgemaster",
            frozenset(['HEALTH', 'WEALTH']): "Dread Tyrant",
            frozenset(['CAREER', 'WEALTH']): "Empire Magnate",
        }
        if pair in hybrid_map:
            return hybrid_map[pair]

    # Pure archetype map
    pure_map = {
        'MIND': "Astral Savant",
        'HEALTH': "Titan Vanguard",
        'CAREER': "Grand Architect",
        'WEALTH': "Sovereign Alchemist"
    }
    return pure_map.get(top_attr, "Novice Seeker")

def get_streak_multiplier(current_streak: int) -> float:
    """Each consecutive active day adds +5% bonus XP (capped at +50% at 10+ days)."""
    bonus = min(0.50, max(0.0, current_streak * 0.05))
    return round(1.0 + bonus, 2)

def calculate_quest_rewards(difficulty_rank: str, current_streak: int) -> Dict[str, int]:
    """Calculates XP (with streak multiplier), Gold, and Boss Damage for a quest rank."""
    base = DIFFICULTY_REWARDS.get(difficulty_rank.upper(), DIFFICULTY_REWARDS['C'])
    multiplier = get_streak_multiplier(current_streak)
    final_xp = int(round(base['xp'] * multiplier))
    return {
        'base_xp': base['xp'],
        'final_xp': final_xp,
        'gold': base['gold'],
        'boss_damage': base['boss_damage'],
        'multiplier': multiplier
    }

def calculate_crucible_rewards(duration_minutes: int, current_streak: int) -> Dict[str, int]:
    """Calculates rewards and boss damage for Pomodoro Crucible deep work."""
    multiplier = get_streak_multiplier(current_streak)
    if duration_minutes == 25:
        base_xp, gold, dmg = 70, 30, 80
    elif duration_minutes == 50:
        base_xp, gold, dmg = 160, 70, 180
    elif duration_minutes == 90:
        base_xp, gold, dmg = 320, 140, 360
    else:
        base_xp = int(duration_minutes * 3.2)
        gold = int(duration_minutes * 1.4)
        dmg = int(duration_minutes * 3.6)

    final_xp = int(round(base_xp * multiplier))
    return {
        'base_xp': base_xp,
        'final_xp': final_xp,
        'gold': gold,
        'boss_damage': dmg,
        'multiplier': multiplier
    }

def update_streak_for_activity(
    current_streak: int,
    longest_streak: int,
    streak_shields: int,
    last_active_date_str: Optional[str],
    activity_date_str: str
) -> Tuple[int, int, int, bool, str]:
    """
    Updates user streak based on activity date:
    - Same day: streak unchanged.
    - Yesterday (+1 day): streak increments by 1.
    - >1 day gap:
        - If shields > 0: shield consumed, streak preserved + 1 for today!
        - Else: streak resets to 1.
    Returns: (new_current, new_longest, new_shields, shield_used, message)
    """
    today_act = date.fromisoformat(activity_date_str)
    
    if not last_active_date_str:
        return 1, max(longest_streak, 1), streak_shields, False, "Streak ignited! Day 1 complete."

    last_act = date.fromisoformat(last_active_date_str)
    day_diff = (today_act - last_act).days

    if day_diff == 0:
        return current_streak, longest_streak, streak_shields, False, "Activity recorded for today."
    elif day_diff == 1:
        new_curr = current_streak + 1
        new_long = max(longest_streak, new_curr)
        return new_curr, new_long, streak_shields, False, f"Streak forged! {new_curr}-day momentum maintained."
    else:
        # Missed at least one day
        if streak_shields > 0:
            new_shields = streak_shields - 1
            new_curr = current_streak + 1
            new_long = max(longest_streak, new_curr)
            return new_curr, new_long, new_shields, True, f"Chronos Aegis activated! Shield consumed. Streak preserved at {new_curr} days."
        else:
            new_curr = 1
            return new_curr, longest_streak, streak_shields, False, "Streak extinguished by absence. Ignited afresh at Day 1."
