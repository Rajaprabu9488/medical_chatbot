from google import genai
from PIL import Image
from sentence_transformers import util
from dotenv import  load_dotenv
import os
import spacy
import re
import joblib

import custom_medical_component

OCR_client = None

intent_model=None

intent_vectors = dict()

nlp = None
def ocr_initial_loader():
    global OCR_client,nlp
    load_dotenv()
    API_KEY = os.getenv("OCR_API")

    OCR_client = genai.Client(api_key=API_KEY)
    
    nlp=spacy.load('saved_files/medical_nlp_model')

    detect_intent_loader()

# ---------------------------------------------------------------------
#                     OCR pipeline
# ---------------------------------------------------------------------



def ocr_pipeline(image_path):
    image = Image.open(image_path)

    response = OCR_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Extract all text from this image and in text have decimal values like .5 change it 0.5",
            image
        ]
    )

    result=NLP_processing(response.text)
    return result


def NLP_processing(image_text):

    medicine_and_dosage = []

    pattern=r'[^A-Za-z0-9 \n \t]'

    filter_result=re.sub(pattern,'',image_text)

    doc=nlp(filter_result)

    for i, ent in enumerate(doc.ents):

        # Case 1: MEDICINE detected
        if ent.label_ in ["MEDICINE", "DRUG"]:

            if i + 1 < len(doc.ents) and doc.ents[i + 1].label_ == "DOSAGE":
                medicine_and_dosage.append(f"{ent.text} -> {doc.ents[i + 1].text}")
            else:
                medicine_and_dosage.append(ent.text)

        # Case 2: DOSAGE detected but no medicine entity
        elif ent.label_ == "DOSAGE":

            medicine = None


            if i - 1 >= 0 and doc.ents[i - 1].label_ in ["MEDICINE", "DRUG"]:
                continue  


            if ent.start > 0:
                prev_token = doc[ent.start - 1]


                if prev_token.is_alpha:
                    medicine = prev_token.text

            if medicine:
                medicine_and_dosage.append(f"{medicine} -> {ent.text}")

    extracted_text=", ".join(medicine_and_dosage)

    return image_prompt_template(extracted_text)

def image_prompt_template(extracted_text):
    return str(f"""
        Medicines: {extracted_text}

        Explain:
            - What each medicine is used for
            - Typical dosage (if available)
            - Brief description of the medicine
            - Common side effects

        Be accurate and do not guess.
    """)

# -------------------------------------------------------------------------------------
#                         ENTITY AND INTENT
# -------------------------------------------------------------------------------------

def detect_entity_and_intent(text:str):
    convo_type=[]
    intent = []

    dependency = ['it','this','that','they','there','those']

    if any(word in text.lower() for word in dependency):
        convo_type.append('dependent convo')

    doc = nlp(text)
    for ent in doc.ents:
        convo_type.append(ent.label_)

    intent.append(detect_intent(text))

    return {"question":text,'conversation':convo_type,"intent":intent}


def detect_intent_loader():
    global intent_model,intent_vectors
    intent_model=joblib.load(r"C:\Users\My-PC\OneDrive\Desktop\medical-chatbot\saved_files\detect_intent.joblib")

    intent_examples = {

        "symptom_description": [
            "I have fever",
            "I am feeling sick",
            "I have headache",
            "my stomach hurts",
            "I feel pain in my chest",
            "having body pain",
            "I got cold and cough",
            "feeling dizzy",
            "I am not well",
            "vomiting and nausea",
            "I have acne",
            "skin problem on face"
        ],

        "severity_update": [
            "it is severe",
            "pain is getting worse",
            "it is mild",
            "very painful",
            "unbearable pain",
            "getting worse day by day",
            "not that serious",
            "slight pain only",
            "feels heavy",
            "high fever",
            "low fever"
        ],

        "treatment_request": [
            "what medicine should I take",
            "suggest some medicine",
            "any tablets for this",
            "what is the treatment",
            "how to cure this",
            "what should I do",
            "give me medicine",
            "how to recover fast",
            "any remedy",
            "what can I take for this",
            "treatment for headache",
            "medicine for acne"
        ],

        "general_query": [
            "tell me something",
            "give information",
            "explain this",
            "what is this"
        ],

        "non_medical": [
            "how to learn python",
            "what is machine learning",
            "tell me about cricket",
            "how to cook rice",
            "what is your name",
            "who is the prime minister",
            "open youtube",
            "play music",
            "how to build a website",
            "what is java",
            "best gaming laptop",
            "weather today"
        ],

        "drug_info": [
        "what is acetaminophen",
        "what is paracetamol",
        "what is ibuprofen tablet",
        "uses of dolo 650",
        "what is amoxicillin",
        "what does this medicine do",
        "what is this drug",
        "medicine information",
        "about crocin tablet"
    ],

    "side_effects": [
        "side effects of paracetamol",
        "what are the side effects of ibuprofen",
        "does dolo cause drowsiness",
        "is there any side effect",
        "what happens if I take this medicine",
        "can this tablet cause vomiting",
        "is it safe or not",
        "adverse effects of this drug"
    ],

    "dosage_info": [
        "what is the dosage of paracetamol",
        "how many tablets can I take",
        "how often should I take this medicine",
        "maximum dose of dolo 650",
        "can I take twice a day",
        "dosage for fever",
        "how much should I take"
    ],

    "disease_info": [
        "what is fever",
        "what is migraine",
        "what is acne",
        "define diabetes",
        "what causes headache",
        "why do we get cold",
        "how fever happens",
        "reason for stomach pain"
    ]
    }

    # Precompute
    intent_vectors = {
        k: intent_model.encode(v) for k, v in intent_examples.items()
    }

