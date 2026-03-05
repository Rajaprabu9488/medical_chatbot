from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
import joblib

from helper import content_retriver,json_uploader


faiss_db_1 = None
faiss_db_2 = None
llm=None 

def rag_initial_loader():
    global faiss_db_1,faiss_db_2,llm

    # load embeddings 
    embeddings_sentence_transformer = joblib.load("C:/Users/My-PC/OneDrive/Desktop/medical-chatbot/saved_files/embedding_sentence_transformers.joblib")
    embeddings_BAAI = joblib.load("C:/Users/My-PC/OneDrive/Desktop/medical-chatbot/saved_files/embedding_BAAI.joblib")

    # load faiss database
    faiss_db_1 = FAISS.load_local(
    "C:/Users/My-PC/OneDrive/Desktop/medical-chatbot/vector_DB/medical_pdf_storage_sentence_transformer",
    embeddings_sentence_transformer,
    allow_dangerous_deserialization=True
    )

    faiss_db_2 = FAISS.load_local(
    "C:/Users/My-PC/OneDrive/Desktop/medical-chatbot/vector_DB/medical_pdf_storage_BAAI",
    embeddings_BAAI,
    allow_dangerous_deserialization=True
    )
    # set llama3.2 as LLM model and set temperture as 0 in ollama
    # ollama is platform to run the large language model in local machine
    # llama 3.2 is the lightweight and less capable model. it works on cpu (no GPU required) and it is a 2 billion to 3 billion parameter
    
    llm = Ollama(
        model="llama3.2",
        temperature=0,
        keep_alive=-1
    )


def rag_pipeline(question):
    
    # perform similarity search with k = 3 sentences
    # the search is based ok cosine similarity
    results_1 = faiss_db_1.similarity_search_with_score(question, k=3)
    results_2 = faiss_db_2.similarity_search_with_score(question, k=3)

    
    # score of documents

        
    result_1_score=max(map(lambda x: x[1],results_1))
    result_2_score=max(map(lambda x: x[1],results_2))


    results = results_1 if result_1_score>=result_2_score else results_2
    
    # convert the vectors to string format
    context ="\n\n".join([i[0].page_content for i in results]) 

    # short term memory retriver
    convo_history = content_retriver()

    # rag prompt that pass the string as parameter to llama model
    rag_prompt = f"""
    You are a medical assistant chatbot designed to provide general health information in a clear, calm, and responsible manner.

    Behavior rules:
    - Show empathy when user mentions illness.
    - Ask follow-up questions after answered the user question.
    - If sufficient symptoms are known, provide general guidance and recommendations.
    - Do NOT diagnose specific diseases.
    - Provide general treatment guidance when relevant medical context is available.
    - Do NOT refuse unnecessarily if question is medical-related.

    Knowledge usage rules:
    - Use BOTH conversation history and medical knowledge context to understand the user's condition.
    - Medical knowledge context is the primary source for treatment guidance.
    - Conversation history contains important symptom information and MUST be used when relevant.
    - If medical knowledge context is empty or insufficient, provide safe general guidance instead of refusing.

    Avoid excessive empathy repetition.
    Keep tone professional, calm, and helpful.
    
    ---------------------
    Conversation History:
    {convo_history}
    ---------------------

    Medical Knowledge Context:
    {context}
    ---------------------

    User Question:
    {question}
    ---------------------

    Medical Assistant Answer:
    """
    
    # LLM query response generating

    response = llm.invoke(rag_prompt)

    json_uploader(question, response)

    return response




#  Your tone should be professional, reassuring, and easy to understand for non-medical users.


#     Answer ONLY using the context below.
#     Do NOT use outside or external knowledge.
#     If answer is missing, tell that content is not related to medical field.