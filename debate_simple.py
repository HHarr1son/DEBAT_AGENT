#!/usr/bin/env python
"""
AI Debate Platform - Streamlit Cloud Compatible Version
Simplified without heavy MetaGPT dependencies
"""

import streamlit as st
import asyncio
import os
from typing import Dict, List
import openai
from duckduckgo_search import DDGS
import aiohttp
from bs4 import BeautifulSoup

# ===== Configuration =====
if hasattr(st, 'secrets') and len(st.secrets) > 0 and "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    st.sidebar.success("✅ Using Streamlit Cloud Secrets")
elif os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    st.sidebar.info("🔧 Using environment variable")
else:
    st.error("⚠️ **API Key Missing**")
    st.markdown("""
    Configure your OpenAI API key:

    **Streamlit Cloud**: Add to App Settings → Secrets:
    ```toml
    OPENAI_API_KEY = "sk-..."
    ```

    **Local**: Set environment variable:
    ```bash
    export OPENAI_API_KEY="sk-..."
    ```
    """)
    st.stop()


# ===== Helper Functions =====
async def call_gpt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Call OpenAI API"""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling GPT: {str(e)}"


async def search_web(query: str, max_results: int = 3) -> List[str]:
    """Search web using DuckDuckGo"""
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        urls = []
        for result in results:
            if 'href' in result:
                urls.append(result['href'])
            elif 'link' in result:
                urls.append(result['link'])
        return urls[:max_results]
    except:
        return []


async def fetch_content(url: str) -> str:
    """Fetch and extract content from URL"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text(separator=' ', strip=True)
                    return text[:1500]
        return ""
    except:
        return ""


async def research_topic(topic: str) -> str:
    """Conduct research on a topic"""
    urls = await search_web(topic, max_results=2)

    if not urls:
        return f"Limited research available on: {topic}"

    contents = []
    for url in urls:
        content = await fetch_content(url)
        if content:
            contents.append(f"[Source: {url}]\n{content}")

    if not contents:
        return f"Could not fetch content for: {topic}"

    research_text = "\n\n---\n\n".join(contents)

    summary_prompt = f"""Summarize the following research about "{topic}" in 200-300 words, highlighting key facts and statistics:

{research_text[:2000]}

Summary:"""

    summary = await call_gpt(summary_prompt)
    return summary


# ===== Debate Agents =====
class Debater:
    def __init__(self, name: str, profile: str, opponent1: str, opponent2: str):
        self.name = name
        self.profile = profile
        self.opponent1 = opponent1
        self.opponent2 = opponent2
        self.research = ""

    async def request_research(self, topic: str):
        """Request research for the debate"""
        query_prompt = f"""You are {self.name}, a {self.profile} preparing for a debate on: {topic}

What specific aspect would you research to strengthen your {self.profile} perspective?
Provide ONE specific research query (1-2 sentences)."""

        query = await call_gpt(query_prompt)
        research = await research_topic(query)
        self.research = f"Research Query: {query}\n\nFindings: {research}"
        return self.research

    async def speak(self, topic: str, context: str, round_num: int) -> str:
        """Generate debate response"""
        if round_num <= 3:
            instruction = f"""Round {round_num}/3 (Opening). State your view on the topic clearly and concisely from a {self.profile} perspective. Use facts from your research. Include citations [Source: ...]."""
        else:
            instruction = f"""Round {round_num}. Defend your arguments and rebut opponents' points. Use evidence from your research with citations."""

        prompt = f"""You are {self.name}, debating with {self.opponent1} and {self.opponent2} on:
{topic}

Previous discussion:
{context[-1500:] if context else "No previous discussion"}

Your research:
{self.research[:1000]}

{instruction}

Your response:"""

        return await call_gpt(prompt)


async def evaluate_debate(topic: str, messages: List[Dict]) -> str:
    """Evaluate the debate"""
    debate_text = "\n\n".join([f"{msg['speaker']}: {msg['content']}" for msg in messages])

    prompt = f"""Analyze this debate on "{topic}" and provide a concise evaluation (200-300 words):

{debate_text[-2000:]}

Evaluation (summarize key arguments, trade-offs, and recommendations):"""

    return await call_gpt(prompt)


