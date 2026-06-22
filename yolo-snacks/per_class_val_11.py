# 对 YOLO11s 的 best.pt 做逐类验证，验证集与 12x 完全相同（data_balanced.yaml 的 val）
from ultralytics import YOLO

W = r"E:\Code\Yueqian\yolo-snacks\runs\detect\runs\snacks\weights\best.pt"
DATA = r"E:\Code\Yueqian\yolo-snacks\data_balanced.yaml"  # val 路径与 12x 一致

m = YOLO(W)
r = m.val(data=DATA, split="val", device="cpu", batch=4, workers=0,
          verbose=True, plots=False,
          project=r"E:\Code\Yueqian\yolo-snacks\runs", name="val_percls_11", exist_ok=True)

names = m.names
idx = list(r.box.ap_class_index)
ap50 = r.box.ap50
ap = r.box.ap

rows = [(names[ci], float(ap50[i]), float(ap[i])) for i, ci in enumerate(idx)]
rows.sort(key=lambda x: x[2])

print("\n================ YOLO11s 逐类（按 mAP50-95 升序）================")
print(f"{'类别':<34}{'mAP50':>9}{'mAP50-95':>11}")
for n, a50, a in rows:
    print(f"{n:<34}{a50:>9.3f}{a:>11.3f}")

print(f"\nYOLO11s 整体: mAP50={float(r.box.map50):.4f}  mAP50-95={float(r.box.map):.4f}  类别数={len(idx)}")
