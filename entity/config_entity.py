from dataclasses import dataclass
from config.settings import settings


@dataclass
class YoutubeLoaderConfig:
    video_id: str

@dataclass
class TextSplitterConfig:
    chunk_size: int = settings.chunk_size
    chunk_overlap: int = settings.chunk_overlap

@dataclass
class EmbeddingModelConfig:
    embedding_model: str = settings.embedding_model

@dataclass
class VectorStoreConfig:
    index_save_path: str = settings.faiss_index_path

@dataclass
class RetrieverConfig:
    search_type: str = "similarity"
    top_k: int = settings.top_k

@dataclass
class RAGChainConfig:
    model_name: str = settings.model_name
    temperature: float = 0.2