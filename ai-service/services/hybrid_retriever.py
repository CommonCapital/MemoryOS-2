import asyncio
from typing import List, Dict, Any
from models.schemas import ChunkResult, NoteResult
from services.vector_store import vector_search, note_search
from services.graph_service import graph_search
from services.embedding_service import embed_text
from services.query_router import route_query, QueryIntent
from db.postgres import get_db

async def get_filtered_note_ids(filters: Dict[str, Any]) -> List[str]:
    async with get_db() as conn:
        # Simple implementation for tags and date range
        where_clauses = []
        params = []
        
        if filters.get("tags"):
            where_clauses.append("tags @> $1")
            params.append(filters["tags"])
        
        if filters.get("date_range"):
            if filters["date_range"] == "last_week":
                where_clauses.append("updatedAt > NOW() - INTERVAL '7 days'")
            elif filters["date_range"] == "last_month":
                where_clauses.append("updatedAt > NOW() - INTERVAL '30 days'")
        
        if not where_clauses:
            return []
            
        query = f"SELECT id FROM notes WHERE {' AND '.join(where_clauses)}"
        rows = await conn.fetch(query, *params)
        return [str(r['id']) for r in rows]

async def retrieve(query: str, session_id: str = None, top_k: int = 12) -> List[Dict[str, Any]]:
    # 1. Route Query
    routing = await route_query(query)
    print(f"Routing query: {routing.intent} (Filters: {routing.structural_filters})")

    embedding = embed_text(query)
    note_ids = None

    # 2. Sequential Filtering (Pattern A)
    if routing.intent in [QueryIntent.STRUCTURAL, QueryIntent.HYBRID]:
        note_ids = await get_filtered_note_ids(routing.structural_filters)
        
        # Guardrail: Limit to 5,000 IDs
        if len(note_ids) > 5000:
            print(f"Filter set too large ({len(note_ids)}), falling back to global search.")
            note_ids = None
        elif not note_ids and routing.intent == QueryIntent.STRUCTURAL:
            print("No notes match structural filters.")
            return []

    # 3. Vector Search (Filtered or Global)
    vector_results = await vector_search(embedding, top_k, note_ids)
    
    # 4. Fetch Raw Content for Vector Results (SQL Ground Truth)
    # We use the pointers stored in the chunks to get the actual text from the notes
    async with get_db() as conn:
        for res in vector_results:
            # We need the startChar and endChar. 
            # Currently vector_search doesn't return them, let's fix that or fetch here.
            row = await conn.fetchrow('SELECT "startChar", "endChar" FROM chunks WHERE id = $1::uuid', res.id)
            if row:
                # Fetch segment from note
                segment = await conn.fetchval('SELECT SUBSTRING(content FROM $1 FOR $2) FROM notes WHERE id = $3::uuid', 
                                              row['startChar'] + 1, row['endChar'] - row['startChar'], res.note_id)
                res.content = segment # Replace summary with raw text for generation

    # 5. Graph-Augmented Search (Pattern B)
    # Use top vector results as anchors for the graph search
    anchor_ids = list(set([res.note_id for res in vector_results[:3]]))
    graph_results = await graph_search(anchor_ids, hops=2)

    merged = {}
    
    for res in vector_results:
        nid = res.note_id
        if nid not in merged:
            merged[nid] = {"note_id": nid, "content": res.content, "score": res.score, "source": "rag", "path": []}
        else:
            merged[nid]["content"] += "\n" + res.content
            if res.score > merged[nid]["score"]:
                merged[nid]["score"] = res.score
                
    for res in graph_results:
        nid = res.id
        if nid in merged:
            merged[nid]["source"] = "both"
            merged[nid]["score"] += 0.1
            merged[nid]["content"] = res.content
            merged[nid]["path"] = res.path or []
        else:
            merged[nid] = {"note_id": nid, "content": res.content, "score": res.score, "source": "graph", "path": res.path or []}

    ranked = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:top_k]
