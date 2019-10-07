# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 01:26:07 2019

@author: Jinghao Wang
"""

import spacy
from spacy.symbols import VERB
from collections import Counter
import requests
import re
from bs4 import BeautifulSoup

# Get book content.
url = 'https://www.gutenberg.org/files/1342/1342-h/1342-h.htm'
r = requests.get(url)

soup = BeautifulSoup(r.content, 'html.parser')
content = soup.find_all('p')
content = str(content)
#print(content)

book = re.findall('      (.+)\n', content)

book_parse = str(book).replace("', '", " ")
book_parse = str(book_parse).replace("\", \"", " ")
book_parse = str(book_parse).replace("\', \"", " ")
book_parse = str(book_parse).replace("\", '", " ")
book_parse = str(book_parse).replace("['", "")
book_parse = str(book_parse).replace("']", "")
book_parse = str(book_parse).replace("\\r", "")
book_parse = str(book_parse).replace("<i>", "")
book_parse = str(book_parse).replace("</i>", "")

#print(book_parse)

# =============================================================================
# with open('book.txt', 'w') as f:
#     f.write(book_parse)
# =============================================================================

# Load large nlp module, convert book into scapy type
nlp = spacy.load("en_core_web_lg")
text = str(book_parse)
doc = nlp(text)

#1. How many tokens are in the document?
num_tokens = 0
for token in doc:
    num_tokens = num_tokens + 1
    #print({token:token.pos_})
print("There're " + str(num_tokens) + " tokens in Pride And Prejudice.")

#2. How many verbs are in the document?
num_verbs = 0
for token in doc:
    if token.pos == VERB:
        num_verbs = num_verbs + 1
print("There're " + str(num_verbs) + " verbs in Pride And Prejudice.")

#3. What is the most frequent named entity?
named_ent = []
for ent in doc.ents:
    named_ent.append(ent.text)
    #print(ent.text, ent.start_char, ent.end_char, ent.label_)
ent_freq = Counter(named_ent)
Most_freq_ent = ent_freq.most_common(1)
print("The most frequent named entity is " + str(Most_freq_ent) + '.')

#4. How many setences are in the document?
num_sent = 0
for sent in doc.sents:
     num_sent = num_sent + 1
print("There're " + str(num_sent) + " sentences in Pride And Prejudice.")

#5. Of all the sentences in the text that are at least 10 words in length, which two are most similar (but not identical)?
sent_list = []
for sent in doc.sents:
    if str(sent).count(' ') >= 9:
        sent_list.append(sent)
#print(sent_list)

similarity_max = float(0.0)
sent1_max = None
sent2_max = None
for sent1 in sent_list:
    for sent2 in sent_list:
        if sent1 != sent2:
            if similarity_max < sent1.similarity(sent2):
                similarity_max = sent1.similarity(sent2)
                sent1_max = sent1
                sent2_max = sent2
        #print(similarity_max, sent1_max, sent2_max)
print("The highest similarity is " + str(similarity_max) + '.','\n',"Sent1: " + str(sent1_max),'\n',"Sent2: " + str(sent2_max))

#6. What is the vector representation of the first word in the 15th sentence in the document?
sent_15 = sent_list[14]
first_token_sent15 = sent_15[0]
print("The vector representation of the first word in the 15th sentence is " + str(first_token_sent15.vector_norm) + ".")

"""
Result:
Question1: There're 143854 tokens in Pride And Prejudice.
Question2: There're 14828 verbs in Pride And Prejudice.
Question3: The most frequent named entity is [('Elizabeth', 624)].
Question4: There're 6141 sentences in Pride And Prejudice.
Question5: The highest similarity is 0.9883196. 
Sent1: “I am by no means of the opinion...and not to any disrespect for her.” 
Sent2: The idea of Mr. Collin,...the honour of calling patroness.
Question6: The vector representation of the first word in the 15th sentence is 4.718869.
"""