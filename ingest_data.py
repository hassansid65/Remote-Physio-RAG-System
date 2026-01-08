import json
from backend.services.weaviate_store import weaviate_store

# Load JSON data
with open("data/assessments/assessment_info_converted_v2.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

documents = []

# Convert raw_data items into dicts
for item in raw_data:
    if isinstance(item, str):
        # If it's a string, wrap it in a dict
        documents.append({
            "content": item,
            "type": "exercise",
            "category": "general"
        })
    elif isinstance(item, dict):
        # If it's already a dict, just use it (ensure 'content' key exists)
        if "content" in item:
            documents.append(item)
        else:
            print(f"⚠️ Skipping invalid item: {item}")
    else:
        print(f"⚠️ Skipping unknown item type: {item}")

print(f"📚 Loading {len(documents)} physiotherapy documents...")

# Add documents to Weaviate
weaviate_store.add_batch_documents(documents)

print("✅ Done! All documents inserted successfully into Weaviate.")
