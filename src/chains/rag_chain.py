import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.prompts.templates import RAG_PROMPT
from src.logger import logging
from src.exception import MyException
from entity.config_entity import RAGChainConfig
from entity.artifact_entity import RetrieverArtifact, RAGChainArtifact


class RAGChain:
    def __init__(self, rag_chain_config: RAGChainConfig, retriever_artifact: RetrieverArtifact):
        try:
            logging.info(f"Initializing RAGChain with model={rag_chain_config.model_name}")
            self.rag_chain_config = rag_chain_config
            self.retriever = retriever_artifact.retriever
            self.llm = ChatOpenAI(model=rag_chain_config.model_name, temperature=rag_chain_config.temperature)
            self.parser = StrOutputParser()
            logging.info("RAGChain initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def _format_docs(self, docs):
        try:
            logging.info(f"Formatting {len(docs)} retrieved documents into context")
            return "\n\n".join(doc.page_content for doc in docs)
        except Exception as e:
            raise MyException(e, sys)

    def _build_chain(self):
        try:
            logging.info("Building RAG chain")
            prompt = PromptTemplate(
                template=RAG_PROMPT,
                input_variables=['context', 'question']
            )
            parallel_chain = RunnableParallel({
                'context': self.retriever | RunnableLambda(self._format_docs),
                'question': RunnablePassthrough()
            })
            chain = parallel_chain | prompt | self.llm | self.parser
            logging.info("RAG chain built successfully")
            return chain
        except Exception as e:
            raise MyException(e, sys)

    def initiate_rag_chain(self, question: str, video_id: str) -> RAGChainArtifact:
        try:
            logging.info(f"Invoking RAG chain with question: {question}")
            chain = self._build_chain()
            answer = chain.invoke(question)
            logging.info("RAG chain invoked successfully")

            rag_chain_artifact = RAGChainArtifact(
                answer=answer,
                video_id=video_id,
                question=question
            )

            logging.info(f"RAGChain artifact created for video_id: {video_id}")
            return rag_chain_artifact

        except Exception as e:
            raise MyException(e, sys)