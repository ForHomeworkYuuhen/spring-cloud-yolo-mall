# -*- coding: utf-8 -*-
"""
推荐模型训练（离线）。基于天池移动推荐用户行为数据，实现 Item-based 协同过滤(ItemCF)。
产出 recommend/model/model.json，供 rec_service.py 在线服务使用。

算法：
  1) 行为加权：浏览=1 收藏=2 加购=3 购买=4，构建用户对物品/类目的兴趣权重。
  2) ItemCF：物品-物品相似度（用户历史里的共现 + 余弦归一化）—— “喜欢A的人也喜欢B”。
  3) 物品/类目热度做兜底；用户->类目偏好，用于给本商城 10 个商品做个性化排序。
运行：
  pip install pandas
  python train_recommend.py
"""
import os
import json
import math
import collections

BASE = os.path.dirname(os.path.abspath(__file__))
USER_CSV = os.path.join(BASE, "..", "tianchi_mobile_recommend_train_user.csv")
MODEL_DIR = os.path.join(BASE, "model")

ROWS = 2_000_000          # 采样行数（全量约 5000 万行，按机器内存可调大）
W = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}   # 浏览/收藏/加购/购买
TOP_ITEMS = 400           # 只对最热的 N 个物品算相似度（控制共现规模）
TOP_CATS = 60             # 对最热的 N 个类目算类目-类目协同过滤相似度
TOPK = 20                 # 每个物品保留 K 个最相似
HIST_CAP = 50             # 单用户历史截断，控制共现计算量
USER_SAMPLE = 8000        # 保存这么多用户的类目偏好（给商城个性化用）
MIN_CATS = 6              # 只保留逛过 >=6 个类目的活跃用户（profile 有信号，个性化更明显）


def main():
    import pandas as pd
    print(f"[1/5] 读取前 {ROWS} 行用户行为 ...")
    df = pd.read_csv(USER_CSV, nrows=ROWS,
                     usecols=["user_id", "item_id", "behavior_type", "item_category"])
    df["w"] = df["behavior_type"].map(W).fillna(1.0)
    print(f"      行数={len(df)} 用户={df.user_id.nunique()} 物品={df.item_id.nunique()} 类目={df.item_category.nunique()}")

    print("[2/5] 物品热度 + 取最热物品 ...")
    item_pop = df.groupby("item_id")["w"].sum()
    top_items = set(item_pop.sort_values(ascending=False).head(TOP_ITEMS).index)
    item_cat = df.drop_duplicates("item_id").set_index("item_id")["item_category"].to_dict()

    print("[3/5] 计算 ItemCF 物品-物品相似度（共现+余弦）...")
    df_top = df[df.item_id.isin(top_items)]
    user_items = df_top.groupby("user_id")["item_id"].apply(lambda s: list(set(s))[:HIST_CAP])
    co = collections.defaultdict(lambda: collections.defaultdict(float))
    pop = collections.defaultdict(float)
    for items in user_items:
        for i in items:
            pop[i] += 1
            for j in items:
                if i != j:
                    co[i][j] += 1.0
    item_sim = {}
    for i, rel in co.items():
        sims = [(j, c / math.sqrt(pop[i] * pop[j])) for j, c in rel.items()]
        sims.sort(key=lambda x: x[1], reverse=True)
        item_sim[str(i)] = [[str(j), round(s, 4)] for j, s in sims[:TOPK]]
    hot_items = [str(i) for i in item_pop.sort_values(ascending=False).head(50).index]

    print("[4/5] 类目热度 + 用户类目偏好 + 类目级协同过滤 ...")
    cat_pop = df.groupby("item_category")["w"].sum().sort_values(ascending=False)
    cat_pop_d = {str(k): round(float(v), 2) for k, v in cat_pop.head(80).items()}

    # 用户 -> {类目: 权重}
    uc = df.groupby(["user_id", "item_category"])["w"].sum().reset_index()
    user_cat_full = {}
    for uid, g in uc.groupby("user_id"):
        user_cat_full[uid] = {int(r.item_category): float(r.w) for r in g.itertuples()}
    active = [(u, d) for u, d in user_cat_full.items() if len(d) >= MIN_CATS]
    user_cat = {str(u): {str(c): round(w, 2) for c, w in d.items()}
                for u, d in active[:USER_SAMPLE]}

    # 类目-类目协同过滤：对最热 TOP_CATS 个类目，算它和其它类目的共现相似度（余弦）。
    # 用户即使没碰过某热门类目、但碰过与它相关的类目，也能被推荐 → 覆盖更广，真正个性化。
    cat_users = uc.groupby("item_category")["user_id"].nunique().to_dict()  # 每个类目的用户数
    top_cats = list(cat_pop.head(TOP_CATS).index)
    top_cats_set = set(top_cats)
    cco = collections.defaultdict(lambda: collections.defaultdict(float))
    for d in user_cat_full.values():
        cats = list(d.keys())[:80]
        tops = [c for c in cats if c in top_cats_set]
        for c in tops:
            for c2 in cats:
                if c != c2:
                    cco[c][c2] += 1.0
    cat_sim = {}
    for c, rel in cco.items():
        sims = [(c2, n / math.sqrt(cat_users.get(c, 1) * cat_users.get(c2, 1))) for c2, n in rel.items()]
        sims.sort(key=lambda x: x[1], reverse=True)
        cat_sim[str(c)] = [[str(c2), round(s, 4)] for c2, s in sims[:30]]

    print("[5/5] 保存模型 ...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    model = {
        "item_sim": item_sim,
        "hot_items": hot_items,
        "item_cat": {str(k): str(v) for k, v in item_cat.items() if k in top_items},
        "cat_pop": cat_pop_d,
        "cat_sim": cat_sim,
        "top_categories": [str(c) for c in top_cats[:10]],
        "user_cat": user_cat,
        "stats": {"rows": int(len(df)), "users": int(df.user_id.nunique()), "items": int(df.item_id.nunique())},
    }
    out = os.path.join(MODEL_DIR, "model.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False)
    sz = round(os.path.getsize(out) / 1024 / 1024, 1)
    print(f"  已保存 {out}  ({sz}MB)  item_sim={len(item_sim)} 物品  user_cat={len(user_cat)} 用户")
    hot = hot_items[0]
    print(f"  示例 ItemCF —— 和热门物品 {hot} 最相似: {item_sim.get(hot, [])[:5]}")


if __name__ == "__main__":
    main()
