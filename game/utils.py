# ==========================
# game/utils.py - 游戏工具
# ==========================

import random
from game.config import ENEMY_TEMPLATES, WEAPON_TEMPLATES, ARMOR_TEMPLATES, POTION_TEMPLATES, ACHIEVEMENTS


def generate_enemy(level):
    is_boss = level % 10 == 0
    is_elite = level % 5 == 0 and not is_boss

    if is_boss:
        base = random.choice([e for e in ENEMY_TEMPLATES if "နဂါး" in e["name"] or "မင်း" in e["name"] or "ဘုရင်" in e["name"]])
        multiplier = 1 + (level - 1) * 0.8
    elif is_elite:
        base = random.choice([e for e in ENEMY_TEMPLATES if "ဧရာမ" in e["name"] or "ဘုရင်" in e["name"]])
        multiplier = 1 + (level - 1) * 0.6
    else:
        base = random.choice(ENEMY_TEMPLATES)
        multiplier = 1 + (level - 1) * 0.5

    return {
        "name": base["name"],
        "hp": int(base["hp"] * multiplier),
        "max_hp": int(base["hp"] * multiplier),
        "attack": int(base["attack"] * multiplier),
        "defense": int(base["defense"] * multiplier),
        "reward": int(base["reward"] * multiplier * (3 if is_boss else 1.5 if is_elite else 1)),
        "exp": int(base["exp"] * multiplier * (3 if is_boss else 1.5 if is_elite else 1)),
        "level": level,
        "is_boss": is_boss,
        "is_elite": is_elite
    }


def generate_shop_items(level):
    items = []
    for w in WEAPON_TEMPLATES:
        if level >= 4 or w["price"] <= 60:
            items.append({"type": "weapon", **w})
    for a in ARMOR_TEMPLATES:
        if level >= 4 or a["price"] <= 60:
            items.append({"type": "armor", **a})
    for p in POTION_TEMPLATES:
        items.append({"type": "potion", **p})
    return items


def get_level_title(level):
    if level >= 85:
        return "🌟 အဆုံးစွန်ဘုရင်"
    elif level >= 75:
        return "👑 ဘုရင်မင်းမြတ်"
    elif level >= 65:
        return "⭐ နတ်ဘုရား"
    elif level >= 55:
        return "🔥 သူရဲကောင်း"
    elif level >= 45:
        return "⚔️ စစ်သည်တော်"
    elif level >= 35:
        return "🌱 ခရီးသည်"
    elif level >= 25:
        return "🌿 လမ်းပျောက်"
    elif level >= 15:
        return "🌱 အစပြုသူ"
    else:
        return "🌱 ခရီးစသူ"


def get_level_emoji(level):
    if level >= 85:
        return "🌟"
    elif level >= 75:
        return "👑"
    elif level >= 65:
        return "⭐"
    elif level >= 55:
        return "🔥"
    elif level >= 45:
        return "⚔️"
    elif level >= 35:
        return "🌱"
    elif level >= 25:
        return "🌿"
    elif level >= 15:
        return "🌱"
    else:
        return "🌱"