import sys
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logger import logging
from src.exception import MyException
from entity.config_entity import TextSplitterConfig
from entity.artifact_entity import YoutubeLoaderArtifact, TextSplitterArtifact


class TextSplitter:
    def __init__(self, text_splitter_config: TextSplitterConfig):
        try:
            logging.info(f"Initializing TextSplitter with chunk_size={text_splitter_config.chunk_size}, chunk_overlap={text_splitter_config.chunk_overlap}")
            self.text_splitter_config = text_splitter_config
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=text_splitter_config.chunk_size,
                chunk_overlap=text_splitter_config.chunk_overlap
            )
            logging.info("TextSplitter initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def initiate_text_splitter(self, youtube_loader_artifact: YoutubeLoaderArtifact) -> TextSplitterArtifact:
        try:
            logging.info("Splitting transcript into chunks")
            chunks = self.splitter.create_documents([youtube_loader_artifact.transcript])
            logging.info(f"Transcript split into {len(chunks)} chunks successfully")

            text_splitter_artifact = TextSplitterArtifact(
                chunks=chunks,
                num_chunks=len(chunks)
            )

            logging.info(f"TextSplitter artifact: {text_splitter_artifact.num_chunks} chunks")
            return text_splitter_artifact

        except Exception as e:
            raise MyException(e, sys)