from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from core.vector_store import build_vector_store,get_retriever
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    llm = ChatGoogleGenerativeAI(model = "gemini-3.5-flash-lite")

    return llm

def format_docs(docs : list):
    return "\n\n".join([doc.page_content for doc in docs])

def build_rag_chain(transcript : str):
    vector_store = build_vector_store(transcript)
    retriever = get_retriever(vector_store,k=5)
    model = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system","""You are an expert video assistant.

Answer the user's question based ONLY on
the video transcript context provided below.

Answer the user's question directly and concisely using the provided context.
Do not begin with phrases such as "Based on the video transcript", "According to the transcript", or "The video states".
Do not mention the retrieval process or the context.

If the answer is not found in the context,
say:

"I could not find this information in
the video transcript."

Do not invent information or use outside
knowledge to answer the question.

Be clear, accurate, and concise.

Video transcript context:
{context}
"""),
("human","{question}")
    ])

    #LCEL Pipeline

    rag_chain = (
        {"context" : retriever | RunnableLambda(format_docs),
        "question" : RunnablePassthrough() }
        | prompt | model | StrOutputParser() 
    )

    return rag_chain

def ask_question(rag_chain, question:str) -> str:
    print(f"Question : {question}")

    answer = rag_chain.invoke(question)

    print(f"Answer : {answer}")

    return answer