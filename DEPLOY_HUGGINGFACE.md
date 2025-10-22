# 🤗 部署到 Hugging Face Spaces 完整教程

## 为什么选择 Hugging Face Spaces？

- ✅ **完全免费** - 无需信用卡
- ✅ **支持 MetaGPT** - 可以安装需要编译的包
- ✅ **自动部署** - 连接 GitHub 自动更新
- ✅ **公开访问** - 获得 `.hf.space` 域名

---

## 📋 前置要求

1. Hugging Face 账号（免费）
2. GitHub 仓库已推送
3. OpenAI API Key

---

## 🚀 部署步骤

### 步骤 1：创建 Hugging Face 账号

1. 访问 https://huggingface.co/join
2. 注册账号（可用 GitHub 登录）
3. 验证邮箱

### 步骤 2：创建新 Space

1. 访问 https://huggingface.co/new-space
2. 填写信息：
   - **Space name**: `debate-agent` (或你喜欢的名字)
   - **License**: MIT
   - **Select the Space SDK**: **Streamlit** ⚠️ 重要
   - **Space hardware**: CPU basic (免费)
   - **Repo type**: Public

3. 点击 **Create Space**

### 步骤 3：配置 Space

#### 方法 A：从 GitHub 导入（推荐）

1. 在 Space 页面，点击 **Files** → **⋯ (三个点)** → **Settings**

2. 找到 **Repository settings** → **Link to GitHub**

3. 授权 Hugging Face 访问你的 GitHub

4. 选择仓库：`HHarr1son/DEBAT_AGENT`

5. 点击 **Link repository**

#### 方法 B：手动上传文件

如果方法 A 不行，手动上传以下文件：

1. 点击 **Files** → **Add file** → **Upload files**

2. 上传这些文件：
   - `debate.py` (原版 MetaGPT 版本)
   - `research_actions.py`
   - `main.py`
   - `requirements.txt`
   - `packages.txt`
   - 整个 `metagpt/` 文件夹

### 步骤 4：创建配置文件

在 Space 的根目录创建以下文件：

#### 1. 创建 `.streamlit/config.toml`

点击 **Files** → **Add file** → **Create a new file**

文件名：`.streamlit/config.toml`

内容：
```toml
[server]
headless = true
port = 7860

[browser]
gatherUsageStats = false
```

#### 2. 创建 `app.py`

文件名：`app.py`

内容：
```python
#!/usr/bin/env python
"""
Entry point for Hugging Face Spaces
Redirect to debate.py (original MetaGPT version)
"""

import sys
import os

# Set environment for MetaGPT
os.environ["METAGPT_PROJECT_ROOT"] = os.getcwd()

# Import and run debate.py
import debate
```

#### 3. 更新 `requirements.txt`

文件名：`requirements.txt`

内容：
```txt
# Streamlit
streamlit==1.28.0

# OpenAI
openai==0.28.0

# MetaGPT dependencies
pyyaml==6.0.1
pydantic==2.5.0
aiohttp==3.9.0
requests==2.31.0
tenacity==8.2.3
jinja2==3.1.2

# Search & Scraping
duckduckgo-search==3.9.0
beautifulsoup4==4.12.2
lxml==4.9.3

# Logging
loguru==0.7.2

# Optional but recommended
tiktoken==0.5.2
```

#### 4. 创建 `packages.txt`（系统依赖）

文件名：`packages.txt`

内容：
```
build-essential
libxml2-dev
libxslt-dev
python3-dev
```

### 步骤 5：配置 Secrets（API Keys）

1. 在 Space 页面，点击 **Settings** (齿轮图标)

2. 找到 **Repository secrets** 部分

3. 点击 **New secret**

4. 添加 OpenAI API Key：
   - **Name**: `OPENAI_API_KEY`
   - **Value**: `sk-你的OpenAI-key`
   - 点击 **Add secret**

5. （可选）添加搜索引擎 Key：
   - **Name**: `SERPAPI_API_KEY`
   - **Value**: `你的SerpAPI-key`

