# 零食识别模型：三模型对比 · 过拟合分析 · 识别服务集成报告

> 广东海洋大学 23 级信管实训 · 粤海购「商品识别」
> 数据集：Iranian Snack and Chips Detection (YOLO Format)，19 类，train≈450 / val=91 / test=91 张
> 设备：RTX 5070 Ti Laptop 12GB（Blackwell sm_120）· Ultralytics 8.4.68 · torch 2.11.0+cu128

---

## 0. 结论速览

1. **三个模型都无实质过拟合**（包括 11s 原始）；判据是 TEST 与 VAL 的 mAP50-95 差距均 < 0.02，且验证 loss 达最低后无回升。
2. **部署选用 `11s + 过采样`**：验证集 mAP50-95 三者最高（0.9865），GPU 单图推理仅 ~2–20ms，比 12x 小 6 倍、快得多。
3. **三个模型已全部接入识别服务**（FastAPI，GPU 加载），前端识别页可**下拉切换模型**并实时画框，已端到端验证。

---

## 1. 三模型总览

| 模型 | 训练数据 | 参数量 | val mAP50 | val mAP50-95 | **test mAP50-95** | 用途 |
|---|---|---|---|---|---|---|
| 11s 原始(baseline) | 未过采样 | 9.4M | 0.9941 | 0.9851 | 0.9743 | 对照基线 |
| **11s + 过采样** | 过采样 | 9.4M | 0.9942 | **0.9865** | 0.9755 | **部署默认** |
| 12x + 过采样 | 过采样 | 59M | 0.9948 | 0.9839 | **0.9770** | 大模型对照 |

- 验证集上 **11s+过采样最高**；留出测试集上 12x 略高（但仅高 0.0015，且慢得多）。
- 三者差距全部在噪声量级（±0.003），数据集已饱和——**模型容量不是瓶颈**，故按"精度持平时取最快最小"原则选 11s。

### 整体指标对比图
![整体指标对比](report_assets/overall_compare.png)

---

## 2. 过拟合分析（重点回答"11s 是否过拟合"）

**结论：三个模型均无实质过拟合，11s 原始也没有。**

### 判据一：训练曲线无过拟合信号
验证 loss 达到最小后没有持续回升（过拟合的典型特征是 train_loss 持续下降而 val_loss 回升）：

| 模型 | val_loss 最低 epoch | 其后是否回升 | 末期 val-train loss 差 |
|---|---|---|---|
| 11s 原始 | ~62 | 否（仅 +0.019 微升） | **-0.085**（val 反低于 train） |
| 11s + 过采样 | ~97 | 否（+0.001） | +0.026 |
| 12x + 过采样 | 48（中断，仍在降） | 未现拐点 | **-0.186** |

> 末期"验证 loss ≤ 训练 loss"（负差）是**强增强训练 / 无增强验证**造成的正常现象，与过拟合方向相反。

![验证loss曲线](report_assets/loss_curves.png)

### 判据二：留出 TEST 集泛化良好
| 模型 | val mAP50-95 | test mAP50-95 | 差距(val-test) |
|---|---|---|---|
| 11s 原始 | 0.9851 | 0.9743 | **0.0108** |
| 11s + 过采样 | 0.9865 | 0.9755 | **0.0110** |
| 12x + 过采样 | 0.9839 | 0.9770 | **0.0069** |

三者差距均 **< 0.02**，远低于 0.05 的过拟合警戒线 → 泛化稳健。

### ⚠️ 需要谨慎解读的两点（真实风险）
1. **评估偏乐观**：训练集仅约 450 张，val/test 由**同源视频抽帧**、分布高度相似，分数天然偏高。真正的考验是**真实手机拍摄照片**（不同光照/角度/背景/压缩），实际部署 mAP 很可能明显低于 0.97。建议补一批真机照片做外部测试。
2. **稀有类记忆风险**：过采样把 4 样本的稀有类（如 Cheetoz snack 30g）重复多次，模型可能"记住"而非"学会"，这几类在分布外的退化风险更高。

---

## 3. 逐类对比（mAP50-95）

9 个类三模型全为 0.995（已饱和，略）。下表为**有差异的 10 个类**（加粗=该行最优）：

| 类别 | val样本 | 11s原始 | 11s+过采样 | 12x+过采样 |
|---|---|---|---|---|
| Cheetoz snack 30g | 4 | **0.964** | **0.964** | 0.937 |
| Maz Maz salty chips | 13 | **0.991** | 0.981 | 0.974 |
| Cheetoz snack 90g | 14 | **0.973** | 0.962 | 0.972 |
| Maz Maz vinegar chips | 14 | 0.972 | **0.986** | 0.980 |
| Minoo cream biscuit | 16 | 0.952 | **0.961** | 0.946 |
| Naderi mini cookie | 16 | 0.987 | **0.989** | **0.989** |
| Chee pellet ketchup | 23 | 0.988 | **0.990** | 0.983 |
| Maz Maz potato sticks | 26 | 0.969 | **0.976** | 0.974 |
| Maz Maz ketchup chips | 31 | 0.983 | **0.995** | **0.995** |
| Mini Lina | 40 | 0.984 | 0.984 | **0.987** |

