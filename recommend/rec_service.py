# -*- coding: utf-8 -*-
"""
个性化推荐服务（在线）。加载 train_recommend.py 产出的 ItemCF 协同过滤模型，
给本商城“热门推荐”做千人千面的个性化排序。

接口：
  GET /recommend?user_id=<id>&n=<数量>   ->  {"user_id","n","item_ids":[商城商品ID...],"source"}
       前端“热门推荐”区自动调用（无需按钮），拿 item_ids 按序展示对应商品。
  GET /similar?item_id=<天池物品ID>&n=    ->  ItemCF “喜欢A的人也喜欢B”，展示协同过滤本身。
  GET /health

数据/模型来源：天池移动推荐用户行为数据 -> recommend/model/model.json（先跑 train_recommend.py）。
运行：
  pip install fastapi "uvicorn[standard]"
  python rec_service.py          # 监听 :8124
"""
import os
import json
import hashlib
import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Recommend Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE, "model", "model.json")
CATALOG_IDS = list(range(1, 20))   # 本商城 19 个零食商品

# ---- 加载离线训练好的模型 ----
MODEL = {}
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, encoding="utf-8") as f:
        MODEL = json.load(f)
ITEM_SIM = MODEL.get("item_sim", {})       # 物品-物品相似度（ItemCF）
USER_CAT = MODEL.get("user_cat", {})       # 采样用户的类目偏好向量
CAT_POP = MODEL.get("cat_pop", {})         # 类目热度
CAT_SIM = MODEL.get("cat_sim", {})         # 类目-类目相似度（category-CF）
TOP_CATS = MODEL.get("top_categories", [])  # 最热的 10 个类目
USER_KEYS = sorted(USER_CAT.keys())

# 商城商品 -> 天池类目 的映射：用最热的 10 个类目把真实行为数据接到本商城目录上。
# （两个目录的物品空间不同，这里用“商品代表一个热门类目”的方式桥接，便于在商城演示个性化。）
# 每个商品映射到一个【不同】的热门类目（用真实行为数据把商城商品接到类目空间），
# 这样不同用户对各类目的偏好不同 -> 商品排序千人千面。
_CAT_LIST = list(CAT_POP.keys()) or TOP_CATS
SHOP_CATEGORY = {pid: (_CAT_LIST[i] if i < len(_CAT_LIST) else None)
                 for i, pid in enumerate(CATALOG_IDS)}


def _profile_for(user_id: str):
    """取用户的类目偏好向量：天池真实用户直接用；商城用户名 -> 确定性映射到一位采样用户。"""
    if user_id in USER_CAT:
        return USER_CAT[user_id]
    if USER_KEYS:
        h = int(hashlib.md5(str(user_id).encode("utf-8")).hexdigest(), 16)
        return USER_CAT[USER_KEYS[h % len(USER_KEYS)]]
    return {}


def recommend_shop(user_id: str, n: int):
    """
    对商城 10 个商品做个性化排序，返回 TopN 商品ID。打分 = 类目级协同过滤：
      score(商品c) = 用户对 c 的兴趣 + Σ_{c'∈用户历史} 用户对c'的兴趣 × 相似度(c,c') + 微弱热度先验
    即使用户没直接碰过商品对应的类目，碰过“相关类目”也会被推荐 → 千人千面。
    """
    prof = _profile_for(user_id)
    scored = []
    for pid in CATALOG_IDS:
        cat = SHOP_CATEGORY.get(pid)
        s = 0.0
        if cat is not None:
            s = float(prof.get(cat, 0.0))                   # 直接兴趣
            for c2, sim in CAT_SIM.get(cat, []):            # 相关类目的兴趣（category-CF）
                s += float(prof.get(c2, 0.0)) * float(sim)
        pop = float(CAT_POP.get(cat, 0.0)) if cat is not None else 0.0
        scored.append((pid, s, pop))
    # 先按个性化分排序，类目热度只用于破平/冷启动（个性化分全为0时退化成热度序）
    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return [pid for pid, _, _ in scored[:n]]


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": bool(MODEL),
            "item_sim_items": len(ITEM_SIM), "user_profiles": len(USER_CAT),
            "stats": MODEL.get("stats", {})}


@app.get("/recommend")
def recommend(user_id: str = "guest", n: int = 4):
    ids = recommend_shop(user_id, n)
    return {"user_id": user_id, "n": n, "item_ids": ids,
            "source": "itemcf" if MODEL else "fallback"}


@app.get("/demo")
def demo(n: int = 8):
    """随机抽取一位真实用户，按其历史行为偏好推荐（推荐测试页用）。"""
    if USER_KEYS:
        uid = random.choice(USER_KEYS)
        cats = len(USER_CAT.get(uid, {}))
    else:
        uid, cats = "guest", 0
    return {"user_id": uid, "profile_categories": cats, "item_ids": recommend_shop(uid, n)}


@app.get("/similar")
def similar(item_id: str, n: int = 10):
    """ItemCF：和某天池物品最相似的物品（喜欢A的人也喜欢B）。直接展示协同过滤结果。"""
    return {"item_id": item_id, "similar": ITEM_SIM.get(str(item_id), [])[:n]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8124)
