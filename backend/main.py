import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from backend.routes.chat import router
from src.logger import logging

load_dotenv() 

logging.info("Starting GenAI RAG API")

app = FastAPI(title="GenAI RAG API")
app.include_router(router, prefix="/api")

logging.info("Routes registered successfully")