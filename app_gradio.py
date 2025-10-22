#!/usr/bin/env python
"""
AI Debate Platform - Gradio version for Hugging Face Spaces
Full MetaGPT integration
"""

import gradio as gr
import asyncio
import os
import sys

# Add current directory to path for MetaGPT imports
sys.path.insert(0, os.path.dirname(__file__))

# Configure environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

# Import debate logic
try:
    from metagpt.actions import Action
    from metagpt.roles import Role
    from metagpt.schema import Message
    from research_actions import CollectLinks, WebBrowseAndSummarize, ConductResearch
    from metagpt.roles.role import RoleReactMode
    import openai

    openai.api_key = os.getenv("OPENAI_API_KEY")
    METAGPT_AVAILABLE = True
except ImportError as e:
    print(f"MetaGPT import failed: {e}")
    METAGPT_AVAILABLE = False
    # Fallback to simple version
    import openai
    from duckduckgo_search import DDGS
    import aiohttp
    from bs4 import BeautifulSoup

    openai.api_key = os.getenv("OPENAI_API_KEY")


# ===== Debate Logic =====
if METAGPT_AVAILABLE:
    # Use full MetaGPT version
    class Researcher(Role):
        name: str = "Researcher"
        profile: str = "Research Assistant"

        def __init__(self, **data):
            super().__init__(**data)
            self.set_actions([CollectLinks, WebBrowseAndSummarize, ConductResearch])
            self._set_react_mode(RoleReactMode.BY_ORDER.value, len(self.actions))

        async def research_topic(self, topic: str) -> str:
            collect_action = CollectLinks()
            links = await collect_action.run(topic, decomposition_nums=2, url_per_query=2)

            browse_action = WebBrowseAndSummarize()
            summaries = []
            url_count = 0
            for query, urls in links.items():
                if urls and url_count < 4:
                    remaining_urls = 4 - url_count
                    limited_urls = urls[:remaining_urls]
                    result = await browse_action.run(*limited_urls, query=query)
                    summaries.extend(result.values())
                    url_count += len(limited_urls)

            research_action = ConductResearch()
            content = "\n---\n".join(summaries)
            report = await research_action.run(topic, content)
            return report

    class Debater(Role):
        name: str = ""
        profile: str = ""
        opponent_name1: str = ""
        opponent_name2: str = ""
        research_info: str = ""

        def __init__(self, **data):
            super().__init__(**data)
            from metagpt.actions import UserRequirement
            class SpeakAloud(Action):
                name: str = "SpeakAloud"
                async def run(self, context: str, name: str, opponent_name1: str, opponent_name2: str,
                            idea: str = "", profile: str = "", round_num: int = 1, research_info: str = "") -> str:
                    if round_num <= 3:
                        instruction = f"Round {round_num}/3: State your {profile} view with evidence"
                    else:
                        instruction = f"Round {round_num}: Defend and rebut with evidence"

                    prompt = f"""You are {name}, debating: {idea}
Previous: {context[-1000:]}
Research: {research_info[:800]}
{instruction}
Response:"""
                    rsp = await self._aask(prompt)
                    return rsp

            self.set_actions([SpeakAloud])
            self._watch([UserRequirement, SpeakAloud])

        async def request_research(self, topic: str, researcher):
            from metagpt.actions import Action
            class RequestResearch(Action):
                name: str = "RequestResearch"
                async def run(self, name: str, profile: str, topic: str) -> str:
                    prompt = f"You are {name}, a {profile}. What would you research about: {topic}? (1 query)"
                    return await self._aask(prompt)

            request_action = RequestResearch()
            query = await request_action.run(name=self.name, profile=self.profile, topic=topic)
            research_result = await researcher.research_topic(query)
            self.research_info = f"Query: {query}\nResult: {research_result}"
            return research_result

