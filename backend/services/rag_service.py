from backend.services.weaviate_store import weaviate_store
from backend.services.gemini_llm import gemini_llm
from typing import List, Dict

class RAGService:
    def __init__(self):
        self.weaviate = weaviate_store
        self.llm = gemini_llm
    
    def generate_search_queries(self, chat_history: List[Dict]) -> List[str]:
        """Generate search queries from chat history"""
        # Extract key symptoms and complaints from chat
        queries = []
        
        for msg in chat_history:
            if msg['role'] == 'user':
                # Simple extraction - can be enhanced
                content = msg['content'].lower()
                queries.append(content)
        
        # Create a consolidated query
        all_user_messages = " ".join([msg['content'] for msg in chat_history if msg['role'] == 'user'])
        queries.append(all_user_messages)
        
        return queries
    
    def retrieve_context(self, queries: List[str], limit: int = 10) -> str:
        """Retrieve relevant context from Weaviate"""
        all_results = []
        
        for query in queries:
            results = self.weaviate.search(query, limit=limit)
            all_results.extend(results)
        
        # Deduplicate and format
        unique_contents = set()
        formatted_context = []
        
        for result in all_results:
            content = result.get('content', '')
            if content and content not in unique_contents:
                unique_contents.add(content)
                doc_type = result.get('type', 'unknown')
                category = result.get('category', '')
                formatted_context.append(f"[{doc_type.upper()} - {category}]\n{content}\n")
        
        return "\n".join(formatted_context)
    
    def get_rag_context(self, chat_history: List[Dict]) -> str:
        """Complete RAG pipeline: generate queries and retrieve context"""
        queries = self.generate_search_queries(chat_history)
        context = self.retrieve_context(queries)
        return context

# Singleton instance
rag_service = RAGService()