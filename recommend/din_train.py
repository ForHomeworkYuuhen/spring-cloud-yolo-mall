# -*- coding: utf-8 -*-
"""
DIN 训练。基于天池移动推荐用户行为数据：
  用「购买前的浏览/收藏/加购的商品序列」预测「会购买哪个商品」。
  正样本 = 用户实际购买的（高频）商品；负样本 = 随机未购买的商品（负采样）。
产出 model/din.pt + din_meta.json + din_users.json，供 rec_service 在线推荐数据集真实商品。
运行：python din_train.py
"""
import os, json, random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from din_model import DIN

BASE = os.path.dirname(os.path.abspath(__file__))
USER_CSV = os.path.join(BASE, "..", "tianchi_mobile_recommend_train_user.csv")
MODEL_DIR = os.path.join(BASE, "model")
ROWS = 2_000_000
TOP_ITEMS = 20000    # 只保留最高频的 N 个商品建词表（控制 embedding 规模）
MAXLEN = 20
EMB = 32
EPOCHS = 6
BATCH = 512
NEG = 1
USER_SAMPLE = 8000
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
random.seed(7); np.random.seed(7); torch.manual_seed(7)


def auc_score(y, s):
    order = np.argsort(s); ranks = np.empty(len(s), float); ranks[order] = np.arange(1, len(s) + 1)
    npos = y.sum(); nneg = len(y) - npos
    if npos == 0 or nneg == 0: return 0.5
    return float((ranks[y == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def main():
    print(f"[1/6] 读数据（{ROWS} 行）device={DEVICE} ...")
    df = pd.read_csv(USER_CSV, nrows=ROWS, usecols=["user_id", "item_id", "item_category", "behavior_type", "time"])
    df = df.sort_values(["user_id", "time"])

    print("[2/6] 建商品/类目词表（高频商品）...")
    top_items = df.item_id.value_counts().head(TOP_ITEMS).index
    item2idx = {int(it): i + 1 for i, it in enumerate(top_items)}
    cats = df.item_category.unique()
    cat2idx = {int(cc): i + 1 for i, cc in enumerate(cats)}
    df["iidx"] = df.item_id.map(item2idx).fillna(0).astype(np.int64)
    df["cidx"] = df.item_category.map(cat2idx).fillna(0).astype(np.int64)
    i2c = df.drop_duplicates("item_id").set_index("item_id")["item_category"].to_dict()
    item_catidx = {idx: cat2idx[int(i2c[it])] for it, idx in item2idx.items()}
    K = len(item2idx); num_item = K + 1; num_cat = len(cat2idx) + 1
    print(f"      行={len(df)} 用户={df.user_id.nunique()} 高频商品={K} 类目={len(cat2idx)}")

    print("[3/6] 构造样本 ...")
    samples = []; user_hist = {}
    for uid, g in df.groupby("user_id"):
        ii = g.iidx.values; cc = g.cidx.values; bt = g.behavior_type.values
        hist = [(int(ii[k]), int(cc[k])) for k in range(len(ii)) if bt[k] in (1, 2, 3) and ii[k] > 0][-MAXLEN:]
        if not hist: continue
        if len(user_hist) < USER_SAMPLE:
            user_hist[str(int(uid))] = {"hi": [h[0] for h in hist], "hc": [h[1] for h in hist]}
        buys = [(int(ii[k]), int(cc[k])) for k in range(len(ii)) if bt[k] == 4 and ii[k] > 0]
        buyset = set(b[0] for b in buys)
        for (pi, pc) in buys:
            samples.append((hist, pi, pc, 1))
            for _ in range(NEG):
                ni = random.randint(1, K)
                while ni in buyset: ni = random.randint(1, K)
                samples.append((hist, ni, item_catidx[ni], 0))
    random.shuffle(samples)
    print(f"      样本={len(samples)}  正样本={sum(s[3] for s in samples)}")

    def to_batch(batch):
        n = len(batch); L = MAXLEN
        HI = np.zeros((n, L), np.int64); HC = np.zeros((n, L), np.int64)
        CI = np.zeros(n, np.int64); CC = np.zeros(n, np.int64); Y = np.zeros(n, np.float32)
        for i, (h, ci, cc_, l) in enumerate(batch):
            st = L - len(h)
            for j, (it, ct) in enumerate(h):
                HI[i, st + j] = it; HC[i, st + j] = ct
            CI[i] = ci; CC[i] = cc_; Y[i] = l
        return (torch.from_numpy(HI), torch.from_numpy(HC), torch.from_numpy(CI), torch.from_numpy(CC), torch.from_numpy(Y))

    n_val = max(1, len(samples) // 10)
    val, train = samples[:n_val], samples[n_val:]

    print("[4/6] 建 DIN + 训练 ...")
    model = DIN(num_item, num_cat, EMB).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()

    def run_eval():
        model.eval(); ss = []; yy = []
        with torch.no_grad():
            for i in range(0, len(val), 2048):
                HI, HC, CI, CC, Y = to_batch(val[i:i + 2048])
                lg = model(HI.to(DEVICE), HC.to(DEVICE), CI.to(DEVICE), CC.to(DEVICE))
                ss.append(torch.sigmoid(lg).cpu().numpy()); yy.append(Y.numpy())
        return auc_score(np.concatenate(yy), np.concatenate(ss))

    for ep in range(EPOCHS):
        model.train(); random.shuffle(train); tot = 0
        for i in range(0, len(train), BATCH):
            HI, HC, CI, CC, Y = to_batch(train[i:i + BATCH])
            lg = model(HI.to(DEVICE), HC.to(DEVICE), CI.to(DEVICE), CC.to(DEVICE))
            loss = lossf(lg, Y.to(DEVICE))
            opt.zero_grad(); loss.backward(); opt.step()
            tot += loss.item() * len(Y)
        print(f"      epoch {ep + 1}/{EPOCHS}  loss={tot / len(train):.4f}  val_AUC={run_eval():.4f}")

    print("[5/6] 保存模型与词表 ...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    torch.save({"state": model.state_dict(), "num_item": num_item, "num_cat": num_cat, "emb": EMB, "maxlen": MAXLEN},
               os.path.join(MODEL_DIR, "din.pt"))
    cand_items = list(range(1, K + 1))
    meta = {
        "maxlen": MAXLEN,
        "cand_items": cand_items,
        "cand_cats": [item_catidx[i] for i in cand_items],
        "idx2item": {str(idx): int(it) for it, idx in item2idx.items()},
        "idx2cat": {str(i + 1): int(cc) for i, cc in enumerate(cats)},
        "top_categories": [int(c) for c in df.item_category.value_counts().head(10).index],
    }
    json.dump(meta, open(os.path.join(MODEL_DIR, "din_meta.json"), "w"))
    json.dump(user_hist, open(os.path.join(MODEL_DIR, "din_users.json"), "w"))
    print(f"[6/6] 完成。采样用户历史={len(user_hist)}  候选商品={K}")


if __name__ == "__main__":
    main()
