# 一键启动 微服务全栈（Windows / PowerShell）
# 用法：在 Week1 目录下右键“用 PowerShell 运行”，或执行  .\start.ps1
$ErrorActionPreference = "Continue"
$compose = Join-Path $PSScriptRoot "docker-compose.yml"

function GatewayCode {
  return (curl.exe -s -o NUL -w "%{http_code}" --max-time 5 "http://localhost:9000/admin/products/1?token=123" 2>$null)
}

Write-Host "==> 构建并启动所有容器（首次会下载依赖+构建，耐心等几分钟）..." -ForegroundColor Cyan
docker compose -f $compose up -d --build

Write-Host "==> 等待网关就绪..." -ForegroundColor Cyan
$ok = $false
for ($i = 0; $i -lt 24; $i++) {
  if ((GatewayCode) -eq "200") { $ok = $true; break }
  Start-Sleep -Seconds 5
}

if (-not $ok) {
  # 已知问题：Java 服务偶尔抢在 Nacos 注册就绪之前启动，重启业务服务即可
  Write-Host "==> 网关未就绪，重启业务服务（修复 Nacos 注册抢跑）..." -ForegroundColor Yellow
  docker compose -f $compose restart gateway product-server order-server user-server
  for ($i = 0; $i -lt 24; $i++) {
    if ((GatewayCode) -eq "200") { $ok = $true; break }
    Start-Sleep -Seconds 5
  }
}

Write-Host ""
if ($ok) { Write-Host "✓ 全部就绪！" -ForegroundColor Green } else { Write-Host "× 网关仍未就绪，请运行: docker compose logs gateway" -ForegroundColor Red }
Write-Host "----------------------------------------"
Write-Host "前端首页 :  http://localhost:8088"
Write-Host "网关     :  http://localhost:9000   (访问商品需带 ?token=123)"
Write-Host "Nacos    :  http://localhost:8848/nacos   (nacos / nacos)"
Write-Host "Sentinel :  http://localhost:8080   (sentinel / sentinel)"
Write-Host "Zipkin   :  http://localhost:9411"
Write-Host "----------------------------------------"
Write-Host "停止：docker compose down    （加 -v 连数据库数据一起删）"
