"""
================================================================================
EigenFlow UI Theme | 主题常量

集中管理颜色、emoji、字体大小等 UI 常量
================================================================================
"""

# ==================== 品牌颜色 ====================

BRAND_COLORS = {
    # 核心配色
    'dark': '#1a1a1a',           # 深黑（文字）
    'gray': '#6b7280',            # 灰色（次要文字）
    'gray_light': '#9ca3af',      # 浅灰（辅助）
    
    # 信号等级颜色
    'gold': '#f59e0b',           # 金色（Rank #1）
    'gold_light': '#fbbf24',     # 浅金
    'silver': '#d1d5db',         # 银灰（Rank #2-3）
    'neutral': '#e5e7eb',       # 中性（Rank #4-10）
    
    # 背景色
    'bg_light': '#f9fafb',       # 浅灰背景
    'bg_white': '#ffffff',        # 白色
    'border': '#e5e7eb',         # 边框
}

# ==================== 排名 Emoji ====================

RANK_EMOJIS = {
    1: '🥇',  # 金牌
    2: '🥈',  # 银牌
    3: '🥉',  # 铜牌
    'default': '📊',  # 默认
}

# ==================== 页面标题 ====================

PAGE_TITLES = {
    'signals': '信号清单',
    'chart': '行情视图',
    'support': '支持订阅',
}

PAGE_ICONS = {
    'signals': '📊',
    'chart': '📈',
    'support': '☕',
}

# ==================== 字体大小 ====================

FONT_SIZES = {
    'brand_logo': '1.6em',
    'brand_tagline': '0.75em',
    'nav': '0.9em',
    'section_title': '0.8em',
    'date_label': '0.78em',
    'disclaimer': '0.7em',
    'watermark': '0.58em',
    'stock_code': '1.1em',
    'stock_name': '1em',
    'score': '0.9em',
}

# ==================== 信号卡片标签 ====================

SIGNAL_LABELS = {
    'featured': ('★', '精选信号 · Featured'),
    'silver': ('◆', '银牌信号 · Silver Tier'),
    'other': ('◇', '其他信号'),
}

# ==================== 快捷映射 ====================

def get_rank_emoji(rank: int) -> str:
    """获取排名的 emoji"""
    return RANK_EMOJIS.get(rank, RANK_EMOJIS['default'])


def get_page_title(page_key: str) -> str:
    """获取页面标题"""
    return PAGE_TITLES.get(page_key, page_key)


def get_page_icon(page_key: str) -> str:
    """获取页面图标"""
    return PAGE_ICONS.get(page_key, PAGE_ICONS['signals'])

