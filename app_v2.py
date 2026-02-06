"""
================================================================================
EigenFlow | 量化研究订阅平台
Subscription-based Quantitative Research Platform

【订阅型研究产品化重构 v2.2】
├── 纯横向导航栏（点击有效）
├── 行情视图需Key验证
├── 反共享风控与水印
└── 合规克制设计

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
from pathlib import Path

# UI 模块
from ui.theme import (
    BRAND_COLORS,
    RANK_EMOJIS,
    FONT_SIZES,
    get_rank_emoji,
    get_page_title,
    get_page_icon,
)

# ==================== 配置 | Configuration ====================

st.set_page_config(
    page_title="EigenFlow | 量化研究",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🔥 彻底隐藏 sidebar（保留 trigger 按钮逻辑）
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

APP_DIR = os.path.dirname(__file__)

# ==================== 文件路径配置 ====================

KEY_STATE_FILE = os.path.join(APP_DIR, 'key_state.json')
USAGE_LOG_FILE = os.path.join(APP_DIR, 'usage_log.jsonl')
KEYS_FILE = os.path.join(APP_DIR, 'keys.json')

# ==================== 风控配置 ====================

SHARE_CONFIG = {
    'max_devices_per_key': 2,
    'time_window_hours': 24,
    'device_threshold': 2,
}

KEY_VALIDITY_DAYS = 30

# ==================== Key 存储与验证 ====================

def load_valid_keys():
    """加载有效 Key 列表（优先 secrets，其次本地 keys.json）"""
    try:
        if hasattr(st.secrets, 'access_keys'):
            return st.secrets.access_keys.get('keys', [])
    except:
        pass
    
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('keys', [])
        except:
            pass
    
    return [
        "EF-26Q1-A9F4KZ2M",
        "EF-26Q1-B3H8LP5N", 
        "EF-26Q1-C7J2MR9R",
    ]


def validate_access_key(key: str) -> dict:
    """验证 Access Key 并返回状态"""
    key = key.strip().upper()
    valid_keys = load_valid_keys()
    
    if key not in valid_keys:
        return {'valid': False, 'key': key[:8] + '****'}
    
    key_state = load_key_state()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    
    if key not in key_state:
        key_state[key] = {
            'first_seen': today,
            'activated_at': now.isoformat(),
            'devices': [],
            'ips': [],
            'warnings': 0
        }
        save_key_state(key_state)
        return {
            'valid': True,
            'key': mask_key(key),
            'first_seen': today,
            'days_remaining': KEY_VALIDITY_DAYS,
            'expired': False,
            'is_first_use': True
        }
    
    first_seen_date = datetime.strptime(key_state[key]['first_seen'], '%Y-%m-%d')
    days_used = (now - first_seen_date).days
    
    if days_used >= KEY_VALIDITY_DAYS:
        return {
            'valid': False,
            'key': mask_key(key),
            'first_seen': key_state[key]['first_seen'],
            'days_remaining': 0,
            'expired': True
        }
    
    return {
        'valid': True,
        'key': mask_key(key),
        'first_seen': key_state[key]['first_seen'],
        'days_remaining': KEY_VALIDITY_DAYS - days_used,
        'expired': False,
        'is_first_use': False
    }


def mask_key(key: str) -> str:
    if len(key) >= 12:
        return f"{key[:8]}{'****'}{key[-4:]}"
    return key[:6] + '****'


# ==================== Key 状态持久化 ====================

def load_key_state() -> dict:
    if os.path.exists(KEY_STATE_FILE):
        try:
            with open(KEY_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_key_state(state: dict):
    with open(KEY_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ==================== 设备指纹与日志 ====================

def get_device_id():
    if 'device_id' not in st.session_state:
        st.session_state.device_id = str(uuid.uuid4())
    return st.session_state.device_id


def get_client_info():
    ip = 'unknown'
    try:
        ip = st.context.headers.get('X-Forwarded-For', 'unknown').split(',')[0].strip()
    except:
        pass
    
    ua = 'unknown'
    try:
        ua = st.context.headers.get('User-Agent', 'unknown')
    except:
        pass
    
    return {
        'ip': hashlib.md5(ip.encode()).hexdigest()[:16] if ip != 'unknown' else 'unknown',
        'ua_hash': hashlib.md5(ua.encode()).hexdigest()[:16] if ua != 'unknown' else 'unknown',
        'device_id': get_device_id()
    }


def log_usage(key: str, status: str = 'access'):
    now = datetime.now()
    client = get_client_info()
    
    log_entry = {
        'timestamp': now.isoformat(),
        'key_mask': mask_key(key),
        'status': status,
        'ip_hash': client['ip'],
        'ua_hash': client['ua_hash'],
        'device_id': client['device_id'],
        'page': st.session_state.get('current_tab', 'unknown')
    }
    
    try:
        with open(USAGE_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except:
        pass


def check_share_anomaly(key: str) -> dict:
    key_state = load_key_state()
    
    if key not in key_state:
        return {'is_anomaly': False, 'warning_message': None, 'should_block': False}
    
    state = key_state[key]
    now = datetime.now()
    window_start = now - timedelta(hours=SHARE_CONFIG['time_window_hours'])
    
    if not os.path.exists(USAGE_LOG_FILE):
        return {'is_anomaly': False, 'warning_message': None, 'should_block': False}
    
    try:
        with open(USAGE_LOG_FILE, 'r', encoding='utf-8') as f:
            recent_devices = set()
            recent_entries = []
            
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get('key_mask', '').replace('*', '') in key:
                        log_time = datetime.fromisoformat(entry['timestamp'])
                        if log_time >= window_start:
                            recent_entries.append(entry)
                            if entry.get('device_id'):
                                recent_devices.add(entry['device_id'])
                except:
                    pass
    
    except:
        return {'is_anomaly': False, 'warning_message': None, 'should_block': False}
    
    device_count = len(recent_devices)
    
    if device_count > SHARE_CONFIG['device_threshold']:
        return {
            'is_anomaly': True,
            'warning_message': f"⚠️ 检测到异常使用行为：同一账号在 {SHARE_CONFIG['time_window_hours']} 小时内被 {device_count} 个设备使用。如需多设备使用，请联系作者。",
            'should_block': False
        }
    
    return {'is_anomaly': False, 'warning_message': None, 'should_block': False}


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


# ==================== CSS 样式 | 顶级设计 ====================

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
    margin-bottom: 20px;
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

/* 免责声明条 */
.disclaimer-bar {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 16px 0;
    font-size: 0.7em;
    color: #9ca3af;
    text-align: center;
    line-height: 1.7;
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
    font-size: 1.25em;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 12px;
}

.lock-desc {
    font-size: 0.88em;
    color: #6b7280;
    line-height: 1.7;
    margin-bottom: 20px;
}

/* 信号卡片 */
.signal-card {
    padding: 18px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: center;
}

/* Featured - 金色 */
.signal-featured {
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    border: 2px solid #f59e0b;
}

.signal-featured .label {
    color: #b45309;
    font-size: 0.65em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

/* Silver */
.signal-silver {
    background: linear-gradient(135deg, #f9fafb, #f3f4f6);
    border: 1px solid #d1d5db;
}

.signal-silver .label {
    color: #6b7280;
    font-size: 0.6em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

/* Other */
.signal-other {
    background: #fff;
    border: 1px solid #e5e7eb;
}

.signal-other .label {
    color: #9ca3af;
    font-size: 0.6em;
    font-weight: 500;
    margin-bottom: 4px;
}

.stock-code {
    font-size: 1.1em;
    font-weight: 600;
    color: #1a1a1a;
}

.stock-name {
    color: #4b5563;
    margin-left: 8px;
}

.signal-score {
    font-size: 0.9em;
    color: #6b7280;
}

/* 分区标题 */
.section-title {
    font-size: 0.8em;
    font-weight: 600;
    color: #374151;
    margin: 20px 0 12px;
    padding-left: 12px;
    border-left: 3px solid #f59e0b;
}

/* 日期标签 */
.date-label {
    text-align: center;
    margin: 12px 0 20px;
    color: #6b7280;
    font-size: 0.78em;
}

/* 水印 */
.watermark {
    position: fixed;
    bottom: 6px;
    left: 0;
    right: 0;
    text-align: center;
    font-size: 0.58em;
    color: #d1d5db;
    padding: 8px;
    background: linear-gradient(to top, rgba(255,255,255,0.95), transparent);
    z-index: 100;
}

/* TradingView */
.tv-container {
    border-radius: 10px;
    overflow: hidden;
    margin: 16px 0;
    border: 1px solid #e5e7eb;
}

.tv-disclaimer {
    font-size: 0.58em;
    color: #9ca3af;
    text-align: center;
    padding: 10px;
    background: #f9fafb;
    margin-top: 8px;
    line-height: 1.5;
}

/* 卡片样式 */
.info-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px;
    margin: 14px 0;
}

.info-card-title {
    font-size: 0.95em;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 10px;
}

.info-card-text {
    font-size: 0.8em;
    color: #6b7280;
    line-height: 1.7;
}

/* 二维码区域 */
.qr-area {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 14px;
    text-align: center;
    margin: 12px 0;
}

.qr-label {
    font-size: 0.78em;
    color: #6b7280;
    margin-top: 8px;
}

/* 输入框组 */
.input-group {
    background: linear-gradient(135deg, #fafafa, #f0f0f0);
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px;
    margin: 16px 0;
}

.input-label {
    font-size: 0.9em;
    font-weight: 600;
    color: #374151;
    margin-bottom: 12px;
    text-align: center;
}

/* 隐藏元素 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* 隐藏触发按钮 */
button[id^="trigger_"] {
    visibility: hidden !important;
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    border: 0 !important;
}

/* 权限提示 */
.locked-prompt {
    background: linear-gradient(135deg, #fef3c7, #fffbeb);
    border: 1px solid #fcd34d;
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    text-align: center;
}

.locked-prompt-icon {
    font-size: 2em;
    margin-bottom: 12px;
}

.locked-prompt-title {
    font-size: 1.1em;
    font-weight: 600;
    color: #92400e;
    margin-bottom: 8px;
}

.locked-prompt-text {
    font-size: 0.85em;
    color: #78350f;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)


# ==================== 页面组件 | 品牌与导航 ====================

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


# ==================== 页面组件 | 导航 ====================

def render_nav_tabs():
    """
    纯横向导航栏 - 点击切换页面
    使用纯 CSS + JavaScript，隐藏按钮放在 sidebar
    """
    # 初始化
    if 'target_tab' not in st.session_state:
        st.session_state.target_tab = 0

    tabs = [
        (0, "📊", "信号清单"),
        (1, "📈", "行情视图"),
        (2, "☕", "支持订阅")
    ]

    # 渲染横向导航栏（纯 CSS + JS）
    tabs_html = '<div class="nav-wrapper"><div class="nav-container">'
    for idx, icon, name in tabs:
        active_class = 'active' if st.session_state.target_tab == idx else ''
        tabs_html += f'<div class="nav-btn {active_class}" onclick="switchTab({idx})"><span class="nav-icon">{icon}</span>{name}</div>'
    tabs_html += '</div></div>'

    # 添加 JavaScript 切换函数
    js_code = '''
    <script>
    function switchTab(idx) {
        // 设置 sessionStorage 标记
        sessionStorage.setItem('pending_tab', idx);
        // 点击隐藏按钮触发
        document.getElementById('trigger_' + idx).click();
    }
    </script>
    '''

    st.markdown(tabs_html + js_code, unsafe_allow_html=True)

    # 隐藏的按钮放 sidebar（逻辑存在，视觉消失）
    with st.sidebar:
        for idx, icon, name in tabs:
            st.button(
                f"{icon} {name}",
                key=f"trigger_{idx}",
                on_click=lambda x=idx: st.session_state.update(target_tab=x)
            )


# ==================== 信号页面组件 ====================

def render_access_input():
    """渲染 Access Key 输入框"""
    st.markdown("""
    <div class="input-group">
        <div class="input-label">🔐 输入访问密钥</div>
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
    
    if confirm_btn and access_key:
        result = validate_access_key(access_key)
        
        if not result['valid']:
            if result.get('expired'):
                st.error(f"❌ Key 已到期（首次使用：{result['first_seen']}，有效期30天）")
            else:
                st.error("❌ 无效的 Access Key")
            log_usage(access_key, 'blocked')
            return None, None
        
        if result.get('is_first_use'):
            st.success(f"✅ Key 已激活！有效期至 {(datetime.strptime(result['first_seen']) + timedelta(days=30)).strftime('%Y-%m-%d')}")
        else:
            st.info(f"剩余有效期：{result['days_remaining']} 天")
        
        anomaly = check_share_anomaly(access_key)
        if anomaly['is_anomaly']:
            st.warning(anomaly['warning_message'])
            log_usage(access_key, 'warning')
        
        log_usage(access_key, 'access')
        
        # 保存验证状态
        st.session_state.verified_key = access_key
        st.session_state.verified_key_mask = result['key']
        
        return access_key, result['key']
    
    return None, None


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


