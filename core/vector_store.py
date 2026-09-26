from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

CHROMA_DIR = "vector_db"
COLLECTION_NAME = "video_transcript"

def get_embedding_model():
    model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    return model

def build_vector_store(transcript : str) -> Chroma:
    print("Building Vector Store")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 150
    )

    chunks = splitter.split_text(transcript)

    docs = []
    for i,chunk in enumerate(chunks):
        doc = Document(page_content=chunk , metadata= {"chunk_index" : i})
        docs.append(doc)

    embedding_model = get_embedding_model()

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        collection_name=COLLECTION_NAME,
        persist_directory=CHROMA_DIR
    )

    return vector_store

def get_retriever(vector_store : Chroma , k : int = 4):
    retriever = vector_store.as_retriever(
        search_type = "similarity", 
        search_kwargs = {"k" : k}
    )

    return retriever

