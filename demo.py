from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Step 1a - Indexing (Document Ingestion)
video_id = "Y0SbCp4fUvA" # only the ID, not full URL
try:
    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    # try English first, fall back to any available language and translate
    try:
        transcript = transcripts.find_transcript(['en'])
    except:
        transcript = transcripts.find_generated_transcript(['bn', 'hi', 'en']) # try these languages
        transcript = transcript.translate('en') # translate to English
    
    data = transcript.fetch()

    # Flatten it to plain text
    transcript = " ".join(chunk["text"] for chunk in data)
    print(transcript)

except TranscriptsDisabled:
    print("No captions available for this video.")


# Step 1b - Indexing (Text Splitting)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])

# Step 1c & 1d - Indexing (Embedding Generation and Storing in Vector Store)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_documents(chunks, embeddings)

# Step 2 - Retrieval
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Step 3 - Augmentation
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables = ['context', 'question']
)

question = "Does this video talk about FastAPI?"
retrieved_docs = retriever.invoke(question)

context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

final_prompt = prompt.invoke({"context": context_text, "question": question})

# Step 4 - Generation
answer = llm.invoke(final_prompt)
print(answer.content)