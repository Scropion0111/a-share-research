"""
EigenFlow | 量化研究订阅平台
Subscription-based Quantitative Research Platform

严格订阅机制：Access Key 解锁核心信号
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 | Configuration ====================
st.set_page_config(
    page_title="EigenFlow | 量化研究",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ==================== CSS 样式 | Research Style ====================
st.markdown("""
<style>
/* 基础重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* 限制宽度 - 研究型布局 */
.block-container {
    max-width: 680px !important;
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
}

/* 标题样式 */
.main-title {
    font-size: 1.3em;
    font-weight: 600;
    text-align: center;
    color: #1a1a2e;
    margin-bottom: 4px;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 0.75em;
    margin-bottom: 12px;
}

/* 免责声明 - 精简 */
.disclaimer-mini {
    background: #f8f9fa;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 12px 0;
    font-size: 0.7em;
    color: #6b7280;
    text-align: center;
}

/* Access Key 输入区 */
.access-section {
    background: linear-gradient(135deg, #fefefe 0%, #f5f5f5 100%);
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 20px;
    margin: 20px 0;
}

.access-title {
    font-size: 0.9em;
    font-weight: 600;
    color: #374151;
    margin-bottom: 12px;
    text-align: center;
}

.stTextInput > div > div {
    border-radius: 6px;
}

/* 解锁成功提示 */
.unlock-badge {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: #1a1a2e;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
    text-align: center;
    margin-bottom: 16px;
}

/* ==================== 信号等级样式 | Signal Tier Styles ==================== */

/* Rank 1 - Featured - 金色 */
.rank-1 {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 50%, #fde68a 100%);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
}

.rank-1 .label {
    color: #b45309;
    font-size: 0.65em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

.rank-1 .stock {
    font-size: 1.1em;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 4px;
}

.rank-1 .meta {
    color: #78350f;
    font-size: 0.75em;
}

/* Rank 2-3 - Silver - 银灰 */
.rank-silver {
    background: #f9fafb;
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 14px;
    margin: 8px 0;
}

.rank-silver .label {
    color: #6b7280;
    font-size: 0.6em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.rank-silver .stock {
    font-size: 1em;
    font-weight: 600;
    color: #374151;
    margin-bottom: 3px;
}

.rank-silver .meta {
    color: #6b7280;
    font-size: 0.7em;
}

/* Rank 4-10 - Neutral - 中性色 */
.rank-neutral {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px;
    margin: 6px 0;
}

.rank-neutral .label {
    color: #9ca3af;
    font-size: 0.6em;
    font-weight: 500;
    margin-bottom: 3px;
}

.rank-neutral .stock {
    font-size: 0.95em;
    font-weight: 500;
    color: #4b5563;
}

.rank-neutral .meta {
    color: #9ca3af;
    font-size: 0.7em;
}

/* 通用行样式 */
.signal-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* TradingView 容器 */
.tv-container {
    border-radius: 8px;
    overflow: hidden;
    margin: 12px 0;
    border: 1px solid #e5e7eb;
}

.tv-disclaimer {
    font-size: 0.65em;
    color: #9ca3af;
    text-align: center;
    padding: 8px;
    background: #f9fafb;
}

/* Support 页面 */
.support-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px;
    margin: 12px 0;
}

.support-title {
    font-size: 0.85em;
    font-weight: 600;
    color: #374151;
    margin-bottom: 10px;
}

.support-item {
    font-size: 0.8em;
    color: #6b7280;
    margin: 6px 0;
}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 0.85em;
    background: #f3f4f6;
}

.stTabs [aria-selected="true"] {
    background: #1a1a2e;
    color: white;
}

/* 隐藏 Streamlit 默认元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==================== 核心配置 | Core Config ====================

# Access Key 验证（生产环境建议使用环境变量或数据库）
VALID_ACCESS_KEYS = [
    "EIGEN-2026-PRO",
    "EIGEN-RESEARCH-X1",
    "EIGEN-VIP-2026",
]

def validate_access_key(key: str) -> bool:
    """验证 Access Key"""
    return key.strip() in VALID_ACCESS_KEYS

def get_csv_path() -> str:
    """获取 CSV 文件路径"""
    return os.path.join(os.path.dirname(__file__), 'trade_list_top10.csv')

def load_signal_data() -> pd.DataFrame:
    """加载信号数据"""
    csv_path = get_csv_path()
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

def format_stock_display(code: str, name: str = None) -> str:
    """格式化股票显示：代码 · 中文名"""
    code = str(code).zfill(6)
    if name and name != code:
        return f"{code} · {name}"
    return code

# ==================== UI 组件 | UI Components ====================

def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="main-title">📊 EigenFlow | 量化研究</div>
    <div class="subtitle">Quantitative Research Platform · Subscription Required</div>
    <div class="disclaimer-mini">
        ⚠️ 本平台仅供学术研究，不构成投资建议，不诱导交易行为<br>
        For Research Only · Not Investment Advice
    </div>
    """, unsafe_allow_html=True)

def render_access_input() -> str:
    """渲染 Access Key 输入框"""
    st.markdown("""
    <div class="access-section">
        <div class="access-title">🔐 输入访问密钥 | Enter Access Key</div>
    """, unsafe_allow_html=True)
    
    access_key = st.text_input(
        "Access Key",
        type="password",
        placeholder="EIGEN-XXXX-XXXX",
        label_visibility="collapsed"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    return access_key

def render_signal_rank_1(row, name: str):
    """渲染 Rank 1 - Featured Signal"""
    code = str(row['symbol']).zfill(6)
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="rank-1">
        <div class="label">★ Featured Signal</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div class="meta">Score: {score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_signal_silver(rank: int, row, name: str):
    """渲染 Rank 2-3 - Silver Tier"""
    code = str(row['symbol']).zfill(6)
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="rank-silver">
        <div class="label">◆ Silver Tier · Rank {rank}</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div class="meta">{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_signal_neutral(rank: int, row, name: str):
    """渲染 Rank 4-10 - Other Signals"""
    code = str(row['symbol']).zfill(6)
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="rank-neutral">
        <div class="label">◇ Signal · #{rank}</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div class="meta">{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_tradingview_widget(symbol: str, height: int = 400):
    """渲染 TradingView 图表"""
    # 生成正确的交易所代码
    code = str(symbol).zfill(6)
    if code.startswith(('600', '601', '603', '605', '688')):
        tv_symbol = f"SSE:{code}"
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        tv_symbol = f"SZSE:{code}"
    else:
        tv_symbol = f"SSE:{code}"
    
    tv_html = f"""
    <div class="tv-container">
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
            <div id="tradingview_widget" style="height:{height}px;"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "width": "100%",
                "height": {height},
                "symbol": "{tv_symbol}",
                "interval": "D",
                "timezone": "Asia/Shanghai",
                "theme": "light",
                "style": "1",
                "locale": "zh_CN",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_widget"
            }});
            </script>
        </div>
        <!-- TradingView Widget END -->
    </div>
    <div class="tv-disclaimer">
        TradingView® 为 TradingView, Inc. 注册商标 · 本平台无关联
    </div>
    """
    st.markdown(tv_html, unsafe_allow_html=True)

def render_support_page():
    """渲染 Support & Access 页面"""
    st.markdown("""
    <div class="support-box">
        <div class="support-title">💡 订阅说明 | Subscription Info</div>
        <div class="support-item">
            EigenFlow 为专业量化研究订阅服务，核心信号仅限订阅用户查阅。
        </div>
        <div class="support-item">
            订阅权益：每日精选信号、市场辅助分析、策略研究支持。
        </div>
    </div>
    
    <div class="support-box">
        <div class="support-title">📧 联系获取 Access Key</div>
        <div class="support-item">
            · 微信：扫描首页二维码<br>
            · Email：research@eigenflow.io<br>
            · Telegram：@eigenflow_research
        </div>
    </div>
    
    <div class="support-box">
        <div class="support-title">💳 支付方式</div>
        <div class="support-item">
            支持微信、支付宝、USDT 等多种方式，请联系获取付款信息。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 二维码区域
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="support-box" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("**💬 微信 | WeChat**")
        try:
            st.image("wechat_qr.png", width=140)
        except:
            st.info("请添加图片")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="support-box" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("**💳 支付宝 | Alipay**")
        try:
            st.image("alipay_qr.png", width=140)
        except:
            st.info("请添加图片")
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== 页面 | Pages ====================

def page_signal_list():
    """Signal List 页面 - 需要 Access Key"""
    render_header()
    
    # Access Key 验证
    if 'access_verified' not in st.session_state:
        st.session_state.access_verified = False
    
    # 顶部输入框
    access_key = render_access_input()
    
    if access_key:
        if validate_access_key(access_key):
            st.session_state.access_verified = True
            st.rerun()
        else:
            st.error("❌ 无效的 Access Key，请检查后重试")
            st.session_state.access_verified = False
    
    # 未验证或验证失败
    if not st.session_state.access_verified:
        st.info("💡 请输入有效的 Access Key 以解锁核心信号")
        render_support_page()
        st.stop()
    
    # 验证成功 - 显示解锁标识
    st.markdown('<div class="unlock-badge">✓ 已解锁 | Access Granted</div>', unsafe_allow_html=True)
    
    # 加载数据
    df = load_signal_data()
    
    if df.empty:
        st.error("❌ 无法加载信号数据，请检查 trade_list_top10.csv")
        st.code(get_csv_path())
        return
    
    # 验证格式
    if 'symbol' not in df.columns:
        st.error("❌ 数据格式错误：缺少 symbol 列")
        return
    
    # 准备数据
    df = df.head(10).copy()
    df['symbol'] = df['symbol'].apply(lambda x: str(x).zfill(6))
    df['display_name'] = df.apply(
        lambda row: format_stock_display(row['symbol'], row.get('name', row['symbol'])), 
        axis=1
    )
    
    # 信号日期
    st.markdown(f"""
    <div style="text-align:center; margin: 12px 0; color: #6b7280; font-size: 0.8em;">
        📅 {datetime.now().strftime('%Y-%m-%d')} · 研究信号
    </div>
    """, unsafe_allow_html=True)
    
    # Rank 1
    if len(df) >= 1:
        render_signal_rank_1(df.iloc[0], df.iloc[0]['display_name'])
    
    # Rank 2-3
    if len(df) >= 3:
        st.markdown('<div style="margin: 16px 0 8px 0;"></div>', unsafe_allow_html=True)
        for i in range(1, 3):
            render_signal_silver(i + 1, df.iloc[i], df.iloc[i]['display_name'])
    
    # Rank 4-10
    if len(df) >= 4:
        st.markdown('<div style="margin: 12px 0 6px 0;"></div>', unsafe_allow_html=True)
        for i in range(3, min(10, len(df))):
            render_signal_neutral(i + 1, df.iloc[i], df.iloc[i]['display_name'])

def page_market_view():
    """Market View 页面 - 辅助查看"""
    render_header()
    
    st.markdown("""
    <div style="text-align:center; margin: 16px 0 20px 0;">
        <div style="font-size: 1.1em; font-weight: 600; color: #374151;">
            📈 Market View
        </div>
        <div style="font-size: 0.75em; color: #6b7280;">
            股票走势辅助查看
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 输入股票代码
    symbol = st.text_input(
        "输入股票代码（6位数字）",
        placeholder="600403, 000001, 300624",
        max_chars=6
    )
    
    if symbol:
        # 清理输入
        symbol = symbol.strip().zfill(6)
        
        if len(symbol) == 6 and symbol.isdigit():
            st.markdown(f"""
            <div style="text-align:center; margin: 12px 0; color: #374151; font-weight: 500;">
                {format_stock_display(symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            render_tradingview_widget(symbol)
        else:
            st.warning("请输入有效的6位股票代码")
    
    # 快速选择
    st.markdown("### 常用股票")
    
    # 加载数据中的股票
    df = load_signal_data()
    if not df.empty:
        quick_symbols = df.head(5)['symbol'].tolist()
        quick_symbols = [str(s).zfill(6) for s in quick_symbols]
        
        cols = st.columns(5)
        for i, sym in enumerate(quick_symbols):
            if cols[i].button(sym, key=f"quick_{sym}"):
                st.rerun()
    
    st.markdown("""
    <div class="tv-disclaimer" style="margin-top: 24px;">
        本页面仅供走势辅助查看，信号内容请在 Signal List 页面获取。
    </div>
    """, unsafe_allow_html=True)

def page_support():
    """Support & Access 页面"""
    render_header()
    st.markdown("""
    <div style="text-align:center; margin: 16px 0 20px 0;">
        <div style="font-size: 1.1em; font-weight: 600; color: #374151;">
            ☕ Support & Access
        </div>
        <div style="font-size: 0.75em; color: #6b7280;">
            订阅说明与联系方式
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    render_support_page()

# ==================== 主程序 | Main ====================

def main():
    """主入口"""
    
    # 页面导航
    tab1, tab2, tab3 = st.tabs([
        "📊 Signal List",
        "📈 Market View",
        "☕ Support"
    ])
    
    with tab1:
        page_signal_list()
    
    with tab2:
        page_market_view()
    
    with tab3:
        page_support()

if __name__ == "__main__":
    main()
