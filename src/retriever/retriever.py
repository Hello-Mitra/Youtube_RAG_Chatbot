import sys
from src.logger import logging
from src.exception import MyException
from langchain_community.vectorstores import FAISS

class Retriever:
    def __init__(self, vector_store: FAISS, search_type: str = "similarity", top_k: int = 4):
        self.vector_store = vector_store
        self.search_type = search_type
        self.top_k = top_k

    def get_retriever(self):
        try:
            logging.info(f"Building retriever with search_type={self.search_type}, top_k={self.top_k}")
            retriever = self.vector_store.as_retriever(
                search_type=self.search_type,
                search_kwargs={"k": self.top_k}
            )
            logging.info("Retriever built successfully")
            return retriever
        except Exception as e:
            raise MyException(e, sys)