"""
拉取 Kaggle「伊朗零食/薯片检测（YOLO 格式）」数据集并训练 YOLO11。
针对 RTX 5070 Ti Laptop (12GB) 调参。

运行： .venv/Scripts/python.exe train.py
依赖： kagglehub（需先配好 ~/.kaggle/kaggle.json）、ultralytics、torch(cu128)
"""
import os
import glob
import yaml
from ultralytics import YOLO

# 本地数据集目录（已手动下载到 archive）；留空则改用 kagglehub 在线下载
DATASET_DIR = r"E:\Code\Yueqian\archive\Iranian Snack and Chips Detection (YOLO Format)"

# ===== 可调参数 =====
MODEL = "yolo11s.pt"   # n=最快 / s=性价比(推荐) / m=更准 / l=接近上限 / x=最准但慢
EPOCHS = 100
IMGSZ = 640
BATCH = 16             # 12GB 显存下 s/m@640 安全；想更快可调大(如 32)，或设 -1 让其自动
DEVICE = 0             # 用第一块 GPU
WORKERS = 0            # Windows 上多 worker 会触发 "页面文件太小"(WinError 1455)，置 0 在主进程加载最稳


def find_data_yaml(root):
    """在下载目录里找 YOLO 的 data.yaml。"""
    direct = glob.glob(os.path.join(root, "**", "data.yaml"), recursive=True)
    if direct:
        return direct[0]
    for y in glob.glob(os.path.join(root, "**", "*.yaml"), recursive=True):
        try:
            d = yaml.safe_load(open(y, encoding="utf-8"))
            if isinstance(d, dict) and ("train" in d or "names" in d):
                return y
        except Exception:
            pass
    return None


def resolve_yaml(yaml_path):
    """把 data.yaml 里的 train/val/test 改成绝对路径，避免相对路径找不到图片。"""
    root = os.path.dirname(os.path.abspath(yaml_path))
    d = yaml.safe_load(open(yaml_path, encoding="utf-8"))

    def find_split(*names):
        for n in names:
            for cand in (os.path.join(root, n, "images"), os.path.join(root, n)):
                if os.path.isdir(cand) and glob.glob(os.path.join(cand, "*")):
                    return cand.replace("\\", "/")
        return None

    train = find_split("train")
    val = find_split("valid", "val")
    test = find_split("test")
    if train:
        d["train"] = train
    if val:
        d["val"] = val
    elif train:
        d["val"] = train  # 没有验证集就退而用训练集
    if test:
        d["test"] = test
    d.pop("path", None)  # 已用绝对路径，去掉相对根
    fixed = os.path.join(root, "data_fixed.yaml")
    yaml.safe_dump(d, open(fixed, "w", encoding="utf-8"), allow_unicode=True, sort_keys=False)
    return fixed, d


def main():
    if DATASET_DIR and os.path.isdir(DATASET_DIR):
        path = DATASET_DIR
    else:
        import kagglehub
        path = kagglehub.dataset_download("halfbloodhamed/iranian-snack-and-chips-detection-yolo-format")
    print("Dataset path:", path)

    # 打印目录结构（前两层），方便核对
    print("---- 数据集结构 ----")
    for r, dirs, files in os.walk(path):
        depth = r[len(path):].count(os.sep)
        if depth <= 2:
            print("  " * depth + (os.path.basename(r) or r) + f"  ({len(files)} files)")

    yp = find_data_yaml(path)
    if not yp:
        raise SystemExit("未找到 data.yaml，请根据上面的结构手动指定。")
    print("Found data.yaml:", yp)

    data_yaml, d = resolve_yaml(yp)
    print("Using data file:", data_yaml)
    print("Classes:", d.get("names"))
    print(f"Model={MODEL}  epochs={EPOCHS}  imgsz={IMGSZ}  batch={BATCH}  device={DEVICE}")

    model = YOLO(MODEL)
    model.train(
        data=data_yaml,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=DEVICE,
        workers=WORKERS,
        cache=True,
        project="runs",
        name="snacks",
        patience=20,   # 20 轮无提升则早停
    )
    print("训练完成。最佳权重：runs/snacks*/weights/best.pt")


if __name__ == "__main__":
    main()
