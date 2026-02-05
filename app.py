"""
A股量化研究工具 | A-Share Quantitative Research Tool
=====================================================
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
    from datetime import datetime
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


# ==================== 工具函数 | Utility Functions ====================

def format_stock_code(code):
    """补齐股票代码至6位 | Pad stock code to 6 digits"""
    return str(code).strip().zfill(6)


def get_latest_signal_folder(base_path):
    """获取最新信号文件夹 | Get latest signal folder"""
    if not os.path.exists(base_path):
        return None, None, None

    folders = [f for f in os.listdir(base_path) 
               if os.path.isdir(os.path.join(base_path, f))]

    if not folders:
        return None, None, None

    folders.sort(reverse=True)
    latest_folder = folders[0]
    
    # 解析日期 | Parse date
    try:
        date_str = latest_folder.split('_')[0]
        signal_date = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        signal_date = None
    
    # 判断类型 | Determine signal type
    if '_risk_on' in latest_folder:
        signal_type = 'risk_on'
    elif '_risk_off' in latest_folder:
        signal_type = 'risk_off'
    else:
        signal_type = 'unknown'
    
    return latest_folder, signal_type, signal_date


def get_tradingview_symbol(stock_code):
    """生成 TradingView 符号 | Generate TradingView symbol"""
    code = format_stock_code(stock_code)
    
    if code.startswith(('600', '601', '603', '605', '688')):
        return f"SSE:{code}"
    elif code.startswith(('000', '001', '002', '003', '300', '301')):
        return f"SZSE:{code}"
    else:
        return f"SSE:{code}"


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
    border-left: 3px solid #e74c3c;
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
</style>
""", unsafe_allow_html=True)


# ==================== 主程序 | Main ====================

