# 推荐模块（个性化推荐 · 协同过滤）

基于**天池移动推荐数据**的用户行为，用**协同过滤（Collaborative Filtering）**做"千人千面"的个性化推荐，接到商城首页"热门推荐"区（自动展示，无需按钮）。

## 数据

项目根目录下两个文件（天池数据集 https://tianchi.aliyun.com/dataset/46 ）：

| 文件 | 大小 | 列 |
|---|---|---|
| `tianchi_mobile_recommend_train_user.csv` | ~507MB | `user_id, item_id, behavior_type, user_geohash, item_category, time` |
| `tianchi_mobile_recommend_train_item.csv` | ~9MB | `item_id, item_geohash, item_category` |

`behavior_type`：**1=浏览，2=收藏，3=加购物车，4=购买**（兴趣强度递增）。

## 算法设计

分两层，都用真实行为数据训练：

1. **行为加权**：把四种行为按强度加权（浏览1 / 收藏2 / 加购3 / 购买4），构建用户对物品、对类目的兴趣权重。
2. **ItemCF（物品-物品协同过滤）**：在用户历史里统计物品共现，用余弦归一化得到"喜欢A的人也喜欢B"的物品相似度。→ 接口 `/similar` 直接展示。
3. **category-CF（类目级协同过滤）**：物品空间太稀疏（113 万物品），按 `item_category` 聚合到类目级算共现相似度。给商城 10 个商品打分时：
   `score(商品) = 用户对该类目的兴趣 + Σ 用户对相关类目的兴趣 × 类目相似度 + 微弱热度先验`
   这样用户即使没碰过该类目、碰过**相关类目**也会被推荐，覆盖更广、个性化更明显。

> 商城 10 个商品与天池物品不是同一套，用"每个商品代表一个热门类目"的方式把真实行为数据桥接到商城目录，便于在商城里演示个性化。

## 文件

| 文件 | 作用 |
|---|---|
| `train_recommend.py` | **离线训练**：读行为数据 → 算 ItemCF / category-CF / 用户类目偏好 → 存 `model/model.json` |
| `rec_service.py` | **在线服务**（FastAPI :8124）：加载模型，对外提供推荐接口 |
| `model/model.json` | 训练产出的模型（item_sim / cat_sim / user_cat / cat_pop / hot_items） |

## 运行

```bash
pip install pandas fastapi "uvicorn[standard]"

# 1) 离线训练（生成 model/model.json；默认采样 200 万行，可在脚本顶部调 ROWS）
python train_recommend.py

# 2) 启动在线推荐服务（:8124）
python rec_service.py
```

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/recommend?user_id=<id>&n=4` | 商城个性化推荐 → `{"item_ids":[商品ID...]}`，前端"热门推荐"自动调用 |
| GET | `/similar?item_id=<天池物品ID>&n=10` | ItemCF：和该物品最相似的物品（喜欢A也喜欢B） |
| GET | `/health` | 模型加载状态、规模统计 |

## 前端接入

`shop-frontend/js/app.js` 顶部 `REC_API` 指向本服务；首页加载时 `fetchRecommend()` 自动拉取推荐并渲染到"热门推荐"区，**推荐服务未启动时自动按销量兜底**（页面不报错）。

## 可调参数（`train_recommend.py` 顶部）

`ROWS` 采样行数 · `W` 行为权重 · `TOP_ITEMS` 参与 ItemCF 的热门物品数 · `TOP_CATS` 参与类目-CF 的类目数 · `USER_SAMPLE` 保存的用户偏好数。机器内存够可把 `ROWS` 调大到全量以提升效果。
