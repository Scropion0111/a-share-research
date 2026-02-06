# 📈 A股量化推荐网站

基于量化策略的A股股票推荐展示系统，使用Streamlit构建的现代化Web应用。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install streamlit pandas plotly
```

### 2. 生成数据文件

```bash
python a_share_web.py
```

### 3. 运行演示

```bash
python demo.py
```

### 4. 启动Web应用

```bash
streamlit run app.py
```

## 📁 项目文件结构

```
├── a_share_web.py          # 数据处理脚本
├── app.py                  # Streamlit Web应用
├── demo.py                 # 演示脚本（无需Streamlit）
├── today.json             # 今日股票推荐数据
├── history.csv            # 历史推荐记录
├── equity.csv             # 资金曲线数据
├── trade_list_today_16features_26-1-12.csv  # 原始量化数据
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 🎯 功能特性

### ✅ 核心功能
- **Top股票推荐**：展示Top1/Top3/Top10推荐股票
- **TradingView图表**：点击股票查看专业K线图
- **资金曲线**：可视化历史表现
- **订阅支持**：二维码支付功能

### 🎨 用户界面
- 现代化响应式设计
- 直观的数据展示
- 专业的图表可视化
- 清晰的风险提示

## 📊 数据说明

### 输入数据
- `trade_list_today_16features_*.csv`：量化模型输出的股票特征数据
- 包含16个特征，包括价格、成交量、排名等指标
- 按`score`字段降序排列

### 生成数据
- `today.json`：今日推荐股票列表
- `history.csv`：历史推荐记录（7天）
- `equity.csv`：模拟资金曲线（30天）

## 🔧 技术栈

- **前端框架**：Streamlit
- **数据处理**：pandas
- **可视化**：Plotly
- **图表服务**：TradingView Widgets

## 🚀 部署选项

### 方式一：Streamlit Cloud（推荐）
1. 上传代码到GitHub仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接GitHub仓库，一键部署

### 方式二：本地服务器
```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 方式三：云服务器
- 阿里云/腾讯云轻量服务器
- 配置Nginx反向代理
- 支持自定义域名

## 📝 开发指南

### 自定义股票名称
编辑 `a_share_web.py` 中的 `stock_names` 字典：

```python
stock_names = {
    '688003': '天宜上佳',
    '300624': '万德斯',
    # 添加更多映射...
}
```

### 添加二维码图片
将真实的收款二维码保存为：
- `wechat_qr.png`：微信支付二维码
- `alipay_qr.png`：支付宝二维码

### 自定义样式
修改 `app.py` 中的CSS样式来自定义界面外观。

## ⚠️ 风险提示

- 本系统仅供学习和研究使用
- 股票投资具有风险，请谨慎决策
- 建议在专业投资顾问指导下进行投资
- 过往表现不代表未来收益

## 📞 技术支持

如需技术支持或定制开发，请联系开发团队。

---

**免责声明**：本项目为技术演示，不构成任何投资建议。使用者需自行承担投资风险。

