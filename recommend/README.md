# 推荐模块（DIN · 深度兴趣网络）

基于**天池移动推荐数据集**的用户行为，用 **DIN（Deep Interest Network，深度兴趣网络）** 做个性化推荐：根据用户购买前的行为序列，预测其最可能购买的商品。

## 数据

`tianchi_mobile_recommend_train_user.csv`（项目根目录，~507MB）：`user_id, item_id, behavior_type, user_geohash, item_category, time`。
`behavior_type`：1 浏览 / 2 收藏 / 3 加购 / 4 购买。

## 算法（DIN 原理）

每个行为表示为 `Embedding(item) ⊕ Embedding(类目)`。给一个候选商品打分时：

1. **局部激活单元（注意力）**：用候选商品去和用户历史里的每条行为算相关性权重——和候选相关的历史行为权重高、无关的低。
2. **加权汇聚**：用这些权重对历史行为加权求和，得到“针对该候选商品”的用户兴趣表示。
3. **MLP**：把 `[用户兴趣 ‖ 候选商品]` 送入多层网络，输出购买概率。

训练：以用户**购买**的（高频）商品为正样本、随机未购买商品为负样本（负采样），历史取购买前的浏览/收藏/加购序列。损失 BCE，用 **AUC** 评估（验证集 ≈0.73）。物品有上百万、极稀疏，故只保留最高频的 2 万个商品建词表。

## 文件

| 文件 | 作用 |
|---|---|
| `din_model.py` | DIN 模型定义（item+类目 Embedding + 注意力 + MLP），训练/服务共用 |
| `din_train.py` | **离线训练**：构样本 → 训练 → 存 `model/din.pt` + `din_meta.json` + `din_users.json` |
| `rec_service.py` | **在线服务**（:8124）：加载模型，对外推荐 |
| `model/din.pt` 等 | 模型权重 + 词表 + 采样用户历史 |

## 运行

```bash
pip install torch pandas numpy fastapi "uvicorn[standard]"
python din_train.py        # 离线训练（GPU 更快）
python rec_service.py       # 在线服务 :8124
```

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/recommend/test?n=8` | 随机抽一位数据集真实用户 → 返回其历史 + DIN 推荐的**数据集真实商品**（供推荐测试页 reco-test.html） |
| GET | `/recommend?user_id=&n=4` | 商城首页个性化：DIN 打分 → 偏好类目 → 映射到商城商品ID |
| GET | `/health` | 模型加载状态 |

## 前端

- 测试页 `reco-test.html`：随机用户 + DIN 推荐数据集商品（带购买概率），演示“千人千面”。
- 首页“热门推荐”：登录用户经 `/recommend` 个性化排序商城商品；服务未起时按销量兜底。
