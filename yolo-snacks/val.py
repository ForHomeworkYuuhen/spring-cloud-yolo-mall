"""
YOLO 验证脚本 - 在验证集上评估模型性能
（适配本项目：YOLO11s + 过采样 部署模型 / data_balanced.yaml / RTX 5070 Ti 12GB）
"""
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if sys.version_info < (3, 8):
    import subprocess
    _orig = subprocess.list2cmdline
    subprocess.list2cmdline = lambda seq: _orig([str(x) if not isinstance(x, str) else x for x in seq])

from ultralytics import YOLO

def main():
    # 本项目部署模型：YOLO11s + 过采样
    model = YOLO(r"E:\Code\Yueqian\yolo-snacks\runs\detect\runs\snacks_11s_balanced\weights\best.pt")

    results = model.val(
        data=r"E:\Code\Yueqian\yolo-snacks\data_balanced.yaml",
        device=0,
        batch=16,            # RTX 5070 Ti 12GB，可比 3060 调大
        imgsz=640,
        conf=0.001,
        iou=0.6,
        max_det=300,
        half=True,
        workers=0,
        project=r"E:\Code\Yueqian\yolo-snacks\runs\val",
        name="snacks_val",
        exist_ok=True,
        plots=True,
    )

    metrics = results.results_dict
    print("=" * 60)
    print("验证结果:")
    print(f"  mAP50:     {metrics.get('metrics/mAP50(B)', 0):.4f}")
    print(f"  mAP50-95:  {metrics.get('metrics/mAP50-95(B)', 0):.4f}")
    print(f"  Precision: {metrics.get('metrics/precision(B)', 0):.4f}")
    print(f"  Recall:    {metrics.get('metrics/recall(B)', 0):.4f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
