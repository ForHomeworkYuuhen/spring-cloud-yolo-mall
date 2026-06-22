# 项目总览 · 广东海洋大学23级信管专业实训（电商·仿淘宝微服务）

> 本文件用于固化项目上下文（技术栈、模块、进度、入口），便于跨会话延续。

## 一、项目定位
仿淘宝的**企业级电商微服务项目**。前台首页有两个 AI 入口：
- **商品识别**：上传图片 → 目标检测模型识别商品（YOLO）。
- **热门推荐**：基于用户行为的个性化推荐（LSTM，**待后续补充**）。

## 二、技术栈（图片要求 + 已落地 + 自行补充）
| 类别 | 技术 | 状态 |
|---|---|---|
| 语言/构建 | Java 8、Maven、Git | ✅ |
| 微服务框架 | SpringBoot 2.3.2 + MyBatis-Plus + **Spring Cloud Alibaba 2.2.3**（Hoxton.SR8）| ✅ Week1 已实现 |
| 服务治理 | **Nacos**(注册/配置)、**Sentinel**(流控容错)、**Gateway**(网关)、OpenFeign、Sleuth+Zipkin(链路) | ✅ Week1 |
| 数据库/缓存 | **MySQL**、Redis、Redisson(分布式锁/秒杀) | MySQL✅ / Redis 待集成 |
| 中间件 | RocketMQ(消息)、Elasticsearch(商品检索/推荐)、XXL-JOB(分布式调度) | 待集成 |
| 分布式事务 | **Seata** | 待集成 |
| 存储/通信/支付 | 阿里云 OSS、WebSocket(实时)、微信支付 | 待集成 |
| 可视化 | ECharts(运营数据多维分析) | 待集成 |
| 部署 | **Docker / docker-compose** | ✅ 全栈容器化(7容器) |
| **AI-商品识别** | **YOLO**(目标检测) | 🔄 训练中(见下) |
| **AI-推荐** | **LSTM** | ⏳ 待补充 |
| 前端 | HTML/CSS/JS(仿淘宝)，调用网关 | ✅ shop-frontend |

## 三、已完成模块
### 1) 微服务（`Week1/shop-parent/`，Day1~Day6 全部实现）
- `shop-gateway` :9000（路由/鉴权/Sentinel限流；访问需 `?token=123`）
- `shop-product-server` :8081（商品；Nacos配置中心；Sleuth/Zipkin）
- `shop-order-server` :8091（订单；Feign调商品；Sentinel全套）
- `shop-product-api / shop-order-api`（实体）
- 已**全栈容器化**：`docker compose up -d --build`（mysql/nacos/zipkin/sentinel + 三服务，共7容器）
- 数据：t_product(小米1000/华为2000/苹果3000/OPPO4000)、t_order；服务名 `shop-product-service`/`shop-order-service`
- 详见 `Week1/README.md`

### 2) 商品识别模型（`yolo-snacks/`）
- 环境：Python 3.12(uv venv) + torch 2.11.0+cu128 + ultralytics 8.4.68；GPU **RTX 5070 Ti Laptop 12G(sm_120)**
- 数据集：`archive/Iranian Snack...(YOLO Format)`，19类零食，train452/val91/test60
- **YOLO11s**：已训完，mAP50=0.994、mAP50-95=0.985（`runs/detect/runs/snacks/weights/best.pt`）
- **YOLO12x（均衡+强增强）训练中**：过采样452→1056(按最稀有类复制≤5x)、mixup0.15、batch6(显存~11.2G不溢出)、workers=0
  - 脚本：`train_balanced.py`；产物：`runs/detect/runs/snacks_12x_balanced/weights/best.pt`

## 四、前端（`Week1/shop-frontend/`，本次新增）
- `login.html` 登录/注册（仿淘宝橙红风，标签切换）
- `index.html` 首页（仿淘宝：顶部搜索 + **两入口：商品识别/热门推荐** + 分类导航 + 轮播 + 商品网格）
- `recognize.html` 商品识别（上传图片→调用识别服务，YOLO模型就绪后接 `/recognize`）
- `js/app.js`：商品数据(优先调网关`/admin/products/{id}?token=123`，失败回退mock)、登录态(localStorage)、识别上传
- 设计为调用网关 :9000；网关未起时自动用 mock 数据，可独立预览

## 五、待办（优先级）
1. 推荐模型 LSTM（用户后续补充）→ 接首页"热门推荐"
2. 商品识别服务：把 YOLO best.pt 包成推理服务(FastAPI/Flask 或 Java 调用) → 网关 `/recognize`
3. 集成 Redis/RocketMQ/ES/Seata/OSS/微信支付/XXL-JOB/WebSocket/ECharts（按实训清单）
4. 用户服务(登录注册后端) + JWT
