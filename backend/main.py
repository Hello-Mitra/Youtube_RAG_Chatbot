from dotenv import load_dotenv
from fastapi import FastAPI
from backend.routes.chat import router
from src.logger import logging
from fastapi.middleware.cors import CORSMiddleware

load_dotenv() 

logging.info("Starting GenAI RAG API")

app = FastAPI(title="GenAI RAG API")
app.include_router(router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

logging.info("Routes registered successfully")