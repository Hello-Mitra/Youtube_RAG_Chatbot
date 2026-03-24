import sys
from langchain_community.vectorstores import FAISS
from src.logger import logging
from src.exception import MyException


class VectorStore:
    def __init__(self, embedding_model):
        try:
            logging.info("Initializing VectorStore")
            self.embedding_model = embedding_model
            self.store = None
            logging.info("VectorStore initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def build(self, chunks):
        try:
            logging.info(f"Building FAISS vector store from {len(chunks)} chunks")
            self.store = FAISS.from_documents(chunks, self.embedding_model)
            logging.info("FAISS vector store built successfully")
            return self.store
        except Exception as e:
            raise MyException(e, sys)

    def save(self, path: str):
        try:
            logging.info(f"Saving FAISS vector store to path: {path}")
            self.store.save_local(path)
            logging.info(f"FAISS vector store saved successfully to {path}")
        except Exception as e:
            raise MyException(e, sys)

    def load(self, path: str):
        try:
            logging.info(f"Loading FAISS vector store from path: {path}")
            self.store = FAISS.load_local(path, self.embedding_model)
            logging.info(f"FAISS vector store loaded successfully from {path}")
            return self.store
        except Exception as e:
            raise MyException(e, sys)