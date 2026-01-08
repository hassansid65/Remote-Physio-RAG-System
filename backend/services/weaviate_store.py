import weaviate
from typing import List, Dict
from backend.config import Config
from backend.services.biobert_embedder import biobert_embedder

class WeaviateStore:
    def __init__(self):
        # Initialize Weaviate client (v3 syntax)
        self.client = weaviate.Client(
            url=Config.WEAVIATE_URL,
            auth_client_secret=weaviate.AuthApiKey(api_key=Config.WEAVIATE_API_KEY)
            if Config.WEAVIATE_API_KEY else None
        )

        # Ensure schema exists
        self._create_schema()

    def _create_schema(self):
        """Create Weaviate schema if it doesn't exist."""
        existing_classes = [cls["class"] for cls in self.client.schema.get()["classes"]]
        if Config.WEAVIATE_CLASS_NAME not in existing_classes:
            schema = {
                "class": Config.WEAVIATE_CLASS_NAME,
                "description": "Physiotherapy knowledge base including assessments and exercises",
                "vectorizer": "none",  # We provide our own vectors
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "The actual content text"
                    },
                    {
                        "name": "type",
                        "dataType": ["string"],
                        "description": "Type: assessment or exercise"
                    },
                    {
                        "name": "category",
                        "dataType": ["string"],
                        "description": "Category or condition name"
                    }
                ]
            }
            self.client.schema.create_class(schema)

    def add_document(self, content: str, doc_type: str, category: str):
        """Add a single document with BioBERT embedding."""
        embedding = biobert_embedder.get_embedding(content)

        data_object = {
            "content": content,
            "type": doc_type,
            "category": category
        }

        self.client.data_object.create(
            data_object=data_object,
            class_name=Config.WEAVIATE_CLASS_NAME,
            vector=embedding
        )

    def add_batch_documents(self, documents: List[Dict]):
        """Add multiple documents in batch."""
        with self.client.batch as batch:
            batch.batch_size = 20  # optional: adjust batch size
            for doc in documents:
                embedding = biobert_embedder.get_embedding(doc['content'])
                data_object = {
                    "content": doc['content'],
                    "type": doc['type'],
                    "category": doc.get('category', '')
                }
                batch.add_data_object(
                    data_object=data_object,
                    class_name=Config.WEAVIATE_CLASS_NAME,
                    vector=embedding
                )

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant documents using BioBERT embedding (with debug logs)."""
        # Generate embedding for query
        query_embedding = biobert_embedder.get_embedding(query)

        # 🧪 Debug logs
        print("\n" + "=" * 60)
        print(f"[RAG DEBUG] Query: {query}")
        print(f"[RAG DEBUG] Query embedding shape: {len(query_embedding)}")

        # Perform semantic search
        result = (
            self.client.query.get(Config.WEAVIATE_CLASS_NAME, ["content", "type", "category"])
            .with_near_vector({"vector": query_embedding})
            .with_limit(limit)
            .with_additional(["distance"])   # Optional: include similarity score
            .do()
        )

        # Extract and debug results
        if result and "data" in result and "Get" in result["data"]:
            hits = result["data"]["Get"].get(Config.WEAVIATE_CLASS_NAME, [])
            print(f"[RAG DEBUG] Retrieved results: {len(hits)}")
            if hits:
                print("[RAG DEBUG] Top result snippet:")
                print(hits[0].get("content", "")[:200] + "...")
                print(f"[RAG DEBUG] Distance: {hits[0].get('_additional', {}).get('distance', 'N/A')}")
            print("=" * 60 + "\n")
            return hits

        # Fallback if no results
        print("[RAG DEBUG] No results found or unexpected response structure.")
        print("=" * 60 + "\n")
        return []

# Singleton instance
weaviate_store = WeaviateStore()
