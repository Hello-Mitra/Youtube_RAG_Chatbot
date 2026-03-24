RAG_PROMPT = """
You are a helpful assistant.
Answer ONLY from the provided transcript context.
If the context is insufficient, just say you don't know.

{context}
Question: {question}
"""

SUMMARY_PROMPT = """
Summarize the following content in a concise manner:
{content}
"""