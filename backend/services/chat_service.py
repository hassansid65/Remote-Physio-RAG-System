from typing import Dict, List
from backend.services.gemini_llm import gemini_llm
from backend.services.rag_service import rag_service
from backend.prompts.greeting_prompt import get_greeting
from backend.prompts.info_gathering_prompt import get_info_gathering_prompt
from backend.prompts.summary_prompt import get_summary_prompt
from backend.models.chat import ChatMessage
from datetime import datetime

class ChatService:
    def __init__(self):
        self.llm = gemini_llm
        self.rag = rag_service
    
    def get_greeting_message(self) -> str:
        """Return initial greeting"""
        return get_greeting()
    
    def format_chat_history(self, messages: List[ChatMessage]) -> str:
        """Format chat messages for prompts"""
        formatted = []
        for msg in messages:
            formatted.append(f"{msg.role.capitalize()}: {msg.content}")
        return "\n".join(formatted)
    
    def process_message(self, message: str, chat_history: List[ChatMessage]) -> Dict:
        """Process user message and return response"""
        
        # Check if we have enough information (basic heuristic)
        user_messages = [msg for msg in chat_history if msg.role == 'user']
        
        # If we have at least 5 exchanges, check if info gathering is complete
        if len(user_messages) >= 5:
            # Prepare prompt to check completeness
            chat_text = self.format_chat_history(chat_history)
            prompt = get_info_gathering_prompt(chat_text)
            
            response = self.llm.generate(prompt)
            
            if "INFORMATION_COMPLETE" in response:
                # Generate summary
                return self.generate_summary(chat_history)
        
        # Continue information gathering
        chat_text = self.format_chat_history(chat_history)
        prompt = get_info_gathering_prompt(chat_text)
        
        response = self.llm.generate(prompt)
        
        # Check again if complete
        if "INFORMATION_COMPLETE" in response:
            return self.generate_summary(chat_history)
        
        return {
            "response": response,
            "is_summary": False
        }
    
    def generate_summary(self, chat_history: List[ChatMessage]) -> Dict:
        """Generate final summary using RAG"""
        
        # Convert chat history to dict format for RAG
        chat_dicts = [{"role": msg.role, "content": msg.content} for msg in chat_history]
        
        # Get RAG context
        rag_context = self.rag.get_rag_context(chat_dicts)
        
        # Format chat transcript
        chat_transcript = self.format_chat_history(chat_history)
        
        # Generate summary
        prompt = get_summary_prompt(chat_transcript, rag_context)
        summary = self.llm.generate(prompt)
        
        return {
            "response": summary,
            "is_summary": True
        }

# Singleton instance
chat_service = ChatService()