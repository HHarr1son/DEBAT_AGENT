# ✅ Streamlit Cloud 部署检查清单

## 部署前检查

### 1. 代码准备
- [x] ✅ `debate.py` 已配置从 Streamlit secrets 读取 API keys
- [x] ✅ `.gitignore` 包含敏感文件 (`config.yaml`, `secrets.toml`)
- [x] ✅ 创建了 `requirements.txt` 包含所有依赖
- [x] ✅ 创建了配置示例文件 (`config.yaml.example`, `secrets.toml.example`)

### 2. 安全检查
```bash
# 运行此命令确保没有敏感文件被 git 追踪
git status
git ls-files | grep -E "(config.yaml|secrets.toml|\.env)"
# 输出应为空！

# 检查 config.yaml 是否包含真实 API key
cat config.yaml | grep -E "sk-|your-"
# 如果看到真实的 key，立即修改！
```

- [ ] `config.yaml` 不包含真实 API keys（或已在 .gitignore）
- [ ] `.streamlit/secrets.toml` 不在 git 追踪中
- [ ] GitHub 仓库中没有提交任何敏感信息

### 3. GitHub 准备
```bash
# 初始化仓库（如果还没有）
git init
git add .
git commit -m "Initial commit for Streamlit deployment"

# 创建 GitHub 仓库，然后：
git remote add origin https://github.com/你的用户名/你的仓库.git
git push -u origin main
```

- [ ] 代码已推送到 GitHub
- [ ] 仓库是 public 或 private（Streamlit Cloud 都支持）

---

## Streamlit Cloud 配置

### 4. 创建应用
1. 访问 https://streamlit.io/cloud
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 填写:
   - **Repository**: `你的用户名/你的仓库名`
   - **Branch**: `main`
   - **Main file path**: `debate.py`
   - **App URL** (optional): 自定义域名

### 5. 配置 Secrets ⚠️ 最重要！

在 "Advanced settings" → "Secrets" 中添加:

**最简配置（推荐）:**
```toml
OPENAI_API_KEY = "sk-proj-你的真实key"
SEARCH_ENGINE = "ddg"
```

**完整配置（如果有 SerpAPI）:**
```toml
# OpenAI 配置
OPENAI_API_KEY = "sk-proj-你的真实key"
OPENAI_MODEL = "gpt-3.5-turbo"

# 搜索引擎配置
SEARCH_ENGINE = "serpapi"
SERPAPI_API_KEY = "你的SerpAPI key"
```

- [ ] 已在 Streamlit Cloud 添加 `OPENAI_API_KEY`
- [ ] 已配置 `SEARCH_ENGINE` (推荐 `ddg` 免费)

### 6. 部署
- [ ] 点击 "Deploy!" 按钮
- [ ] 等待构建完成（通常 2-5 分钟）
- [ ] 访问生成的 URL 测试应用

---

## 部署后验证

### 7. 功能测试
- [ ] 应用可以正常访问
- [ ] 左侧边栏显示 "✅ 使用 Streamlit Cloud Secrets 配置"
- [ ] 输入话题可以开始辩论
- [ ] AI agents 能正常响应
- [ ] 没有 API key 相关错误

### 8. 安全验证
- [ ] 查看页面源代码，确认没有暴露 API keys
- [ ] 检查 Streamlit Cloud 日志，确认没有 key 泄露
- [ ] 在 GitHub 仓库中搜索，确认没有敏感信息

---

## 故障排除

### 应用无法启动
1. 检查 Streamlit Cloud 日志 (App → Manage app → Logs)
2. 确认 `requirements.txt` 中的包都能安装
3. 验证 `debate.py` 路径正确

### API 调用失败
1. 检查 Secrets 配置是否正确（注意拼写和格式）
2. 验证 OpenAI API key 是否有效
3. 检查 API 配额是否用尽

### 依赖安装失败
1. 更新 `requirements.txt` 中的版本号
2. 移除可能冲突的包
3. 查看错误日志确定具体问题

---

## 维护和更新

### 更新代码
```bash
git add .
git commit -m "Update feature"
git push
```
Streamlit Cloud 会自动重新部署。

### 更新 Secrets
1. 在 Streamlit Cloud → App settings → Secrets
2. 修改配置
3. 点击 "Save" 会自动重启应用

### 监控使用
- 定期检查 OpenAI API 使用情况
- 如果使用 SerpAPI，监控搜索配额
- 查看 Streamlit Cloud 应用分析

---

## 获取 API Keys

### OpenAI API Key
1. 访问 https://platform.openai.com/api-keys
2. 登录/注册
3. 点击 "Create new secret key"
4. 复制并保存（只显示一次！）

### SerpAPI Key (可选)
1. 访问 https://serpapi.com/
2. 注册账号
3. 在 Dashboard 查看 API key
4. 免费版: 100 searches/month

### 或使用免费替代
- DuckDuckGo (`SEARCH_ENGINE = "ddg"`): 完全免费，无需 API key

---

## 成本估算

- **Streamlit Cloud**: 免费（Community Cloud）
- **OpenAI API**:
  - GPT-3.5-turbo: ~$0.002/1K tokens
  - 每次辩论约 5-10K tokens = $0.01-0.02
- **搜索 API**:
  - DuckDuckGo: 免费
  - SerpAPI: 100 次/月 免费，超过 $50/1000 次

估算: 100 次辩论 ≈ $1-2 (仅 OpenAI)

---

## 完成！🎉

部署完成后，你会得到一个类似这样的公开 URL:
```
https://你的应用名.streamlit.app
```

分享给任何人使用，无需担心 API keys 泄露！
