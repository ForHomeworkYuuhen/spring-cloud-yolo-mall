# -*- coding: utf-8 -*-
"""DIN（Deep Interest Network）模型定义，训练与在线服务共用。

物品级 DIN：每个行为 = (item, item 的类目)，候选 = (item, 类目)。
  Embedding(item) ⊕ Embedding(cat) 作为行为向量
  -> 局部激活单元(注意力：候选对每条历史行为打权重)
  -> 加权汇聚成用户兴趣
  -> [兴趣 ‖ 候选] -> MLP -> 购买概率 logit
"""
import torch
import torch.nn as nn


class DIN(nn.Module):
    def __init__(self, num_item: int, num_cat: int, emb: int = 32):
        super().__init__()
        self.item_emb = nn.Embedding(num_item, emb, padding_idx=0)
        self.cat_emb = nn.Embedding(num_cat, emb, padding_idx=0)
        d = emb * 2                                   # 行为向量维度 = item ⊕ cat
        self.att = nn.Sequential(nn.Linear(d * 4, 80), nn.ReLU(), nn.Linear(80, 1))
        self.mlp = nn.Sequential(nn.Linear(d * 2, 80), nn.ReLU(),
                                 nn.Linear(80, 16), nn.ReLU(), nn.Linear(16, 1))

    def behavior(self, item, cat):
        return torch.cat([self.item_emb(item), self.cat_emb(cat)], dim=-1)

    def forward(self, hist_item, hist_cat, cand_item, cand_cat):
        he = self.behavior(hist_item, hist_cat)       # (B,L,2D)
        ce = self.behavior(cand_item, cand_cat)       # (B,2D)
        ce_e = ce.unsqueeze(1).expand_as(he)          # (B,L,2D)
        att_in = torch.cat([he, ce_e, he * ce_e, he - ce_e], dim=-1)  # (B,L,8D)
        w = self.att(att_in).squeeze(-1)              # (B,L) 注意力权重
        w = w * (hist_item > 0).float()               # padding 置 0（DIN 不做 softmax）
        interest = (w.unsqueeze(-1) * he).sum(1)      # (B,2D) 加权兴趣
        x = torch.cat([interest, ce], dim=-1)         # (B,4D)
        return self.mlp(x).squeeze(-1)                # (B,) logit
