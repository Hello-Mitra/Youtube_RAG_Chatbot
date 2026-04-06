import sys
from src.logger import logging
from src.exception import MyException
from entity.config_entity import RetrieverConfig
from entity.artifact_entity import VectorStoreArtifact, RetrieverArtifact


class Retriever:
    def __init__(self, retriever_config: RetrieverConfig, vector_store_artifact: VectorStoreArtifact):
        try:
            logging.info(f"Initializing Retriever with search_type={retriever_config.search_type}, top_k={retriever_config.top_k}")
            self.retriever_config = retriever_config
            self.vector_store = vector_store_artifact.vector_store
            logging.info("Retriever initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_retriever(self) -> RetrieverArtifact:
        try:
            logging.info("Building retriever")
            retriever = self.vector_store.as_retriever(
                search_type=self.retriever_config.search_type,
                search_kwargs={"k": self.retriever_config.top_k}
            )
            logging.info("Retriever built successfully")

            retriever_artifact = RetrieverArtifact(
                retriever=retriever,
                search_type=self.retriever_config.search_type,
                top_k=self.retriever_config.top_k
            )

            logging.info(f"Retriever artifact: search_type={retriever_artifact.search_type}, top_k={retriever_artifact.top_k}")
            return retriever_artifact

        except Exception as e:
            raise MyException(e, sys)