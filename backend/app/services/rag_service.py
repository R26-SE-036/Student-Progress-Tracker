import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Load environment variables
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(base_dir, '.env')
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini Embeddings (Converts text to vectors)
try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
except Exception as e:
    print(f"⚠️ Embeddings initialization failed: {e}")
    embeddings = None

# Paths for data and vector database
data_dir = os.path.join(base_dir, "data")
db_dir = os.path.join(base_dir, "chroma_db")

def initialize_knowledge_base():
    """Reads text files from the data folder and stores them in ChromaDB"""
    print("\n⏳ Initializing Vector Database from University Syllabus Notes...")
    documents = []
    
    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    documents.append(Document(page_content=text, metadata={"source": filename}))
    
    if not documents:
        print("⚠️ No syllabus documents found in the 'data' folder.")
        return None

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    # Create and save the Chroma Vector DB
    if embeddings:
        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_dir)
        print("✅ Vector Database (ChromaDB) Initialized Successfully!\n")
        return vectorstore
    return None

def get_vectorstore():
    """Returns the existing ChromaDB or creates a new one if it doesn't exist"""
    if os.path.exists(db_dir) and os.listdir(db_dir):
        return Chroma(persist_directory=db_dir, embedding_function=embeddings)
    else:
        return initialize_knowledge_base()

def retrieve_context(query: str, k=2):
    """Searches the Vector DB for notes related to the student's error"""
    try:
        vectorstore = get_vectorstore()
        if not vectorstore:
            return "No specific university guidelines available."
        
        # Retrieve the top 'k' most relevant chunks
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(query)
        
        context = "\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        print(f"⚠️ Retrieval Error: {e}")
        return "No specific university guidelines available."