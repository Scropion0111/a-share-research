"""
================================================================================
EigenFlow Navbar | 顶部导航组件

纯横向导航栏，使用 CSS + JavaScript 实现点击切换
可复用，直接 import 即可使用
================================================================================
"""

import streamlit as st
from .theme import PAGE_TITLES, PAGE_ICONS


def eigenflow_navbar(active_page: str = 'signals') -> str:
    """
    渲染 EigenFlow 顶部横向导航栏
    
    Args:
        active_page: 当前激活的页面 key ('signals' | 'chart' | 'support')
    
    Returns:
        当前选中的页面 key
    
    Usage:
        from ui.navbar import eigenflow_navbar
        
        page = eigenflow_navbar('signals')
        if page == 'signals':
            ...
        elif page == 'chart':
            ...
        elif page == 'support':
            ...
    """
    # 页面映射
    PAGES = {
        'signals': 0,
        'chart': 1,
        'support': 2,
    }
    
    PAGES_REVERSE = {v: k for k, v in PAGES.items()}
    
    # 初始化 session_state
    if 'target_tab' not in st.session_state:
        st.session_state.target_tab = PAGES.get(active_page, 0)
    
    current_idx = st.session_state.target_tab
    
    # 页面配置
    tabs = [
        (0, PAGE_ICONS['signals'], PAGE_TITLES['signals']),
        (1, PAGE_ICONS['chart'], PAGE_TITLES['chart']),
        (2, PAGE_ICONS['support'], PAGE_TITLES['support']),
    ]
    
    # CSS 样式
    st.markdown("""
    <style>
    /* 导航容器 */
    .nav-wrapper {
        display: flex;
        justify-content: center;
        margin: 24px 0 28px;
    }
    
    .nav-container {
        display: inline-flex;
        gap: 6px;
        padding: 5px;
        background: #f9fafb;
        border-radius: 12px;
    }
    
    /* 导航按钮 */
    .nav-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 0.9em;
        font-weight: 500;
        color: #6b7280;
        cursor: pointer;
        transition: all 0.25s ease;
        border: none;
        background: transparent;
        outline: none;
    }
    
    .nav-btn:hover {
        color: #1a1a1a;
        background: #fff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    .nav-btn.active {
        color: #1a1a1a;
        background: #fff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }
    
    .nav-icon {
        font-size: 1.1em;
    }
    
    /* 隐藏触发按钮（用于逻辑控制） */
    button[id^="trigger_tab_"] {
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
    </style>
    """, unsafe_allow_html=True)
    
    # 渲染横向导航栏
    tabs_html = '<div class="nav-wrapper"><div class="nav-container">'
    for idx, icon, name in tabs:
        active_class = 'active' if current_idx == idx else ''
        tabs_html += f'''
        <div class="nav-btn {active_class}" 
             onclick="switchTab({idx})">
            <span class="nav-icon">{icon}</span>
            <span>{name}</span>
        </div>
        '''
    tabs_html += '</div></div>'
    
    # JavaScript 切换函数
    js_code = '''
    <script>
    function switchTab(idx) {
        document.getElementById('trigger_tab_' + idx).click();
    }
    </script>
    '''
    
    st.markdown(tabs_html + js_code, unsafe_allow_html=True)
    
    # 隐藏的按钮（用于触发 session_state 更新）
    for idx, icon, name in tabs:
        st.button(
            f"{icon} {name}", 
            key=f"trigger_tab_{idx}",
            on_click=lambda x=idx: st.session_state.update(target_tab=x),
            help=f"切换到{name}"
        )
    
    return PAGES_REVERSE.get(current_idx, 'signals')


def disable_sidebar():
    """
    彻底禁用 Streamlit sidebar
    
    调用此函数后，sidebar 将从 DOM 中完全移除
    """
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

