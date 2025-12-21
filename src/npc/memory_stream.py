"""
NPC Memory Stream Module.
Handles the storage, retrieval (RAG), and consolidation of NPC memories.
Uses Vector Embeddings for semantic search.
"""

from __future__ import annotations
from typing import List, Generator
import os
import math
import uuid
from datetime import datetime
import google.generativeai as genai
import numpy as np
import json
from src.npc.schemas import MemoryObject, CognitiveState

# Initialize Gemini for Embeddings
GENAI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

class NPCMemoryStream:
    """
    Manages the 'Stream of Consciousness' for an NPC.
    """
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        from src.database import get_db
        self.db = get_db()
        self._ensure_npc_exists()

    def _ensure_npc_exists(self):
        """Ensure entity record exists."""
        try:
            self.db.execute(
                "INSERT OR IGNORE INTO entities (entity_id, entity_type, name, created_at) VALUES (?, ?, ?, ?)",
                (self.npc_id, 'npc', self.npc_id, int(datetime.now().timestamp()))
            )
        except Exception as e:
            print(f"[Memory Init Error] {e}")

    def _get_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text."""
        if not GENAI_API_KEY:
            # Fallback for offline/no-key mode: Random vector or keyword hash
            # This allows the system to run somewhat even if API fails
            import random
            return [random.random() for _ in range(768)]
            
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document",
                title="NPC Memory"
            )
            return result['embedding']
        except Exception as e:
            print(f"[Memory Error] Embedding failed: {e}")
            return [0.0] * 768

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-9)

    def add_memory(
        self, 
        state: CognitiveState, 
        content: str, 
        importance: int = 1, 
        m_type: str = "observation",
        timestamp: str = "Unknown",
        related_entities: List[str] = None
    ) -> MemoryObject:
        """Create and store a new memory in SQLite."""
        embedding = self._get_embedding(content)
        embedding_blob = json.dumps(embedding).encode('utf-8')
        
        try:
            # 1. Create global Event
            cursor = self.db.execute(
                """
                INSERT INTO events (event_type, game_timestamp, summary, importance, embedding)
                VALUES (?, ?, ?, ?, ?)
                """,
                (m_type, timestamp, content, importance, embedding_blob)
            )
            event_id = cursor.lastrowid
            
            # 2. Add as Knowledge for this NPC (source=witnessed)
            self.db.execute(
                """
                INSERT INTO npc_knowledge (npc_entity_id, event_id, learned_at, confidence, source_type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.npc_id, event_id, datetime.now().isoformat(), 1.0, 'witnessed')
            )
            
            # 3. Use memory object for immediate return
            memory = MemoryObject(
                memory_id=None, # knowledge_id not set yet, handled by retrieve next time
                event_id=event_id,
                timestamp=timestamp,
                content=content,
                importance_score=importance,
                type=m_type,
                embedding=embedding
            )
            
            # Update working memory in state (optional, or rely on retrieve)
            # state.memories.append(memory) 
            return memory
            
        except Exception as e:
            print(f"[Add Memory Error] {e}")
            return None

    def retrieve(self, state: CognitiveState, query: str, k: int = 5) -> List[MemoryObject]:
        """
        Retrieve relevant memories from SQLite using weighted scoring.
        """
        query_vec = self._get_embedding(query)
        
        # Fetch ALL knowledge for this NPC (filtering happens in python for now for simplicity w/ embeddings)
        # Optimization: Fetch only recent + high importance first?
        # For MVP, fetch last 100 items.
        
        rows = self.db.query(
            """
            SELECT k.knowledge_id, k.confidence, k.learned_at,
                   e.event_id, e.summary, e.importance, e.embedding, e.game_timestamp, e.event_type
            FROM npc_knowledge k
            JOIN events e ON k.event_id = e.event_id
            WHERE k.npc_entity_id = ?
            ORDER BY e.event_id DESC
            LIMIT 100
            """,
            (self.npc_id,)
        )
        
        scored_memories = []
        current_time_val = datetime.now().timestamp()
        
        for row in rows:
            # Parse embedding
            try:
                mem_vec = json.loads(row['embedding'])
            except:
                mem_vec = [0.0] * 768
                
            # 1. Relevance
            relevance = self._cosine_similarity(query_vec, mem_vec)
            
            # 2. Recency (Decay based on Event ID or timestamp)
            # Using simple index decay as proxy if timestamp parsing is hard
            # Ideally parse game_timestamp.
            recency = 1.0 # default high
            
            # 3. Importance
            importance = row['importance'] / 10.0
            
            # Total Score
            score = (0.5 * relevance) + (0.3 * importance) + (0.2 * recency)
            
            scored_memories.append((score, row))
            
        # Top K
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_k_rows = [x[1] for x in scored_memories[:k]]
        
        # Convert to Objects
        results = []
        for r in top_k_rows:
            results.append(MemoryObject(
                memory_id=r['knowledge_id'],
                event_id=r['event_id'],
                timestamp=r['game_timestamp'],
                content=r['summary'],
                importance_score=r['importance'],
                type=r['event_type']
            ))
            
        return results

    async def reflect(self, state: CognitiveState, llm_client) -> List[str]:
        """
        Periodically synthesize new high-level thoughts.
        """
        # Fetch recent observations (not reflections)
        rows = self.db.query(
            """
            SELECT e.summary 
            FROM npc_knowledge k
            JOIN events e ON k.event_id = e.event_id
            WHERE k.npc_entity_id = ? AND e.event_type = 'observation'
            ORDER BY k.knowledge_id DESC
            LIMIT 20
            """,
            (self.npc_id,)
        )
        
        if not rows:
            return []
            
        memory_text = "\n".join([f"- {r['summary']}" for r in rows])
        
        prompt = f"""
        Analyze the following recent memories of {state.profile.name}:
        {memory_text}
        
        Task: Identify 1-2 high-level insights or generalizations about the character's situation or relationships.
        Output format: Just the insights, one per line.
        """
        
        try:
             response = llm_client.generate_sync(prompt)
             insights = [line.strip("- ") for line in response.split("\n") if line.strip()]
             
             for insight in insights:
                 self.add_memory(state, insight, importance=8, m_type="reflection")
                 
             return insights
        except Exception as e:
            print(f"[Reflection Error] {e}")
            return []
