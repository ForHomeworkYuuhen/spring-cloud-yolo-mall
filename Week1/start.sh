#!/usr/bin/env bash
# 一键启动 微服务全栈（Linux / macOS）
# 用法：cd Week1 && bash start.sh
cd "$(dirname "$0")"

gateway_code() {
  curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://localhost:9000/admin/products/1?token=123" 2>/dev/null || true
}

echo "==> 构建并启动所有容器（首次会下载依赖+构建，耐心等几分钟）..."
docker compose up -d --build

echo "==> 等待网关就绪..."
ok=0
for i in $(seq 1 24); do
  [ "$(gateway_code)" = "200" ] && { ok=1; break; }
  sleep 5
done

if [ "$ok" != "1" ]; then
  # 已知问题：Java 服务偶尔抢在 Nacos 注册就绪之前启动，重启业务服务即可
  echo "==> 网关未就绪，重启业务服务（修复 Nacos 注册抢跑）..."
  docker compose restart gateway product-server order-server user-server
  for i in $(seq 1 24); do
    [ "$(gateway_code)" = "200" ] && { ok=1; break; }
    sleep 5
  done
fi

echo ""
[ "$ok" = "1" ] && echo "✓ 全部就绪！" || echo "× 网关仍未就绪，请运行: docker compose logs gateway"
echo "----------------------------------------"
echo "前端首页 :  http://localhost:8088"
echo "网关     :  http://localhost:9000   (访问商品需带 ?token=123)"
echo "Nacos    :  http://localhost:8848/nacos   (nacos / nacos)"
echo "Sentinel :  http://localhost:8080   (sentinel / sentinel)"
echo "Zipkin   :  http://localhost:9411"
echo "----------------------------------------"
echo "停止：docker compose down    （加 -v 连数据库数据一起删）"
