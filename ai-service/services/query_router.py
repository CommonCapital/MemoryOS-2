import os
from enum import Enum
from typing import List, Optional, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class QueryIntent(str, Enum):
    STRUCTURAL = "STRUCTURAL"      # Dates, tags, specific IDs, "last week", "project X"
    CONCEPTUAL = "CONCEPTUAL"      # "How does X work?", "What is the relationship between Y and Z?"
    HYBRID = "HYBRID"              # Both

class QueryRoutingPlan(BaseModel):
    intent: QueryIntent
    structural_filters: Dict[str, Any] = {}
    reason: str

AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()

def get_llm():
    if AI_PROVIDER == "anthropic":
        return ChatAnthropic(model="claude-3-haiku-20240307", max_tokens=512, temperature=0)
    else:
        return ChatOpenAI(model="gpt-4o-mini", max_tokens=512, temperature=0)

async def route_query(query: str) -> QueryRoutingPlan:
    # Deterministic check for simple keyword/tag queries
    if query.startswith("#") or query.startswith("tag:"):
        tag = query.split(":")[1] if ":" in query else query[1:]
        return QueryRoutingPlan(
            intent=QueryIntent.STRUCTURAL,
            structural_filters={"tags": [tag]},
            reason="Explicit tag query detected."
        )

    llm = get_llm()
    prompt = f"""
    Analyze the user's search query for a personal knowledge base.
    Determine if the query has structural constraints (dates, tags, specific entities) or if it's purely conceptual.
    
    Query: "{query}"
    
    Return ONLY JSON:
    {{
      "intent": "STRUCTURAL" | "CONCEPTUAL" | "HYBRID",
      "structural_filters": {{
        "tags": ["string"],
        "date_range": "last_week" | "last_month" | "this_year" | null,
        "note_ids": ["uuid"]
      }},
      "reason": "explanation"
    }}
    """
    try:
        response = await llm.ainvoke(prompt)
        import json
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        data = json.loads(content)
        return QueryRoutingPlan(**data)
    except Exception as e:
        print(f"Routing error: {e}")
        return QueryRoutingPlan(intent=QueryIntent.CONCEPTUAL, reason="Fallback to conceptual search.")
