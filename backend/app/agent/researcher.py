import logging
import uuid
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
from app.models.schemas import ResearchPlan, SearchResult, ToolCallLog
from app.services.search_service import search_service
from app.services.web_scraper import web_scraper
from app.services.llm_service import llm_service
from app.agent.prompts import TOOL_SELECTOR_SYSTEM_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)

class ToolResearcher:
    def __init__(self, max_loops: Optional[int] = None):
        self.max_loops = max_loops or settings.MAX_RESEARCH_LOOPS

    def execute_retrieval(
        self,
        plan: ResearchPlan,
        on_tool_call: Optional[Callable[[ToolCallLog], None]] = None
    ) -> List[SearchResult]:
        """Execute bounded search and content extraction iterations."""
        discovered_sources: Dict[str, SearchResult] = {}
        executed_queries = set()
        scraped_urls = set()

        # Step 1: Initial automated search passes from suggested sub-question queries
        logger.info("Executing initial planned search queries...")
        for sub_q in plan.sub_questions:
            for query in sub_q.suggested_queries[:1]: # Take top query per sub-question
                if query.lower() in executed_queries:
                    continue
                executed_queries.add(query.lower())
                
                tool_log = ToolCallLog(
                    id=f"tool-{uuid.uuid4().hex[:8]}",
                    iteration=1,
                    tool_name="web_search",
                    arguments={"query": query, "sub_question_id": sub_q.id},
                    summary_result=f"Query executed: '{query}'",
                    timestamp=datetime.utcnow()
                )
                if on_tool_call:
                    on_tool_call(tool_log)

                try:
                    results = search_service.search(query, max_results=settings.MAX_SEARCH_RESULTS_PER_QUERY)
                    for r in results:
                        if r.url not in discovered_sources:
                            discovered_sources[r.url] = r
                except Exception as e:
                    logger.error(f"Search query '{query}' failed: {e}")

        # Step 2: Bounded iterative tool loop guided by LLM
        current_loop = 2
        while current_loop <= self.max_loops:
            sources_summary = "\n".join([
                f"- [{s.id}] {s.title} ({s.url}): {s.snippet[:160]}"
                for s in list(discovered_sources.values())[:8]
            ])
            
            prompt_context = f"""Research Plan Question: {plan.main_question}
Sub-Questions to Answer:
{chr(10).join([f"- [{sq.id}] {sq.question}" for sq in plan.sub_questions])}

Current Discovered Sources ({len(discovered_sources)} total):
{sources_summary}

Determine if additional searches or deep page extractions are required.
Iteration: {current_loop} of {self.max_loops}.
"""
            messages = [{"role": "user", "content": prompt_context}]
            tool_calls = llm_service.select_tools(
                system_prompt=TOOL_SELECTOR_SYSTEM_PROMPT,
                messages=messages
            )

            if not tool_calls:
                logger.info(f"LLM decided no further tool calls are required at loop {current_loop}.")
                break

            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("arguments", {})
                
                if name == "web_search":
                    query = args.get("query", "").strip()
                    if query and query.lower() not in executed_queries:
                        executed_queries.add(query.lower())
                        try:
                            results = search_service.search(query, max_results=3)
                            for r in results:
                                if r.url not in discovered_sources:
                                    discovered_sources[r.url] = r
                            summary = f"Discovered {len(results)} sources for query '{query}'"
                        except Exception as e:
                            summary = f"Search failed: {e}"
                    else:
                        summary = f"Query '{query}' already executed or empty."
                        
                    log = ToolCallLog(
                        id=f"tool-{uuid.uuid4().hex[:8]}",
                        iteration=current_loop,
                        tool_name="web_search",
                        arguments=args,
                        summary_result=summary,
                        timestamp=datetime.utcnow()
                    )
                    if on_tool_call:
                        on_tool_call(log)

                elif name == "extract_page_content":
                    url = args.get("url", "").strip()
                    if url and url not in scraped_urls:
                        scraped_urls.add(url)
                        try:
                            content = web_scraper.scrape_url(url)
                            # Update source if present
                            if url in discovered_sources:
                                discovered_sources[url].content = content
                            else:
                                discovered_sources[url] = SearchResult(
                                    id=f"src-{uuid.uuid4().hex[:8]}",
                                    title=f"Extracted page from {url}",
                                    url=url,
                                    snippet=content[:200],
                                    content=content,
                                    query="direct_url_extract",
                                    timestamp=datetime.utcnow()
                                )
                            summary = f"Extracted {len(content)} characters of text from {url}"
                        except Exception as e:
                            summary = f"Extraction failed: {e}"
                    else:
                        summary = f"URL '{url}' already extracted or invalid."

                    log = ToolCallLog(
                        id=f"tool-{uuid.uuid4().hex[:8]}",
                        iteration=current_loop,
                        tool_name="extract_page_content",
                        arguments=args,
                        summary_result=summary,
                        timestamp=datetime.utcnow()
                    )
                    if on_tool_call:
                        on_tool_call(log)

            current_loop += 1

        # Step 3: Ensure top 2 sources have full page content extracted for deep evidence
        for source in list(discovered_sources.values())[:2]:
            if not source.content and source.url not in scraped_urls:
                scraped_urls.add(source.url)
                try:
                    source.content = web_scraper.scrape_url(source.url)
                except Exception as e:
                    logger.warning(f"Fallback scrape failed for {source.url}: {e}")

        logger.info(f"Retrieval complete. Total unique sources gathered: {len(discovered_sources)}")
        return list(discovered_sources.values())

researcher = ToolResearcher()
