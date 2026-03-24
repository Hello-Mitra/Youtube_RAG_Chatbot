import sys
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.prompts.templates import RAG_PROMPT
from src.logger import logging
from src.exception import MyException
from config.settings import settings


class RAGChain:
    def __init__(self, retriever):
        try:
            logging.info(f"Initializing RAGChain with model={settings.model_name}")
            self.retriever = retriever
            self.llm = ChatOpenAI(model=settings.model_name, temperature=0.2)
            self.parser = StrOutputParser()
            logging.info("RAGChain initialized successfully")
        except Exception as e:
            raise MyException(e, sys)

    def format_docs(self, docs):
        try:
            logging.info(f"Formatting {len(docs)} retrieved documents into context")
            context = "\n\n".join(doc.page_content for doc in docs)
            logging.info("Documents formatted successfully")
            return context
        except Exception as e:
            raise MyException(e, sys)

    def build(self):
        try:
            logging.info("Building RAG chain")
            prompt = PromptTemplate(
                template=RAG_PROMPT,
                input_variables=['context', 'question']
            )
            parallel_chain = RunnableParallel({
                'context': self.retriever | RunnableLambda(self.format_docs),
                'question': RunnablePassthrough()
            })
            chain = parallel_chain | prompt | self.llm | self.parser
            logging.info("RAG chain built successfully")
            return chain
        except Exception as e:
            raise MyException(e, sys)

    def invoke(self, question: str):
        try:
            logging.info(f"Invoking RAG chain with question: {question}")
            chain = self.build()
            result = chain.invoke(question)
            logging.info("RAG chain invoked successfully")
            return result
        except Exception as e:
            raise MyException(e, sys)