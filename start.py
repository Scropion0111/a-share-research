#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股量化推荐网站 - 一键启动脚本
"""

import os
import sys
import subprocess
import io

# 修复Windows中文编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import pandas
        import plotly
        print("[成功] 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"[错误] 缺少依赖: {e}")
        print("请运行: pip install streamlit pandas plotly")
        return False

def start_app():
    """启动Streamlit应用"""
    try:
        print("[火箭] 启动A股推荐网站...")
        print("[手机] 浏览器将自动打开: http://localhost:8501")
        print("[叉号] 如需停止，按 Ctrl+C")

        # 检查是否安装了streamlit
        try:
            import streamlit
        except ImportError:
            print("[错误] Streamlit未安装，请先安装：")
            print("pip install streamlit pandas plotly")
            return

        # 启动streamlit
        print("\n正在启动浏览器...")
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "true",
            "--server.address", "localhost",
            "--server.port", "8501"
        ])
    except KeyboardInterrupt:
        print("\n[再见] 网站已停止")
    except Exception as e:
        print(f"[错误] 启动失败: {e}")
        print("请尝试手动运行：streamlit run app.py")

def main():
    print("=" * 50)
    print("[图表] A股量化推荐网站启动器")
    print("=" * 50)

    if not check_dependencies():
        print("\n[工具] 请先安装依赖包：")
        print("pip install streamlit pandas plotly")
        input("\n按回车键退出...")
        return

    print("\n[目标] 网站功能：")
    print("  • Top 10股票推荐")
    print("  • TradingView专业图表")
    print("  • 历史资金曲线")
    print("  • 订阅支持")

    print("\n" + "=" * 50)

    start_app()

if __name__ == "__main__":
    main()
