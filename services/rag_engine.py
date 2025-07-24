# services/rag_engine.py

import openai
import faiss
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#load the data
def load_chunks(filepath, chunk_size=500):
    with open(filepath, 'r') as f:
        text = f.read()
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

#embeddings
def get_embedding(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding, dtype="float32")

#index
def build_faiss_index(chunks):
    dim = len(get_embedding("test"))
    index = faiss.IndexFlatL2(dim)
    embeddings = [get_embedding(chunk) for chunk in chunks]
    index.add(np.array(embeddings))
    return index, chunks, embeddings

#retrive the context on the basis of similarity.
def retrieve_context(query, index, chunks, top_k=4):
    query_vector = get_embedding(query)
    D, I = index.search(np.array([query_vector]), top_k)
    return [chunks[i] for i in I[0]]
