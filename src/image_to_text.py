from google import genai
from PIL import Image
from sentence_transformers import util
from dotenv import  load_dotenv
import os
import spacy
import re
import dateparser
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



def ocr_pipeline(image_path):
    image = Image.open(image_path)

    response = OCR_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Extract all text from this image",
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
        medicine_name=None
        dosage=None
        if ent.label_ == "MEDICINE" or ent.label_ == "DRUG":
            if i + 1 < len(doc.ents):
                medicine_name=ent.text
                next_ent = doc.ents[i + 1]
                if next_ent.label_ == "DOSAGE":
                    dosage = next_ent.text
        if(medicine_name is not None and dosage is None):
            medicine_and_dosage.append(f'{medicine_name}')
        elif(medicine_name is not None or dosage is not None):
            medicine_and_dosage.append(f'{medicine_name} - {dosage}')

    return "\n".join(medicine_and_dosage)

def detect_entity_and_intent(text):
    convo_type=[]
    intent = []
    dependency = ['it','this','that','they','there','those']
    
    if any(word in word.lower() for word in dependency):
        convo_type.append('dependent convo')
    
    doc = nlp(word)
    for ent in doc.ents:
        convo_type.append(ent.label_)

    intent.append(detect_intent(word))

    return {'conversation':convo_type,"intent":intent}


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
            "what is fever",
            "what is migraine",
            "define headache",
            "what causes fever",
            "why do we get cold",
            "what is acne",
            "explain diabetes",
            "what is the reason for headache",
            "how fever happens"
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

def content_details(doc):
    trigger_verbs = ["have",'give', 'take', "suffer", "experience", "diagnose", "feel",'be']

    severity_map = {
    "severe": ["severe", "extreme", "intense", "unbearable", "very bad","very severe","critical","acute","serious"],
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


    def identify_subject(text):
        doc = nlp(text)

        for token in doc:
            word = token.text.lower()

            if word in family_terms:
                return word
            elif word in friend_terms:
                return "friends"
            elif word in self_terms:
                return "I"
    
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
    'disease':None,
    'medicine':[],
    'duration':None,
    'timestamp':None
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
        if ent.label_ == "TIME_EXPRESSION" or ent.label_ == 'DATE':
            detail_extract['duration'] = ent.text
                        

                    
    if(detail_extract['duration']):
        parsed_date = dateparser.parse(detail_extract['duration'])
        try:
            formatted_date = parsed_date.strftime("%d/%m/%Y")
            detail_extract['timestamp']=formatted_date
        except:
            detail_extract['timestamp'] = None

    return detail_extract


if __name__=='__main__':
    ocr_initial_loader()

    # with open('models/demo_nlp_text.txt','r') as file:
    #     demo_test=file.read()

    # print(NLP_processing(demo_test))
    query = ["what is this",'i am feeling heavy fever and it is so dizziness to me','it is mild and vommiting sensation','what is medicine for it','what is python',"what is paracetamol"]
    for word in query:
        print(detect_entity_and_intent(word))

    for word in query:
        doc=nlp(word)
        print(doc)
        print(content_details(doc),end='\n\n')