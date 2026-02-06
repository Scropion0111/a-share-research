@echo off
chcp 65001 >nul
echo === 启动A股量化推荐网站 ===
echo.

REM 检查是否安装了streamlit
python -c "import streamlit; print('Streamlit已安装')" >nul 2>&1
if errorlevel 1 (
    echo [错误] Streamlit未安装，请先安装：
    echo pip install streamlit pandas plotly
    echo.
    pause
    exit /b 1
)

echo [火箭] 正在启动网站...
echo [浏览器] 网站地址: http://localhost:8501
echo [退出] 关闭此窗口可停止网站
echo.

REM 启动streamlit
python -m streamlit run app.py --server.address localhost --server.port 8501

echo.
echo [再见] 网站已停止
pause

