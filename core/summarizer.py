from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    llm = ChatGroq(model="openai/gpt-oss-20b",temperature=0.3)
    return llm

def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 10000,
        chunk_overlap = 1000
    )

    chunks = splitter.split_text(transcript)

    return chunks

def summarizer(transcript : str) -> str:
    chunks = split_transcript(transcript)

    model = get_llm()

    summary_prompt = ChatPromptTemplate.from_messages([
        ("system","""You are an expert video transcript summarizer.

Summarize the following portion of a video transcript clearly and accurately.

Instructions:

* Identify the main concepts and important information.
* Preserve important technical terms, explanations, examples, and facts.
* Remove unnecessary repetition, filler words, and informal conversation.
* Do not invent information or add details that are not present in the transcript.
* If the transcript contains unclear or incorrect wording, infer the intended meaning only when the surrounding context supports it.
* Write in clear, concise English.
* Organize the summary into meaningful bullet points when appropriate.
"""),
   ("human","{text}")
    ])

    summary_chain = summary_prompt | model | StrOutputParser()

    chunk_summary = []

    for chunk in chunks:
        text = summary_chain.invoke(chunk)
        chunk_summary.append(text)

    if(len(chunk_summary)==1):
        return chunk_summary[0]

    all_summary = "\n\n".join(chunk_summary)

    combine_prompt = ChatPromptTemplate.from_messages([
        ("system","""You are an expert summarizer.

You will receive partial summaries of different sections of a larger piece of content. 
Combine them into one coherent, accurate, and well-structured final summary in bullet points.

Instructions:
- Identify and preserve the main ideas and important information from all partial summaries.
- Organize the information in a logical and natural order.
- Remove duplicate information, unnecessary repetition, and irrelevant details.
- Maintain the original meaning and context of the provided summaries.
- Do not introduce information, assumptions, or conclusions that are not supported by the input.
- Ensure smooth transitions between topics and sections.
- Use clear, concise, and easy-to-understand language.
- Choose the most suitable format for the content, such as headings, paragraphs, or bullet points.
- Include important examples, facts, explanations, and details when relevant.
- Produce a complete summary that accurately represents all the provided partial summaries.
- Do not include any commentary about how the summary was generated.
- Do not add a concluding statement describing the summary itself.
- Return only the actual summary content.
"""),
("human","{text}")
    ])

    combine_chain = combine_prompt | model | StrOutputParser()

    final_summary = combine_chain.invoke(all_summary)

    return final_summary


def generate_summary_title(summary : str) -> str:
    model = get_llm()

    title_prompt = ChatPromptTemplate.from_messages([
        ("system","Generate a short, relevant title based on the summary. Maximum 8 words. Return only the title."),
        ("human","{text}")
    ])

    title_chain = title_prompt | model | StrOutputParser()

    return title_chain.invoke(summary).strip()