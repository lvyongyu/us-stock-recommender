#!/bin/bash
# Safari 兼容性启动脚本

echo "🦉 启动 Safari 兼容的股票推荐应用..."
echo "========================================="

# 使用 Safari 兼容的配置启动
"/Users/Eric/stock recommander/.venv/bin/python" -m streamlit run portfolio_app.py \
    --server.headless false \
    --server.port 8501 \
    --server.address localhost \
    --server.enableCORS true \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

echo ""
echo "🦉 Safari 兼容应用已启动!"
echo "🌐 访问地址: http://localhost:8501"
echo ""
echo "Safari 用户注意事项："
echo "• 如果页面无法加载，请清除 Safari 缓存"
echo "• 禁用内容阻止器和广告拦截器"
echo "• 在 Safari 偏好设置中允许弹出式窗口"
echo "• 推荐使用 Chrome 或 Firefox 获得最佳体验"
echo ""
echo "💡 按 Ctrl+C 停止应用"