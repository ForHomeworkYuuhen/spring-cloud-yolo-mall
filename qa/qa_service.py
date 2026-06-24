# -*- coding: utf-8 -*-
"""
AI 客服问答服务（知识图谱 + LLM）。
流程（GraphRAG 思路）：用户提问 -> 解析品牌/类目/价格意图 -> 从 neo4j 知识图谱检索相关商品事实
-> 把事实喂给 LLM 生成自然回答（杜绝编造）。没配 LLM key 时用图谱模板回答；neo4j 没起时用内存图谱兜底。

接口：
  POST /ask  body {"question": "有哪些手机？"}   或   GET /ask?q=...
  GET  /health
运行：
  pip install fastapi "uvicorn[standard]" neo4j requests
  python qa_service.py        # 监听 :8125
LLM 配置（你来填，OpenAI 兼容即可，如 DeepSeek/通义/智谱）：
  环境变量 LLM_API_KEY（必填才走LLM） LLM_BASE_URL(默认 https://api.deepseek.com) LLM_MODEL(默认 deepseek-chat)
neo4j 配置：NEO4J_URI(bolt://localhost:7687) NEO4J_USER(neo4j) NEO4J_PASSWORD(neo4j12345)
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from catalog import PRODUCTS, BRANDS, CATEGORIES, BRAND_ALIAS, CATEGORY_ALIAS, FLAVOR_ALIAS

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PASSWORD", "neo4j12345")

app = FastAPI(title="AI 客服 (KG + LLM)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ---------------- 知识图谱：neo4j 优先，连不上则用内存兜底 ----------------
class KnowledgeGraph:
    def __init__(self):
        self.driver = None
        self.backend = "memory"
        try:
            from neo4j import GraphDatabase
            d = GraphDatabase.driver(URI, auth=(USER, PWD))
            d.verify_connectivity()
            self.driver = d
            self.backend = "neo4j"
        except Exception as e:
            print(f"[KG] neo4j 不可用({e})，改用内存图谱。")

    def query(self, brands, cats, order=None, limit=8, kws=None):
        kws = kws or []
        if self.driver:
            rows = self._neo4j_query(brands, cats, kws)
        else:
            rows = [dict(brand=p["brand"], category=p["category"], id=p["id"], name=p["name"], price=p["price"])
                    for p in PRODUCTS
                    if (not brands or p["brand"] in brands)
                    and (not cats or p["category"] in cats)
                    and (not kws or any(k in p["name"].lower() for k in kws))]
        if order == "asc":
            rows.sort(key=lambda x: x["price"])
        elif order == "desc":
            rows.sort(key=lambda x: x["price"], reverse=True)
        return rows[:limit]

    def _neo4j_query(self, brands, cats, kws):
        cy = (
            "MATCH (p:Product)-[:MADE_BY]->(b:Brand), (p)-[:BELONGS_TO]->(c:Category) "
            "WHERE ($brands=[] OR b.name IN $brands) AND ($cats=[] OR c.name IN $cats) "
            "AND ($kws=[] OR any(k IN $kws WHERE toLower(p.name) CONTAINS k)) "
            "RETURN p.id AS id, p.name AS name, p.price AS price, b.name AS brand, c.name AS category"
        )
        with self.driver.session() as s:
            return [r.data() for r in s.run(cy, brands=brands or [], cats=cats or [], kws=kws or [])]


KG = KnowledgeGraph()


# ---------------- 提问解析：品牌 / 类目 / 价格意图 ----------------
def parse(q: str):
    ql = q.lower()
    brands = set()
    for b in BRANDS:
        if b.lower() in ql or b in q:
            brands.add(b)
    for alias, b in BRAND_ALIAS.items():
        if alias in ql:
            brands.add(b)
    # 去掉被其它命中品牌包含的（如 'Chee' 是 'Cheetoz' 的子串，问 Cheetoz 时不该带出 Chee）
    brands = {b for b in brands if not any(b != o and b in o for o in brands)}
    cats = set()
    for alias, c in CATEGORY_ALIAS.items():
        if alias in ql or alias in q:
            cats.add(c)
    kws = set()
    for alias, kw in FLAVOR_ALIAS.items():
        if alias in ql or alias in q:
            kws.add(kw)
    order = None
    if any(w in q for w in ["便宜", "最低", "实惠", "划算", "最便宜"]):
        order = "asc"
    elif any(w in q for w in ["最贵", "高端", "最好", "最高", "贵"]):
        order = "desc"
    return list(brands), list(cats), order, list(kws)


# ---------------- LLM（OpenAI 兼容；没 key 返回 None 走模板） ----------------
SYS = ("你是粤海购商城的AI客服。只能依据【商品资料】回答用户问题，"
       "不得编造资料中没有的商品、价格或参数。回答用中文，简洁友好口语化，可适当推荐。")


def call_llm(question, facts):
    key = os.getenv("LLM_API_KEY", "").strip()
    if not key:
        return None
    base = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("LLM_MODEL", "deepseek-chat")
    facts_txt = "\n".join(f"- {f['name']}，品牌{f['brand']}，类目{f['category']}，售价¥{f['price']}"
                          for f in facts) or "（没有匹配到商品）"
    prompt = f"【商品资料】\n{facts_txt}\n\n【用户问题】{question}"
    try:
        import requests
        r = requests.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": model, "temperature": 0.3, "max_tokens": 400,
                  "messages": [{"role": "system", "content": SYS}, {"role": "user", "content": prompt}]},
            timeout=30,
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[LLM] 调用失败({e})，改用模板回答。")
        return None


def template_answer(facts, order):
    if not facts:
        return (f"我们目前有这些类目：{'、'.join(CATEGORIES)}；品牌有 {'、'.join(BRANDS)}。"
                "你可以问“有哪些薯片”“Cheetoz 有什么”“最便宜的零食”这类问题～")
    desc = "、".join(f"{f['name']}（¥{f['price']}）" for f in facts[:5])
    tip = ""
    if order == "asc":
        tip = f" 其中最实惠的是 {facts[0]['name']}，¥{facts[0]['price']}。"
    elif order == "desc":
        tip = f" 其中最高端的是 {facts[0]['name']}，¥{facts[0]['price']}。"
    return f"为你找到 {len(facts)} 款商品：{desc}。{tip}"


class AskBody(BaseModel):
    question: str = ""


def answer(q: str):
    q = (q or "").strip()
    if not q:
        return {"question": q, "answer": "你好，我是粤海购AI客服，有什么可以帮你的？", "facts": [], "source": "greet", "kg": KG.backend}
    brands, cats, order, kws = parse(q)
    if brands or cats or kws:
        facts = KG.query(brands, cats, order, kws=kws)  # 命中品牌/类目/口味 -> 过滤检索
    elif order:
        facts = KG.query([], [], order)                 # 只问“最便宜/最贵” -> 全场排序
    else:
        facts = []                                      # 没命中任何商品 -> 走帮助文案（如“卖辣条吗”）
    ans = call_llm(q, facts)
    source = "llm"
    if not ans:
        ans = template_answer(facts, order)
        source = "kg-template"
    return {"question": q, "answer": ans, "facts": facts, "source": source, "kg": KG.backend}


@app.get("/health")
def health():
    return {"status": "ok", "kg_backend": KG.backend, "llm": bool(os.getenv("LLM_API_KEY", "").strip()),
            "products": len(PRODUCTS)}


@app.post("/ask")
def ask_post(body: AskBody):
    return answer(body.question)


@app.get("/ask")
def ask_get(q: str = ""):
    return answer(q)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8125)
