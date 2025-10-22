#!/usr/bin/env python
"""
Research actions for debate agents
Simplified version for Streamlit Cloud deployment
"""

from typing import Dict, List
from metagpt.actions import Action
from duckduckgo_search import DDGS
import asyncio
import aiohttp
from bs4 import BeautifulSoup


class CollectLinks(Action):
    """Collect search result links using DuckDuckGo"""

    name: str = "CollectLinks"

    async def run(self, topic: str, decomposition_nums: int = 2, url_per_query: int = 3) -> Dict[str, List[str]]:
        """
        Search for links related to the topic

        Args:
            topic: Search topic
            decomposition_nums: Number of search queries (simplified to 1 for cloud)
            url_per_query: Number of URLs per query

        Returns:
            Dict mapping queries to lists of URLs
        """
        try:
            # Use DuckDuckGo search (free, no API key needed)
            ddgs = DDGS()
            results = ddgs.text(topic, max_results=url_per_query)

            urls = []
            for result in results:
                if 'href' in result:
                    urls.append(result['href'])
                elif 'link' in result:
                    urls.append(result['link'])

            return {topic: urls[:url_per_query]}

        except Exception as e:
            # Fallback to empty results if search fails
            return {topic: []}


class WebBrowseAndSummarize(Action):
    """Browse web pages and extract content"""

    name: str = "WebBrowseAndSummarize"

    async def run(self, *urls: str, query: str = "") -> Dict[str, str]:
        """
        Fetch and summarize web pages

        Args:
            urls: URLs to fetch
            query: Original search query

        Returns:
            Dict mapping URLs to their content summaries
        """
        results = {}

        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    # Set timeout and user agent
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }

                    async with session.get(url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'lxml')

                            # Remove script and style elements
                            for script in soup(["script", "style"]):
                                script.decompose()

                            # Get text
                            text = soup.get_text(separator=' ', strip=True)

                            # Limit text length
                            text = text[:2000] if len(text) > 2000 else text

                            results[url] = f"[Source: {url}]\n{text}"
                        else:
                            results[url] = f"[Source: {url}]\nFailed to fetch content (HTTP {response.status})"

                except asyncio.TimeoutError:
                    results[url] = f"[Source: {url}]\nTimeout while fetching content"
                except Exception as e:
                    results[url] = f"[Source: {url}]\nError: {str(e)}"

        return results


class ConductResearch(Action):
    """Compile research from collected information"""

    name: str = "ConductResearch"

    async def run(self, topic: str, content: str) -> str:
        """
        Summarize research findings using LLM

        Args:
            topic: Research topic
            content: Collected content from web sources

        Returns:
            Research summary
        """
        if not content or content.strip() == "":
            return f"No research data available for topic: {topic}"

        prompt = f"""Based on the following web search results about "{topic}", provide a concise research summary (200-300 words) with key facts, statistics, and relevant information.

Web Content:
{content[:3000]}

Research Summary:"""

        try:
            # Use LLM to summarize
            rsp = await self._aask(prompt)
            return rsp
        except Exception as e:
            # Fallback: return raw content summary
            return f"Research on '{topic}':\n\n{content[:1000]}..."
