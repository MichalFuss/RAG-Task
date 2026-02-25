import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone

load_dotenv()

# הגדרות מפתחות
MY_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# 1. מודל ה-Embedding (המתרגם לווקטורים)
embed_model = CohereEmbedding(api_key=MY_API_KEY, model_name="embed-multilingual-v3.0")

# 2. חיבור ל-Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("agentic-docs-index")
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 3. טעינת המסמכים מהתיקייה
print("📂 טוען מסמכים מתיקיית agent_docs...")
data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent_docs")
documents = SimpleDirectoryReader(data_path, recursive=True, required_exts=[".md"]).load_data()

# 4. פירוק ל-Nodes (Chunking) - זה החלק החשוב במטלה!
print("✂️ מפרק מסמכים ל-Chunks ממוקדים...")
parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)

# 5. יצירת האינדקס ושמירה ב-Pinecone
print("🌲 מעלה ווקטורים ל-Pinecone... זה עשוי לקחת רגע")
index = VectorStoreIndex(
    nodes, 
    storage_context=storage_context,
    embed_model=embed_model
)

if __name__ == "__main__":
    print("✅ תהליך ה-Ingest הסתיים בהצלחה! הנתונים שמורים ב-Pinecone.")