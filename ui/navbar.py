"""
================================================================================
EigenFlow Navbar | 顶部导航组件

纯横向导航栏，使用 Streamlit 原生 Radio 按钮 + CSS 样式控制
避免 JavaScript 重复渲染问题
================================================================================
"""

import streamlit as st
from .theme import PAGE_TITLES, PAGE_ICONS


# ==================== 初始化函数 ====================

def init_navbar_state():
    """初始化导航状态"""
    if 'target_tab' not in st.session_state:
        st.session_state.target_tab = 0


# ==================== 渲染函数 ====================

def eigenflow_navbar(active_page: str = 'signals') -> str:
    """
    渲染 EigenFlow 顶部横向导航栏
    
    Args:
        active_page: 当前激活的页面 key
    
    Returns:
        当前选中的页面 key
    
    Usage:
        from ui.navbar import eigenflow_navbar
        
        page = eigenflow_navbar('signals')
    """
    # 页面映射
    PAGES = {
        'signals': 0,
        'chart': 1,
        'support': 2,
    }
    
    PAGES_REVERSE = {v: k for k, v in PAGES.items()}
    
    # 初始化
    init_navbar_state()
    
    current_idx = st.session_state.target_tab
    
    # 1. 渲染 CSS 样式（只渲染一次）
    if 'navbar_css_rendered' not in st.session_state:
        st.markdown("""
        <style>
        /* 隐藏原生 radio 按钮 */
        .nav-radio-hidden [data-testid="stRadioValue"] {
            display: none !important;
        }
        
        /* 隐藏 radio 选项之间的间距 */
        .nav-radio-hidden .stRadio > div {
            gap: 0 !important;
        }
        
        /* 横向导航容器 */
        .eigen-nav-container {
            display: flex;
            justify-content: center;
            margin: 20px 0 24px;
        }
        
        /* 导航按钮组 */
        .eigen-nav-buttons {
            display: inline-flex;
            gap: 4px;
            padding: 4px;
            background: #f3f4f6;
            border-radius: 10px;
        }
        
        /* 单个导航标签 */
        .eigen-nav-item {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 500;
            color: #6b7280;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
            background: transparent;
        }
        
        .eigen-nav-item:hover {
            color: #1f2937;
            background: #fff;
        }
        
        /* 激活状态 */
        .eigen-nav-item.active {
            color: #111827;
            background: #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .eigen-nav-icon {
            font-size: 1em;
        }
        
        .eigen-nav-label {
            color: inherit;
        }
        </style>
        """, unsafe_allow_html=True)
        st.session_state.navbar_css_rendered = True
    
    # 2. 准备选项数据
    tabs = [
        (0, PAGE_ICONS['signals'], PAGE_TITLES['signals']),
        (1, PAGE_ICONS['chart'], PAGE_TITLES['chart']),
        (2, PAGE_ICONS['support'], PAGE_TITLES['support']),
    ]
    
    options = [f"{icon}  {title}" for idx, icon, title in tabs]
    
    # 3. 渲染导航 HTML（视觉层）
    tabs_html = '<div class="eigen-nav-container"><div class="eigen-nav-buttons">'
    for idx, icon, title in tabs:
        active_class = 'active' if current_idx == idx else ''
        tabs_html += f'''
        <div class="eigen-nav-item {active_class}" data-value="{idx}" onclick="selectNav({idx})">
            <span class="eigen-nav-icon">{icon}</span>
            <span class="eigen-nav-label">{title}</span>
        </div>
        '''
    tabs_html += '</div></div>'
    
    # JavaScript 处理点击
    js_code = '''
    <script>
    function selectNav(idx) {
        // 找到对应的 radio 并选中
        var radios = document.querySelectorAll('[data-testid="stRadioValue"]');
        if (radios[idx]) {
            radios[idx].click();
        }
    }
    </script>
    '''
    
    st.markdown(tabs_html + js_code, unsafe_allow_html=True)
    
    # 4. 隐藏的原生 Radio（逻辑层）
    with st.container():
        with st.radio("", options=options, index=current_idx, 
                      label_visibility="collapsed", key="nav_radio"):
            pass
        # 监听变化并更新 session_state
        new_idx = options.index(st.session_state.nav_radio) if hasattr(st.session_state, 'nav_radio') else current_idx
        if new_idx != current_idx:
            st.session_state.target_tab = new_idx
            st.rerun()
    
    return PAGES_REVERSE.get(current_idx, 'signals')


def disable_sidebar():
    """
    彻底禁用 Streamlit sidebar
    """
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
