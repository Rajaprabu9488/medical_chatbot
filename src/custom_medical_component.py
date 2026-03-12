import spacy
from spacy.matcher import PhraseMatcher, Matcher
from spacy.language import Language
from spacy.tokens import Span
from spacy.util import filter_spans
import re
import pandas as pd

# load matcher 

nlp=spacy.load('en_core_web_md')
matcher_0 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_1 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_2 = Matcher(nlp.vocab)
matcher_3 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_4 = PhraseMatcher(nlp.vocab, attr="LOWER")
matcher_5 = Matcher(nlp.vocab)


# identify the medicine and drugs using csv

# drug_pattern
df=pd.read_csv('saved_files/nlp_dataset/A_Z_medicines_dataset_of_India.csv')


list1 = df['short_composition1'].dropna().unique().tolist()
list2 = df['short_composition2'].dropna().unique().tolist()


drug_list = list1+list2

pattern=r"\s*\(.*?\)"

for i in range(len(drug_list)):
    drug_list[i] = re.sub(pattern,"", drug_list[i].strip())

patterns = [nlp.make_doc(med) for med in drug_list]

matcher_0.add("DRUGS", patterns)


# medicine pattern

df_medicine_list= df['name'].dropna().unique().tolist()

raw_medicine_list= [ i.split() for i in df_medicine_list ]

medicine_list= list(set(map(lambda x : ' '.join(x[:2]),raw_medicine_list)))

patterns = [nlp.make_doc(med) for med in medicine_list]

matcher_1.add("MEDICINE", patterns)

# dosage pattern 

pattern = [
    {"LIKE_NUM": True},
    {"LOWER": {"IN": ["mg", "ml","g","mcg"]}}
]

matcher_2.add("DOSAGE", [pattern])

# disease pattern 

disease_dataset = pd.read_csv('saved_files/nlp_dataset/Disease and symptoms dataset.csv')

disease_name = disease_dataset['diseases'].dropna().unique().tolist()

disease_list = list(map(lambda x: x.lower(),disease_name)) 

patterns = [nlp.make_doc(med) for med in disease_list]

matcher_3.add("DISEASES", patterns)

# symptoms pattern 

add_common_disease = pd.read_csv('saved_files/nlp_dataset/symptom_dataset.csv')  

common_disease = add_common_disease['Symptom_Name'].tolist()

patterns = [nlp.make_doc(med) for med in common_disease]

matcher_4.add("SYMPTOM", patterns)

# date and time pattern 

pattern_1 = [
    {"LIKE_NUM": True},
    {"LOWER": {"IN": ["day", "days", "week", "weeks", "month", "months"]}}
]

pattern_2 = [
    {"LOWER": {"IN": ["yesterday", "today", "tomorrow"]}}
]

pattern_3 = [
    {"LOWER": "day"},
    {"LOWER": "before"},
    {"LOWER": "yesterday"}
]

pattern_4 = [
    {"LOWER": "last"},
    {"LOWER": {'IN': ['day','month','week','year','morning','afternoon','evening','night']}},

]

matcher_5.add("DURATION", [pattern_1])
matcher_5.add("RELATIVE_DATE", [pattern_2, pattern_3,pattern_4])


matchers = [
    (matcher_0, "DRUG"),
    (matcher_1, "MEDICINE"),
    (matcher_2, "DOSAGE"),
    (matcher_4, "SYMPTOM"),
    (matcher_3, "DISEASE"),
    (matcher_5, "TIME_EXPRESSION"),
]

# custom components 

@Language.component("medical_matcher")
def medicine_words(doc):

    new_ents = list(doc.ents)

    for matcher, label in matchers:
        for _, start, end in matcher(doc):

            span = Span(doc, start, end, label=label)

            new_ents = [
                e for e in new_ents
                if not (e.start < end and e.end > start)
            ]

            new_ents.append(span)

    doc.ents = filter_spans(new_ents)
    return doc
