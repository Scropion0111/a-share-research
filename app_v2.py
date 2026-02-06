"""
================================================================================
EigenFlow | 量化研究订阅平台
Subscription-based Quantitative Research Platform

Designed for Premium Research Experience
================================================================================
"""

import streamlit as st
import pandas as pd
import os
import uuid
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# ==================== 配置 | Configuration ====================

st.set_page_config(
    page_title="EigenFlow | 量化研究",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

APP_DIR = os.path.dirname(__file__)

# ==================== Access Keys ====================

VALID_ACCESS_KEYS = [
    "EF-26Q1-A9F4KZ2M",
    "EF-26Q1-B3H8LP5N",
    "EF-26Q1-C7J2MR9R",
]

def validate_access_key(key: str) -> bool:
    return key.strip() in VALID_ACCESS_KEYS

# ==================== 工具函数 ====================

def format_stock_code(code):
    return str(code).strip().zfill(6)

def get_tradingview_symbol(stock_code):
    code = format_stock_code(stock_code)
    if code.startswith(('600', '601', '603', '605', '688')):
        return f"SSE:{code}"
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        return f"SZSE:{code}"
    else:
        return f"SSE:{code}"

def load_signal_data():
    csv_path = os.path.join(APP_DIR, 'trade_list_top10.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

# ==================== 品牌与设计系统 ====================

BRAND_COLORS = {
    'gold': '#f59e0b',
    'gold_light': '#fbbf24',
    'dark': '#1a1a1a',
    'gray': '#6b7280',
    'gray_light': '#9ca3af',
    'bg_light': '#f9fafb',
    'border': '#e5e7eb',
}

# ==================== CSS 样式 ====================

st.markdown("""
<style>
/* 基础设置 */
.block-container {
    max-width: 680px !important;
    padding-top: 0.5rem !important;
    padding-bottom: 4rem !important;
}

/* 品牌头部 */
.brand-header {
    text-align: center;
    padding: 20px 0 16px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 24px;
}

.brand-logo {
    font-size: 1.6em;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: -0.5px;
}

.brand-tagline {
    font-size: 0.75em;
    color: #6b7280;
    margin-top: 4px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* 导航栏 */
.nav-container {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin: 24px 0 32px;
    padding: 6px;
    background: #f9fafb;
    border-radius: 12px;
}

.nav-item {
    flex: 1;
    text-align: center;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.9em;
    font-weight: 500;
    color: #6b7280;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    background: transparent;
}

.nav-item:hover {
    color: #1a1a1a;
    background: #fff;
}

.nav-item.active {
    color: #1a1a1a;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* 免责声明 */
.disclaimer-bar {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 16px 0;
    font-size: 0.7em;
    color: #9ca3af;
    text-align: center;
    line-height: 1.6;
}

/* 锁定屏幕 */
.lock-screen {
    background: linear-gradient(135deg, #fff 0%, #f9fafb 100%);
    border: 2px solid #fbbf24;
    border-radius: 16px;
    padding: 32px 24px;
    margin: 24px 0;
    text-align: center;
}

.lock-icon {
    font-size: 2.5em;
    margin-bottom: 16px;
}

.lock-title {
    font-size: 1.3em;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 12px;
}

.lock-desc {
    font-size: 0.9em;
    color: #6b7280;
    line-height: 1.7;
    margin-bottom: 20px;
}

/* 解锁按钮 */
.unlock-btn {
    width: 100%;
    padding: 14px 24px;
    font-size: 1em;
    font-weight: 600;
    border-radius: 10px;
    margin: 16px 0 24px;
}

/* 解锁标识 */
.unlock-badge {
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: #1a1a1a;
    padding: 10px 24px;
    border-radius: 24px;
    font-size: 0.85em;
    font-weight: 600;
    text-align: center;
    margin: 16px 0;
}

/* 信号卡片 */
.signal-card {
    padding: 20px;
    border-radius: 12px;
    margin: 12px 0;
    text-align: center;
}

/* Featured - 金色 */
.signal-featured {
    background: linear-gradient(135deg, #fffbeb, #fef3c7, #fde68a);
    border: 2px solid #f59e0b;
}

.signal-featured .label {
    color: #b45309;
    font-size: 0.7em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.signal-featured .stock {
    font-size: 1.2em;
    font-weight: 700;
    color: #1a1a1a;
}

/* Silver */
.signal-silver {
    background: linear-gradient(135deg, #f9fafb, #f3f4f6);
    border: 1px solid #d1d5db;
}

.signal-silver .label {
    color: #6b7280;
    font-size: 0.65em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

.signal-silver .stock {
    font-size: 1em;
    font-weight: 600;
    color: #374151;
}

/* Other */
.signal-other {
    background: #fff;
    border: 1px solid #e5e7eb;
}

.signal-other .label {
    color: #9ca3af;
    font-size: 0.65em;
    font-weight: 500;
    margin-bottom: 4px;
}

.signal-other .stock {
    font-size: 0.95em;
    font-weight: 500;
    color: #4b5563;
}

.signal-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 8px;
}

.signal-score {
    font-size: 0.9em;
}

/* 日期标签 */
.date-label {
    text-align: center;
    margin: 12px 0 20px;
    color: #6b7280;
    font-size: 0.8em;
}

/* 分区标题 */
.section-title {
    font-size: 0.85em;
    font-weight: 600;
    color: #374151;
    margin: 20px 0 12px;
    padding-left: 12px;
    border-left: 3px solid #f59e0b;
}

/* TradingView 容器 */
.tv-container {
    border-radius: 10px;
    overflow: hidden;
    margin: 16px 0;
    border: 1px solid #e5e7eb;
}

.tv-disclaimer {
    font-size: 0.6em;
    color: #9ca3af;
    text-align: center;
    padding: 10px;
    background: #f9fafb;
    margin-top: 8px;
    line-height: 1.5;
}

/* 选择框样式 */
.stSelectbox > div > div {
    border-radius: 8px;
}

/* 输入框样式 */
.stTextInput > div > div {
    border-radius: 8px;
}

/* 水印 */
.watermark {
    position: fixed;
    bottom: 6px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 0.6em;
    color: #d1d5db;
    padding: 8px;
    background: linear-gradient(to top, rgba(255,255,255,0.95), transparent);
    z-index: 100;
}

/* 订阅卡片 */
.sub-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}

.sub-card-title {
    font-size: 1em;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 12px;
}

.sub-card-text {
    font-size: 0.8em;
    color: #6b7280;
    line-height: 1.7;
}

/* 二维码区域 */
.qr-area {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin: 12px 0;
}

.qr-label {
    font-size: 0.8em;
    color: #6b7280;
    margin-top: 8px;
}

/* 隐藏元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 间距调整 */
div[data-testid="stVerticalBlock"] > div > div {
    gap: 0;
}
</style>
""", unsafe_allow_html=True)


# ==================== 品牌头部 ====================

def render_brand_header():
    """渲染 EigenFlow 品牌头部"""
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">📊 EigenFlow</div>
        <div class="brand-tagline">Quantitative Research Platform</div>
    </div>
    """, unsafe_allow_html=True)


def render_disclaimer():
    """渲染精简免责声明"""
    st.markdown("""
    <div class="disclaimer-bar">
        本平台仅供学术研究，不构成投资建议，不诱导交易行为<br>
        For Research Only · Not Investment Advice
    </div>
    """, unsafe_allow_html=True)


def render_navigation(active_tab):
    """渲染导航栏"""
    tabs = [
        ("📊", "信号清单", 0),
        ("📈", "行情视图", 1),
        ("☕", "支持订阅", 2),
    ]
    
    tabs_html = '<div class="nav-container">'
    for icon, name, idx in tabs:
        active_class = 'active' if active_tab == idx else ''
        tabs_html += f'<button class="nav-item {active_class}" onclick="document.getElementById(\'nav-{idx}\').click()">{icon} {name}</button>'
    tabs_html += '</div>'
    
    st.markdown(tabs_html, unsafe_allow_html=True)
    
    # 隐藏的 radio 用于状态管理
    st.radio("", options=range(3), index=active_tab, key="nav_radio", label_visibility="collapsed", on_change=None)


# ==================== 信号页面组件 ====================

def render_lock_screen():
    """渲染锁定屏幕"""
    st.markdown("""
    <div class="lock-screen">
        <div class="lock-icon">🔐</div>
        <div class="lock-title">核心信号已锁定</div>
        <div class="lock-desc">
            本页面展示 EigenFlow 量化研究核心信号<br>
            包括 Rank 1-10 精选股票与评分<br><br>
            <strong style="color:#f59e0b;">请切换至「支持订阅」页面获取 Access Key</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 解锁按钮
    if st.button("🎯 立即获取 Access Key →", use_container_width=True, type="primary", key="unlock_btn"):
        st.session_state.target_tab = 2
        st.rerun()
    
    # 试用提示
    st.markdown("""
    <div style="background:#f8f9fa; border-radius:12px; padding:16px; margin-top:24px;">
        <div style="font-weight:600; font-size:0.9em; color:#374151; margin-bottom:10px;">
            🔓 您可先试用以下功能
        </div>
        <ul style="margin:0; padding-left:20px; font-size:0.85em; color:#6b7280;">
            <li>📈 切换至「行情视图」查看 TradingView 图表</li>
            <li>📊 输入股票代码试用实时行情</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def render_access_input():
    """渲染 Access Key 输入"""
    st.markdown("""
    <div style="background:linear-gradient(135deg,#fafafa,#f0f0f0); border:1px solid #e5e7eb; border-radius:12px; padding:20px; margin:16px 0;">
        <div style="font-size:0.95em; font-weight:600; color:#374151; margin-bottom:14px; text-align:center;">
            🔐 输入访问密钥
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        access_key = st.text_input(
            "Access Key",
            type="password",
            placeholder="EF-26Q1-XXXXXXXX",
            label_visibility="collapsed",
            key="access_key_input"
        )
    with col2:
        confirm_btn = st.button("确认", use_container_width=True, type="primary")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 初始化
    if 'access_verified' not in st.session_state:
        st.session_state.access_verified = False
        st.session_state.verified_key_mask = ""
    
    # 验证
    if confirm_btn and access_key:
        if validate_access_key(access_key):
            st.session_state.access_verified = True
            st.session_state.verified_key_mask = access_key[:8] + "****"
            st.rerun()
        else:
            st.session_state.access_verified = False
            st.error("❌ 无效的 Access Key")
    
    return st.session_state.access_verified, st.session_state.verified_key_mask


def render_signal_featured(row, name: str):
    """渲染 Featured Signal"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-card signal-featured">
        <div class="label">★ 精选信号 · Featured</div>
        <div class="stock">{code} · {name}</div>
        <div class="signal-row">
            <div style="color:#78350f; font-size:0.85em;">评分：{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_silver(rank: int, row, name: str):
    """渲染 Silver Tier"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-card signal-silver">
        <div class="label">◆ 银牌信号 · Silver #{rank}</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div class="signal-score" style="color:#6b7280;">{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_other(rank: int, row, name: str):
    """渲染 Other Signals"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-card signal-other">
        <div class="label">◇ 其他信号 · #{rank}</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div class="signal-score" style="color:#9ca3af;">{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==================== TradingView 组件 ====================

def render_tradingview_chart(symbol: str, height: int = 400):
    """渲染 TradingView 图表"""
    tv_html = f"""
    <div class="tv-container">
        <div id="tradingview_widget" style="height:{height}px;"></div>
    </div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({{
        "width": "100%",
        "height": {height},
        "symbol": "{symbol}",
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
    <div class="tv-disclaimer">
        TradingView® 为 TradingView, Inc. 注册商标 · 本平台与 TradingView 无关联
    </div>
    """
    components.html(tv_html, height=height + 60)


def render_trial_chart():
    """渲染试用版图表"""
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">🔓 TradingView 试用</div>
        <div class="sub-card-text">
            输入任意股票代码，查看实时行情图表。
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    trial_symbol = st.text_input(
        "输入股票代码",
        placeholder="600519, 000001, 300624",
        max_chars=6,
        label_visibility="visible",
        key="trial_symbol"
    )
    
    if trial_symbol:
        trial_symbol = trial_symbol.strip().zfill(6)
        if len(trial_symbol) == 6 and trial_symbol.isdigit():
            tv_symbol = get_tradingview_symbol(trial_symbol)
            render_tradingview_chart(tv_symbol)


# ==================== 支持订阅页面 ====================

def render_support_page():
    """渲染支持订阅页面"""
    # 订阅说明
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">💡 订阅说明</div>
        <div class="sub-card-text">
            <p>EigenFlow 为专业量化研究订阅服务，核心信号仅限订阅用户查阅。</p>
            <p><strong>订阅权益：</strong>每日精选信号、行情辅助分析、研究方法支持。</p>
            <p style="color:#9ca3af; margin-top:8px;">订阅内容为研究资料访问授权，非交易指令。</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 联系信息
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">📧 获取 Access Key</div>
        <div class="sub-card-text">
            <ul style="margin:8px 0; padding-left:16px;">
                <li>微信：扫描下方二维码联系</li>
                <li>Email：research@eigenflow.io</li>
                <li>Telegram：@eigenflow_research</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 二维码
    col_qr1, col_qr2 = st.columns(2)
    
    with col_qr1:
        st.markdown('<div class="qr-area">', unsafe_allow_html=True)
        st.markdown("**💬 微信**")
        try:
            st.image("wechat_qr.png", width=140)
        except:
            st.info("添加 wechat_qr.png")
        st.markdown('<div class="qr-label">扫码联系</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_qr2:
        st.markdown('<div class="qr-area">', unsafe_allow_html=True)
        st.markdown("**💳 支付宝**")
        try:
            st.image("alipay_qr.png", width=140)
        except:
            st.info("添加 alipay_qr.png")
        st.markdown('<div class="qr-label">扫码支付</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 使用声明
    st.markdown("---")
    st.markdown("""
    <div class="sub-card">
        <div class="sub-card-title">⚖️ 使用声明</div>
        <div class="sub-card-text">
            <ul style="margin:8px 0; padding-left:16px;">
                <li><strong>使用范围：</strong>本内容仅供个人研究与学习使用，禁止转售、二次分发或公开传播。</li>
                <li><strong>二次收费禁止：</strong>严禁任何形式的二次收费、转售或商业化使用。</li>
                <li><strong>违约后果：</strong>如发现违规行为，访问授权可能被立即终止。</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==================== 页面内容 ====================

def page_signal_list(key_mask: str):
    """信号清单页面"""
    # 已解锁标识
    st.markdown('<div class="unlock-badge">✓ 已解锁 · Access Granted</div>', unsafe_allow_html=True)
    
    # 加载数据
    csv_path = os.path.join(APP_DIR, 'trade_list_top10.csv')
    if not os.path.exists(csv_path):
        st.error("❌ 数据文件不存在，请上传 trade_list_top10.csv")
        return
    
    df = load_signal_data()
    if df.empty:
        st.error("❌ 无法加载信号数据")
        return
    
    if 'symbol' not in df.columns:
        st.error("❌ 数据格式错误：缺少 symbol 列")
        return
    
    # 准备数据
    df_top10 = df.head(10).copy()
    df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
    stock_names = df_top10.get('name', df_top10['symbol']).tolist()
    
    # 日期
    now = datetime.now()
    current_hour = now.hour
    date_label = "下一个交易日" if current_hour >= 16 else "今日"
    
    st.markdown(f"""
    <div class="date-label">📅 {date_label}信号 · {now.strftime('%Y-%m-%d')}</div>
    """, unsafe_allow_html=True)
    
    # Featured
    if len(df_top10) >= 1:
        render_signal_featured(df_top10.iloc[0], stock_names[0])
    
    # Silver Tier
    if len(df_top10) >= 3:
        st.markdown('<div class="section-title">◆ 银牌信号 · Silver Tier</div>', unsafe_allow_html=True)
        for i in range(1, 3):
            render_signal_silver(i + 1, df_top10.iloc[i], stock_names[i])
    
    # Other
    if len(df_top10) >= 4:
        st.markdown('<div class="section-title">◇ 其他信号</div>', unsafe_allow_html=True)
        for i in range(3, min(10, len(df_top10))):
            render_signal_other(i + 1, df_top10.iloc[i], stock_names[i])
    
    # 底部声明
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-bar">
        信号具有时效性，仅在研究窗口期内具有参考意义<br>
        Past performance ≠ future results
    </div>
    """, unsafe_allow_html=True)
    
    # 水印
    st.markdown(f"""
    <div class="watermark">授权码：{key_mask}｜仅限个人研究使用</div>
    """, unsafe_allow_html=True)


def page_chart():
    """行情视图页面"""
    st.markdown("""
    <div class="date-label" style="font-size:1em; font-weight:600; color:#374151;">
        📈 行情视图 · Chart
    </div>
    """, unsafe_allow_html=True)
    
    df = load_signal_data()
    
    if df.empty:
        st.warning("暂无信号数据，请上传 trade_list_top10.csv")
        return
    
    if 'symbol' not in df.columns:
        st.error("数据格式错误：缺少 symbol 列")
        return
    
    # 准备数据
    df_top10 = df.head(10).copy()
    df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
    
    stock_options = [f"{row['symbol']} · {row.get('name', row['symbol'])}" for _, row in df_top10.iterrows()]
    
    if not stock_options:
        st.warning("无法生成股票选项")
        return
    
    selected = st.selectbox("选择股票", options=stock_options, index=0, label_visibility="visible", key="chart_select")
    
    if selected:
        selected_code = selected.split(" · ")[0]
        symbol = get_tradingview_symbol(selected_code)
        render_tradingview_chart(symbol)
    
    st.markdown('<div class="watermark">试用模式</div>', unsafe_allow_html=True)


# ==================== 主程序 ====================

def main():
    """主入口"""
    render_brand_header()
    render_disclaimer()
    
    # 获取当前 tab
    if 'target_tab' not in st.session_state:
        st.session_state.target_tab = 0
    
    current_tab = st.session_state.get('nav_radio', 0)
    render_navigation(current_tab)
    
    if current_tab == 0:
        # ========== 信号清单 ==========
        is_verified, key_mask = render_access_input()
        
        if not is_verified:
            render_lock_screen()
            render_trial_chart()
            st.markdown('<div class="watermark">试用模式</div>', unsafe_allow_html=True)
            st.stop()
        
        page_signal_list(key_mask)
    
    elif current_tab == 1:
        # ========== 行情视图 ==========
        page_chart()
    
    else:
        # ========== 支持订阅 ==========
        render_support_page()


if __name__ == "__main__":
    main()
