# -*- coding: utf-8 -*-
"""零食识别服务：基于 ultralytics YOLO 的多模型推理 HTTP 服务。"""
import time
from io import BytesIO

import torch
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from ultralytics import YOLO

# 设备选择：有 GPU 用 cuda:0，否则回退到 cpu
DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# 模型注册表：保持顺序，11s_balanced 在最前（部署默认）
MODEL_CONFIG = [
    {
        "key": "11s_balanced",
        "path": "E:/Code/Yueqian/yolo-snacks/runs/detect/runs/snacks_11s_balanced/weights/best.pt",
        "label": "YOLO11s · 过采样（推荐）",
        "note": "9.4M参数·最快·部署默认",
    },
    {
        "key": "11s_base",
        "path": "E:/Code/Yueqian/yolo-snacks/runs/detect/runs/snacks/weights/best.pt",
        "label": "YOLO11s · 原始",
        "note": "未过采样·对照基线",
    },
    {
        "key": "12x_balanced",
        "path": "E:/Code/Yueqian/yolo-snacks/runs/detect/runs/snacks_12x_balanced/weights/best.pt",
        "label": "YOLO12x · 过采样",
        "note": "59M参数·大模型对照",
    },
]

# 全局模型字典：key -> YOLO 实例
MODELS = {}

app = FastAPI(title="Yueqian Snacks Recognition Service")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_models():
    """启动时把所有模型加载进全局 MODELS，并绑定到目标设备。"""
    for cfg in MODEL_CONFIG:
        model = YOLO(cfg["path"])
        model.to(DEVICE)  # 统一放到选定设备
        MODELS[cfg["key"]] = model
        print(f"[load] {cfg['key']} -> {cfg['path']} ({DEVICE})")


@app.get("/health")
def health():
    """健康检查：返回设备与已加载模型键列表。"""
    return {"status": "ok", "device": DEVICE, "models": list(MODELS.keys())}


@app.get("/models")
def list_models():
    """返回模型元信息列表，保持注册顺序。"""
    return [{"key": c["key"], "label": c["label"], "note": c["note"]} for c in MODEL_CONFIG]


@app.post("/recognize")
async def recognize(file: UploadFile = File(...), model: str = Form("11s_balanced")):
    """对上传图片做目标检测，返回检测框与耗时等信息。"""
    try:
        # 校验模型 key
        if model not in MODELS:
            return JSONResponse(status_code=400, content={"error": f"unknown model: {model}"})

        # 读取上传图片并转为 RGB
        raw = await file.read()
        img = Image.open(BytesIO(raw)).convert("RGB")

        # 推理并记录毫秒耗时
        t0 = time.perf_counter()
        res = MODELS[model].predict(img, conf=0.25, verbose=False)[0]
        infer_ms = (time.perf_counter() - t0) * 1000.0

        # 解析检测框
        detections = []
        boxes = res.boxes
        if boxes is not None:
            for cls, conf, xyxy in zip(boxes.cls, boxes.conf, boxes.xyxy):
                x1, y1, x2, y2 = xyxy.tolist()
                detections.append({
                    "name": res.names[int(cls)],
                    "conf": round(float(conf), 3),
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                })
        # 按置信度降序
        detections.sort(key=lambda d: d["conf"], reverse=True)

        # 取当前模型 label
        label = next((c["label"] for c in MODEL_CONFIG if c["key"] == model), model)

        return {
            "model": model,
            "label": label,
            "device": DEVICE,
            "count": len(detections),
            "image_w": img.width,
            "image_h": img.height,
            "infer_ms": round(infer_ms, 1),
            "detections": detections,
        }
    except Exception as e:  # 兜底异常处理
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8123)
