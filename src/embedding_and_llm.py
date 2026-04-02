from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
import joblib

from helper import content_retriver,Redis_uploader,question_retriver,update_patient_condition,user_details_template


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


def rag_pipeline(user_id,session_id,question):
    # past question retriver
    past_question=question_retriver(session_id, question)
    update_patient_condition(user_id,past_question['question'])
    # perform similarity search with k = 3 sentences
    # the search is based ok cosine similarity
    results_1 = faiss_db_1.similarity_search_with_score(past_question['question'], k=3)
    results_2 = faiss_db_2.similarity_search_with_score(past_question['question'], k=3)

    
    # score of documents

        
    result_1_score=min(map(lambda x: x[1],results_1))
    result_2_score=min(map(lambda x: x[1],results_2))


    results = results_1 if result_1_score<=result_2_score else results_2
    
    # convert the vectors to string format
    context ="\n\n".join([i[0].page_content for i in results]) 
    # short term memory retriver
    convo_history = content_retriver(session_id)

    user_medical_history = user_details_template(user_id)
    
    # rag prompt that pass the string as parameter to llama model
    rag_prompt = f"""
    You are a medical assistant chatbot that provides general health guidance. 
    
    Behavior rules: 
        - Respond calmly and professionally. 
        - Show brief empathy when the user mentions illness. 
        - First answer the user's concern with general medical guidance. 
        - If enough symptom information is available, give possible explanations and safe advice. 
        - Never repeat questions that are already answered in the conversation history. 
        - Do NOT diagnose diseases without proper symptoms. 
    
    Knowledge usage rules: 
        - Use both conversation history and medical knowledge context. 
        - Conversation history contains important symptom information and MUST be used when relevant. 
        - Avoid asking about symptoms that are already mentioned. 
        - If medical context is limited, give safe general advice instead of refusing. 

    Response structure: 
        1. Brief acknowledgement or empathy If the user describes their own symptoms, illness, or discomfort. 
        2. General explanation or guidance. 
        3. Keep response concise and easy to understand
        4. Format the answer in clear bullet points when explaining causes, Treatments, symptoms, or advice.
        5. Use simple and easy-to-understand language (avoid long paragraphs).
        6. Use short headings if needed (e.g., "Possible causes:", "What you can do:").

    ---------------------
    Medical History
    {user_medical_history}
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

    complete_response=""
    for chunk in llm.stream(rag_prompt):
        complete_response +=chunk
        yield chunk

    Redis_uploader(session_id,question, complete_response, past_question['conversation'] ,past_question['intent'])


    # - Provide safe suggestions such as rest, hydration, or when to seek medical help.
#  Your tone should be professional, reassuring, and easy to understand for non-medical users.


#     Answer ONLY using the context below.
#     Do NOT use outside or external knowledge.
#     If answer is missing, tell that content is not related to medical field.