def render_signal_featured(row, name: str, rank: int = 1):
    """渲染 Featured Signal"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-card signal-featured">
        <div class="label">🥇 精选信号 · Featured #{rank}</div>
        <div class="stock-code">{code} <span class="stock-name">{name}</span></div>
        <div class="signal-score" style="margin-top:8px;">评分：{score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_silver(rank: int, row, name: str):
    """渲染 Silver Tier"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-card signal-silver">
        <div class="label">🥈 银牌信号 · Silver Tier #{rank}</div>
        <div class="stock-code">{code} <span class="stock-name">{name}</span></div>
        <div class="signal-score" style="margin-top:6px;">{score:.2f}</div>
    </div>
    """, unsafe_allow_html=True)


def render_signal_other(rank: int, row, name: str):
    """渲染 Other Signals"""
    code = format_stock_code(str(row.get('symbol', '')))
    score = row.get('score', 0)
    
    st.markdown(f"""
    <div class="signal-card signal-other">
        <div class="label">🥉 其他信号 #{rank}</div>
        <div class="stock-code">{code} <span class="stock-name">{name}</span></div>
        <div class="signal-score" style="margin-top:4px;">{score:.2f}</div>
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
        图表由 TradingView 提供。TradingView® 为 TradingView, Inc. 的注册商标。
        本平台与 TradingView, Inc. 无合作、授权或隶属关系。该图表仅作为第三方市场可视化参考。
    </div>
    """
    components.html(tv_html, height=height + 70)


def render_trial_chart():
    """渲染试用版图表"""
    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">🔓 TradingView 试用</div>
        <div class="info-card-text">
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


# ==================== 订阅与支持页面 ====================

def render_support_page():
    """渲染支持订阅页面"""
    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">💡 订阅说明</div>
        <div class="info-card-text">
            <p>EigenFlow 为专业量化研究订阅服务，核心信号仅限订阅用户查阅。</p>
            <p style="margin-top:10px;"><strong>订阅权益：</strong>每日精选信号、行情辅助分析、研究方法支持。</p>
            <p style="margin-top:10px; color:#9ca3af;">订阅内容为研究资料访问授权，非交易指令。</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">📧 获取 Access Key</div>
        <div class="info-card-text">
            <ul style="margin:8px 0; padding-left:16px;">
                <li>微信：扫描下方二维码联系</li>
                <li>Email：research@eigenflow.io</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    st.markdown("---")
    st.markdown("""
    <div class="info-card">
        <div class="info-card-title">⚖️ 使用声明</div>
        <div class="info-card-text">
            <ul style="margin:8px 0; padding-left:16px;">
                <li><strong>使用范围：</strong>本内容仅供个人研究与学习使用，禁止转售、二次分发或任何形式的公开传播。</li>
                <li><strong>二次收费禁止：</strong>严禁任何形式的二次收费、转售或商业化使用。</li>
                <li><strong>违约后果：</strong>如发现违规行为，访问授权可能被立即终止，恕不另行通知。</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==================== 水印组件 ====================

