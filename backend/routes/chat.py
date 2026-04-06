import sys
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from functools import lru_cache
from src.logger import logging
from src.exception import MyException
from pipeline.rag_pipeline import RAGPipeline

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    video_id: str

@lru_cache(maxsize=5)
def build_pipeline(video_id: str):
    try:
        logging.info(f"Building pipeline for video_id: {video_id}")
        pipeline = RAGPipeline()

        # run all steps except rag_chain (cache the retriever)
        youtube_loader_artifact  = pipeline.start_youtube_loader(video_id=video_id)
        text_splitter_artifact   = pipeline.start_text_splitter(youtube_loader_artifact=youtube_loader_artifact)
        embedding_model_artifact = pipeline.start_embedding_model()
        vector_store_artifact    = pipeline.start_vector_store(
                                        text_splitter_artifact=text_splitter_artifact,
                                        embedding_model_artifact=embedding_model_artifact
                                    )
        retriever_artifact       = pipeline.start_retriever(vector_store_artifact=vector_store_artifact)

        logging.info(f"Pipeline built and cached for video_id: {video_id}")
        return retriever_artifact

    except MyException as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise MyException(e, sys)

@router.post("/chat")
def chat(request: QueryRequest):
    try:
        logging.info(f"Received request - video_id: {request.video_id}, question: {request.question}")

        pipeline = RAGPipeline()

        # fetch retriever from cache
        retriever_artifact = build_pipeline(request.video_id)

        # only rag_chain runs every time
        rag_chain_artifact = pipeline.start_rag_chain(
            retriever_artifact=retriever_artifact,
            question=request.question,
            video_id=request.video_id
        )

        logging.info("Request processed successfully")
        return {"answer": rag_chain_artifact.answer}

    except MyException as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise MyException(e, sys)