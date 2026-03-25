import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from functools import lru_cache
from src.logger import logging
from src.exception import MyException
from src.ingestion.youtube_loader import YoutubeLoader
from src.text_splitter.text_splitter import TextSplitter
from src.embeddings.embedding_model import EmbeddingModel
from src.vector_store.faiss_store import VectorStore
from src.retriever.retriever import Retriever
from src.chains.rag_chain import RAGChain

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    video_id: str

@lru_cache(maxsize=5)   # caches last 5 videos
def build_pipeline(video_id: str):
    try:
        logging.info(f"Building pipeline for video_id: {video_id}")

        # Step 1a - Load transcript
        loader = YoutubeLoader()
        transcript = loader.load(video_id)

        # Step 1b - Split text
        splitter = TextSplitter()
        chunks = splitter.split(transcript)

        # Step 1c & 1d - Embeddings + Vector Store
        embedding_model = EmbeddingModel().get()
        vector_store = VectorStore(embedding_model)
        store = vector_store.build(chunks)

        # Step 2 - Retriever
        retriever = Retriever(vector_store=store).get_retriever()

        logging.info(f"Pipeline built and cached for video_id: {video_id}")
        return retriever

    except Exception as e:
        raise MyException(e, sys)

@router.post("/chat")
def chat(request: QueryRequest):
    try:
        logging.info(f"Received request - video_id: {request.video_id}, question: {request.question}")

        # fetch from cache if same video, else rebuild
        retriever = build_pipeline(request.video_id)

        # Step 3 - RAG Chain
        rag_chain = RAGChain(retriever=retriever)
        result = rag_chain.invoke(request.question)

        logging.info("Request processed successfully")
        return {"answer": result}

    except MyException as e:
        logging.error(f"MyException occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise MyException(e, sys)