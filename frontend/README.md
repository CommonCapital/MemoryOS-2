# MemoryOS-2: Agent Health & Monitoring Dashboard

This is the control plane for the **Enterprise Memory Layer**. It provides real-time visualization and management of the tiered memory systems used by your AI agents.

## 📊 Dashboard Modules

### 1. Vector Cluster Map (UMAP)
A high-dimensional projection of the **Abstract Vector Index**. Monitor semantic "islands" of enterprise knowledge and identify areas of contextual drift.

### 2. Knowledge Graph Explorer
Visualize the relationships between high-value entities. React Flow-based canvas with support for:
- Degree-based node sizing.
- Confidence-aware relation translucency.
- Retrieval Path Inspection (X-ray view of agent queries).

### 3. Memory Health & VFS Browser
- **VFS Exploration:** Browse the PostgreSQL-backed Virtual File System.
- **Relational Integrity:** Monitor SQL ground truth health and token distribution.
- **Batch Operations:** Trigger re-indexing or re-extraction across millions of documents.

## 🚀 Development

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to access the monitoring interface.
