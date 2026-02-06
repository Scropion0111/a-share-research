"""
A股量化研究工具 | A-Share Quantitative Research Tool
=====================================================
订阅版 | Subscription Edition
本项目仅供研究与学习 | For Research and Educational Purposes Only

免责声明 | Disclaimer:
- 不构成任何投资建议 | Not Investment Advice
- 不诱导任何交易行为 | No Trading Inducement
- 过往表现不代表未来收益 | Past Performance ≠ Future Results
"""

try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import streamlit.components.v1 as components
    import os
    from datetime import datetime, timedelta
    STREAMLIT_AVAILABLE = True

    # 页面配置 | Page Config
    st.set_page_config(
        page_title="EigenFlow | 量化研究",
        page_icon="📊",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("请安装必要依赖 | Install dependencies:")
    print("pip install streamlit pandas plotly")
    exit(1)


# ==================== 订阅配置 | Subscription Config ====================

# Access Keys（生产环境建议使用环境变量）
VALID_ACCESS_KEYS = [
    "EIGEN-2026-PRO",
    "EIGEN-RESEARCH-X1",
    "EIGEN-VIP-2026",
]

def validate_access_key(key: str) -> bool:
    """验证 Access Key"""
    return key.strip() in VALID_ACCESS_KEYS


# ==================== 工具函数 | Utility Functions ====================

def format_stock_code(code):
    """补齐股票代码至6位 | Pad stock code to 6 digits"""
    return str(code).strip().zfill(6)


def get_tradingview_symbol(stock_code):
    """生成 TradingView 符号 | Generate TradingView symbol"""
    code = format_stock_code(stock_code)

    if code.startswith(('600', '601', '603', '605', '688')):
        return f"SSE:{code}"
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        return f"SZSE:{code}"
    else:
        return f"SSE:{code}"


def load_signal_data():
    """加载信号数据"""
    csv_path = os.path.join(os.path.dirname(__file__), 'trade_list_top10.csv')
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()


# ==================== 自定义 CSS | Custom CSS ====================

st.markdown("""
<style>
/* 限制宽度 | Limit Width */
.block-container {
    max-width: 700px !important;
    padding-top: 0.5rem !important;
    padding-bottom: 3rem !important;
}

/* 标题 | Title */
.main-title {
    font-size: 1.2em;
    font-weight: 600;
    text-align: center;
    margin-bottom: 5px;
    color: #2c3e50;
}

.subtitle {
    text-align: center;
    color: #7f8c8d;
    font-size: 0.75em;
    margin-bottom: 10px;
}

/* Access Key 输入区 | Access Key Input */
.access-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border: 1px solid #dee2e6;
    border-radius: 12px;
    padding: 24px;
    margin: 20px 0;
}

.access-title {
    font-size: 1em;
    font-weight: 600;
    color: #495057;
    margin-bottom: 16px;
    text-align: center;
}

.unlock-badge {
    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
    color: #1a1a2e;
    padding: 8px 20px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    text-align: center;
    margin-bottom: 16px;
}

/* 信号卡片 | Signal Card */
.signal-card {
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
    text-align: center;
}

.risk-on {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
    border: 1px solid #bdc3c7;
}

.risk-off {
    background: linear-gradient(135deg, #fff5f5 0%, #ffe0e0 100%);
    border: 1px solid #e74c3c;
}

.signal-label {
    font-size: 0.85em;
    color: #7f8c8d;
    margin-bottom: 5px;
}

.signal-value {
    font-size: 1.1em;
    font-weight: 500;
    color: #2c3e50;
}

/* 股票卡片 | Stock Card */
.stock-item {
    background: #fafafa;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 3px solid #3498db;
}

.stock-item.top-pick {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-left: 3px solid #f59e0b;
}

/* 免责声明 | Disclaimer */
.disclaimer-box {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 15px;
    margin: 20px 0;
    font-size: 0.8em;
    color: #6c757d;
}

.disclaimer-title {
    font-weight: 600;
    margin-bottom: 8px;
    color: #495057;
}

/* 标签页样式 | Tab Style */
.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 16px;
    background: #f0f2f5;
}

.stTabs [aria-selected="true"] {
    background: #3498db;
    color: white;
}

/* TradingView 容器 | TV Container */
.tv-container {
    border-radius: 10px;
    overflow: hidden;
    margin: 15px 0;
}

/* 二维码区域 | QR Area */
.qr-section {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    margin: 10px 0;
}

.qr-note {
    font-size: 0.75em;
    color: #6c757d;
    margin-top: 8px;
}

/* 隐藏 Streamlit 默认元素 */
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
    <div class="subtitle">Quantitative Research Tool · Subscription Required</div>
    """, unsafe_allow_html=True)


def render_access_input() -> bool:
    """渲染 Access Key 输入框，返回是否验证成功"""

    st.markdown("""
    <div class="access-section">
        <div class="access-title">🔐 输入访问密钥 | Enter Access Key</div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        access_key = st.text_input(
            "Access Key",
            type="password",
            placeholder="EIGEN-XXXX-XXXX",
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

    # 点击确认按钮时验证
    if confirm_btn and access_key:
        if validate_access_key(access_key):
            st.session_state.access_verified = True
            st.rerun()
        else:
            st.session_state.access_verified = False
            st.error("❌ 无效的 Access Key")

    return st.session_state.access_verified


def render_support_page():
    """渲染支持页面"""
    st.markdown("""
    <div class="disclaimer-box">
        <div class="disclaimer-title">💡 订阅说明 | Subscription Info</div>
        <p>EigenFlow 为专业量化研究订阅服务，核心信号仅限订阅用户查阅。</p>
        <p>订阅权益：每日精选信号、市场辅助分析、策略研究支持。</p>
    </div>
    
    <div class="disclaimer-box">
        <div class="disclaimer-title">📧 联系获取 Access Key</div>
        <ul style="margin: 10px 0; padding-left: 20px;">
            <li>微信：扫描下方二维码</li>
            <li>Email：research@eigenflow.io</li>
            <li>Telegram：@eigenflow_research</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 二维码
    col_qr1, col_qr2 = st.columns(2)

    with col_qr1:
        st.markdown('<div class="qr-section">', unsafe_allow_html=True)
        st.markdown("**💬 微信 | WeChat**")
        try:
            st.image("wechat_qr.png", width=160)
        except:
            st.info("请添加图片: wechat_qr.png")
        st.markdown('<div class="qr-note">扫码联系 | Scan to contact</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_qr2:
        st.markdown('<div class="qr-section">', unsafe_allow_html=True)
        st.markdown("**💳 支付宝 | Alipay**")
        try:
            st.image("alipay_qr.png", width=160)
        except:
            st.info("请添加图片: alipay_qr.png")
        st.markdown('<div class="qr-note">扫码支付 | Scan to pay</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==================== 主程序 | Main ====================

def main():
    # ==================== 页面头部 | Header ====================
    render_header()

    # ==================== 核心免责声明 | Core Disclaimer ====================
    st.info("""
    ⚠️ **重要提示 | Important Notice**
    
    本平台展示的内容为量化模型的历史输出结果，仅供学术研究与技术交流。
    **不构成任何投资建议，不诱导任何交易行为。**
    """)

    st.markdown("---")

    # ==================== Access Key 验证 | Access Key Verification ====================
    is_verified = render_access_input()

    # ==================== 验证失败显示支持页 | Show Support if Not Verified ====================
    if not is_verified:
        if 'access_verified' not in st.session_state or not st.session_state.access_verified:
            st.info("💡 请输入有效的 Access Key 以解锁核心信号")
            render_support_page()
            st.markdown("---")
            st.markdown("""
            <div class="disclaimer-box">
                <div class="disclaimer-title">🔓 试用功能 | Trial Features</div>
                <p>您仍可查看以下辅助功能：</p>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>TradingView 图表参考</li>
                    <li>研究方法说明</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # 简化版图表（不显示具体信号）
            st.markdown("### 📊 TradingView 试用")
            st.caption("输入任意股票代码查看走势")

            trial_symbol = st.text_input(
                "输入股票代码",
                placeholder="600519, 000001",
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
                        <div id="tradingview_trial"></div>
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
                    <div style="font-size: 0.75em; color: #999; margin-top: 5px; text-align: center;">
                        TradingView® 为 TradingView, Inc. 注册商标
                    </div>
                    """
                    components.html(tv_html, height=480)

            st.stop()

    # ==================== 验证成功 - 加载数据 | Load Data ====================
    st.markdown('<div class="unlock-badge">✓ 已解锁 | Access Granted</div>', unsafe_allow_html=True)

    csv_path = os.path.join(os.path.dirname(__file__), 'trade_list_top10.csv')

    if not os.path.exists(csv_path):
        st.error("❌ 数据文件不存在 | Data file not found")
        st.info("请上传 trade_list_top10.csv 到项目目录")
        return

    try:
        df = pd.read_csv(csv_path)

        # 交易日判断
        now = datetime.now()
        current_hour = now.hour

        if current_hour >= 16:
            display_date = now + timedelta(days=1)
            date_label = "下一个交易日"
        else:
            display_date = now
            date_label = "今日"

        date_display = display_date.strftime('%Y-%m-%d')
        st.caption(f"📅 {date_label} | Trading Day: {date_display}")

    except Exception as e:
        st.error(f"❌ 读取数据失败 | Data read failed: {e}")
        return

    # 验证数据格式
    if 'symbol' not in df.columns:
        st.error("❌ 数据格式错误 | Data format error")
        return

    df_top10 = df.head(10).copy()
    df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
    stock_names = df_top10.get('name', df_top10['symbol']).tolist()

    # ==================== 标签页 | Tabs ====================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Signal List",
        "📈 Chart",
        "📉 Backtest",
        "☕ Support"
    ])

    with tab1:
        # ==================== 信号展示 | Signal Display ====================
        st.markdown("### 📊 Signal List")
        st.caption("Rank 1–10 | 基于模型历史输出")

        # Rank 1 - Featured
        if len(df_top10) > 0:
            code = df_top10.iloc[0]['symbol']
            name = stock_names[0]
            score = df_top10.iloc[0].get('score', 0)

            st.markdown(f"""
            <div class="signal-card risk-on" style="border: 2px solid #f59e0b;">
                <div class="signal-label" style="color: #b45309;">★ Featured Signal</div>
                <div style="font-size: 1.2em; font-weight: 700; color: #1a1a2e;">
                    {code} · {name}
                </div>
                <div style="font-size: 0.85em; color: #78350f; margin-top: 4px;">
                    Score: {score:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Rank 2-3 - Silver
        if len(df_top10) >= 3:
            st.markdown("#### ◆ Silver Tier")
            for i in range(1, 3):
                if i < len(df_top10):
                    code = df_top10.iloc[i]['symbol']
                    name = stock_names[i]
                    score = df_top10.iloc[i].get('score', 0)
                    st.markdown(f"""
                    <div class="stock-item" style="border-left-color: #6b7280;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{code}</strong>
                                <span style="color: #666; margin-left: 8px;">{name}</span>
                            </div>
                            <div style="color: #6b7280; font-weight: 500;">{score:.2f}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Rank 4-10 - Other
        if len(df_top10) >= 4:
            st.markdown("#### ◇ Other Signals")
            for i in range(3, min(10, len(df_top10))):
                code = df_top10.iloc[i]['symbol']
                name = stock_names[i]
                score = df_top10.iloc[i].get('score', 0)
                st.markdown(f"""
                <div class="stock-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #999; margin-right: 8px;">{i}.</span>
                            <strong>{code}</strong>
                            <span style="color: #666; margin-left: 8px;">{name}</span>
                        </div>
                        <div style="color: #9ca3af;">{score:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        # ==================== TradingView 图表 | Chart ====================
        st.markdown("""
        ### 📈 Chart Reference
        """)

        st.caption("""
        ⚠️ 第三方市场行情工具 | TradingView® 为 TradingView, Inc. 注册商标
        """)

        # 创建选择器
        stock_options = [f"{code} - {name}" for code, name in zip(df_top10['symbol'], stock_names)]
        selected = st.selectbox(
            "选择股票 | Select Stock",
            stock_options,
            index=0,
            label_visibility="visible"
        )

        if selected:
            selected_code = selected.split(" - ")[0]
            selected_name = selected.split(" - ")[1]
            symbol = get_tradingview_symbol(selected_code)

            # TradingView Widget
            tv_html = f"""
            <div class="tv-container">
                <div id="tradingview_widget"></div>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
            new TradingView.widget({{
                "width": "100%",
                "height": 480,
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
            <div style="font-size: 0.75em; color: #999; margin-top: 5px; text-align: center;">
                TradingView® 为 TradingView, Inc. 注册商标 | 本平台无关联
            </div>
            """
            components.html(tv_html, height=550)

    with tab3:
        # ==================== 历史回测 | Backtest ====================
        st.markdown("""
        ### 📉 Backtest History
        """)
        st.caption("策略历史表现，仅供研究参考 | Historical strategy performance for reference only")

        equity_path = 'equity.csv'

        if os.path.exists(equity_path):
            try:
                equity_df = pd.read_csv(equity_path)
                equity_df['date'] = pd.to_datetime(equity_df['date'])

                initial = equity_df['equity'].iloc[0]
                final = equity_df['equity'].iloc[-1]
                total_return = (final - initial) / initial * 100

                # 指标卡片
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "初始净值 | Initial",
                        f"{initial:.4f}"
                    )
                with col2:
                    st.metric(
                        "当前净值 | Current",
                        f"{final:.4f}"
                    )
                with col3:
                    delta_color = "normal" if total_return >= 0 else "inverse"
                    st.metric(
                        "收益率 | Return",
                        f"{total_return:.2f}%",
                        delta=f"{total_return:.2f}%",
                        delta_color=delta_color
                    )

                # 曲线图
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=equity_df['date'],
                    y=equity_df['equity'],
                    mode='lines',
                    name='净值 | NAV',
                    line=dict(color='#3498db', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(52, 152, 219, 0.1)'
                ))

                fig.update_layout(
                    title="策略净值曲线 | Strategy NAV Curve",
                    xaxis_title="日期 | Date",
                    yaxis_title="净值 | NAV",
                    height=350,
                    template="plotly_white",
                    hovermode="x unified"
                )

                st.plotly_chart(fig, use_container_width=True)

                st.caption("⚠️ 历史表现不代表未来收益 | Past performance ≠ future results")

            except Exception as e:
                st.warning(f"数据加载失败 | Data load failed: {e}")
        else:
            st.info("暂无历史数据 | No historical data available")

    with tab4:
        # ==================== 支持作者 | Support ====================
        render_support_page()

    # ==================== 底部免责声明 | Footer Disclaimer ====================
    st.markdown("---")

    st.markdown(f"""
    <div class="disclaimer-box">
        <div class="disclaimer-title">⚠️ 法律声明 | Legal Disclaimer</div>
        <ul style="margin: 0; padding-left: 20px;">
            <li>本平台为独立量化研究工具 | This is an independent quantitative research tool</li>
            <li>不构成投资建议 | Not investment advice</li>
            <li>不诱导任何交易行为 | No trading inducement</li>
            <li>过往表现不代表未来收益 | Past performance ≠ future results</li>
            <li>投资者应自行判断并承担风险 | Investors should make their own decisions</li>
        </ul>
        <hr style="margin: 15px 0; border-color: #dee2e6;">
        <div style="font-size: 0.75em; color: #999;">
            <strong>TradingView 声明 | TradingView Notice:</strong><br>
            TradingView® 为 TradingView, Inc. 的注册商标 | Registered trademark of TradingView, Inc.<br>
            本平台与 TradingView, Inc. 不存在任何合作、授权或隶属关系 | No affiliation with TradingView, Inc.
        </div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
