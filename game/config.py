# ==========================
# game/config.py - 游戏配置
# ==========================

MAX_HP = 80
MAX_ENERGY = 40

ENEMY_TEMPLATES = [
    {"name": "🐺 ဝံပုလွေသိုက်", "hp": 50, "attack": 15, "defense": 3, "reward": 15, "exp": 8},
    {"name": "🐻 ဝက်ဝံဧရာမ", "hp": 80, "attack": 20, "defense": 5, "reward": 25, "exp": 15},
    {"name": "🐉 နဂါးရိုင်း", "hp": 120, "attack": 30, "defense": 8, "reward": 45, "exp": 25},
    {"name": "🧙 မှော်ဆရာမည်း", "hp": 70, "attack": 35, "defense": 2, "reward": 35, "exp": 20},
    {"name": "⚔️ သူရဲကောင်းကျဆုံး", "hp": 100, "attack": 25, "defense": 12, "reward": 50, "exp": 28},
    {"name": "👹 နတ်ဆိုးမင်း", "hp": 150, "attack": 40, "defense": 10, "reward": 70, "exp": 35},
    {"name": "🐍 မြွေဘုရင်", "hp": 90, "attack": 30, "defense": 6, "reward": 40, "exp": 22},
    {"name": "🦅 လင်းယုန်မင်းကြီး", "hp": 110, "attack": 35, "defense": 8, "reward": 55, "exp": 30},
    {"name": "👑 မှောင်မိုက်မင်းကြီး", "hp": 200, "attack": 50, "defense": 15, "reward": 100, "exp": 50},
    {"name": "🐲 နဂါးမင်းကြီး", "hp": 300, "attack": 60, "defense": 20, "reward": 150, "exp": 70},
]

WEAPON_TEMPLATES = [
    {"name": "🗡️ သံဓားမ", "attack": 4, "price": 30},
    {"name": "⚔️ ငွေဓားမ", "attack": 8, "price": 60},
    {"name": "🗡️ ရွှေဓားမ", "attack": 13, "price": 120},
    {"name": "⚔️ မှော်ဓားမ", "attack": 20, "price": 200},
    {"name": "⚔️ ဒဏ္ဍာရီဓားမ", "attack": 32, "price": 400},
]

ARMOR_TEMPLATES = [
    {"name": "🛡️ သားရေဒိုင်း", "defense": 4, "price": 30},
    {"name": "🛡️ သံဒိုင်း", "defense": 8, "price": 60},
    {"name": "🛡️ ငွေဒိုင်း", "defense": 13, "price": 120},
    {"name": "🛡️ မှော်ဒိုင်း", "defense": 20, "price": 200},
    {"name": "🛡️ ဒဏ္ဍာရီဒိုင်း", "defense": 32, "price": 400},
]

POTION_TEMPLATES = [
    {"name": "🧪 သေးငယ်သောဆေး", "heal": 15, "price": 10},
    {"name": "🧪 ပုံမှန်ဆေး", "heal": 30, "price": 25},
    {"name": "🧪 ကြီးမားသောဆေး", "heal": 50, "price": 50},
    {"name": "🧪 အသက်ဆေး", "heal": 80, "price": 80},
]

ACHIEVEMENTS = {
    5: "🌱 ရှင်သန်သူ",
    10: "🌟 ခရီးသည်",
    20: "⚔️ စစ်သည်တော်",
    30: "🔥 သူရဲကောင်း",
    40: "⭐ ဒဏ္ဍာရီ",
    50: "👑 မင်းသား",
    60: "🏆 ချန်ပီယံ",
    70: "💀 သေခြင်းကိုအောင်သူ",
    80: "👑 ဘုရင်မင်းမြတ်",
    90: "🌟 အဆုံးစွန်ဘုရင်",
}