import sys
from langchain_openai import OpenAIEmbeddings
from config.settings import settings
from src.logger import logging
from src.exception import MyException
from dotenv import load_dotenv

load_dotenv()


class EmbeddingModel:
    def __init__(self):
        try:
            logging.info(f"Initializing EmbeddingModel with model={settings.embedding_model}")
            self.model = OpenAIEmbeddings(model=settings.embedding_model)
            logging.info("EmbeddingModel initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def get(self):
        try:
            logging.info("Fetching embedding model")
            return self.model
        except Exception as e:
            raise MyException(e, sys)