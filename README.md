# 微服务智能商城 · Spring Cloud Alibaba + YOLO 商品识别

一个微服务实训项目：基于 Spring Cloud Alibaba 的电商后端 + 仿淘宝前端，并集成了基于 YOLO 的「商品识别」能力（上传图片，模型框出并识别其中的商品）。

## 技术栈

**后端（微服务）**
- Spring Boot 2.3.2 / Spring Cloud Hoxton.SR8 / Spring Cloud Alibaba 2.2.3，JDK 8
- Nacos（服务注册 + 配置中心）、Ribbon + OpenFeign（负载均衡 / 声明式调用）
- Sentinel（流控、降级、热点、授权、网关限流）、Spring Cloud Gateway（路由 / 鉴权 / 限流）
- Sleuth + Zipkin（链路追踪）、MyBatis-Plus + MySQL、BCrypt（密码加密）
- 全部容器化：`docker-compose` 一键拉起 MySQL / Nacos / Sentinel / Zipkin + 各微服务

**前端**
- 原生 HTML / CSS / JS，编辑杂志风；首页两个入口：商品识别、热门推荐

**AI 商品识别**
- Ultralytics YOLO（YOLO11s / YOLO12x），PyTorch（CUDA 12.8），GPU 训练
- 类别不均衡的过采样处理；模型接成 FastAPI 在线识别服务

## 目录结构

```
Week1/                     # 微服务后端 + 前端
  shop-parent/             #   Maven 多模块（gateway / product / order / user）
  shop-frontend/           #   前端页面（首页 / 登录注册 / 商品识别）
  sql/                     #   建库建表脚本
  nacos-config/            #   Nacos 配置中心的配置文件
  docker-compose.yml       #   一键启动全栈
yolo-snacks/               # 商品识别模型训练 / 推理
  train_11s_balanced.py    #   训练（过采样 + GPU）
  per_class_val_*.py       #   逐类精度验证
  reco_service.py          #   FastAPI 在线识别服务
  MODEL_REPORT.md          #   三模型对比与选型
```

## 快速开始

**后端（Docker）**
```bash
cd Week1
docker compose up -d        # 启动 MySQL / Nacos / Sentinel / Zipkin + 微服务
# 前端：http://localhost:8088    网关：http://localhost:9000
# Nacos：http://localhost:8848/nacos   Sentinel：http://localhost:8080
```

**模型训练 / 推理**
```bash
# 需自备 GPU 环境（Python 3.12 + PyTorch cu128 + ultralytics）
python train_11s_balanced.py     # 训练
python reco_service.py           # 启动识别服务（:8123）
```

## 说明

- **数据集与模型权重未包含在仓库内**（体积较大且数据集有各自许可）。零食检测数据集为 Kaggle「Iranian Snack and Chips Detection (YOLO Format)」，训练脚本支持用 `kagglehub` 自动下载。
- 仓库内的 `12345`、`token=123` 等均为本地教学演示用的占位值，非真实凭据。
- 部分脚本中的路径为本地绝对路径，克隆后按需调整。
