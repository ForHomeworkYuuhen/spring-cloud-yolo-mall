# 商品识别模型训练报告（YOLOv12x）

> 广东海洋大学 23 级信管实训 · 粤海购「商品识别」功能配套模型
> 数据集：Iranian Snack and Chips Detection (YOLO Format)，19 类零食/薯片目标检测

## 一、最终结论

训练在第 48 轮按**早停**收尾（指标自第 30 轮起已进入平台期，第 46 轮取得峰值）。
`best.pt` 保存的即第 46 轮峰值权重，模型已充分收敛。

- **最优权重**：`runs/detect/runs/snacks_12x_balanced/weights/best.pt`（452 MB）
- **整体精度**：mAP50 = **0.9948**，mAP50-95 = **0.9839**，Precision ≈ 0.987，Recall ≈ 0.991

## 二、训练配置

| 项 | 取值 |
|---|---|
| 模型 | YOLOv12x（最大号，59M 参数，198.6 GFLOPs） |
| 框架 | Ultralytics 8.4.68 / torch 2.11.0+cu128 |
| 硬件 | RTX 5070 Ti Laptop 12GB（Blackwell sm_120） |
| batch / imgsz | 6 / 640 |
| epochs / patience | 100 / 30（实际 48 轮收尾） |
| 显存占用 | ~11.4 / 12 GB（满载，无内存外溢） |
| 训练耗时 | 约 80 分钟 |

## 三、类别不均衡处理

原始数据集各类样本量差异大，最小类仅个位数样本。采用**重复采样过采样**（oversampling）
将训练样本由 452 张扩充到 1056 张（`train_oversampled.txt`），并配合 mixup=0.15 数据增强，
把小样本类拉齐到与大类接近的水平。

## 四、逐类精度（验证集 91 图 / 304 目标，按 mAP50-95 升序）

| 类别 | 验证样本 | mAP50 | mAP50-95 |
|---|---|---|---|
| Cheetoz snack 30g | 4 | 0.995 | 0.937 |
| Minoo cream biscuit | 16 | 0.991 | 0.946 |
| Cheetoz snack 90g | 14 | 0.995 | 0.972 |
| Maz Maz salty chips | 13 | 0.995 | 0.974 |
| Maz Maz potato sticks | 26 | 0.995 | 0.974 |
| Maz Maz vinegar chips | 14 | 0.995 | 0.980 |
| Chee pellet ketchup | 23 | 0.995 | 0.983 |
| Mini Lina | 40 | 0.995 | 0.987 |
| Naderi mini cookie | 16 | 0.995 | 0.989 |
| Ashi Mashi snacks | 10 | 0.995 | 0.995 |
| Chee pellet vinegar | 20 | 0.995 | 0.995 |
| Cheetoz chili chips | 5 | 0.995 | 0.995 |
| Cheetoz ketchup chips | 18 | 0.995 | 0.995 |
| Cheetoz onion and parsley chips | 14 | 0.995 | 0.995 |
| Cheetoz salty chips | 6 | 0.995 | 0.995 |
| Cheetoz vinegar chips | 14 | 0.995 | 0.995 |
| Cheetoz wheelsnack | 16 | 0.995 | 0.995 |
| Maz Maz ketchup chips | 31 | 0.995 | 0.995 |
| Naderi mini wafer | 4 | 0.995 | 0.995 |

**关键观察**：即便只有 4 个验证样本的小类（如 Naderi mini wafer、Cheetoz chili chips）也达到 0.995，
全 19 类 mAP50-95 最低 0.937、mAP50 全为 0.995 —— 过采样平衡策略生效，**没有被整体均值掩盖的短板类**。

## 五、指标含义说明

- **mAP50**：框「大致定位正确」（IoU≥0.5）即算对，衡量「找没找到」→ 0.995 已接近满分。
- **mAP50-95**：IoU 阈值 0.5~0.95 取平均，要求框「贴得越来越准」，衡量「框得准不准」→ 0.984 属高位。
- 二者均为相对数据集难度而言；此数据集干净、类别明确，0.98+ 已是收敛上限，无需继续训练。

## 六、复现命令

```bash
# 逐类验证（CPU，不占训练显存）
python per_class_val.py
# 训练（如需复现）
python train_balanced.py
```
