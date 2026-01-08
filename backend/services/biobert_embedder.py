from transformers import AutoTokenizer, AutoModel
import torch
from typing import List
from backend.config import Config

class BioBERTEmbedder:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(Config.BIOBERT_MODEL)
        self.model = AutoModel.from_pretrained(Config.BIOBERT_MODEL)
        self.model.eval()
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate BioBERT embedding for a single text"""
        inputs = self.tokenizer(text, return_tensors="pt", 
                               padding=True, truncation=True, 
                               max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use mean pooling of last hidden state
            embeddings = outputs.last_hidden_state.mean(dim=1)
            
        return embeddings[0].tolist()
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate BioBERT embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embeddings.append(self.get_embedding(text))
        return embeddings

# Singleton instance
biobert_embedder = BioBERTEmbedder()