def detect_intent(text):
    vec = intent_model.encode(text)

    best_intent = None
    best_score = -1

    for intent, vectors in intent_vectors.items():
        score = max(util.cos_sim(vec, v) for v in vectors)

        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent

# ------------------------------------------------------------------------------------------------------------------------
#                             USER DETAILS EXTRACTION FOR LONG TERM STORAGE
# ------------------------------------------------------------------------------------------------------------------------

def content_details(sentence):
    doc=nlp(sentence)
    trigger_verbs = ["have",'give', 'take', "suffer", "experience", "diagnose", "feel",'be']

    severity_map = {
    "severe": ["severe", "extreme", "intense", "unbearable", "very bad","very severe","critical","acute","serious","heavy"],
    "moderate": ["moderate", "average", "normal pain","chronic"],
    "mild": ["mild", "slight", "little", "light"]
    }
    
    self_terms = {"i", "me","mine"}

    family_terms = {
        "mother","father","mom","dad","brother","sister",
        "uncle","aunt","grandmother","grandfather",
        "son","daughter","wife","husband","child","baby","aunt"
    }

    friend_terms = {
        "friend","buddy","colleague","roommate",
        "classmate","neighbor"
    }

    def detect_recovery_advanced(doc):
        for token in doc:
            if token.dep_ == "neg":
                return "inactive"

            if token.lemma_ in ["recover", "heal", "cure"]:
                return "inactive"

        return "active"


    def identify_subject(text):
        doc = nlp(text)

        for token in doc:
            word = token.text.lower()

            if word in family_terms:
                return word
            elif word in friend_terms:
                return "friends"
            elif word in self_terms:
                return "user"
    
    def get_severity(text):
        text = text.lower()

        for level, words in severity_map.items():
            for word in words:
                if word in text:
                    return level

        return None

    detail_extract={'patient': None,
    'severity':None,
    'condition':[],
    'disease': None,
    'medicine':[],
    'status':None,
    }

    detail_extract['severity']=get_severity(doc.text)
    
    detail_extract['patient']= identify_subject(doc)
    

    for ent in doc.ents:
        if ent.label_ == "MEDICINE" or ent.label_=="DRUG":
            detail_extract['medicine'].append(ent.text) 
        if ent.label_ == "DISEASE":
            detail_extract['disease'] = ent.text
        if ent.label_ == "SYMPTOM":
            detail_extract['condition'].append(ent.text)
                        
    if detail_extract['status'] is None:
        detail_extract['status'] = detect_recovery_advanced(doc)
    

    if detail_extract['patient'] and detail_extract['condition'] != [] or (detail_extract["disease"] is not None or (detail_extract["disease"] is not None and detail_extract["medicine"] != [])):
        return detail_extract


# ------------------------------------------------------------------------------------------------------------------------
#                                       continuous convo detection
# ------------------------------------------------------------------------------------------------------------------------

def continuous_question(question ,past_query=None):
    current_concat = []
    current_ques = detect_entity_and_intent(question)

    current_concat.append(question)

    if current_ques['conversation'] !=[] and any('dependent convo' in convo for convo in current_ques['conversation']) and 'non_medical' not in current_ques['intent']:
        for past_intent in past_query[::-1]:
            if any('dependent convo' in convo for convo in past_intent['conversation']) or (current_ques['conversation'] == []):
                if (past_intent['intent'][0] not in ['symptom_description','general_query',"dosage_info",'drug_info',"disease_info"]):
                    current_concat.append(past_intent["question"])
                    continue
                else:
                    current_concat.append(past_intent["question"])
                    break

            else:
                current_concat.append(past_intent["question"])
                break

    
    concat_question=" ,".join(current_concat[::-1])

    return {'question':concat_question,"conversation":current_ques['conversation'], "intent":current_ques['intent']} 


    
if __name__=='__main__':
    ocr_initial_loader()

    # with open('models/extracted_text/sample_2.txt','r') as file:
    #     demo_test=file.read()

    # print(NLP_processing(demo_test))

    # print(ocr_pipeline('models/train_image/IMG_20260311_164336359_HDR.jpg'))

    query = [
        "what is this",
        'i am feeling heavy fever and it is so dizziness to me',
        'it is mild and vommiting sensation',
        'what is medicine for it',
        'what is python',
        "what is DOLO 650",
        'i have acne in my chicks',
        "what is acetaminophen",
        "i have heart attack past 2 years",
        "i completedly cured from headache",
        "my sister is innocent"        
        ]
    
    
    # query_entity = []
    # for word in query:
    #     entity = detect_entity_and_intent(word)
    #     query_entity.append(entity)

    # print(continuous_question("this medicine is using only for body pain",query_entity))

    for word in query:
        print(word)
        print(content_details(word),end='\n\n')