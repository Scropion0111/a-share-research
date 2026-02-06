"""
================================================================================
EigenFlow | 量化研究订阅平台
Subscription-based Quantitative Research Platform

功能：
├── 3 页面结构：信号清单（需Key）、行情视图、订阅支持
├── Access Key 解锁机制
├── TradingView 试用功能
└── 水印 + 法务声明

================================================================================
"""

import streamlit as st
import pandas as pd
import os
import uuid
import json
import hashlib
import streamlit.components.v1 as components
from datetime import datetime, timedelta

# ==================== 配置 | Configuration ====================

st.set_page_config(
    page_title="EigenFlow | 量化研究",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 路径配置
APP_DIR = os.path.dirname(__file__)

# ==================== Access Keys（简单验证） ====================

# 可用 Keys（和 keys.json 一致）
VALID_ACCESS_KEYS = [
    "EF-26Q1-A9F4KZ2M",
    "EF-26Q1-B3H8LP5N",
    "EF-26Q1-C7J2MR9R",
]

def validate_access_key(key: str) -> bool:
    """验证 Access Key"""
    return key.strip() in VALID_ACCESS_KEYS


# ==================== 工具函数 | Utility Functions ====================

def format_stock_code(code):
    """补齐股票代码至6位"""
    return str(code).strip().zfill(6)


def get_tradingview_symbol(stock_code):
    """生成 TradingView 符号"""
    code = format_stock_code(stock_code)
    
    if code.startswith(('600', '601', '603', '605', '688')):
        return f"SSE:{code}"
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        return f"SZSE:{code}"
    else:
        return f"SSE:{code}"


def load_signal_data():
    """加载信号数据"""
    csv_path = os.path.join(APP_DIR, 'trade_list_top10.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


def get_device_id() -> str:
    """获取或生成设备 ID"""
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id


# ==================== CSS 样式 | Custom CSS ====================

st.markdown("""
<style>
/* 基础设置 */
.block-container {
    max-width: 680px !important;
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
}

/* 标题 */
.main-title {
    font-size: 1.3em;
    font-weight: 600;
    text-align: center;
    margin-bottom: 6px;
    color: #1a1a1a;
}

.subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 0.75em;
    margin-bottom: 14px;
}

/* Access Key 输入区 */
.access-section {
    background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
}

.access-title {
    font-size: 1em;
    font-weight: 600;
    color: #374151;
    margin-bottom: 16px;
    text-align: center;
}

.unlock-badge {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: #1a1a1a;
    padding: 8px 20px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    text-align: center;
    margin: 12px 0;
}

/* 信号卡片 - Featured / 精选（金色） */
.signal-featured {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 50%, #fde68a 100%);
    border: 2px solid #f59e0b;
    border-radius: 12px;
    padding: 18px;
    margin: 12px 0;
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
    font-size: 1.15em;
    font-weight: 700;
    color: #1a1a1a;
}

/* 信号卡片 - Silver Tier / 银牌 */
.signal-silver {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    border: 1px solid #d1d5db;
    border-radius: 10px;
    padding: 14px;
    margin: 8px 0;
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

/* 信号卡片 - Other Signals / 其他 */
.signal-other {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px;
    margin: 6px 0;
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

/* 信号行样式 */
.signal-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 6px;
}

.signal-meta {
    font-size: 0.85em;
    color: #78350f;
}

/* 免责声明 */
.disclaimer-mini {
    background: #f8f9fa;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 0.7em;
    color: #6b7280;
    text-align: center;
}

.disclaimer-box {
    background: #f8f9fa;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
}

.disclaimer-title {
    font-weight: 600;
    color: #374151;
    margin-bottom: 10px;
    font-size: 0.9em;
}

.disclaimer-text {
    font-size: 0.75em;
    color: #6b7280;
    line-height: 1.6;
}

/* 水印 */
.watermark {
    position: fixed;
    bottom: 8px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 0.65em;
    color: #9ca3af;
    padding: 8px;
    background: linear-gradient(to top, rgba(255,255,255,0.9), transparent);
    z-index: 100;
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
    margin-top: 8px;
}

/* 二维码区域 */
.qr-section {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    margin: 12px 0;
}

.qr-note {
    font-size: 0.75em;
    color: #6b7280;
    margin-top: 8px;
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
    background: #1a1a1a;
    color: white;
}

/* 隐藏元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ==================== UI 组件 | UI Components ====================

def render_header():
    """渲染页面头部"""
    st.markdown("""
    <div class="main-title">📊 EigenFlow | 量化研究</div>
    <div class="subtitle">Quantitative Research Platform</div>
    """, unsafe_allow_html=True)


def render_disclaimer_mini():
    """渲染精简免责声明"""
    st.markdown("""
    <div class="disclaimer-mini">
        ⚠️ 本平台仅供学术研究，不构成投资建议，不诱导交易行为<br>
        For Research Only · Not Investment Advice
    </div>
    """, unsafe_allow_html=True)


def render_access_input() -> tuple[bool, str]:
    """
    渲染 Access Key 输入框
    返回: (是否验证成功, Key掩码)
    """
    st.markdown("""
    <div class="access-section">
        <div class="access-title">🔐 输入访问密钥 | Enter Access Key</div>
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
        st.markdown("<br>", unsafe_allow_html=True)
        confirm_btn = st.button("确认", use_container_width=True, type="primary")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 初始化 session state
    if 'access_verified' not in st.session_state:
        st.session_state.access_verified = False
        st.session_state.verified_key_mask = ""
    
    # 点击确认按钮时验证
    if confirm_btn and access_key:
        if validate_access_key(access_key):
            st.session_state.access_verified = True
            st.session_state.verified_key_mask = access_key[:8] + "****"
            st.rerun()
        else:
            st.session_state.access_verified = False
            st.session_state.verified_key_mask = ""
            st.error("❌ 无效的 Access Key")
    
    return st.session_state.access_verified, st.session_state.verified_key_mask


def render_watermark(key_mask: str):
    """渲染水印"""
    st.markdown(f"""
    <div class="watermark">
        授权码：{key_mask}｜仅限个人研究使用 · Licensed for personal research use only
    </div>
    """, unsafe_allow_html=True)


def render_signal_featured(row, name: str):
    """渲染 Featured Signal - 精选（Rank #1）"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-featured">
        <div class="label">★ 精选信号 · Featured Signal</div>
        <div class="stock">{code} · {name}</div>
        <div class="signal-row">
            <div class="signal-meta">评分：{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_silver(rank: int, row, name: str):
    """渲染 Silver Tier - 银牌（Rank #2-3）"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-silver">
        <div class="label">◆ 银牌信号 · Silver Tier · #{rank}</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div style="color: #6b7280;">{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_other(rank: int, row, name: str):
    """渲染 Other Signals - 其他（Rank #4-10）"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-other">
        <div class="label">◇ 其他信号 · #{rank}</div>
        <div class="signal-row">
            <div class="stock">{code} · {name}</div>
            <div style="color: #9ca3af;">{score:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_tradingview_chart(symbol: str, height: int = 420):
    """渲染 TradingView 图表"""
    
    tv_html = f"""
    <div class="tv-container">
        <div id="tradingview_widget" style="height: {height}px;"></div>
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
        图表由 TradingView 提供。TradingView® 为 TradingView, Inc. 的注册商标。
        本平台与 TradingView, Inc. 无合作、授权或隶属关系。
        该图表仅作为第三方市场可视化参考。
    </div>
    """
    components.html(tv_html, height=height + 80)


def render_trial_chart():
    """渲染试用版图表（未验证用户）"""
    
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">🔓 TradingView 试用</div>
        <div class="disclaimer-text">
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
            
            tv_html = f"""
            <div class="tv-container">
                <div id="tradingview_trial" style="height: 400px;"></div>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "width": "100%",
                "height": 400,
                "symbol": "{tv_symbol}",
                "interval": "D",
                "timezone": "Asia/Shanghai",
                "theme": "light",
                "style": "1",
                "locale": "zh_CN",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_trial"
            }});
            </script>
            """
            components.html(tv_html, height=480)
            
            st.markdown("""
            <div class="tv-disclaimer">
                TradingView® 为 TradingView, Inc. 注册商标
            </div>
            """, unsafe_allow_html=True)


def render_support_page():
    """渲染 Support & Access 页面"""
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">💡 订阅说明</div>
        <div class="disclaimer-text">
            <p>EigenFlow 为专业量化研究订阅服务，核心信号仅限订阅用户查阅。</p>
            <p>订阅权益：每日精选信号、行情辅助分析、研究方法支持。</p>
            <p><strong>注意：订阅内容为研究资料访问授权，非交易指令。</strong></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">📧 获取 Access Key</div>
        <div class="disclaimer-text">
            <ul style="margin: 8px 0; padding-left: 20px;">
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
        st.markdown('<div class="qr-section">', unsafe_allow_html=True)
        st.markdown("**💬 微信 | WeChat**")
        try:
            st.image("wechat_qr.png", width=150)
        except:
            st.info("请添加图片: wechat_qr.png")
        st.markdown('<div class="qr-note">扫码联系 | Scan to contact</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_qr2:
        st.markdown('<div class="qr-section">', unsafe_allow_html=True)
        st.markdown("**💳 支付宝 | Alipay**")
        try:
            st.image("alipay_qr.png", width=150)
        except:
            st.info("请添加图片: alipay_qr.png")
        st.markdown('<div class="qr-note">扫码支付 | Scan to pay</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 法务声明
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⚖️ 使用声明</div>
        <div class="disclaimer-text">
            <ul style="margin: 8px 0; padding-left: 20px;">
                <li><strong>使用范围：</strong>本内容仅供个人研究与学习使用，禁止转售、二次分发或任何形式的公开传播。</li>
                <li><strong>二次收费禁止：</strong>严禁任何形式的二次收费、转售或商业化使用。</li>
                <li><strong>违约后果：</strong>如发现违规行为，访问授权可能被立即终止，恕不另行通知。</li>
                <li><strong>保留权利：</strong>在必要情况下，保留采取进一步措施的权利。</li>
            </ul>
        </div>
    </div>
    """)


