"""
类别均衡 + 强增强 训练 YOLO12x。
- 过采样：按"图片中最稀有类"决定复制倍数，写入图片列表 txt（不复制文件，列表里重复行即过采样）
- 强增强：mixup / 小角度旋转 / HSV / mosaic
- val/test 用原始集（在真实分布上评估）
"""
import os
import glob
import collections
import yaml
from ultralytics import YOLO

BASE = r"E:\Code\Yueqian\archive\Iranian Snack and Chips Detection (YOLO Format)"
WORKDIR = r"E:\Code\Yueqian\yolo-snacks"

TARGET = 120      # 每类过采样目标图片数
MAXDUP = 5        # 单张图最大复制倍数
MODEL = "yolo12x.pt"
EPOCHS = 100
IMGSZ = 640
BATCH = 6         # YOLO12x@640：约占 10.6G，填满显存但不溢出(batch=10 会超12G→换内存抖动慢100倍)
DEVICE = 0
WORKERS = 0
NAME = "snacks_12x_balanced"


def label_of(img):
    return img.replace(os.sep + "images" + os.sep, os.sep + "labels" + os.sep).rsplit(".", 1)[0] + ".txt"


def classes_in(lbl):
    s = set()
    if os.path.exists(lbl):
        for ln in open(lbl):
            t = ln.split()
            if t:
                s.add(int(t[0]))
    return s


def main():
    names = yaml.safe_load(open(os.path.join(BASE, "data.yaml"), encoding="utf-8"))["names"]
    train_imgs = sorted(glob.glob(os.path.join(BASE, "train", "images", "*.*")))

    imgcount = collections.Counter()
    img_classes = {}
    for im in train_imgs:
        cs = classes_in(label_of(im))
        img_classes[im] = cs
        for c in cs:
            imgcount[c] += 1

    lines = []
    eff = collections.Counter()
    for im in train_imgs:
        cs = img_classes[im]
        f = 1 if not cs else max(1, min(MAXDUP, round(TARGET / min(imgcount[c] for c in cs))))
        for _ in range(f):
            lines.append(im.replace("\\", "/"))
            for c in cs:
                eff[c] += 1

    txt = os.path.join(WORKDIR, "train_oversampled.txt")
    with open(txt, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    data = {
        "train": txt.replace("\\", "/"),
        "val": os.path.join(BASE, "valid", "images").replace("\\", "/"),
        "test": os.path.join(BASE, "test", "images").replace("\\", "/"),
        "nc": len(names),
        "names": names,
    }
    dy = os.path.join(WORKDIR, "data_balanced.yaml")
    yaml.safe_dump(data, open(dy, "w", encoding="utf-8"), allow_unicode=True, sort_keys=False)

    print("过采样: %d 行 (原 %d 张)" % (len(lines), len(train_imgs)))
    print("每类有效图片数（过采样后，按原始升序）:")
    for c in sorted(range(len(names)), key=lambda c: imgcount[c]):
        print("  cls%2d  原%3d -> %4d  %s" % (c, imgcount[c], eff[c], names[c]))
    print("Model=%s batch=%d imgsz=%d epochs=%d" % (MODEL, BATCH, IMGSZ, EPOCHS))

    model = YOLO(MODEL)
    model.train(
        data=dy, epochs=EPOCHS, imgsz=IMGSZ, batch=BATCH, device=DEVICE,
        workers=WORKERS, cache=True, project="runs", name=NAME, patience=30,
        # 强增强（提升稀有类泛化）
        mosaic=1.0, mixup=0.15, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
        degrees=5.0, translate=0.1, scale=0.5, fliplr=0.5, close_mosaic=10,
    )
    print("训练完成。best.pt 在 runs/.../%s/weights/best.pt" % NAME)


if __name__ == "__main__":
    main()
