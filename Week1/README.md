# Week1 — Spring Cloud Alibaba 电商微服务实战

本项目是对课程资料 `Day_01 ~ Day_06`（Nacos / Ribbon / Feign / Sentinel / Gateway / Nacos Config / Sleuth & Zipkin）
六天内容的**完整落地实现**：一个由「商品微服务 + 订单微服务 + API 网关」组成的电商微服务工程。
六天的功能是**累积**的，最终汇总到这一套可运行的工程里。

> 课程原始讲义（`Day_01 ~ Day_06` 的 Markdown 及配图）即随附的 `Markdown.rar`，可对照阅读。
> 如需放入本工程，解压后置于 `docs/` 目录即可。

---

## 一、技术选型与版本

| 组件 | 版本 |
| --- | --- |
| JDK | 1.8 |
| 构建工具 | Maven |
| Spring Boot | 2.3.2.RELEASE |
| Spring Cloud | Hoxton.SR8 |
| Spring Cloud Alibaba | 2.2.3.RELEASE |
| 持久层 | MyBatis-Plus 3.4.0 |
| 数据库 | MySQL（5.7 / 8.x 均可，URL 用的是 MySQL8 驱动 `com.mysql.cj.jdbc.Driver`）|
| 注册/配置中心 | Nacos（建议 1.3.2 及以上）|
| 流控容错 | Sentinel Dashboard 1.8.9 |
| 链路追踪 | Sleuth + Zipkin（zipkin-server 2.x）|
| 压测工具（可选）| Apache JMeter |

---

## 二、模块结构

```
shop-parent                      父工程（统一依赖版本管理 + 模块聚合）
├── shop-product-api             商品实体 Product（解耦，供 order 依赖）
├── shop-product-server  :8081   商品微服务（提供商品查询接口）
├── shop-order-api               订单实体 Order
├── shop-order-server    :8091   订单微服务（创建订单，远程调用商品服务）
└── shop-gateway         :9000   API 网关（路由 / 鉴权 / 限流）
```

服务在 Nacos 上注册的服务名：

| 微服务 | 服务名 | 端口 |
| --- | --- | --- |
| 商品 | `shop-product-service` | 8081（演示负载均衡再开一个 8082）|
| 订单 | `shop-order-service`   | 8091 |
| 网关 | `shop-gateway`         | 9000 |

> 说明：课程讲义里服务名在 `product-service` 与 `shop-product-service` 之间存在前后不一致。
> 本工程统一规范为 **`shop-product-service` / `shop-order-service`**（与 `application.yml` 中
> `spring.application.name` 以及网关 `lb://` 一致），Feign / Ribbon / Gateway 全部使用该名称，确保可运行。

---

## 三、准备工作

### 0. 用 Docker 一键运行整套项目（推荐）
项目根目录的 `docker-compose.yml` 已把 **全部 7 个容器**编排好：MySQL（自动建库建表）、Nacos、Zipkin、Sentinel 控制台，外加商品/订单/网关三个微服务（**容器内用 Maven 自动构建，无需本地装 Maven/JDK**）。

```powershell
cd E:\Code\Yueqian\Week1
docker compose up -d --build    # 首次拉镜像 + 容器内构建，耗时较久（取决于网络）
docker compose ps               # 等所有容器 Up（mysql 显示 healthy）
docker compose logs -f gateway  # 查看某个服务日志
docker compose down             # 停止（加 -v 连数据卷一起删）
```

容器与端口（均映射到宿主机 localhost）：

| 容器 | 端口 | 说明 |
| --- | --- | --- |
| shop-mysql | 3306 | 自动建 `shop-product`/`shop-order` 两库及数据，root/12345 |
| shop-nacos | 8848 | http://localhost:8848/nacos （nacos/nacos）|
| shop-zipkin | 9411 | http://localhost:9411 |
| shop-sentinel | 8080 | http://localhost:8080 （sentinel/sentinel）|
| shop-product-server | 8081 | 商品服务 |
| shop-order-server | 8091 | 订单服务 |
| shop-gateway | 9000 | 网关 |

- 容器间通过服务名互访（`application-docker.yml` / `bootstrap-docker.yml` 把地址改成 mysql/nacos/zipkin/sentinel-dashboard），全部在同一 compose 网络内，**Sentinel 规则下发也正常**。
- 验证：`http://localhost:8081/products/1`、`http://localhost:8091/orders/save?pid=1&uid=1`、`http://localhost:9000/product/hello?token=123`。
- **用了 Docker 就不必再做下面的「1. 数据库」「2. 中间件」两步，也不用在 IDEA 里启动服务。**
- 只想用 Docker 起依赖、三个服务仍在 IDEA 里跑？只起基础设施即可：`docker compose up -d mysql nacos zipkin sentinel-dashboard`。

### 1. 数据库
执行 `sql/` 下两个脚本（会自动建库建表并插入初始数据）：

```sql
source sql/shop-product.sql;   -- 库 shop-product，表 t_product
source sql/shop-order.sql;     -- 库 shop-order，表 t_order
```

然后把两个 `application.yml`（product / order）里的数据库 **用户名 / 密码** 改成你自己的。

### 2. 中间件（按需启动）

| 用途 | 启动命令 | 访问地址 |
| --- | --- | --- |
| Nacos（注册+配置中心）| `startup.cmd -m standalone` | http://localhost:8848/nacos （nacos/nacos）|
| Sentinel 控制台 | `java -Dserver.port=8080 -Dcsp.sentinel.dashboard.server=localhost:8080 -Dproject.name=sentinel-dashboard -jar sentinel-dashboard-1.8.9.jar` | http://localhost:8080 （sentinel/sentinel）|
| Zipkin | `java -jar zipkin-server-2.x-exec.jar` | http://localhost:9411 |

