<p align="center">
  <img src="frontend/public/logo-3.png" width="120" alt="MemoryOS Logo">
</p>

# MemoryOS-2 🧠🕸️

MemoryOS is a powerful personal knowledge base that combines traditional **RAG (Vector Search)** with a **High-Fidelity Knowledge Graph**. It doesn't just store your notes; it understands the structural, causal, and semantic relationships between your ideas.

## 🚀 Key Features

### 1. Tiered Memory Architecture
MemoryOS-2 uses a high-efficiency **Tiered Ingestion** pipeline to eliminate vector bloat and write amplification:
- **Data Classifier Router:** Every note is analyzed before processing. Structured logs and small texts skip expensive Vector/Graph processing (Deterministic Bypass).
- **SQL Ground Truth:** The relational layer acts as the master source of truth and metadata.
- **Vector Layer (Abstract Indexes):** Stores semantic chunks with pointers back to SQL. No redundant full-text storage in the vector DB.
- **Knowledge Graph (High-Value Entities):** Reserved for complex concepts and relationships. Node-level embeddings are eliminated to save GPU cycles, using the vector layer as anchors instead.

### 2. Dual-Path Smart Routing
Instead of brute-force parallel queries, the system uses **Intent-Based Routing**:
- **Sequential Filtering (Structural):** Queries with dates or tags filter SQL first. **SQL Guardrails** cap filters at 5,000 IDs to ensure sub-millisecond lookups.
- **Graph-Augmented Search (Conceptual):** Uses top vector chunks as "anchors" to enter the graph for shallow, context-rich traversals (Depth 1-2).
- **Fallback Logic:** Automatically reverts to global vector search if structural filters are too broad.

### 3. High-Fidelity Knowledge Graph
Nodes are not just buckets for notes; they are first-class entities (People, Concepts, Tech, etc.) with:
- **Typed Relations:** `is_a`, `causes`, `works_at`, `part_of`, and more.
- **Directional Links:** Solid arrows for 1-way relationships, double arrows for bidirectional.
- **Confidence Scores:** Visual translucency for AI-extracted relations with lower confidence.

### 4. Interactive Memory Visualization
- **Graph Explorer:** A React Flow-based canvas with automatic degree-based sizing and relation-aware styling.
- **Vector Cluster Map:** A 2D UMAP projection of your entire note library, allowing you to see semantic "islands" of thought.
- **Retrieval Inspector:** An X-ray view of the last AI query, showing the exact path the graph traversal took.

### 5. Memory Health Dashboard
Monitor your memory in real-time. Trigger batch re-indexing or re-extraction of entities across your entire database with a single click.

---

## 🛠️ Tech Stack

### Frontend (Next.js)
- **Framework:** Next.js 14 (App Router)
- **Graphing:** React Flow
- **Visualization:** Plotly.js (UMAP Projection)
- **State:** Zustand & SWR
- **Editor:** TipTap with Wikilink support

### AI Service (Python/FastAPI)
- **Engine:** FastAPI
- **LLM Orchestration:** LangChain (Anthropic Claude-3 / OpenAI GPT-4)
- **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
- **Analysis:** UMAP-Learn & Scikit-learn

### Database
- **Primary DB:** PostgreSQL
- **Vector Extension:** `pgvector`
- **ORM:** Prisma

---

## 🚦 Getting Started

### 1. Prerequisites
- Node.js v18+
- Python 3.10+
- PostgreSQL with `pgvector` installed

### 2. Environment Setup
Create a `.env.local` (frontend) and `.env` (ai-service) file:
```env
DATABASE_URL="postgresql://user:pass@localhost:5432/memoryos"
OPENAI_API_KEY="your_key"
ANTHROPIC_API_KEY="your_key"
AI_PROVIDER="anthropic" # or "openai"
```

### 3. Install Dependencies
```bash
# Frontend
cd frontend
npm install
npx prisma db push

# AI Service
cd ../ai-service
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Terminal 1: AI Service
cd ai-service
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## 🕸️ Graph Taxonomy
MemoryOS uses a canonical taxonomy for extracted relations to ensure consistency:
- **Structural:** `is_a`, `part_of`, `type_of`
- **Causal:** `causes`, `enables`, `requires`
- **Social:** `works_at`, `knows`, `founded`
- **Temporal:** `precedes`, `succeeded_by`
- **Hierarchy:** `broader_than`, `narrower_than`

---

## 🤖 AI Integration (MCP)
MemoryOS supports the **Model Context Protocol (MCP)**, allowing you to connect AI assistants (like Antigravity or Claude Code) directly to your knowledge base.

### Connecting an Assistant
1. **Build the MCP Server:**
   ```bash
   cd mcp-server
   npm install
   npm run build
   ```
2. **Configure your AI Client:**
   Add the following to your AI client's MCP configuration (e.g., `mcp-config.json`):
   ```json
   {
     "mcpServers": {
       "memoryos": {
         "command": "node",
         "args": ["/absolute/path/to/mcp-server/dist/index.js"]
       }
     }
   }
   ```
3. **Available Tools:**
   Once connected, the AI can use tools like `search_notes`, `graph_query`, and `ask_memory` to interact with your data.

---

## 📜 License
MIT License - 2026 MemoryOS Team.
# MemoryOS
# MemoryOS
# MemoryOS-2
