import json
import os
from datetime import datetime
import re

# Simple JSON-based Long-term Memory
# We will store facts in a simple list and use keyword matching for retrieval
# A full Vector DB (Chromadb/Pinecone) requires heavy dependencies

MEMORY_FILE = "materials/long_term_memory.json"

class MemoryModule:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self.memories = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_memory(self):
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2)

    def add_memory(self, text, tags=None):
        """Add a new fact to memory"""
        memory_item = {
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or []
        }
        self.memories.append(memory_item)
        self.save_memory()
        print(f"[Memory] Added: {text}")
        return "Memory stored."

    def search_memory(self, query):
        """Search memory for relevant facts"""
        query_words = set(re.findall(r'\w+', query.lower()))
        results = []
        
        for mem in self.memories:
            mem_text = mem['text'].lower()
            score = 0
            for word in query_words:
                if word in mem_text:
                    score += 1
            
            if score > 0:
                results.append((score, mem['text']))
        
        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:3]] # Return top 3 match

# Global Instance
_memory_module = None

def get_memory_module():
    global _memory_module
    if _memory_module is None:
        _memory_module = MemoryModule()
    return _memory_module

def remember_fact(fact):
    mem = get_memory_module()
    return mem.add_memory(fact)

def recall_fact(query):
    mem = get_memory_module()
    results = mem.search_memory(query)
    if results:
        return "Here is what I remember:\n" + "\n".join(f"- {r}" for r in results)
    else:
        return "I don't recall anything about that."