def main():
    # ==================== 页面头部 | Header ====================
    st.markdown("""
    <div class="main-title">📊 EigenFlow | 量化研究工具</div>
    <div class="subtitle">Quantitative Research Tool · 仅供研究与学习 | For Research Only</div>
    """, unsafe_allow_html=True)

    # ==================== 核心免责声明 | Core Disclaimer ====================
    st.info("""
    ⚠️ **重要提示 | Important Notice**
    
    本平台展示的内容为量化模型的历史输出结果，仅供学术研究与技术交流。
    **不构成任何投资建议，不诱导任何交易行为。**
    
    This platform displays historical output from quantitative models for research purposes only. 
    **Not investment advice. No trading inducement.**
    """)
    
    st.markdown("---")

    # ==================== 数据加载 | Data Loading ====================
    # 简化路径：只从项目根目录读取 trade_list_top10.csv
    csv_path = os.path.join(os.path.dirname(__file__), 'trade_list_top10.csv')
    
    if not os.path.exists(csv_path):
        st.error("❌ 数据文件不存在 | Data file not found")
        st.info("请上传 trade_list_top10.csv 到项目目录")
        st.code(csv_path)
        return
    
    try:
        df = pd.read_csv(csv_path)
        
        # ==================== 自动判断交易日 | Auto Detect Trading Date ====================
        now = datetime.now()
        current_hour = now.hour
        
        if current_hour >= 16:
            # 16:00 之后，显示下一个交易日
            display_date = now + timedelta(days=1)
            date_label = "下一个交易日"
        else:
            # 16:00 之前，显示今天
            display_date = now
            date_label = "今日"
        
        signal_date = display_date
        latest_folder = f"{display_date.strftime('%Y-%m-%d')} (自动判断)"
        date_display = display_date.strftime('%Y-%m-%d')
        
        # 判断风险类型（如果有 risk_on/risk_off 标记）
        signal_type = "unknown"
        if 'risk_on' in csv_path.lower():
            signal_type = 'risk_on'
        elif 'risk_off' in csv_path.lower():
            signal_type = 'risk_off'
        
        st.caption(f"📅 {date_label} | Trading Day: {date_display}")
        
    except Exception as e:
        st.error(f"❌ 读取数据失败 | Data read failed: {e}")
        return

    # 验证数据格式 | Validate data format
    if 'symbol' not in df.columns or 'score' not in df.columns:
        st.error("❌ 数据格式错误 | Data format error")
        st.write("可用列 | Available columns:", df.columns.tolist())
        return

    df_top10 = df.head(10).copy()
    df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
    stock_names = df_top10.get('name', df_top10['symbol']).tolist()

    # ==================== 信号展示 | Signal Display ====================
    
    # 市场信号 | Market Signal
    if signal_type == 'risk_on':
        signal_icon = "🟢"
        signal_text_cn = "模型输出倾向：风险偏好上升"
        signal_text_en = "Model Output: Risk Appetite Rising"
        signal_detail = "数据日期 | Date: " + date_display
    elif signal_type == 'risk_off':
        signal_icon = "🔴"
        signal_text_cn = "模型输出倾向：风险偏好下降"
        signal_text_en = "Model Output: Risk Appetite Declining"
        signal_detail = "数据日期 | Date: " + date_display
    else:
        signal_icon = "🟡"
        signal_text_cn = "模型输出：观望"
        signal_text_en = "Model Output: Neutral"
        signal_detail = date_display

    st.markdown(f"""
    <div class="signal-card {'risk-on' if signal_type == 'risk_on' else 'risk-off'}">
        <div class="signal-label">{signal_icon} {signal_text_cn}</div>
        <div class="signal-value">{signal_text_en}</div>
        <div style="font-size: 0.8em; color: #666; margin-top: 5px;">{signal_detail}</div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("""
    💡 说明 | Note: 此为模型历史输出结果，不预测未来走势。
    This is historical model output, not a future prediction.
    """)

    # ==================== 内容标签页 | Content Tabs ====================
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 股票清单 | Stock List",
        "📊 图表参考 | Chart Reference", 
        "📉 历史回测 | Backtest History",
        "☕ 支持作者 | Support"
    ])

    with tab1:
        # ==================== 股票清单 | Stock List ====================
        st.markdown("### 股票清单 | Stock List")
        st.caption("基于模型历史输出的股票排序 | Historical model output ranking")

        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            # 精选推荐 | Top Pick
            st.markdown("#### 🔍 精选 | Featured")
            
            if len(df_top10) > 0:
                code = df_top10.iloc[0]['symbol']
                name = stock_names[0]
                score = df_top10.iloc[0]['score']
                
                st.markdown(f"""
                <div class="stock-item top-pick">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="font-size: 1.1em; color: #e74c3c;">{code}</strong>
                            <span style="color: #666; margin-left: 8px;">{name}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2em; font-weight: 600; color: #27ae60;">
                                {score:.2f}
                            </div>
                            <div style="font-size: 0.7em; color: #999;">分数 | Score</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 其他推荐 | Other Picks
                st.markdown("#### 📋 其他 | Others")
                
                for i in range(1, min(4, len(df_top10))):
                    code = df_top10.iloc[i]['symbol']
                    name = stock_names[i]
                    score = df_top10.iloc[i]['score']
                    
                    st.markdown(f"""
                    <div class="stock-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="color: #999; margin-right: 8px;">{i}.</span>
                                <strong>{code}</strong>
                                <span style="color: #666; margin-left: 8px;">{name}</span>
                            </div>
                            <div style="color: #27ae60; font-weight: 500;">{score:.2f}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with col_right:
            # 完整列表 | Full List
            st.markdown("#### 📊 完整排名 | Full Ranking")
            
            display_df = df_top10[['symbol', 'score']].copy()
            display_df.insert(0, '排名', range(1, len(display_df) + 1))
            display_df.columns = ['#', '代码 | Code', '分数 | Score']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        with tab2:
            # ==================== TradingView 图表 | Chart Reference ====================
            st.markdown("""
            ### 📊 图表参考 | Chart Reference
            """)
            
            st.caption("""
            ⚠️ 第三方市场行情工具 | Third-party market visualization tool
            
            TradingView® 为 TradingView, Inc. 的注册商标。
            本平台为独立研究工具，与 TradingView 不存在任何合作或隶属关系。
            """)

            # 创建选择器 | Create Selector
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
                <div style="font-size: 0.75em; color: #999; margin-top: 5px;">
                    Chart provided by TradingView® | 图表由 TradingView 提供
                </div>
                """

                components.html(tv_html, height=550)

        with tab3:
            # ==================== 历史回测 | Backtest ====================
            st.markdown("""
            ### 📉 历史回测 | Backtest History
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

                    # 指标卡片 | Metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "初始净值 | Initial", 
                            f"{initial:.4f}",
                            help="回测起始点 | Backtest start"
                        )
                    with col2:
                        st.metric(
                            "当前净值 | Current", 
                            f"{final:.4f}",
                            help="回测结束点 | Backtest end"
                        )
                    with col3:
                        delta_color = "normal" if total_return >= 0 else "inverse"
                        st.metric(
                            "收益率 | Return", 
                            f"{total_return:.2f}%",
                            delta=f"{total_return:.2f}%",
                            delta_color=delta_color,
                            help="总收益率 | Total return"
                        )

                    # 曲线图 | Chart
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
            st.markdown("""
            ### ☕ 支持作者 | Support
            """)
            
            st.markdown("""
            <div class="disclaimer-box">
                <div class="disclaimer-title">💡 支持说明 | Support Info</div>
                <p>您的支持有助于：</p>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>持续运行模型服务器 | Keep model server running</li>
                    <li>优化研究工具 | Optimize research tools</li>
                    <li>开发新功能 | Develop new features</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            col_qr1, col_qr2 = st.columns(2)

            with col_qr1:
                st.markdown('<div class="qr-section">', unsafe_allow_html=True)
                st.markdown("**💬 微信 | WeChat**")
                try:
                    st.image("wechat_qr.png", width=160)
                except:
                    st.warning("请添加图片 | Add image: wechat_qr.png")
                st.markdown('<div class="qr-note">扫码支持 | Scan to support</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_qr2:
                st.markdown('<div class="qr-section">', unsafe_allow_html=True)
                st.markdown("**💳 支付宝 | Alipay**")
                try:
                    st.image("alipay_qr.png", width=160)
                except:
                    st.warning("请添加图片 | Add image: alipay_qr.png")
                st.markdown('<div class="qr-note">扫码支持 | Scan to support</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # ==================== 底部免责声明 | Footer Disclaimer ====================
    st.markdown("---")
    
    st.markdown("""
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