# ==================== 页面 | Pages ====================

def page_signal_list(key_mask: str):
    """Signal List 页面 - 订阅核心"""
    render_header()
    render_disclaimer_mini()
    
    # 已解锁标识
    st.markdown(f'<div class="unlock-badge">✓ 已解锁 · Access Granted</div>', unsafe_allow_html=True)
    
    # 加载数据
    csv_path = os.path.join(APP_DIR, 'trade_list_top10.csv')
    if not os.path.exists(csv_path):
        st.error("❌ 数据文件不存在，请上传 trade_list_top10.csv")
        st.code(csv_path)
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
    
    # 交易日提示
    now = datetime.now()
    current_hour = now.hour
    if current_hour >= 16:
        date_label = "下一个交易日"
    else:
        date_label = "今日"
    
    st.markdown(f"""
    <div style="text-align:center; margin: 12px 0 16px 0; color: #6b7280; font-size: 0.8em;">
        📅 {date_label}信号 · {now.strftime('%Y-%m-%d')}
    </div>
    """, unsafe_allow_html=True)
    
    # 分区展示
    # Featured / 精选
    if len(df_top10) >= 1:
        render_signal_featured(df_top10.iloc[0], stock_names[0])
    
    # Silver Tier / 银牌
    if len(df_top10) >= 3:
        st.markdown("#### ◆ 银牌信号 · Silver Tier", unsafe_allow_html=True)
        for i in range(1, 3):
            render_signal_silver(i + 1, df_top10.iloc[i], stock_names[i])
    
    # Other Signals / 其他
    if len(df_top10) >= 4:
        st.markdown("#### ◇ 其他信号", unsafe_allow_html=True)
        for i in range(3, min(10, len(df_top10))):
            render_signal_other(i + 1, df_top10.iloc[i], stock_names[i])
    
    # 时效性提示
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⏰ 时效性提示</div>
        <div class="disclaimer-text">
            信号具有时效性，仅在研究窗口期内具有参考意义。<br>
            <span style="color: #9ca3af;">Signals are time-sensitive and valid only within the intended research window.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 法务声明
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⚖️ 使用声明</div>
        <div class="disclaimer-text">
            <ul style="margin: 6px 0; padding-left: 16px;">
                <li>本内容仅供个人研究与学习使用，禁止转售、二次分发或公开传播。</li>
                <li>严禁二次收费、转售或商业化使用。</li>
                <li>违约可能导致访问授权被立即终止。</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 水印
    render_watermark(key_mask)


