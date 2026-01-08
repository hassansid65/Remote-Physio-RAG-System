import google.generativeai as genai
from backend.config import Config

class GeminiLLM:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate(self, prompt: str) -> str:
        """Generate response from Gemini"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def chat_generate(self, messages: list) -> str:
        """Generate response based on chat history"""
        # Format messages into a prompt
        formatted_prompt = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in messages
        ])
        
        response = self.model.generate_content(formatted_prompt)
        return response.text

# Singleton instance
gemini_llm = GeminiLLM()