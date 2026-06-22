"""
训练 YOLO12x（YOLO12 最大模型），用 batch=0.85 撑满显存，尽量压榨 RTX 5070 Ti。
"""
import os
import glob
import yaml
import time
import torch
from ultralytics import YOLO

DATASET_DIR = r"E:\Code\Yueqian\archive\Iranian Snack and Chips Detection (YOLO Format)"
MODEL = "yolo12x.pt"   # YOLO12 最大模型
EPOCHS = 100
IMGSZ = 640
BATCH = 12             # YOLO12x@640 显式 batch（auto-batch 在 12x 上会回退成 1）；12 约吃 9~10G 撑满卡且不易OOM
DEVICE = 0
WORKERS = 0            # Windows 上多 worker 触发页面文件错误，0 最稳
NAME = "snacks_12x"


def find_data_yaml(root):
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
        d["val"] = train
    if test:
        d["test"] = test
    d.pop("path", None)
    fixed = os.path.join(root, "data_fixed.yaml")
    yaml.safe_dump(d, open(fixed, "w", encoding="utf-8"), allow_unicode=True, sort_keys=False)
    return fixed


def main():
    data_yaml = resolve_yaml(find_data_yaml(DATASET_DIR))
    print("data:", data_yaml)
    print(f"Model={MODEL} epochs={EPOCHS} imgsz={IMGSZ} batch={BATCH}(按85%显存自动) device={DEVICE}")
    t0 = time.time()
    model = YOLO(MODEL)
    model.train(data=data_yaml, epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH,
                device=DEVICE, workers=WORKERS, cache=True,
                project="runs", name=NAME, patience=20)
    dt = time.time() - t0
    try:
        peak = "%.2f GB" % (torch.cuda.max_memory_reserved(DEVICE) / 1e9)
    except Exception:
        peak = "(见 nvidia-smi)"
    print("==================================================")
    print(f"YOLO12x 训练完成：用时 {dt/60:.1f} 分钟，峰值显存 {peak} / 12.8 GB")
    print("最佳权重：runs/<...>/snacks_12x/weights/best.pt")


if __name__ == "__main__":
    main()
