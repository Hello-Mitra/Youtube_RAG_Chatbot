import sys
from langchain_openai import OpenAIEmbeddings
from src.logger import logging
from src.exception import MyException
from entity.config_entity import EmbeddingModelConfig
from entity.artifact_entity import EmbeddingModelArtifact


class EmbeddingModel:
    def __init__(self, embedding_model_config: EmbeddingModelConfig):
        try:
            logging.info(f"Initializing EmbeddingModel with model={embedding_model_config.embedding_model}")
            self.embedding_model_config = embedding_model_config
            self.model = OpenAIEmbeddings(model=embedding_model_config.embedding_model)
            logging.info("EmbeddingModel initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_embedding_model(self) -> EmbeddingModelArtifact:
        try:
            logging.info("Fetching embedding model")

            embedding_model_artifact = EmbeddingModelArtifact(
                embedding_model=self.model
            )

            logging.info("EmbeddingModel artifact created successfully")
            return embedding_model_artifact

        except Exception as e:
            raise MyException(e, sys)