from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    return llm

def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 15000,
        chunk_overlap = 1500
    )

    chunks = splitter.split_text(transcript)

    return chunks

def get_notes(transcript : str) -> str:
    chunks = split_transcript(transcript)

    model = get_llm()

    notes_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert technical note-taking assistant.

Create detailed, accurate, and well-structured notes from the provided portion
of a video transcript.

Your goal is to help someone understand and revise the content without
needing to watch the entire video again.

Instructions:

1. Identify the main topics and subtopics discussed.
2. Explain important concepts clearly and concisely.
3. Preserve important technical terms, definitions, facts, examples, and explanations.
4. Include step-by-step processes when they are present in the transcript.
5. Use meaningful headings and subheadings to organize the notes.
6. Use bullet points and numbered lists where appropriate.
7. Highlight important distinctions, advantages, disadvantages, and comparisons
   when explicitly mentioned.
8. Preserve formulas, code-related concepts, and technical details when present.
9. Remove filler words, repetition, greetings, and irrelevant conversation.
10. Do not invent information or add outside knowledge.
11. Do not omit important details merely to make the notes shorter.
12. If a statement in the transcript is unclear, retain the uncertainty rather
    than confidently guessing.
13. Write in clear, readable English.

The output should contain detailed notes, not a short summary.
"""),
    ("human", "{text}")
])

    notes_chain = notes_prompt | model | StrOutputParser()

    chunk_notes = []

    for chunk in chunks:
        text = notes_chain.invoke(chunk)
        chunk_notes.append(text)

    if(len(chunk_notes)==1):
        return chunk_notes[0]

    complete_notes = "\n\n".join(chunk_notes)

    combine_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert editor who combines notes from different
sections of a video into one complete and well-organized set of notes.

You will receive notes generated from multiple sections of the same video.

Instructions:

1. Combine all important information into a coherent set of notes.
2. Organize the content in the logical order in which it was presented.
3. Use clear headings and subheadings.
4. Remove duplicate information without losing meaningful details.
5. Preserve important definitions, explanations, examples, technical terms, and step-by-step processes.
6. Maintain relationships between concepts and their context.
7. Ensure that information from different sections is connected naturally.
8. Do not introduce information, assumptions, or conclusions that are not supported by the provided notes.
9. Do not unnecessarily shorten the notes.
10. Do not claim that the notes contain the complete or full content unless this can be reliably established from the input.
11. Remove unnecessary repetition, but retain repeated information when it reinforces an important concept or ratio.
12. Make the final notes useful for learning, revision, and future reference.
13. Use Markdown formatting, bullet points, and numbered lists where appropriate.
- Do not include any commentary about how the notes were generated.
- Do not add a concluding statement describing the notes itself.
- Return only the actual notes content.
- Dont give conclusion lines summarizing notes content in the end.
- Dont include End of Notes section or anyhing like that.

FORMATTING RULES:
- Use Markdown for headings, bullets, and lists.
- For inline formulas, use $...$.
  Example: $F = ma$
- For standalone formulas, use $$...$$.
  Example:
  $$F = ma$$
- Do NOT place formulas inside code blocks.
- Keep all LaTeX commands inside $...$ or $$...$$.

Produce only the final, well-structured notes.

"""),
    ("human", "{text}")
])

    combine_chain = combine_prompt | model | StrOutputParser()

    final_notes = combine_chain.invoke(complete_notes)

    return final_notes


def generate_notes_title(notes : str) -> str:
    model = get_llm()

    title_prompt = ChatPromptTemplate.from_messages([
        ("system","Generate a short, relevant title based on the notes. Maximum 8 words. Return only the title."),
        ("human","{text}")
    ])

    title_chain = title_prompt | model | StrOutputParser()

    return title_chain.invoke(notes).strip()