from backend.services.weaviate_store import weaviate_store
from backend.config import Config

# Check how many objects exist in the class
count = weaviate_store.client.query.aggregate(Config.WEAVIATE_CLASS_NAME).with_meta_count().do()
print(count)
