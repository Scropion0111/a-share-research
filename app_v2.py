"""
================================================================================
EigenFlow | 量化研究订阅平台
Subscription-based Quantitative Research Platform

文件结构：
├── app.py              # 主程序
├── keys.json           # Access Keys 配置（生产环境请用 st.secrets）
├── key_state.json      # Key 激活状态（自动生成）
└── usage_log.jsonl     # 使用日志（自动生成）

================================================================================
"""

import streamlit as st
import pandas as pd
import os
import json
import hashlib
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path

# ==================== 配置 | Configuration ====================

st.set_page_config(
    page_title="EigenFlow | 量化研究",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 路径配置
APP_DIR = os.path.dirname(__file__)
KEYS_FILE = os.path.join(APP_DIR, 'keys.json')
KEY_STATE_FILE = os.path.join(APP_DIR, 'key_state.json')
USAGE_LOG_FILE = os.path.join(APP_DIR, 'usage_log.jsonl')

# ==================== 风控配置 | Risk Control Config ====================
# 【异常阈值配置位置】
# - 同一 key 24h 内最大设备数：2
# - 短时间窗口（秒）：300（5分钟内）
# - 最大不同IP/UA/设备组合数：3
DEVICE_LIMIT_PER_KEY = 2
TIME_WINDOW_SECONDS = 300
MAX_DEVICE_COMBINATIONS = 3


# ==================== 工具函数 | Utility Functions ====================

def get_file_hash(text: str) -> str:
    """生成文本的短 hash（用于日志脱敏）"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def get_ip():
    """获取客户端 IP（可能为空）"""
    # Streamlit 在某些部署环境下可获取
    try:
        return st.session_state.get('client_ip', 'unknown')
    except:
        return 'unknown'


def get_user_agent():
    """获取 User-Agent"""
    try:
        return st.context.headers.get('user-agent', 'unknown') if hasattr(st.context, 'headers') else 'unknown'
    except:
        return 'unknown'


def load_keys():
    """
    加载 Access Keys
    优先级：st.secrets > keys.json 文件
    """
    # 优先从 secrets 加载（生产环境推荐）
    try:
        if hasattr(st, 'secrets') and 'keys' in st.secrets:
            return st.secrets['keys']
    except:
        pass
    
    # 从 keys.json 文件加载
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 过滤注释键
                return {k: v for k, v in data.items() if not k.startswith('_')}
        except Exception as e:
            st.error(f"加载 keys.json 失败: {e}")
            return {}
    
    return {}


def load_key_state():
    """加载 Key 使用状态（首次激活时间等）"""
    if os.path.exists(KEY_STATE_FILE):
        try:
            with open(KEY_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_key_state(state: dict):
    """保存 Key 使用状态"""
    with open(KEY_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def log_access(key: str, device_id: str, status: str, details: dict = None):
    """
    记录使用日志
    【日志记录字段】
    - key_mask: Key 的部分掩码（安全）
    - timestamp: ISO 格式时间
    - ip_hash: IP 的 hash（脱敏）
    - ua_hash: User-Agent 的 hash（脱敏）
    - device_id: 设备标识
    - status: 状态（success/denied/expired/suspicious）
    - details: 附加信息
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "key_mask": key[:8] + "****" if len(key) > 8 else "****",
        "ip_hash": get_file_hash(get_ip()),
        "ua_hash": get_file_hash(get_user_agent()),
        "device_id": device_id,
        "status": status,
        "details": details or {}
    }
    
    # 写入日志文件
    try:
        with open(USAGE_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        pass  # 日志写入失败不应影响主流程


def check_device_anomaly(key: str, device_id: str) -> tuple[bool, str]:
    """
    检查设备异常
    【异常检测规则】
    1. 同一 key 24h 内出现 >2 个不同 device_id
    2. 短时间内出现多个不同 IP/UA/device 组合
    
    返回: (是否异常, 警告信息)
    """
    if not os.path.exists(USAGE_LOG_FILE):
        return False, ""
    
    try:
        with open(USAGE_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = [json.loads(line) for line in f if line.strip()]
    except:
        return False, ""
    
    now = datetime.now()
    recent_logs = [
        log for log in logs
        if log.get('key_mask') == (key[:8] + "****" if len(key) > 8 else key)
        and (now - datetime.fromisoformat(log['timestamp'])).total_seconds() < 86400  # 24h
    ]
    
    # 获取不同 device_id 数量
    device_ids = set(log.get('device_id', '') for log in recent_logs)
    if len(device_ids) > DEVICE_LIMIT_PER_KEY:
        return True, f"检测到异常使用行为：同一密钥在24小时内使用于 {len(device_ids)} 个设备。"
    
    # 短时间多组合检测
    short_window = [
        log for log in logs
        if log.get('key_mask') == (key[:8] + "****" if len(key) > 8 else key)
        and (now - datetime.fromisoformat(log['timestamp'])).total_seconds() < TIME_WINDOW_SECONDS
    ]
    
    combinations = set(
        (log.get('ip_hash', ''), log.get('ua_hash', ''), log.get('device_id', ''))
        for log in short_window
    )
    
    if len(combinations) > MAX_DEVICE_COMBINATIONS:
        return True, f"检测到异常使用行为：短时间内出现 {len(combinations)} 个不同访问组合。"
    
    return False, ""


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
    """获取或生成设备 ID（session 持久化）"""
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id


# ==================== Access Key 验证 | Access Key Validation ====================

def validate_key(key: str) -> tuple[bool, str, int]:
    """
    验证 Access Key
    【Key 首次激活与到期逻辑】
    1. 检查 Key 格式是否有效
    2. 检查是否首次使用：若是，记录 first_seen = 今天
    3. 检查是否过期：first_seen + days > 今天
    4. 检查是否在黑名单/异常
    
    返回: (是否有效, 状态信息, 剩余天数)
    """
    keys = load_keys()
    key_state = load_key_state()
    
    # Key 格式验证
    if key not in keys:
        return False, "Key 无效", 0
    
    key_info = keys[key]
    days_allowed = key_info.get('days', 30)
    
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    # 检查首次激活时间
    if key not in key_state:
        # 首次使用，记录激活时间
        key_state[key] = {
            'first_seen': today,
            'name': key_info.get('name', '用户'),
            'last_seen': today
        }
        save_key_state(key_state)
    
    first_seen = datetime.strptime(key_state[key]['first_seen'], '%Y-%m-%d')
    expiry_date = first_seen + timedelta(days=days_allowed)
    remaining_days = (expiry_date - now).days
    
    # 检查是否过期
    if remaining_days < 0:
        return False, f"Key 已过期（于 {key_state[key]['first_seen']} 激活，有效期 {days_allowed} 天）", remaining_days
    
    # 更新最后使用时间
    key_state[key]['last_seen'] = today
    save_key_state(key_state)
    
    return True, f"有效（剩余 {remaining_days} 天）", remaining_days


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


def render_access_input() -> tuple[bool, str, int]:
    """
    渲染 Access Key 输入框
    返回: (是否验证成功, Key掩码, 剩余天数)
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
    
    # 初始化
    if 'access_verified' not in st.session_state:
        st.session_state.access_verified = False
        st.session_state.verified_key_mask = ""
        st.session_state.verified_remaining_days = 0
    
    device_id = get_device_id()
    
    # 点击确认按钮时验证
    if confirm_btn and access_key:
        is_valid, message, remaining = validate_key(access_key)
        
        if is_valid:
            # 检查设备异常
            is_suspicious, warning = check_device_anomaly(access_key, device_id)
            
            if is_suspicious:
                log_access(access_key, device_id, "suspicious", {"reason": warning})
                st.warning(f"⚠️ {warning} 如需多设备使用请联系作者。")
            else:
                st.session_state.access_verified = True
                st.session_state.verified_key_mask = access_key[:8] + "****"
                st.session_state.verified_remaining_days = remaining
                log_access(access_key, device_id, "success", {"remaining_days": remaining})
                st.rerun()
        else:
            log_access(access_key, device_id, "denied", {"reason": message})
            st.error(f"❌ {message}")
    
    return st.session_state.access_verified, st.session_state.verified_key_mask, st.session_state.verified_remaining_days


def render_watermark(key_mask: str):
    """渲染水印【授权码：EF-26Q1-****KZ2M｜仅限个人研究使用】"""
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
    """
    st.markdown(tv_html, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tv-disclaimer">
        图表由 TradingView 提供。TradingView® 为 TradingView, Inc. 的注册商标。
        本平台与 TradingView, Inc. 无合作、授权或隶属关系。
        该图表仅作为第三方市场可视化参考。
    </div>
    """, unsafe_allow_html=True)


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
    
    # 创建选择器
    if not df.empty:
        df_top10 = df.head(10).copy()
        df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
        
        stock_options = [
            f"{row['symbol']} · {row.get('name', row['symbol'])}"
            for _, row in df_top10.iterrows()
        ]
        
        selected = st.selectbox(
            "选择股票",
            options=stock_options,
            index=0,
            label_visibility="visible"
        )
        
        if selected:
            selected_code = selected.split(" · ")[0]
            symbol = get_tradingview_symbol(selected_code)
            render_tradingview_chart(symbol)
    else:
        st.info("暂无信号数据")
    
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
    
    # 页面导航
    tab1, tab2, tab3 = st.tabs([
        "📊 信号清单",
        "📈 行情视图",
        "☕ 支持订阅"
    ])
    
    with tab1:
        # 验证 Access Key
        is_verified, key_mask, remaining_days = render_access_input()
        
        if not is_verified:
            # 未验证 - 显示试用信息
            st.info("💡 请输入有效的 Access Key 解锁核心信号")
            st.markdown("""
            <div class="disclaimer-box">
                <div class="disclaimer-title">🔓 试用功能</div>
                <div class="disclaimer-text">
                    您可切换至「行情视图」标签查看股票走势图。
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        # 已验证 - 显示信号清单
        if remaining_days <= 7 and remaining_days > 0:
            st.warning(f"⚠️ Key 即将到期（剩余 {remaining_days} 天），请及时续费")
        
        page_signal_list(key_mask)
    
    with tab2:
        page_chart()
    
    with tab3:
        page_support()


if __name__ == "__main__":
    main()