def render_watermark(key_mask: str = None, mode: str = "licensed"):
    if mode == "trial":
        text = "试用模式 | 仅供演示"
    elif key_mask:
        text = f"授权码：{key_mask}｜仅限个人研究使用"
    else:
        text = "EigenFlow Research"
    
    st.markdown(f'<div class="watermark">{text}</div>', unsafe_allow_html=True)


# ==================== 页面内容 | 完整页面定义 ====================

def page_signal_list(key_mask: str):
    """【信号清单页】"""
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
    
    df_top10 = df.head(10).copy()
    df_top10['symbol'] = df_top10['symbol'].apply(format_stock_code)
    stock_names = df_top10.get('name', df_top10['symbol']).tolist()
    
    now = datetime.now()
    current_hour = now.hour
    date_label = "下一个交易日" if current_hour >= 16 else "今日信号"
    
    st.markdown(f"""
    <div class="date-label">📅 {date_label} · {now.strftime('%Y-%m-%d')}</div>
    """, unsafe_allow_html=True)
    
    # Featured
    if len(df_top10) >= 1:
        render_signal_featured(df_top10.iloc[0], stock_names[0], rank=1)
    
    # Silver
    if len(df_top10) >= 3:
        st.markdown('<div class="section-title">🥈银牌信号 · Silver Tier</div>', unsafe_allow_html=True)
        for i in range(1, 3):
            render_signal_silver(i + 1, df_top10.iloc[i], stock_names[i])
    
    # Other
    if len(df_top10) >= 4:
        st.markdown('<div class="section-title">🥉 其他信号</div>', unsafe_allow_html=True)
        for i in range(3, min(10, len(df_top10))):
            render_signal_other(i + 1, df_top10.iloc[i], stock_names[i])
    
    st.markdown("---")
    st.markdown("""
    <div class="disclaimer-bar">
        信号具有时效性，仅在研究窗口期内具有参考意义。<br>
        Signals are time-sensitive and valid only within the intended research window.
    </div>
    """, unsafe_allow_html=True)
    
    render_watermark(key_mask)


