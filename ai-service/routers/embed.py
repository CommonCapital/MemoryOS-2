from fastapi import APIRouter, BackgroundTasks
from models.schemas import EmbedNoteRequest
from services.embedding_service import embed_text
from services.chunker import chunk_note
from services.graph_service import extract_entities, upsert_graph
from services.classification_service import classify_data, IngestionLayer
from db.postgres import get_db
import json

router = APIRouter()

async def process_note_embedding(note_id: str, title: str, content: str, tags: list[str] = []):
    try:
        # 1. Classify Data
        classification = await classify_data(title, content, tags)
        print(f"Classification for {note_id}: {classification.layers} (Reason: {classification.reason})")
        
        async with get_db() as conn:
            # 2. Vector Layer (Conditional)
            if IngestionLayer.VECTOR in classification.layers:
                full_text = f"{title}\n\n{content}"
                full_embed = embed_text(full_text)
                await conn.execute('UPDATE notes SET embedding = $1::vector WHERE id = $2', json.dumps(full_embed), note_id)
                
                await conn.execute('DELETE FROM chunks WHERE "noteId" = $1', note_id)
                chunks = await chunk_note(content)
                for i, chunk_data in enumerate(chunks):
                    # Embed the raw chunk text (for semantic accuracy) 
                    # but only store the summary in SQL
                    chunk_embed = embed_text(chunk_data["raw"])
                    await conn.execute('''
                        INSERT INTO chunks ("noteId", summary, "startChar", "endChar", "chunkIndex", embedding)
                        VALUES ($1, $2, $3, $4, $5, $6::vector)
                    ''', note_id, chunk_data["summary"], chunk_data["start"], chunk_data["end"], i, json.dumps(chunk_embed))
            
            # 3. Knowledge Graph Layer (Conditional)
            if IngestionLayer.GRAPH in classification.layers:
                full_text = f"{title}\n\n{content}"
                extract_res = await extract_entities(full_text)
                if extract_res.nodes:
                    await upsert_graph(note_id, extract_res.nodes, extract_res.edges)
                    
    except Exception as e:
        print(f"Error processing embedding for {note_id}: {e}")

@router.post("/note")
async def embed_note_endpoint(req: EmbedNoteRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_note_embedding, req.id, req.title, req.content, req.tags)
    return {"status": "accepted", "note_id": req.id}
