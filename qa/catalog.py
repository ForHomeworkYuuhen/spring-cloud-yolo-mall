# -*- coding: utf-8 -*-
"""
商城商品目录 —— 即 YOLO 识别的 19 种零食（伊朗零食/薯片数据集）。
知识图谱、问答检索、商品展示、数据库 seed 都以这里为准（id 一致）。
品牌 brand / 类目 category（薯片·膨化零食·饼干）。
"""

PRODUCTS = [
    {"id": 1,  "name": "Ashi Mashi snacks",              "price": 6.5,  "brand": "Ashi Mashi", "category": "膨化零食", "shop": "Ashi Mashi 旗舰店"},
    {"id": 2,  "name": "Chee pellet ketchup",            "price": 5.0,  "brand": "Chee",       "category": "膨化零食", "shop": "Chee 旗舰店"},
    {"id": 3,  "name": "Chee pellet vinegar",            "price": 5.0,  "brand": "Chee",       "category": "膨化零食", "shop": "Chee 旗舰店"},
    {"id": 4,  "name": "Cheetoz chili chips",            "price": 8.5,  "brand": "Cheetoz",    "category": "薯片",     "shop": "Cheetoz 旗舰店"},
    {"id": 5,  "name": "Cheetoz ketchup chips",          "price": 8.5,  "brand": "Cheetoz",    "category": "薯片",     "shop": "Cheetoz 旗舰店"},
    {"id": 6,  "name": "Cheetoz onion and parsley chips","price": 8.5,  "brand": "Cheetoz",    "category": "薯片",     "shop": "Cheetoz 旗舰店"},
    {"id": 7,  "name": "Cheetoz salty chips",            "price": 8.0,  "brand": "Cheetoz",    "category": "薯片",     "shop": "Cheetoz 旗舰店"},
    {"id": 8,  "name": "Cheetoz snack 30g",              "price": 3.5,  "brand": "Cheetoz",    "category": "膨化零食", "shop": "Cheetoz 旗舰店"},
    {"id": 9,  "name": "Cheetoz snack 90g",              "price": 7.9,  "brand": "Cheetoz",    "category": "膨化零食", "shop": "Cheetoz 旗舰店"},
    {"id": 10, "name": "Cheetoz vinegar chips",          "price": 8.5,  "brand": "Cheetoz",    "category": "薯片",     "shop": "Cheetoz 旗舰店"},
    {"id": 11, "name": "Cheetoz wheelsnack",             "price": 6.0,  "brand": "Cheetoz",    "category": "膨化零食", "shop": "Cheetoz 旗舰店"},
    {"id": 12, "name": "Maz Maz ketchup chips",          "price": 7.5,  "brand": "Maz Maz",    "category": "薯片",     "shop": "Maz Maz 旗舰店"},
    {"id": 13, "name": "Maz Maz potato sticks",          "price": 6.5,  "brand": "Maz Maz",    "category": "膨化零食", "shop": "Maz Maz 旗舰店"},
    {"id": 14, "name": "Maz Maz salty chips",            "price": 7.0,  "brand": "Maz Maz",    "category": "薯片",     "shop": "Maz Maz 旗舰店"},
    {"id": 15, "name": "Maz Maz vinegar chips",          "price": 7.5,  "brand": "Maz Maz",    "category": "薯片",     "shop": "Maz Maz 旗舰店"},
    {"id": 16, "name": "Mini Lina",                      "price": 9.9,  "brand": "Mini Lina",  "category": "饼干",     "shop": "Mini Lina 旗舰店"},
    {"id": 17, "name": "Minoo cream biscuit",            "price": 10.5, "brand": "Minoo",      "category": "饼干",     "shop": "Minoo 旗舰店"},
    {"id": 18, "name": "Naderi mini cookie",             "price": 11.0, "brand": "Naderi",     "category": "饼干",     "shop": "Naderi 旗舰店"},
    {"id": 19, "name": "Naderi mini wafer",              "price": 9.5,  "brand": "Naderi",     "category": "饼干",     "shop": "Naderi 旗舰店"},
]

BRANDS = sorted({p["brand"] for p in PRODUCTS})
CATEGORIES = sorted({p["category"] for p in PRODUCTS})

# 提问里可能出现的别名 -> 规范品牌（parse 会先转小写）
BRAND_ALIAS = {"mazmaz": "Maz Maz", "奇多": "Cheetoz", "cheetos": "Cheetoz",
               "ashimashi": "Ashi Mashi", "minilina": "Mini Lina"}
# 口味别名 -> 商品名里的英文关键词（按口味检索，如“辣味”->含 chili 的商品）
FLAVOR_ALIAS = {
    "辣": "chili", "辣味": "chili", "麻辣": "chili", "chili": "chili",
    "番茄": "ketchup", "茄汁": "ketchup", "番茄味": "ketchup", "ketchup": "ketchup",
    "醋": "vinegar", "酸": "vinegar", "醋味": "vinegar", "vinegar": "vinegar",
    "咸": "salty", "咸味": "salty", "salty": "salty",
    "洋葱": "onion", "onion": "onion",
    "奶油": "cream", "奶油味": "cream", "cream": "cream",
    "土豆": "potato", "土豆条": "potato", "potato": "potato",
}

# 提问里可能出现的别名 -> 规范类目
CATEGORY_ALIAS = {
    "薯片": "薯片", "chips": "薯片", "脆片": "薯片", "署片": "薯片",
    "膨化": "膨化零食", "膨化零食": "膨化零食", "薯条": "膨化零食", "脆条": "膨化零食",
    "粟米条": "膨化零食", "玉米卷": "膨化零食", "pellet": "膨化零食", "stick": "膨化零食",
    "饼干": "饼干", "曲奇": "饼干", "威化": "饼干", "wafer": "饼干", "cookie": "饼干", "biscuit": "饼干",
}
