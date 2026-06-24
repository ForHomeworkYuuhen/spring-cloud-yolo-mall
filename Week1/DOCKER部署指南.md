# Docker 一键部署指南（给队友）

这套微服务（商品 / 订单 / 用户 / 网关 + Nacos / Sentinel / Zipkin / MySQL + 前端）全部用 Docker 跑，**不用装 JDK、Maven、MySQL、Nacos**，只要有 Docker 就能起。

## 一、前置条件

- 安装 **Docker Desktop**（Windows / macOS）或 **Docker Engine + compose 插件**（Linux），并启动它。
- 第一次启动会联网下载基础镜像和 Maven 依赖，需要能正常访问网络。

## 二、一键启动

进入 `Week1` 目录：

- **Windows**：`.\start.ps1`
- **Linux / macOS**：`bash start.sh`

脚本会自动 `docker compose up -d --build` 构建并启动全部容器，等网关就绪，并自动处理一个已知的启动时序问题（见下方"常见问题"）。

> 也可以手动：`docker compose up -d --build`

首次构建大约几分钟（要下依赖、编译 4 个 Java 服务），之后启动很快。

## 三、访问入口

| 服务 | 地址 | 账号 / 说明 |
|---|---|---|
| 前端首页 | http://localhost:8088 | 仿淘宝首页 + 登录注册 + 商品识别入口 |
| 网关 Gateway | http://localhost:9000 | 访问商品接口要带 `?token=123`，如 `http://localhost:9000/admin/products/1?token=123` |
| Nacos 控制台 | http://localhost:8848/nacos | `nacos` / `nacos` |
| Sentinel 控制台 | http://localhost:8080 | `sentinel` / `sentinel` |
| Zipkin 链路追踪 | http://localhost:9411 | 免登录 |
| MySQL | localhost:**3307** | root / `12345`（主机端口用 3307 避免和本机已有 MySQL 的 3306 冲突；容器间走内部 `mysql:3306`） |

## 四、常见问题

1. **端口被占用**（如 8080 / 9000 / 3307 / 8848 启动报 `port is already allocated`）
   → 本机已有程序占了这些端口。改 `docker-compose.yml` 里对应服务的宿主机端口（冒号左边）即可，例如 `"3307:3306"` 改成 `"3308:3306"`。

2. **网关返回 500 或无响应、Nacos 控制台里看不到服务**
   → Java 服务偶尔会"抢跑"在 Nacos 注册服务完全就绪之前启动、注册失败。**重启业务服务**即可（`start` 脚本已自动做这一步）：
   ```
   docker compose restart gateway product-server order-server user-server
   ```

3. **首次构建很慢 / 卡住**
   → 在下 Maven 依赖。耐心等；网络差可多等或重试 `docker compose up -d --build`。

4. **想清空数据库重来**
   → `docker compose down -v`（`-v` 会删掉数据库数据卷），再 `up` 会重新执行 `sql/` 下的建库建表脚本。

## 五、说明

- "**商品识别**"（YOLO 图像识别）的 AI 推理服务**不在这个 Docker 包里**——它需要 NVIDIA GPU + 模型权重，单独运行（见仓库 `yolo-snacks/reco_service.py`）。前端识别页在没连上该服务时会**用示例结果兜底**，不影响其余功能演示。
- 停止全部：`docker compose down`。
