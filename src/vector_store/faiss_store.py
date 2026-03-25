import sys
import os
from langchain_community.vectorstores import FAISS
from src.logger import logging
from src.exception import MyException
from entity.config_entity import VectorStoreConfig
from entity.artifact_entity import EmbeddingModelArtifact, TextSplitterArtifact, VectorStoreArtifact


class VectorStore:
    def __init__(self, vector_store_config: VectorStoreConfig, embedding_model_artifact: EmbeddingModelArtifact):
        try:
            logging.info("Initializing VectorStore")
            self.vector_store_config = vector_store_config
            self.embedding_model = embedding_model_artifact.embedding_model
            self.store = None
            logging.info("VectorStore initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_vector_store(self, text_splitter_artifact: TextSplitterArtifact) -> VectorStoreArtifact:
        try:
            logging.info(f"Building FAISS vector store from {text_splitter_artifact.num_chunks} chunks")
            self.store = FAISS.from_documents(text_splitter_artifact.chunks, self.embedding_model)
            logging.info("FAISS vector store built successfully")

            os.makedirs(self.vector_store_config.index_save_path, exist_ok=True)
            self.store.save_local(self.vector_store_config.index_save_path)
            logging.info(f"FAISS vector store saved to {self.vector_store_config.index_save_path}")

            vector_store_artifact = VectorStoreArtifact(
                vector_store=self.store,
                index_save_path=self.vector_store_config.index_save_path
            )

            logging.info(f"VectorStore artifact: saved at {vector_store_artifact.index_save_path}")
            return vector_store_artifact

        except Exception as e:
            raise MyException(e, sys)