def page_chart():
    """Chart 页面 - 辅助行情"""
    render_header()
    render_disclaimer_mini()
    
    st.markdown("""
    <div style="text-align:center; margin: 16px 0 20px 0;">
        <div style="font-size: 1.1em; font-weight: 600; color: #374151;">
            📈 行情视图 · Chart
        </div>
        <div style="font-size: 0.75em; color: #6b7280;">
            股票走势辅助查看
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    df = load_signal_data()
    
    if df.empty:
        st.warning("暂无信号数据，请上传 trade_list_top10.csv")
        st.markdown("""
        <div class="disclaimer-box">
            <div class="disclaimer-title">📁 数据文件位置</div>
            <div class="disclaimer-text">
                请将 <code>trade_list_top10.csv</code> 文件上传到项目目录<br>
                文件路径: <code>{app_dir}/trade_list_top10.csv</code>
            </div>
        </div>
        """.format(app_dir=APP_DIR), unsafe_allow_html=True)
        return
    
    if 'symbol' not in df.columns:
        st.error("数据格式错误：缺少 symbol 列")
        return
    
    # 准备数据
    df_top10 = df.head(10).copy()
    df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
    
    # 创建选项列表
    stock_options = []
    for _, row in df_top10.iterrows():
        code = row['symbol']
        name = row.get('name', code)
        stock_options.append(f"{code} · {name}")
    
    if not stock_options:
        st.warning("无法生成股票选项")
        return
    
    # 选择器
    selected = st.selectbox(
        "选择股票",
        options=stock_options,
        index=0,
        label_visibility="visible",
        key="chart_select"
    )
    
    if selected:
        selected_code = selected.split(" · ")[0]
        symbol = get_tradingview_symbol(selected_code)
        
        # 调试信息（可以删除）
        # st.caption(f"股票代码: {selected_code} -> TradingView: {symbol}")
        
        render_tradingview_chart(symbol)
    
    # 水印
    render_watermark("试用模式")


def page_support():
    """Support & Access 页面"""
    render_header()
    render_disclaimer_mini()
    
    st.markdown("""
    <div style="text-align:center; margin: 16px 0 20px 0;">
        <div style="font-size: 1.1em; font-weight: 600; color: #374151;">
            ☕ 支持与订阅 · Support
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
    
    # 初始化 tab 索引
    if 'target_tab' not in st.session_state:
        st.session_state.target_tab = 0
    
    # 点击切换到支持订阅
    if st.session_state.get('switch_to_support', False):
        st.session_state.target_tab = 2
        st.session_state.switch_to_support = False
    
    # 使用 radio 作为导航（可控制切换）
    tab_options = ["📊 信号清单", "📈 行情视图", "☕ 支持订阅"]
    selected_tab_idx = st.radio(
        "",
        options=range(len(tab_options)),
        format_func=lambda x: tab_options[x],
        index=st.session_state.target_tab,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    # 重置目标
    st.session_state.target_tab = selected_tab_idx
    
    # 渲染对应页面
    if selected_tab_idx == 0:
        # ==================== 信号清单页 ====================
        
        # 验证 Access Key
        is_verified, key_mask = render_access_input()
        
        if not is_verified:
            # 未验证 - 显示醒目引导
            st.markdown("""
            <style>
            .lock-screen {
                background: linear-gradient(135deg, #fefefe 0%, #f5f5f5 100%);
                border: 2px solid #fbbf24;
                border-radius: 16px;
                padding: 32px;
                margin: 24px 0;
                text-align: center;
            }
            .lock-title {
                font-size: 1.4em;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 16px;
            }
            .lock-desc {
                font-size: 0.95em;
                color: #6b7280;
                margin-bottom: 24px;
                line-height: 1.6;
            }
            .trial-info {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                margin: 24px 0;
            }
            </style>
            
            <div class="lock-screen">
                <div class="lock-title">🔐 核心信号已锁定</div>
                <div class="lock-desc">
                    本页面展示 EigenFlow 量化研究核心信号<br>
                    包括 Rank 1-10 精选股票与评分<br><br>
                    <strong style="color:#f59e0b;">请切换至「☕ 支持订阅」页面获取 Access Key</strong>
                </div>
            </div>
            
            <!-- 切换按钮 -->
            st.markdown('<div style="text-align:center; margin: 20px 0;">', unsafe_allow_html=True)
            if st.button("🎯 立即获取 Access Key →", use_container_width=True, type="primary"):
                st.session_state.target_tab = 2
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            <div class="trial-info">
                <div style="font-weight:600; margin-bottom:12px; color:#374151;">
                    🔓 您可先试用以下功能：
                </div>
                <ul style="text-align:left; margin:0; padding-left:20px; color:#6b7280;">
                    <li>📈 切换至「行情视图」查看 TradingView 图表</li>
                    <li>📊 输入股票代码试用实时行情</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # TradingView 试用
            render_trial_chart()
            
            render_watermark("试用模式")
            st.stop()
        
        # 已验证 - 显示信号清单
        page_signal_list(key_mask)
    
    elif selected_tab_idx == 1:
        # ==================== 行情视图页 ====================
        page_chart()
    
    else:
        # ==================== 支持订阅页 ====================
        page_support()


if __name__ == "__main__":
    main()
