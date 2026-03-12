from google import genai
from PIL import Image
from dotenv import  load_dotenv
import os
import spacy
from spacy.language import Language
import re

import custom_medical_component

OCR_client = None

nlp = None
def ocr_initial_loader():
    global OCR_client,nlp
    load_dotenv()
    API_KEY = os.getenv("OCR_API")

    OCR_client = genai.Client(api_key=API_KEY)
    
    nlp=spacy.load('saved_files/medical_nlp_model')
    print(nlp.pipe_names)



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
                print(medicine_name)
                next_ent = doc.ents[i + 1]
                if next_ent.label_ == "DOSAGE":
                    dosage = next_ent.text
        if(medicine_name is not None or dosage is not None):
            print(f'{ent.text} - {ent.label_} - {next_ent.text} - {next_ent.label_}')
            medicine_and_dosage.append(f'{ent.text} - {next_ent.text}')

    return "\n".join(medicine_and_dosage)


if __name__=='__main__':
    ocr_initial_loader()

    with open('models/demo_nlp_text.txt','r') as file:
        demo_test=file.read()

    print(NLP_processing(demo_test))