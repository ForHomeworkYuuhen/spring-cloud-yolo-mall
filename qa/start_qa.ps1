# 启动 AI 客服问答服务（接入 DeepSeek 大模型）。
# 用法：把你的 DeepSeek key 写进同目录的 .llm_key 文件（单独一行），再运行：  .\start_qa.ps1
# .llm_key 已被 .gitignore 忽略，不会进仓库；key 不写在任何代码里。
$keyFile = Join-Path $PSScriptRoot ".llm_key"
if (Test-Path $keyFile) {
    $env:LLM_API_KEY = (Get-Content $keyFile -Raw).Trim()
    Write-Host "[LLM] 已从 .llm_key 读取 DeepSeek key，启用大模型回答。"
} elseif ($env:LLM_API_KEY) {
    Write-Host "[LLM] 使用环境变量里的 key，启用大模型回答。"
} else {
    Write-Host "[LLM] 未提供 key（.llm_key 不存在、环境变量也未设）-> 用知识图谱模板回答。"
}
$env:LLM_BASE_URL = "https://api.deepseek.com"
$env:LLM_MODEL    = "deepseek-chat"
$env:PYTHONUTF8   = "1"
& "E:\Code\Yueqian\yolo-snacks\.venv\Scripts\python.exe" "$PSScriptRoot\qa_service.py"