### 步骤 6：修改代码读取 Secrets

更新 `debate.py` 开头的配置部分：

```python
import os

# Hugging Face Spaces 使用环境变量
if os.getenv("OPENAI_API_KEY"):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
elif hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
    import openai
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("⚠️ API Key 缺失")
    st.stop()
```

### 步骤 7：等待构建

1. Space 会自动开始构建
2. 查看 **Logs** 标签查看进度
3. 首次构建需要 5-10 分钟（安装依赖）
4. 成功后会显示 **Running** 状态

### 步骤 8：访问应用

1. 构建成功后，点击 **App** 标签
2. 你的应用 URL：`https://huggingface.co/spaces/你的用户名/debate-agent`
3. 分享给任何人使用！

---

## 🔧 故障排除

### 问题 1：构建失败 - 依赖安装错误

**解决方案：**
1. 检查 `requirements.txt` 版本号
2. 查看 Logs 找到具体失败的包
3. 降低有问题的包版本

### 问题 2：应用启动但白屏

**解决方案：**
1. 确保 `app.py` 正确导入 `debate.py`
2. 检查是否有语法错误
3. 查看 Logs 中的 Python 错误

### 问题 3：API Key 不生效

**解决方案：**
1. 确认在 Settings → Secrets 中添加了 `OPENAI_API_KEY`
2. 重启 Space：Settings → Factory reboot
3. 检查代码是否正确读取环境变量

### 问题 4：MetaGPT 导入失败

**解决方案：**
1. 确保上传了完整的 `metagpt/` 文件夹
2. 检查 `research_actions.py` 是否存在
3. 添加到 `app.py`：
   ```python
   import sys
   sys.path.insert(0, os.getcwd())
   ```

---

## 🎨 高级配置

### 自定义域名

Hugging Face Spaces 提供免费的自定义域名：

1. Settings → **Custom domain**
2. 输入你想要的子域名
3. 等待 DNS 生效

### 增加资源（付费）

如果应用需要更多资源：

1. Settings → **Space hardware**
2. 选择更高级的硬件
3. 价格：CPU Upgrade $0.03/小时，GPU 更贵

### 私有部署

如果不想公开：

1. Space 创建时选择 **Private**
2. 只有你和授权的人能访问

---

## 📊 监控和维护

### 查看使用情况

1. Space 页面 → **Analytics**
2. 查看访问量、错误率

### 更新应用

**方法 1：GitHub 自动同步**
- 推送到 GitHub，Hugging Face 自动更新

**方法 2：手动上传**
- Files → Upload files → 覆盖旧文件

### 重启应用

Settings → **Factory reboot** → 确认

---

## ✅ 检查清单

部署前确认：

- [ ] 所有文件已上传（debate.py, research_actions.py, metagpt/, etc.）
- [ ] requirements.txt 包含所有依赖
- [ ] packages.txt 包含系统依赖
- [ ] app.py 正确导入 debate.py
- [ ] Secrets 中添加了 OPENAI_API_KEY
- [ ] .streamlit/config.toml 已创建
- [ ] 构建完成，状态显示 "Running"
- [ ] 应用可以正常访问

---

## 🆚 对比 Streamlit Cloud

| 特性 | Streamlit Cloud | Hugging Face Spaces |
|------|----------------|---------------------|
| 编译支持 | ❌ 有限 | ✅ 完整支持 |
| MetaGPT | ❌ 无法部署 | ✅ 可以部署 |
| 免费额度 | ✅ 无限 | ✅ 无限 |
| 构建时间 | 快 | 较慢（首次） |
| 资源限制 | 1GB RAM | 16GB RAM |

---

## 🎉 完成！

你的完整 MetaGPT 辩论应用现在已经部署到 Hugging Face Spaces！

**你的应用 URL：**
```
https://huggingface.co/spaces/你的用户名/debate-agent
```

需要帮助？
- [Hugging Face Docs](https://huggingface.co/docs/hub/spaces)
- [Discord 社区](https://discord.gg/hugging-face)
