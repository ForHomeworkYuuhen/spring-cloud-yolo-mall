# -*- coding: utf-8 -*-
"""
个性化推荐在线服务（DIN，深度兴趣网络）。加载 din_train.py 产出的模型，对外提供：
  GET /recommend/test?user_id=&n=8   -> 取一个数据集真实用户，返回其历史行为 + DIN 推荐的【数据集真实商品】
                                        （user_id 省略则随机选一个用户）。供推荐测试页使用。
  GET /recommend?user_id=&n=4         -> 商城首页个性化：DIN 打分 -> 偏好类目 -> 映射到商城商品ID。
  GET /health
模型/数据来自天池移动推荐数据集（先跑 din_train.py）。
"""
import os
import json
import random
import hashlib

import numpy as np
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from din_model import DIN

app = FastAPI(title="Recommend Service (DIN)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, "model")

MODEL = None
try:
    ck = torch.load(os.path.join(MODEL_DIR, "din.pt"), map_location="cpu")
    MODEL = DIN(ck["num_item"], ck["num_cat"], ck["emb"])
    MODEL.load_state_dict(ck["state"]); MODEL.eval()
    MAXLEN = ck["maxlen"]
    meta = json.load(open(os.path.join(MODEL_DIR, "din_meta.json"), encoding="utf-8"))
    CAND_ITEMS = meta["cand_items"]; CAND_CATS = meta["cand_cats"]
    IDX2ITEM = meta["idx2item"]; IDX2CAT = meta["idx2cat"]; TOP_CATS = meta["top_categories"]
    USERS = json.load(open(os.path.join(MODEL_DIR, "din_users.json"), encoding="utf-8"))
    USER_KEYS = list(USERS.keys())
    CAND_ITEM_T = torch.tensor(CAND_ITEMS, dtype=torch.long)
    CAND_CAT_T = torch.tensor(CAND_CATS, dtype=torch.long)
except Exception as e:
    print("模型未加载（请先跑 din_train.py）：", e)

_shop_cache = {}


def _pad(hi, hc):
    hi = hi[-MAXLEN:]; hc = hc[-MAXLEN:]
    return [0] * (MAXLEN - len(hi)) + hi, [0] * (MAXLEN - len(hc)) + hc


def _score_all(hi, hc):
    """对该用户历史，给所有候选商品打分（购买概率），返回与 CAND_ITEMS 对齐的分数。"""
    HI, HC = _pad(hi, hc)
    K = len(CAND_ITEMS)
    histI = torch.tensor(HI, dtype=torch.long).unsqueeze(0).expand(K, -1)
    histC = torch.tensor(HC, dtype=torch.long).unsqueeze(0).expand(K, -1)
    out = []
    with torch.no_grad():
        for s in range(0, K, 4096):
            lg = MODEL(histI[s:s+4096], histC[s:s+4096], CAND_ITEM_T[s:s+4096], CAND_CAT_T[s:s+4096])
            out.append(torch.sigmoid(lg).numpy())
    return np.concatenate(out)


@app.get("/health")
def health():
    return {"status": "ok", "model": "DIN", "loaded": MODEL is not None,
            "candidates": len(CAND_ITEMS) if MODEL else 0, "users": len(USERS) if MODEL else 0}


@app.get("/recommend/test")
def recommend_test(user_id: str = "", n: int = 8):
    """取数据集真实用户，返回历史 + DIN 推荐的数据集真实商品。"""
    if MODEL is None:
        return {"error": "模型未加载，请先训练 din_train.py"}
    if user_id not in USERS:
        rich = [k for k in USER_KEYS if len(USERS[k]["hi"]) >= 3]
        user_id = random.choice(rich or USER_KEYS)
    u = USERS[user_id]
    scores = _score_all(u["hi"], u["hc"])
    seen = set(u["hi"])
    recs = []
    for k in np.argsort(-scores):
        idx = CAND_ITEMS[k]
        if idx in seen:
            continue
        recs.append({"item": int(IDX2ITEM[str(idx)]), "category": int(IDX2CAT[str(CAND_CATS[k])]),
                     "score": round(float(scores[k]), 4)})
        if len(recs) >= n:
            break
    hist = [{"item": int(IDX2ITEM[str(i)]), "category": int(IDX2CAT[str(cc)])}
            for i, cc in zip(u["hi"], u["hc"]) if str(i) in IDX2ITEM][-12:]
    return {"user_id": user_id, "history": hist, "recommendations": recs}


@app.get("/recommend")
def recommend(user_id: str = "guest", n: int = 4):
    """商城首页个性化：DIN 打分 -> 用户偏好类目 -> 映射到商城商品ID。"""
    if MODEL is None:
        return {"user_id": user_id, "n": n, "item_ids": [1, 2, 3, 4], "source": "fallback"}
    key = user_id if user_id in USERS else USER_KEYS[int(hashlib.md5(user_id.encode()).hexdigest(), 16) % len(USER_KEYS)]
    if key in _shop_cache:
        tally = _shop_cache[key]
    else:
        u = USERS[key]; scores = _score_all(u["hi"], u["hc"])
        tally = {}
        for k in np.argsort(-scores)[:200]:
            cat = int(IDX2CAT[str(CAND_CATS[k])])
            tally[cat] = tally.get(cat, 0.0) + float(scores[k])
        _shop_cache[key] = tally
    shop_cat = {i + 1: TOP_CATS[i] for i in range(min(10, len(TOP_CATS)))}
    ranked = sorted(range(1, 11), key=lambda pid: tally.get(shop_cat.get(pid, -1), 0.0), reverse=True)
    return {"user_id": user_id, "n": n, "item_ids": ranked[:n], "source": "din"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8124)
