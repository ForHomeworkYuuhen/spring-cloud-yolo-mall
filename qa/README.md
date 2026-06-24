# 问答模块（AI 客服 · 知识图谱 + LLM）

把商城商品建成**知识图谱**存进 **neo4j**，用户提问时先从图谱检索相关商品事实，再交给 **LLM** 生成自然回答（GraphRAG 思路，回答有据可依、不瞎编）。接到前端右下角的"AI 客服"悬浮聊天窗。

## 知识图谱结构

```
(商品 Product)-[:MADE_BY 品牌]->(品牌 Brand)
(商品 Product)-[:BELONGS_TO 类目]->(类目 Category)
(商品 Product)-[:SOLD_BY 售卖于]->(店铺 Shop)
```
节点：19 个零食商品（与 YOLO 识别的零食一致）、7 个品牌（Cheetoz/Maz Maz/Chee/Naderi/Ashi Mashi/Mini Lina/Minoo）、3 个类目（薯片/膨化零食/饼干）、店铺。

## 问答流程

1. **解析**：从问题里识别品牌、类目、价格意图（"最便宜/最贵"）。
2. **图谱检索**：用 Cypher 在 neo4j 里查出匹配的商品事实（例 `MATCH (p:Product)-[:MADE_BY]->(b:Brand {name:'Cheetoz'})`）。
3. **生成**：把检索到的事实作为上下文喂给 LLM 生成回答；约束"只能依据资料、不得编造"。
   - **没配 LLM key** → 用图谱事实做模板回答（也能演示）。
   - **neo4j 没起** → 自动用内存图谱兜底（同一份商品数据）。

## 文件

| 文件 | 作用 |
|---|---|
| `catalog.py` | 商品目录（与商城一致），建图与检索共用 |
| `kg_build.py` | 把商品写入 neo4j 知识图谱（节点 + 关系） |
| `qa_service.py` | 在线问答服务（FastAPI :8125），图谱检索 + LLM 生成 |

## 运行

```powershell
pip install fastapi "uvicorn[standard]" neo4j requests

# 1) 启动 neo4j（Docker）。国内拉不动官方镜像用镜像源（实测 1ms.run 可用）：
#    docker pull docker.1ms.run/library/neo4j:5
#    docker tag docker.1ms.run/library/neo4j:5 neo4j:5
docker run -d --name shop-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/neo4j12345 neo4j:5

# 2) 构建知识图谱（写入 neo4j）
python kg_build.py            # 浏览器 http://localhost:7474 可查看图谱

# 3) 启动问答服务（:8125）
python qa_service.py
```

## 接入 LLM（你来填 key，OpenAI 兼容即可）

设置环境变量后重启 `qa_service.py`（DeepSeek / 通义千问 / 智谱 GLM 都行）：

```powershell
$env:LLM_API_KEY  = "你的key"
$env:LLM_BASE_URL = "https://api.deepseek.com"   # 默认值，可换通义/智谱的兼容地址
$env:LLM_MODEL    = "deepseek-chat"
```
不填则用图谱模板回答，服务照常可用。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/ask`  body `{"question":"有哪些手机？"}` | 问答，返回 `{answer, facts, source, kg}` |
| GET | `/ask?q=...` | 同上（便于浏览器/命令行测试） |
| GET | `/health` | 状态：kg 后端(neo4j/memory)、是否配了 LLM |

## 前端接入

`shop-frontend/js/app.js` 的 `initChat()` 在每个页面注入右下角"AI 客服"悬浮窗，`QA_API` 指向本服务；问答服务未启动时聊天窗会提示"服务不可用"，不影响其它功能。

## neo4j 连接配置（环境变量）

`NEO4J_URI`(默认 `bolt://localhost:7687`)、`NEO4J_USER`(neo4j)、`NEO4J_PASSWORD`(neo4j12345)。