async def provide_advice(topic: str, evaluation: str) -> str:
    """Provide compromise solutions"""
    prompt = f"""Based on this debate evaluation, provide 3 compromise solutions:

Topic: {topic}
Evaluation: {evaluation}

For each solution, include:
1. Description
2. Benefits for all parties
3. Potential consequences
4. Implementation steps

Compromise solutions:"""

    return await call_gpt(prompt)


# ===== Main Debate Function =====
async def run_debate(topic: str, n_rounds: int = 6):
    """Run the debate"""
    # Create debaters
    principal = Debater("Principal", "School Administrator", "John", "Mom")
    student = Debater("John", "Student", "Mom", "Principal")
    parent = Debater("Mom", "Parent", "Principal", "John")

    debaters = [principal, student, parent]

    # Research phase
    research_results = []
    for debater in debaters:
        result = await debater.request_research(topic)
        research_results.append({"debater": debater.name, "research": result})

    # Debate rounds
    debate_messages = []
    context = ""
    speakers = [principal, student, parent]

    for round_num in range(n_rounds):
        current = speakers[round_num % 3]
        response = await current.speak(topic, context, round_num + 1)

        debate_messages.append({
            "round": round_num + 1,
            "speaker": current.name,
            "content": response
        })

        context += f"\n\n{current.name}: {response}"

    # Evaluation
    evaluation = await evaluate_debate(topic, debate_messages)
    advice = await provide_advice(topic, evaluation)

    return debate_messages, evaluation, research_results, advice


# ===== Streamlit UI =====
st.set_page_config(page_title="AI Debate Platform", page_icon="🗣️", layout="wide")

st.title("🗣️ AI Debate Platform")
st.markdown("Enter a debate topic and watch AI agents discuss different perspectives!")

# Input
with st.form("debate_form"):
    topic = st.text_input(
        "Debate Topic:",
        placeholder="e.g., Should schools ban smartphones?",
        help="Enter any topic for school policy debate"
    )

    n_rounds = st.slider("Number of rounds:", min_value=3, max_value=10, value=6)
    submitted = st.form_submit_button("Start Debate", type="primary")

if submitted and topic:
    with st.spinner("🤖 AI agents are debating..."):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Starting debate...")
            progress_bar.progress(10)

            # Run debate
            debate_log, evaluation, research_log, advice = asyncio.run(
                run_debate(topic, n_rounds)
            )

            progress_bar.progress(100)
            status_text.text("Debate completed!")

            # Display results
            st.subheader("💡 Advisor Recommendations")
            st.info(advice)

            st.subheader("📋 Debate Evaluation")
            st.success(evaluation)

            with st.expander("🔍 Research Phase", expanded=False):
                for entry in research_log:
                    st.markdown(f"**{entry['debater']} Research:**")
                    st.write(entry['research'])
                    st.divider()

            with st.expander("🗣️ View Full Debate", expanded=False):
                for entry in debate_log:
                    st.markdown(f"**Round {entry['round']} - {entry['speaker']}:**")
                    st.write(entry['content'])
                    st.divider()

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please try again or check your API key.")

elif submitted and not topic:
    st.warning("Please enter a debate topic!")

# Sidebar
with st.sidebar:
    st.header("How it works")
    st.markdown("""
    1. **Enter topic** - School policy debate topics
    2. **Choose rounds** - More rounds = deeper discussion
    3. **Start debate** - Three AI agents debate:
       - 🏫 **Principal** (School perspective)
       - 👨‍🎓 **John** (Student perspective)
       - 👩‍👧 **Mom** (Parent perspective)
    4. **View results** - Evaluation and recommendations
    """)

    st.header("Example Topics")
    st.markdown("""
    - Should schools ban smartphones?
    - Is homework necessary?
    - Should school start later?
    - Should uniforms be required?
    """)
