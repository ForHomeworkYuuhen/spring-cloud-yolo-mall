# 逐类验证：用当前 best.pt 在 val 集上输出每个类别的 mAP（CPU，不抢训练显存）
from ultralytics import YOLO

W = r"E:\Code\Yueqian\yolo-snacks\runs\detect\runs\snacks_12x_balanced\weights\best.pt"
DATA = r"E:\Code\Yueqian\yolo-snacks\data_balanced.yaml"

m = YOLO(W)
r = m.val(data=DATA, split="val", device="cpu", batch=4, workers=0,
          verbose=True, plots=False,
          project=r"E:\Code\Yueqian\yolo-snacks\runs", name="val_percls", exist_ok=True)

names = m.names
idx = list(r.box.ap_class_index)
ap50 = r.box.ap50   # 每类 AP@0.5
ap = r.box.ap       # 每类 AP@0.5:0.95 (mAP50-95)

rows = [(names[ci], float(ap50[i]), float(ap[i])) for i, ci in enumerate(idx)]
rows.sort(key=lambda x: x[2])  # 按 mAP50-95 升序，最弱的排最上面

print("\n================ 逐类汇总（按 mAP50-95 升序，最弱在上）================")
print(f"{'类别':<34}{'mAP50':>9}{'mAP50-95':>11}")
for n, a50, a in rows:
    flag = "   <== 偏低" if a < 0.85 else ("   <- 一般" if a < 0.92 else "")
    print(f"{n:<34}{a50:>9.3f}{a:>11.3f}{flag}")

print(f"\n整体: mAP50={float(r.box.map50):.4f}  mAP50-95={float(r.box.map):.4f}  类别数={len(idx)}")
print("（注：ultralytics 上方表格的 Instances 列即各类验证集样本数）")