> JDK 17 启动 Sentinel 控制台需追加：`--add-opens java.base/java.lang=ALL-UNNAMED`

---

## 四、构建与运行

```bash
# 在 shop-parent 目录下
mvn clean install -DskipTests        # 编译并把 api 模块安装到本地仓库

# 分别启动（也可在 IDEA 中运行各自的启动类）
mvn -pl shop-product-server spring-boot:run
mvn -pl shop-order-server   spring-boot:run
mvn -pl shop-gateway        spring-boot:run
```

**演示负载均衡**：再启动一个商品实例（IDEA 中复制启动配置，或命令行）：

```bash
java -jar shop-product-server/target/shop-product-server-1.0-SNAPSHOT.jar --server.port=8082
```

> 仅做基础功能体验时，可只启动 MySQL + Nacos + 商品 + 订单服务；
> Sentinel / Zipkin / 网关限流 等按对应章节需要再启动。
> 各 `application.yml` 中即便 Nacos/Sentinel/Zipkin 未启动，服务也能启动（仅打印连接告警）。

---

## 五、按天功能清单与验证

### Day01 — 服务治理 Nacos Discovery
- 父子工程、MyBatis-Plus、RestTemplate / DiscoveryClient 远程调用、`@EnableDiscoveryClient` 注册到 Nacos。
- 验证：`http://localhost:8081/products/1` 返回商品；Nacos 控制台能看到两个服务。
- 下单：`http://localhost:8091/orders/save?pid=1&uid=1`

### Day02 — 负载均衡 Ribbon + 远程调用 Feign
- `@LoadBalanced RestTemplate`（方案4）、`IProductFeginService`（方案5，最终采用）。
- 商品名拼接了端口号，多次下单可见 8081/8082 轮询。
- 负载策略可在 order 的 `application.yml` 中 `shop-product-service.ribbon.NFLoadBalancerRuleClassName` 调整。

### Day03 — 流控容错 Sentinel（订单服务）
- 流控：`/sentinel1` `/sentinel2`；关联：`/sentinel-read` `/sentinel-write`；链路：`/queryOrder` `/createOrder`（已关闭 `web-context-unify`）。
- 降级：`/fallBack1`（慢调用）`/fallBack2`（异常比例）`/fallBack3?name=dafei`（异常数）。
- 热点：`/hotSpot1?productId=1`（`@SentinelResource`）。
- 授权：`/auth1?serviceName=app`（白名单）/ `pc`（黑名单），来源由 `RequestOriginParserDefinition` 解析。
- 自定义异常返回：`ExceptionHandlerPage`（限流/降级/参数/授权/系统 五类）。
- 注解用法：`/anno1?name=dafei`（`blockHandler` + `fallback`）。
- Feign 整合 Sentinel：`feign.sentinel.enabled=true` + `ProductFeignFallBack` 兜底（停掉商品服务后访问下单可见"兜底数据"）。
- 规则需在 Sentinel 控制台配置（先访问几次接口让其出现在簇点链路中）。

### Day04 — 服务网关 Gateway（端口 9000）
- 路由 + 谓词 + 过滤器；`lb://` 负载均衡；`/admin/**` 路径重写到 `/**`。
- 全局过滤器 `AuthGlobalFilter`：**所有请求必须带 `?token=123`，否则 401**。
- 自定义局部过滤器 `TimeGatewayFilterFactory`（`- Time=true`）：打印订单路由请求耗时。
- 集成 Sentinel 网关限流（route 维度 / API 分组），需在 Sentinel 控制台配置。
- 自定义限流返回（§7.9.3）：`GatewayConfiguration` 注册 `BlockRequestHandler`，被限流时统一返回 JSON `{"code":0,"message":"接口被限流了"}`。
- 验证：
  - `http://localhost:9000/product/hello?token=123`
  - `http://localhost:9000/admin/product/hello?token=123`
  - `http://localhost:9000/order/hi?token=123`

### Day05 — 配置中心 Nacos Config（商品服务）
- 使用 `bootstrap.yml` 从 Nacos 拉取配置；`@RefreshScope` 实现动态刷新。
- 把 `nacos-config/` 下三个文件上传到 Nacos：
  - `shop-product-service-dev.yaml`（dev 环境）
  - `shop-product-service.yaml`（同服务各环境共享）
  - `global-config.yaml`（跨服务共享，已在 bootstrap.yml 的 `shared-configs` 引入）
- 验证：`http://localhost:8081/appconfigname`、`/nacosConfig`、`/nacosConfig2`；
  在 Nacos 改配置点发布，无需重启即可读到最新值。

### Day06 — 链路追踪 Sleuth & Zipkin
- 商品/订单服务均接入 Sleuth + Zipkin，采样率 100%。
- 启动 Zipkin 后下单 `http://localhost:8091/orders/save?pid=1&uid=1`，
  到 `http://localhost:9411` 查看 `order -> product` 的调用链路。
- 日志格式：`[服务名, TraceId, SpanId, 是否上报zipkin]`。

---

## 六、常见问题
- **`Load balancer does not have available server for client: xxx`**：被调用服务没启动或服务名写错。
- **Feign 404 / 405**：Feign 接口的路径或参数注解与提供方不一致。
- **网关访问返回 401**：没带 `?token=123`（这是 `AuthGlobalFilter` 的预期行为）。
- **配置中心读不到值**：检查 Nacos 中的 Data ID / Group / 格式是否与 `bootstrap.yml` 匹配，
  以及 profile（dev）是否对应。
