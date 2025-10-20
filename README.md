# AI Debate Platform

An interactive Streamlit application that facilitates AI-powered debates between three perspectives (Principal, Student, Parent) on various topics, with research capabilities and compromise recommendations.

## Features

- **Multi-Agent Debate**: Three AI agents debate from different perspectives
- **Research Integration**: Agents conduct web research to support their arguments
- **Evaluation & Advice**: Neutral evaluator and advisor provide analysis and compromise solutions
- **Interactive UI**: Clean Streamlit interface with expandable sections

## 🚀 Quick Deploy to Streamlit Cloud

**详细部署指南**: 查看 [DEPLOYMENT.md](DEPLOYMENT.md)

### 快速步骤:

1. **Fork** 此仓库到你的 GitHub
2. **登录** [Streamlit Cloud](https://streamlit.io/cloud)
3. **创建新应用**:
   - Repository: 你的 fork
   - Branch: main
   - Main file: `debate.py`
4. **配置 Secrets** (App Settings → Secrets):
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   SEARCH_ENGINE = "ddg"
   ```
5. **Deploy!** 🎉

**重要**: 不要将 API keys 提交到 GitHub！已在 `.gitignore` 中排除敏感文件。

## Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
3. Add your API keys to the secrets file
4. Run: `streamlit run streamlit_debate.py`

## Usage

1. Enter a debate topic (works best with school policy topics)
2. Select number of debate rounds (3-10)
3. Click "Start Debate" and wait for results
4. View advisor recommendations, evaluation, research, and full debate transcript

## Requirements

- OpenAI API key (required)
- SerpAPI key (optional, for enhanced research)
- Python 3.8+
- Dependencies listed in requirements.txt