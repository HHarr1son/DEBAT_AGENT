# AI Debate Platform

AI-powered debate application with three agents (Principal, Student, Parent) discussing school policy topics.

## Deployment

**Live on Streamlit Cloud**: [https://hharr1son-debat-agent.streamlit.app](https://hharr1son-debat-agent.streamlit.app)

### Deploy Your Own

1. Fork this repository
2. Login to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create new app:
   - Main file: `debate_simple.py`
4. Configure Secrets (Settings → Secrets):
   ```toml
   OPENAI_API_KEY = "sk-your-key"
   ```

## Local Development

```bash
pip install -r requirements.txt
streamlit run debate_simple.py
```

Set `OPENAI_API_KEY` environment variable or create `.streamlit/secrets.toml`