**过采样对 11s 的作用**：净增益 +0.0014，主要拉起几个偏难的中等类（Maz Maz ketchup 0.983→0.995、Maz Maz vinegar 0.972→0.986、Minoo 0.952→0.961）；最小的几类本就 0.995 无需再抬。

![逐类对比](report_assets/percls_compare.png)

### 12x 训练曲线（训练中断后补绘）
![12x 训练曲线](runs/detect/runs/snacks_12x_balanced/results.png)

---

## 4. 识别服务集成（三模型可选）

### 架构
```
前端 recognize.html  ──POST 图片+model──▶  FastAPI 识别服务(:8123, GPU)  ──▶  3 个 YOLO best.pt
   (下拉选模型/画框/列表)         CORS              (启动时全部加载到 cuda:0)
```

### 服务：`yolo-snacks/reco_service.py`
- 启动时把 3 个模型全部加载到 `cuda:0`（无 GPU 自动回退 cpu）。
- 接口：
  - `GET /health` → `{status, device, models}`
  - `GET /models` → `[{key,label,note}]`（11s_balanced 默认在最前）
  - `POST /recognize`（multipart：`file` 图片 + `model` 键）→ `{model,label,device,count,image_w,image_h,infer_ms,detections:[{name,conf,box:[x1,y1,x2,y2]}]}`
- 模型键：`11s_balanced`（推荐/默认）、`11s_base`（原始）、`12x_balanced`。

### 前端：`Week1/shop-frontend/recognize.html`
- 顶部**分段按钮选择器**（从 `/models` 拉取，失败用兜底），默认 11s_balanced；
- 上传图片后 POST 到服务，在图上用 `<canvas>` 叠加**陶土色检测框 + 标签**，下方用置信度条列出每个目标；
- 汇总行显示「模型 · 设备 · 用时 · 目标数」；
- 服务不可达时优雅降级为示例结果（toast 提示），页面不报错。

### 启动方式
```powershell
# 1) 启动识别服务（GPU 加载 3 模型）
& "E:\Code\Yueqian\yolo-snacks\.venv\Scripts\python.exe" "E:\Code\Yueqian\yolo-snacks\reco_service.py"
# 2) 打开前端识别页（Docker nginx 或本地预览）
#    http://localhost:8088/recognize.html   或   http://localhost:5500/recognize.html
```

### 端到端验证结果（test 真图，cuda:0）
- `/health`：`{"status":"ok","device":"cuda:0","models":["11s_balanced","11s_base","12x_balanced"]}`
- 同一张图：11s+过采样测出 **3 个目标**（Cheetoz snack 90g 0.976 / Maz Maz vinegar chips 0.955 / Minoo cream biscuit 0.943，22.5ms）；12x 测出 4 个。
- 前端实测：选择器三段正常、默认选中 11s+过采样、画框 + 置信度条 + 汇总行全部正确，模型切换即时重识别。

> 端口说明：默认 8000 被本机其他进程占用，已改用 **8123**（服务与前端 `RECO` 均已同步）。

---

## 5. 文件清单

| 文件 | 说明 |
|---|---|
| `runs/detect/runs/snacks/` | ① 11s 原始 训练产物（best.pt / results.png） |
| `runs/detect/runs/snacks_11s_balanced/` | ② 11s+过采样 训练产物（**部署权重** best.pt） |
| `runs/detect/runs/snacks_12x_balanced/` | ③ 12x+过采样 训练产物（best.pt / 补绘 results.png） |
| `report_assets/percls_compare.png` | 逐类 mAP50-95 三模型对比图 |
| `report_assets/overall_compare.png` | 整体指标对比图 |
| `report_assets/loss_curves.png` | 验证 loss 曲线（过拟合检查） |
| `reco_service.py` | 多模型识别服务（FastAPI） |
| `per_class_val*.py` / `_test_eval.py` / `_make_plots.py` | 验证 / 评估 / 出图脚本 |
| `Week1/shop-frontend/recognize.html` | 识别页（三模型可选 + 画框） |
| `TRAINING_REPORT.md` / `MODEL_REPORT.md` | 训练报告 / 本对比报告 |

---

## 6. 选型结论

**部署权重 = `runs/detect/runs/snacks_11s_balanced/weights/best.pt`（YOLO11s + 过采样）**
理由：验证集 mAP50-95 三者最高、测试集与最优仅差 0.0015、推理最快、模型最小；过采样净提升泛化且对中等难度类有针对性改善。12x 作为"吃满 GPU 的大模型对照"保留，结论是"再大也已到顶"。
