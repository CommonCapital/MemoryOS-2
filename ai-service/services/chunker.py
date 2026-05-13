from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
from services.graph_service import get_llm

async def chunk_note(content: str) -> List[Dict[str, Any]]:
    if not content:
        return []
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", "?", "!", " ", ""]
    )
    
    raw_chunks = splitter.split_text(content)
    
    llm = get_llm()
    results = []
    current_pos = 0
    
    for i, chunk in enumerate(raw_chunks):
        start = content.find(chunk, max(0, current_pos - 100))
        if start == -1: start = current_pos
        end = start + len(chunk)
        current_pos = end
        
        prompt = f"""
        Summarize the following text chunk into a single, dense informational sentence for a vector index.
        Focus on key facts and entities.
        
        Chunk: {chunk}
        
        Summary:"""
        try:
            response = await llm.ainvoke(prompt)
            summary = response.content.strip()
        except:
            summary = chunk[:100] + "..." 
            
        results.append({
            "summary": summary,
            "start": start,
            "end": end,
            "raw": chunk 
        })
        
    return results
