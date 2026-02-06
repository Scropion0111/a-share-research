"""
================================================================================
EigenFlow Navbar | 顶部导航组件

使用 Streamlit 按钮 + session_state 实现页面切换
完全避免 JavaScript 和 Radio 问题
================================================================================
"""

import streamlit as st


# ==================== CSS 样式 ====================

NAVBAR_CSS = """
<style>
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
.eigen-nav-btn {
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

.eigen-nav-btn:hover {
    color: #1f2937;
    background: #fff;
}

/* 激活状态 */
.eigen-nav-btn.active {
    color: #111827;
    background: #fff;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.eigen-nav-icon {
    font-size: 1em;
}
</style>
"""


def eigenflow_navbar(active_page: str = 'signals') -> str:
    """
    渲染 EigenFlow 顶部横向导航栏
    
    Args:
        active_page: 当前激活的页面 key
    
    Returns:
        当前选中的页面 key
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
    
    # 渲染 CSS
    st.markdown(NAVBAR_CSS, unsafe_allow_html=True)
    
    # 定义页面标签
    tabs = [
        (0, "📊", "信号清单"),
        (1, "📈", "行情视图"),
        (2, "☕", "支持订阅"),
    ]
    
    # 使用 st.columns 渲染导航
    st.markdown('<div class="eigen-nav-container"><div class="eigen-nav-buttons">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    # 信号清单按钮
    with col1:
        if st.button(f"📊 信号清单", 
                     key="nav_signals",
                     help="查看量化信号",
                     type="secondary" if current_idx != 0 else "primary"):
            st.session_state.target_tab = 0
            st.rerun()
    
    # 行情视图按钮
    with col2:
        if st.button(f"📈 行情视图", 
                     key="nav_chart",
                     help="查看行情图表",
                     type="secondary" if current_idx != 1 else "primary"):
            st.session_state.target_tab = 1
            st.rerun()
    
    # 支持订阅按钮
    with col3:
        if st.button(f"☕ 支持订阅", 
                     key="nav_support",
                     help="获取 Access Key",
                     type="secondary" if current_idx != 2 else "primary"):
            st.session_state.target_tab = 2
            st.rerun()
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
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
