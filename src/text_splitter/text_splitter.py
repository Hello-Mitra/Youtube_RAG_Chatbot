import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings
from src.logger import logging
from src.exception import MyException


class TextSplitter:
    def __init__(self):
        try:
            logging.info(f"Initializing TextSplitter with chunk_size={settings.chunk_size}, chunk_overlap={settings.chunk_overlap}")
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
            logging.info("TextSplitter initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def split(self, text: str):
        try:
            logging.info("Splitting text into chunks")
            chunks = self.splitter.create_documents([text])
            logging.info(f"Text split into {len(chunks)} chunks successfully")
            return chunks
        except Exception as e:
            raise MyException(e, sys)