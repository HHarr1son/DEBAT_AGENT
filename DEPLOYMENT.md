# 🚀 Streamlit Cloud 部署指南

## 部署到 Streamlit Community Cloud

### 前提条件
- GitHub 账号
- Streamlit Community Cloud 账号（免费）
- OpenAI API Key
- SerpAPI Key（可选，用于搜索功能）

---

## 📝 部署步骤

### 1. 准备 GitHub 仓库

```bash
# 初始化 git 仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 提交代码（敏感文件已在 .gitignore 中排除）
git add .
git commit -m "Initial commit for Streamlit deployment"
git push -u origin main
```

**重要**: 确保以下文件不会被提交:
- ✅ `.streamlit/secrets.toml` (已在 .gitignore)
- ✅ `config.yaml` (已在 .gitignore)
- ✅ `.env` 文件 (已在 .gitignore)

---

### 2. 登录 Streamlit Community Cloud

1. 访问 https://streamlit.io/cloud
2. 使用 GitHub 账号登录
3. 点击 "New app"

---

### 3. 配置应用

填写以下信息:
- **Repository**: 选择你的 GitHub 仓库
- **Branch**: main
- **Main file path**: `main.py`

---

### 4. 配置 Secrets（最重要！）

在 Streamlit Cloud 应用设置中，找到 "Secrets" 部分，添加以下内容:

```toml
# OpenAI API 配置
OPENAI_API_KEY = "sk-your-actual-openai-api-key-here"
OPENAI_MODEL = "gpt-3.5-turbo"

# 搜索引擎配置（选择一个）
SEARCH_ENGINE = "serpapi"  # 或 "serper" 或 "ddg"（DuckDuckGo 免费）
SERPAPI_API_KEY = "your-serpapi-key-here"  # 如果使用 SerpAPI
# SERPER_API_KEY = "your-serper-key-here"  # 如果使用 Serper

# MetaGPT 配置
METAGPT_CONFIG = """
llm:
  api_type: "openai"
  model: "gpt-3.5-turbo"
  max_tokens: 1000
  temperature: 0.7

search:
  api_type: "serpapi"

workspace:
  path: "/tmp"
"""
```

**获取 API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- SerpAPI: https://serpapi.com/
- Serper: https://serper.dev/

**免费替代方案:**
- 使用 DuckDuckGo 搜索（无需 API key）:
  ```toml
  SEARCH_ENGINE = "ddg"
  ```

---

### 5. 部署应用

1. 点击 "Deploy!"
2. 等待几分钟，应用会自动构建和部署
3. 部署成功后，你会获得一个公开的 URL

---

## 🔒 安全检查清单

在部署前确保:

- [ ] `config.yaml` 中没有真实的 API keys
- [ ] `.gitignore` 包含敏感文件
- [ ] GitHub 仓库中没有提交敏感信息
- [ ] Streamlit Cloud Secrets 已正确配置
- [ ] 本地测试通过

检查命令:
```bash
# 检查 git 状态
git status

# 查看即将提交的文件
git diff --cached

# 确保敏感文件不在追踪中
git ls-files | grep -E "(config.yaml|secrets.toml|\.env)"
```

---

## 🧪 本地测试

创建本地 secrets 文件进行测试:

```bash
# 创建 .streamlit 目录
mkdir -p .streamlit

# 复制示例文件并填写真实的 API keys
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# 编辑 secrets.toml，添加你的 API keys
nano .streamlit/secrets.toml
```

运行本地测试:
```bash
streamlit run main.py
```

---

## 🐛 故障排除

### 应用无法启动
- 检查 Streamlit Cloud 日志
- 确认 `requirements.txt` 包含所有依赖
- 验证 Python 版本兼容性

### API 调用失败
- 检查 Secrets 配置是否正确
- 验证 API keys 是否有效
- 检查 API 配额是否用尽

### 依赖安装失败
- 更新 `requirements.txt`
- 固定特定版本号
- 检查包名是否正确

---

## 📚 相关资源

- [Streamlit Secrets 官方文档](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [MetaGPT 文档](https://docs.deepwisdom.ai/main/en/)
- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-community-cloud)

---

## 💡 优化建议

1. **使用免费搜索引擎**: DuckDuckGo 无需 API key
2. **限制使用量**: 设置 rate limiting 避免超出 API 配额
3. **缓存结果**: 使用 `@st.cache_data` 缓存搜索结果
4. **监控成本**: 定期检查 OpenAI 使用情况

---

## 🔄 更新部署

代码更新后自动部署:

```bash
git add .
git commit -m "Update feature"
git push
```

Streamlit Cloud 会自动检测更改并重新部署。
