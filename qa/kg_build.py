# -*- coding: utf-8 -*-
"""
构建商品知识图谱并写入 neo4j。
图谱结构（节点 + 关系）：
  (商品 Product)-[:属于类目 BELONGS_TO]->(类目 Category)
  (商品 Product)-[:品牌 MADE_BY]->(品牌 Brand)
  (商品 Product)-[:售卖于 SOLD_BY]->(店铺 Shop)

运行：
  pip install neo4j
  # 先起 neo4j（见 README）；连接参数用环境变量覆盖：
  #   NEO4J_URI(默认 bolt://localhost:7687) NEO4J_USER(neo4j) NEO4J_PASSWORD(neo4j12345)
  python kg_build.py
"""
import os
from neo4j import GraphDatabase
from catalog import PRODUCTS

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD = os.getenv("NEO4J_PASSWORD", "neo4j12345")


def build(tx):
    tx.run("MATCH (n) DETACH DELETE n")  # 重建：清空旧图
    for p in PRODUCTS:
        tx.run(
            """
            MERGE (prod:Product {id:$id})
              SET prod.name=$name, prod.price=$price
            MERGE (b:Brand {name:$brand})
            MERGE (c:Category {name:$category})
            MERGE (s:Shop {name:$shop})
            MERGE (prod)-[:MADE_BY]->(b)
            MERGE (prod)-[:BELONGS_TO]->(c)
            MERGE (prod)-[:SOLD_BY]->(s)
            """,
            **p,
        )


def main():
    print(f"连接 neo4j: {URI} (user={USER})")
    driver = GraphDatabase.driver(URI, auth=(USER, PWD))
    with driver.session() as s:
        s.execute_write(build)
        n_prod = s.run("MATCH (p:Product) RETURN count(p) AS c").single()["c"]
        n_node = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        n_rel = s.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    driver.close()
    print(f"知识图谱已写入：{n_prod} 个商品，共 {n_node} 个节点 / {n_rel} 条关系。")
    print("可在 neo4j 浏览器 http://localhost:7474 用 `MATCH (n) RETURN n` 查看。")


if __name__ == "__main__":
    main()