def page_chart(key_verified: bool = False):
    """【行情视图页】"""
    st.markdown("""
    <div class="date-label" style="font-size:1em; font-weight:600; color:#374151;">
        📈 行情视图
    </div>
    """, unsafe_allow_html=True)
    
    if not key_verified:
        # ==================== 黄色授权码威慑 ====================
        st.markdown("""
        <style>
        .auth-warning {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fbbf24 100%);
            border: 2px solid #f59e0b;
            border-radius: 16px;
            padding: 28px 24px;
            margin: 20px 0 28px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);
        }
        
        .auth-warning-icon {
            font-size: 2.8em;
            margin-bottom: 16px;
        }
        
        .auth-warning-title {
            font-size: 1.3em;
            font-weight: 700;
            color: #92400e;
            margin-bottom: 12px;
            letter-spacing: 1px;
        }
        
        .auth-warning-text {
            font-size: 0.95em;
            color: #78350f;
            line-height: 1.7;
            margin-bottom: 20px;
        }
        
        .auth-warning-code {
            background: #fff;
            border: 1px dashed #f59e0b;
            border-radius: 8px;
            padding: 12px 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #92400e;
            display: inline-block;
            margin-top: 8px;
        }
        </style>
        
        <div class="auth-warning">
            <div class="auth-warning-icon">🔐</div>
            <div class="auth-warning-title">⚠️ 授权码验证 Required</div>
            <div class="auth-warning-text">
                行情视图为<span style="color:#dc2626; font-weight:600;">订阅专属功能</span><br>
                请输入有效的 <span style="color:#f59e0b; font-weight:600;">Access Key</span> 解锁完整功能
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Key 验证入口
        st.markdown("""
        <div class="input-group">
            <div class="input-label">🔐 输入 Access Key 解锁</div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            chart_key = st.text_input(
                "Access Key",
                type="password",
                placeholder="EF-26Q1-XXXXXXXX",
                label_visibility="collapsed",
                key="chart_key_input"
            )
        with col2:
            chart_confirm = st.button("解锁", use_container_width=True, type="primary")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 验证逻辑
        if chart_confirm and chart_key:
            result = validate_access_key(chart_key)
            if result['valid']:
                st.session_state.verified_key = chart_key
                st.session_state.verified_key_mask = result['key']
                st.success("✅ 验证成功！")
                st.rerun()
            else:
                if result.get('expired'):
                    st.error(f"❌ Key 已到期")
                else:
                    st.error("❌ 无效的 Access Key")
        
        # 快捷入口
        if st.button("→ 获取 Access Key", type="secondary", use_container_width=True):
            st.session_state.target_tab = 2
            st.rerun()
        
        render_watermark(mode="trial")
        return
    
    df = load_signal_data()
    
    if df.empty:
        st.warning("暂无信号数据，请上传 trade_list_top10.csv")
        return
    
    if 'symbol' not in df.columns:
        st.error("数据格式错误：缺少 symbol 列")
        return
    
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
    
    render_watermark()


# ==================== 主程序 | 页面调度 ====================

def main():
    """
    【主入口】
    
    纯横向导航栏
    行情视图需要 Key 验证
    """
    render_brand_header()
    render_disclaimer()

    # 横向导航栏
    render_nav_tabs()

    # 获取当前 tab
    current_tab = st.session_state.get('target_tab', 0)

    if current_tab == 0:
        # ========== 信号清单 ==========
        access_key, key_mask = render_access_input()
        
        if not access_key:
            render_lock_screen()
            render_trial_chart()
            render_watermark(mode="trial")
            st.markdown("""
            <div style="text-align:center; padding:16px 0 24px;">
                <strong style="color:#f59e0b; cursor:pointer;" onclick="document.getElementById('trigger_2').click()">
                    → 切换至「支持订阅」获取 Access Key
                </strong>
            </div>
            """, unsafe_allow_html=True)
            st.stop()
        
        page_signal_list(key_mask)
    
    elif current_tab == 1:
        # ========== 行情视图 ==========
        access_key = st.session_state.get('verified_key', None)
        
        if access_key:
            page_chart(key_verified=True)
        else:
            page_chart(key_verified=False)
    
    elif current_tab == 2:
        # ========== 支持订阅 ==========
        render_support_page()


if __name__ == "__main__":
    main()
