import re
import os
from typing import List, Optional
from enum import Enum
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class IngestionLayer(str, Enum):
    VECTOR = "VECTOR"
    GRAPH = "GRAPH"
    SQL_ONLY = "SQL_ONLY"

class ClassificationResult(BaseModel):
    layers: List[IngestionLayer]
    reason: str

AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic").lower()

def get_llm():
    if AI_PROVIDER == "anthropic":
        return ChatAnthropic(model="claude-3-haiku-20240307", max_tokens=256, temperature=0)
    else:
        return ChatOpenAI(model="gpt-4o-mini", max_tokens=256, temperature=0)

def is_log_content(content: str) -> bool:
    # Deterministic bypass for logs: starts with timestamp or contains common log patterns
    log_patterns = [
        r'^\d{4}-\d{2}-\d{2}', # ISO date
        r'^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}', # Syslog date
        r'\[(INFO|DEBUG|ERROR|WARN|TRACE)\]', # Common log levels
        r'level=(info|debug|error|warn)', # Logfmt
    ]
    for pattern in log_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False

async def classify_data(title: str, content: str, tags: List[str] = []) -> ClassificationResult:
    # 1. Deterministic Bypass: Small texts or Logs
    if len(content) < 100 or is_log_content(content):
        return ClassificationResult(
            layers=[IngestionLayer.SQL_ONLY],
            reason="Small text or structured log detected. Skipping expensive processing."
        )
    
    # 2. Tag-based Shortcut
    if any(t.lower() in ["log", "structural", "metadata"] for t in tags):
        return ClassificationResult(layers=[IngestionLayer.SQL_ONLY], reason="Tagged as structural.")
    
    if any(t.lower() in ["entity", "concept", "knowledge", "research"] for t in tags):
        return ClassificationResult(layers=[IngestionLayer.VECTOR, IngestionLayer.GRAPH], reason="Tagged as high-value knowledge.")

    # 3. LLM-based Classification
    llm = get_llm()
    prompt = f"""
    Analyze the following document and determine which memory layers it should be stored in.
    
    Layers:
    - VECTOR: For unstructured text, notes, or descriptions that need semantic search.
    - GRAPH: For content rich in entities (people, projects, systems) and relationships.
    - SQL_ONLY: For structured data, short status updates, or logs that only need exact retrieval.
    
    Document Title: {title}
    Document Content: {content[:500]}...
    
    Return ONLY JSON:
    {{
      "layers": ["VECTOR", "GRAPH", "SQL_ONLY"],
      "reason": "short explanation"
    }}
    """
    try:
        response = await llm.ainvoke(prompt)
        import json
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        data = json.loads(content)
        return ClassificationResult(**data)
    except Exception as e:
        print(f"Classification error: {e}")
        return ClassificationResult(layers=[IngestionLayer.VECTOR], reason="Fallback to vector due to error.")
