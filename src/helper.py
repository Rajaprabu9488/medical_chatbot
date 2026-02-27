from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
import joblib


faiss_db=None
llm=None 

def rag_initial_loader():
    global faiss_db,llm
    # load embeddings 
    embeddings=joblib.load("C:/Users/My-PC/OneDrive/Desktop/medical-chatbot/saved_files/embedding_BAAI.joblib")

    # load faiss database
    faiss_db = FAISS.load_local(
    "C:/Users/My-PC/OneDrive/Desktop/medical-chatbot/vector_DB/medical_pdf_storage_BAAI",
    embeddings,
    allow_dangerous_deserialization=True
    )

    # set llama3.2 as LLM model and set temperture as 0 in ollama
    # ollama is platform to run the large language model in local machine
    # llama 3.2 is the lightweight and less capable model. it works on cpu (no GPU required) and it is a 2 billion to 3 billion parameter
    
    llm = Ollama(
        model="llama3.2",
        temperature=0
    )


def rag_pipeline(question):
    
    
    # perform similarity search with k = 3 sentences
    # the search is based ok cosine similarity
    results = faiss_db.similarity_search(question, k=3)

    # convert the vectors to string format
    context ="\n\n".join([i.page_content for i in results]) 

    # rag prompt that pass the string as parameter to llama model
    rag_prompt = f"""
    You are a medical assistance chatbot and advisor designed to provide general health information in a clear, calm, and responsible manner.


    Your tone should be professional, reassuring, and easy to understand for non-medical users.


    Answer ONLY using the context below.
    Do NOT use outside or external knowledge.
    If answer is missing, tell that content is not related to medical field.


    context:
    {context}

    Question:
    {question}

    Answer:
    """
    
    # LLM query response generating

    response = llm.invoke(rag_prompt)
    return response
