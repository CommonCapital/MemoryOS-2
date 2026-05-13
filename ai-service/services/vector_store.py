import json
from typing import List
from models.schemas import ChunkResult, NoteResult
from db.postgres import get_db

async def vector_search(embedding: List[float], top_k: int, note_ids: List[str] = None) -> List[ChunkResult]:
    embed_str = json.dumps(embedding)
    
    if note_ids:
        query = """
            SELECT id, "noteId", summary, 1 - (embedding <=> $1::vector) as score
            FROM chunks
            WHERE "noteId" = ANY($3::uuid[])
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """
        async with get_db() as conn:
            rows = await conn.fetch(query, embed_str, top_k, note_ids)
    else:
        query = """
            SELECT id, "noteId", summary, 1 - (embedding <=> $1::vector) as score
            FROM chunks
            ORDER BY embedding <=> $1::vector
            LIMIT $2
        """
        async with get_db() as conn:
            rows = await conn.fetch(query, embed_str, top_k)
            
    return [ChunkResult(id=str(r['id']), note_id=str(r['noteId']), content=r['summary'], score=r['score']) for r in rows]

async def note_search(embedding: List[float], top_k: int) -> List[NoteResult]:
    embed_str = json.dumps(embedding)
    query = """
        SELECT id, title, content, 1 - (embedding <=> $1::vector) as score
        FROM notes
        ORDER BY embedding <=> $1::vector
        LIMIT $2
    """
    async with get_db() as conn:
        rows = await conn.fetch(query, embed_str, top_k)
        
    return [NoteResult(id=str(r['id']), title=r['title'], content=r['content'], score=r['score']) for r in rows]
