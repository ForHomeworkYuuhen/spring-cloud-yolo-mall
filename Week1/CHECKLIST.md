# 技术栈落地清单（对照实训方案）

✅ 已实现 ｜ 🟡 部分/脚手架 ｜ ⬜ 未开始

| # | 实训要求技术 | 状态 | 落地位置 / 说明 |
|---|---|---|---|
| 1 | Java + Maven + Git | ✅ | 全工程；多模块 Maven |
| 2 | MySQL 设计与优化 | ✅ | shop-product / shop-order / shop-user 三库；`sql/*.sql` |
| 3 | SpringBoot + MyBatis-Plus | ✅ | 所有微服务 |
| 4 | Spring Cloud Alibaba | ✅ | Nacos + Sentinel + Gateway + OpenFeign + Sleuth/Zipkin |
| 5 | Nacos 注册/配置中心 | ✅ | 全服务注册；商品服务配置中心(Day5) |
| 6 | Sentinel 流控容错 | ✅ | 订单服务全套规则 + 网关限流 |
| 7 | Gateway 网关 | ✅ | 路由/鉴权/路径重写/限流；`/user/**` 公开 |
| 8 | Docker 容器化 | ✅ | docker-compose：mysql/nacos/zipkin/sentinel + 商品/订单/网关/**用户**/**前端** |
| 9 | 用户登录注册 + 安全 | ✅ | shop-user-server；**BCrypt 加密**；前端登录页对接 |
| 10 | **商品识别(YOLO)** | 🟡 | 模型已训(11s mAP0.994 / 12x 训练中)；待包成推理服务接 `/recognize` |
| 11 | 前端(仿淘宝, 两入口) | ✅ | shop-frontend：首页/登录/识别，编辑杂志风 |
| 12 | Redis 缓存 | ⬜ | 计划：商品详情/列表缓存（你机器已有 redis 容器） |
| 13 | Redisson 分布式锁/秒杀 | ⬜ | 计划：秒杀场景 |
| 14 | RocketMQ 消息队列 | ⬜ | 计划：下单异步/削峰 |
| 15 | Elasticsearch 商品检索 | ⬜ | 计划：首页搜索接 ES |
| 16 | Seata 分布式事务 | ⬜ | 计划：下单跨服务(扣库存+建订单)一致性 |
| 17 | 阿里云 OSS | ⬜ | 计划：商品图/识别图上传 |
| 18 | WebSocket 实时通信 | ⬜ | 计划：订单状态/客服 |
| 19 | 微信支付 | ⬜ | 计划：订单支付 |
| 20 | XXL-JOB 分布式调度 | ⬜ | 计划：定时任务(对账/榜单) |
| 21 | ECharts 数据可视化 | ⬜ | 计划：运营看板 |
| 22 | **LSTM 推荐模型** | ⬜ | 你后续补充；接首页"热门推荐" |

> 结论：**核心微服务骨架 + 容器化 + 商品识别 + 用户/前端**已就绪；**中间件与第二个 AI（推荐）大多待落地**——这也是你"感觉还有没用到"的原因。建议优先级：Redis 缓存 → ES 检索 → Seata 下单事务 → RocketMQ → 其余。
