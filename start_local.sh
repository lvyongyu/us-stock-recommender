#!/bin/bash
# 本地启动脚本

echo "🚀 启动股票推荐应用..."
echo "================================"

# 激活虚拟环境并启动应用
"/Users/Eric/stock recommander/.venv/bin/python" -m streamlit run portfolio_app.py \
    --server.headless false \
    --server.port 8501 \
    --server.address localhost \
    --browser.gatherUsageStats false

echo ""
echo "📱 应用已启动!"
echo "🌐 访问地址: http://localhost:8501"
echo "💡 按 Ctrl+C 停止应用"