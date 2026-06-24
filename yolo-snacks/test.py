"""
YOLO 测试脚本 - 在测试集上运行推理并生成结果
（适配本项目：YOLO11s + 过采样 部署模型 / 我们的测试集 / RTX 5070 Ti 12GB）
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

    results = model.predict(
        source=r"E:\Code\Yueqian\archive\Iranian Snack and Chips Detection (YOLO Format)\test\images",
        device=0,
        imgsz=640,
        conf=0.25,
        iou=0.45,
        max_det=300,
        half=True,
        project=r"E:\Code\Yueqian\yolo-snacks\runs\test",
        name="snacks_test",
        exist_ok=True,
        save=True,
        save_txt=True,
        save_conf=True,
        line_width=2,
    )

    print("=" * 60)
    print(f"测试完成！检测了 {len(results)} 张图片")
    print(r"检测结果图片保存在: E:\Code\Yueqian\yolo-snacks\runs\test\snacks_test\\")
    print(r"检测标签保存在:   E:\Code\Yueqian\yolo-snacks\runs\test\snacks_test\labels\\")
    print("=" * 60)

if __name__ == "__main__":
    main()
