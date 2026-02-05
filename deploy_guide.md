# 📚 A股量化研究数据 - 部署指南

## 方案1：Streamlit Cloud（推荐 ⭐⭐⭐⭐⭐）

**完全免费**，一键部署，自动更新。

### 步骤：

#### 1️⃣ 创建 GitHub 仓库

1. 打开 https://github.com
2. 点击右上角 **+** → **New repository**
3. 仓库名：`a-share-research`（或其他名字）
4. 选择 **Public**（公开）
5. 点击 **Create repository**

#### 2️⃣ 上传文件

**方法A：网页上传（最简单）**

1. 进入刚创建的仓库页面
2. 点击 **uploading an existing file**
3. 拖拽上传以下文件：
   ```
   ✅ app.py
   ✅ requirements.txt
   ✅ wechat_qr.png（可选）
   ✅ alipay_qr.png（可选）
   ❌ 不传 equity.csv（会报错，因为数据路径不对）
   ❌ 不传 .csv 数据文件（数据从本地读取）
   ```
4. 点击 **Commit changes**

**方法B：Git 命令行（学会后更方便）**

```bash
# 在项目目录执行
cd D:\Python_homework\A_share_web

# 初始化Git
git init

# 添加文件（排除大文件和数据文件）
git add app.py requirements.txt wechat_qr.png alipay_qr.png

# 提交
git commit -m "Initial commit: 量化研究数据网站"

# 关联GitHub仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/a-share-research.git

# 推送
git push -u origin main
```

#### 3️⃣ 部署到 Streamlit Cloud

1. 打开 https://share.streamlit.io
2. 点击 **New app**
3. 选择你的 GitHub 仓库
4. 选择分支：`main`
5. 主文件路径：`app.py`
6. 点击 **Deploy**

#### 4️⃣ 等待部署完成（约1-2分钟）

部署成功后，你会得到一个链接，类似：
```
https://a-share-research.streamlit.app
```

分享这个链接给别人，他们就能看到了！

---

## ⚠️ 重要注意事项

### 数据问题

**Streamlit Cloud 无法读取本地文件！**

你的数据路径：
```python
base_path = r"C:\Users\Administrator\A_share_index\daily_signals"
```

这是你**本地电脑**的路径，GitHub和云端都访问不到。

### 解决方案（二选一）：

**方案A：只展示静态网页（推荐）**

修改代码，把数据路径改成相对路径或注释掉，只展示基础界面：

```python
# 注释掉本地数据读取
# base_path = r"C:\Users\Administrator\A_share_index\daily_signals"
# ... 数据读取代码 ...
```

然后部署后，网页会显示基础信息，但不能实时更新数据。

**方案B：使用云端数据源**

1. 把数据文件（trade_list_top10.csv）也上传到GitHub
2. 修改代码使用相对路径：
```python
base_path = "data"  # GitHub仓库里的data文件夹
```

---

## 方案2：Vercel + Docker（进阶）

需要Docker知识，更复杂，不推荐新手。

---

## 方案3：购买服务器（花钱）

- 阿里云、腾讯云学生机约 10-50元/月
- 需要配置Linux和Nginx
- 可以7×24小时运行

不推荐，除非你有钱+有时间学习。

---

## 📋 部署前检查清单

- [ ] GitHub仓库已创建
- [ ] 文件已上传（app.py, requirements.txt, 图片）
- [ ] requirements.txt 内容正确
- [ ] Streamlit Cloud 账号已登录

---

## 🔧 后续更新代码

修改本地代码后，如何更新到网站？

```bash
cd D:\Python_homework\A_share_web

# 查看修改
git status

# 添加修改的文件
git add app.py

# 提交
git commit -m "更新：修改了UI样式"

# 推送到GitHub
git push
```

**Streamlit Cloud 会自动检测到更新，约1-2分钟后网站自动更新。**

---

## ❓ 常见问题

**Q: GitHub打不开？**
A: 需要翻墙或用镜像站 https://hub.fastgit.org

**Q: Streamlit Cloud 打不开？**
A: 需要翻墙，或用国内替代方案

**Q: 网页显示数据错误？**
A: 因为数据在本地，云端读取不到。按上面"数据问题"说明处理。

**Q: 想让网站实时更新数据？**
A: 需要把数据也传到GitHub，或使用API接口。

---

## 📞 遇到问题？

1. 先看GitHub仓库的 **Actions** 标签页，有错误日志
2. 检查 requirements.txt 格式
3. 检查文件是否都上传了

---

**有问题随时问我！** 😊
