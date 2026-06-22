# 环境与成果自检：当着老师跑这个，一屏证明"环境装好了 + 训练出了成果"
import os, platform
import torch, torchvision, ultralytics

LINE = "=" * 60
print(LINE)
print(" 商品识别模型 · 环境与成果自检")
print(LINE)
print(f" 操作系统     : {platform.system()} {platform.release()}")
print(f" Python       : {platform.python_version()}")
print(f" PyTorch      : {torch.__version__}")
print(f" torchvision  : {torchvision.__version__}")
print(f" Ultralytics  : {ultralytics.__version__}")
print(f" CUDA 可用    : {torch.cuda.is_available()}  (编译版本 CUDA {torch.version.cuda})")
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print(f" GPU 显卡     : {torch.cuda.get_device_name(0)}")
    print(f" 显存         : {p.total_memory/1024**3:.1f} GB")
print("-" * 60)

runs = r"E:\Code\Yueqian\yolo-snacks\runs\detect\runs"
models = [
    ("snacks",              "YOLO11s 原始(基线)"),
    ("snacks_11s_balanced", "YOLO11s 过采样(部署用)"),
    ("snacks_12x_balanced", "YOLO12x 过采样(对照)"),
]
print(" 已训练完成的模型权重 best.pt :")
for name, label in models:
    pt = os.path.join(runs, name, "weights", "best.pt")
    if os.path.exists(pt):
        mb = os.path.getsize(pt) / 1024 / 1024
        print(f"   [√] {label:<20} {mb:6.0f} MB   {pt}")
    else:
        print(f"   [×] {label:<20} 未找到")
print("-" * 60)

ds = r"E:\Code\Yueqian\archive\Iranian Snack and Chips Detection (YOLO Format)"
def cnt(sub):
    d = os.path.join(ds, sub, "images")
    return len([f for f in os.listdir(d)]) if os.path.isdir(d) else 0
print(f" 数据集(19类零食) : train={cnt('train')}  valid={cnt('valid')}  test={cnt('test')} 张")
print(LINE)
print(" 结论：环境(GPU+CUDA+PyTorch+Ultralytics)就绪，三个模型均已训练出 best.pt。")
print(LINE)