else:
    # Simplified fallback
    async def call_gpt(prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    class Debater:
        def __init__(self, name: str, profile: str, opponent1: str, opponent2: str):
            self.name = name
            self.profile = profile
            self.research_info = ""

        async def request_research(self, topic: str, researcher=None):
            self.research_info = f"Basic research on: {topic}"
            return self.research_info

        async def speak(self, topic: str, context: str, round_num: int) -> str:
            prompt = f"You are {self.name} ({self.profile}), debating: {topic}\nRound {round_num}.\nRespond (200 words):"
            return await call_gpt(prompt)


async def run_debate(topic: str, n_rounds: int = 6):
    """Run debate and return formatted results"""

    if not os.getenv("OPENAI_API_KEY"):
        return "❌ Error: OPENAI_API_KEY not configured", "", ""

    try:
        # Create debaters
        if METAGPT_AVAILABLE:
            researcher = Researcher()
            principal = Debater(name="Principal", profile="School", opponent_name1="John", opponent_name2="Mom")
            student = Debater(name="John", profile="Student", opponent_name1="Mom", opponent_name2="Principal")
            parent = Debater(name="Mom", profile="Parent", opponent_name1="Principal", opponent_name2="John")
        else:
            principal = Debater("Principal", "School", "John", "Mom")
            student = Debater("John", "Student", "Mom", "Principal")
            parent = Debater("Mom", "Parent", "Principal", "John")
            researcher = None

        # Research phase
        research_text = "## 🔍 Research Phase\n\n"
        for debater in [principal, student, parent]:
            result = await debater.request_research(topic, researcher)
            research_text += f"**{debater.name}**: {result[:200]}...\n\n"

        # Debate
        debate_text = "## 🗣️ Debate\n\n"
        speakers = [principal, student, parent]
        context = ""

        for round_num in range(min(n_rounds, 6)):
            current = speakers[round_num % 3]

            if METAGPT_AVAILABLE:
                msg = Message(content=topic, role="user", send_to={current.name}, sent_from="User")
                response = await current.run(msg)
                content = response.content
            else:
                content = await current.speak(topic, context, round_num + 1)

            debate_text += f"### Round {round_num + 1} - {current.name}\n{content}\n\n---\n\n"
            context += f"\n{current.name}: {content}"

        # Evaluation
        eval_prompt = f"Summarize this debate and provide recommendations:\n\n{context[-2000:]}"

        if METAGPT_AVAILABLE:
            from metagpt.actions import Action
            class EvaluateDebate(Action):
                name: str = "EvaluateDebate"
                async def run(self, topic: str, content: str) -> str:
                    prompt = f"Evaluate debate on '{topic}':\n{content}\nProvide summary and recommendations:"
                    return await self._aask(prompt)

            evaluator = EvaluateDebate()
            evaluation = await evaluator.run(topic, context)
        else:
            evaluation = await call_gpt(eval_prompt)

        eval_text = f"## 📋 Evaluation\n\n{evaluation}"

        return research_text, debate_text, eval_text

    except Exception as e:
        return f"❌ Error: {str(e)}", "", ""


def debate_interface(topic: str, rounds: int):
    """Gradio interface wrapper"""
    if not topic:
        return "⚠️ Please enter a debate topic", "", ""

    try:
        research, debate, evaluation = asyncio.run(run_debate(topic, rounds))
        return research, debate, evaluation
    except Exception as e:
        return f"❌ Error: {str(e)}", "", ""


# ===== Gradio UI =====
with gr.Blocks(title="AI Debate Platform", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🗣️ AI Debate Platform")
    gr.Markdown("Three AI agents debate different perspectives on school policy topics")

    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        gr.Markdown("### ⚠️ Configuration Required")
        gr.Markdown("""
        **For Hugging Face Spaces:**
        1. Go to Settings → Repository secrets
        2. Add secret: `OPENAI_API_KEY` = `sk-your-key`
        3. Restart the Space

        **For local:**
        ```bash
        export OPENAI_API_KEY="sk-your-key"
        ```
        """)

    with gr.Row():
        with gr.Column(scale=2):
            topic_input = gr.Textbox(
                label="Debate Topic",
                placeholder="e.g., Should schools ban smartphones?",
                lines=2
            )
            rounds_slider = gr.Slider(
                minimum=3,
                maximum=9,
                value=6,
                step=1,
                label="Number of Rounds"
            )
            submit_btn = gr.Button("Start Debate", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### Example Topics")
            gr.Markdown("""
            - Should schools ban smartphones?
            - Is homework necessary?
            - Should school start later?
            - Should uniforms be required?
            """)

    gr.Markdown("---")

    with gr.Tabs():
        with gr.Tab("📋 Evaluation"):
            eval_output = gr.Markdown(label="Evaluation")

        with gr.Tab("🗣️ Full Debate"):
            debate_output = gr.Markdown(label="Debate Transcript")

        with gr.Tab("🔍 Research"):
            research_output = gr.Markdown(label="Research Phase")

    # Event handler
    submit_btn.click(
        fn=debate_interface,
        inputs=[topic_input, rounds_slider],
        outputs=[research_output, debate_output, eval_output]
    )

    gr.Markdown("---")
    gr.Markdown("💡 **Powered by**: " + ("MetaGPT Framework" if METAGPT_AVAILABLE else "OpenAI API"))

# Launch
if __name__ == "__main__":
    demo.launch()
