import sys
from src.logger import logging
from src.exception import MyException
from entity.config_entity import (
    YoutubeLoaderConfig,
    TextSplitterConfig,
    EmbeddingModelConfig,
    VectorStoreConfig,
    RetrieverConfig,
    RAGChainConfig
)
from entity.artifact_entity import (
    YoutubeLoaderArtifact,
    TextSplitterArtifact,
    EmbeddingModelArtifact,
    VectorStoreArtifact,
    RetrieverArtifact,
    RAGChainArtifact
)
from src.ingestion.youtube_loader import YoutubeLoader
from src.text_splitter.text_splitter import TextSplitter
from src.embeddings.embedding_model import EmbeddingModel
from src.vector_store.faiss_store import VectorStore
from src.retriever.retriever import Retriever
from src.chains.rag_chain import RAGChain


class RAGPipeline:
    def __init__(self):
        self.youtube_loader_config   = YoutubeLoaderConfig(video_id="")
        self.text_splitter_config    = TextSplitterConfig()
        self.embedding_model_config  = EmbeddingModelConfig()
        self.vector_store_config     = VectorStoreConfig()
        self.retriever_config        = RetrieverConfig()
        self.rag_chain_config        = RAGChainConfig()

    def start_youtube_loader(self, video_id: str) -> YoutubeLoaderArtifact:
        print("-" * 120)
        print("Starting Youtube Loader Component")
        logging.info("Entered start_youtube_loader method of RAGPipeline")
        try:
            self.youtube_loader_config = YoutubeLoaderConfig(video_id=video_id)
            youtube_loader = YoutubeLoader(youtube_loader_config=self.youtube_loader_config)
            youtube_loader_artifact = youtube_loader.initiate_youtube_loader()
            logging.info("Exited start_youtube_loader method of RAGPipeline")
            return youtube_loader_artifact
        except Exception as e:
            raise MyException(e, sys)

    def start_text_splitter(self, youtube_loader_artifact: YoutubeLoaderArtifact) -> TextSplitterArtifact:
        print("-" * 120)
        print("Starting Text Splitter Component")
        logging.info("Entered start_text_splitter method of RAGPipeline")
        try:
            text_splitter = TextSplitter(text_splitter_config=self.text_splitter_config)
            text_splitter_artifact = text_splitter.initiate_text_splitter(youtube_loader_artifact=youtube_loader_artifact)
            logging.info("Exited start_text_splitter method of RAGPipeline")
            return text_splitter_artifact
        except Exception as e:
            raise MyException(e, sys)

    def start_embedding_model(self) -> EmbeddingModelArtifact:
        print("-" * 120)
        print("Starting Embedding Model Component")
        logging.info("Entered start_embedding_model method of RAGPipeline")
        try:
            embedding_model = EmbeddingModel(embedding_model_config=self.embedding_model_config)
            embedding_model_artifact = embedding_model.initiate_embedding_model()
            logging.info("Exited start_embedding_model method of RAGPipeline")
            return embedding_model_artifact
        except Exception as e:
            raise MyException(e, sys)

    def start_vector_store(self, text_splitter_artifact: TextSplitterArtifact, embedding_model_artifact: EmbeddingModelArtifact) -> VectorStoreArtifact:
        print("-" * 120)
        print("Starting Vector Store Component")
        logging.info("Entered start_vector_store method of RAGPipeline")
        try:
            vector_store = VectorStore(
                vector_store_config=self.vector_store_config,
                embedding_model_artifact=embedding_model_artifact
            )
            vector_store_artifact = vector_store.initiate_vector_store(text_splitter_artifact=text_splitter_artifact)
            logging.info("Exited start_vector_store method of RAGPipeline")
            return vector_store_artifact
        except Exception as e:
            raise MyException(e, sys)

    def start_retriever(self, vector_store_artifact: VectorStoreArtifact) -> RetrieverArtifact:
        print("-" * 120)
        print("Starting Retriever Component")
        logging.info("Entered start_retriever method of RAGPipeline")
        try:
            retriever = Retriever(
                retriever_config=self.retriever_config,
                vector_store_artifact=vector_store_artifact
            )
            retriever_artifact = retriever.initiate_retriever()
            logging.info("Exited start_retriever method of RAGPipeline")
            return retriever_artifact
        except Exception as e:
            raise MyException(e, sys)

    def start_rag_chain(self, retriever_artifact: RetrieverArtifact, question: str, video_id: str) -> RAGChainArtifact:
        print("-" * 120)
        print("Starting RAG Chain Component")
        logging.info("Entered start_rag_chain method of RAGPipeline")
        try:
            rag_chain = RAGChain(
                rag_chain_config=self.rag_chain_config,
                retriever_artifact=retriever_artifact
            )
            rag_chain_artifact = rag_chain.initiate_rag_chain(question=question, video_id=video_id)
            logging.info("Exited start_rag_chain method of RAGPipeline")
            return rag_chain_artifact
        except Exception as e:
            raise MyException(e, sys)

    def run_pipeline(self, video_id: str, question: str) -> RAGChainArtifact:
        logging.info("=" * 120)
        logging.info("Starting RAG Pipeline")
        logging.info("=" * 120)
        try:
            youtube_loader_artifact  = self.start_youtube_loader(video_id=video_id)
            text_splitter_artifact   = self.start_text_splitter(youtube_loader_artifact=youtube_loader_artifact)
            embedding_model_artifact = self.start_embedding_model()
            vector_store_artifact    = self.start_vector_store(
                                            text_splitter_artifact=text_splitter_artifact,
                                            embedding_model_artifact=embedding_model_artifact
                                        )
            retriever_artifact       = self.start_retriever(vector_store_artifact=vector_store_artifact)
            rag_chain_artifact       = self.start_rag_chain(
                                            retriever_artifact=retriever_artifact,
                                            question=question,
                                            video_id=video_id
                                        )

            logging.info("=" * 120)
            logging.info("RAG Pipeline completed successfully")
            logging.info("=" * 120)
            return rag_chain_artifact

        except Exception as e:
            raise MyException(e, sys)