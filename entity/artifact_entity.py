from dataclasses import dataclass
from typing import Any, List


@dataclass
class YoutubeLoaderArtifact:
    transcript: str
    video_id: str

@dataclass
class TextSplitterArtifact:
    chunks: List[Any]
    num_chunks: int

@dataclass
class EmbeddingModelArtifact:
    embedding_model: Any

@dataclass
class VectorStoreArtifact:
    vector_store: Any
    index_save_path: str

@dataclass
class RetrieverArtifact:
    retriever: Any
    search_type: str
    top_k: int

@dataclass
class RAGChainArtifact:
    answer: str
    video_id: str
    question: str