#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 19:12:10 2019

@author: jinghaowang
"""

'''Create an inverted index for jeopardy questions.'''

import csv
import re
import spacy

nlp = spacy.load("en_core_web_lg")

# Create dictionary of inverted index
inverted_idx = {}

# Create list of rows from Jeopardy.csv
docs = []

# Create list of word tokens after removing stopwords
words_parsed =[]

with open ("JEOPARDY_CSV.csv", "r") as f:
    reader = csv.reader(f, delimiter=",")
    next(reader)
    
    for i, row in enumerate(reader):
        
        # Join the parts that need parsing
        text = ' '.join([row[3],row[5],row[6]])
        
        # Remove punctuation
        text_punc_removed = re.sub(r'[^\w\s]','',text)
        
        text = nlp(text_punc_removed)
        
        # Remove stopwords
        for word in text:
            if word.is_stop == False:
                # Lemmanize words
                words_parsed.append(str(word.lemma_).lower())
    
        # Deduplicate words
        text = list(set(words_parsed))
        
        docs.append(' '.join(row))

    for word in text:
        if word not in inverted_idx:
            inverted_idx[word] = []
        inverted_idx[word].append(i)
    

def retrieve(query):
    query_terms = query.split()
    results = []
    for term in query_terms:
        results.extend(inverted_idx[term.lower()])
    results = list(set(results))
    return [docs[i] for i in results]

# =============================================================================
#     print(term, inverted_idx[term.lower()])
#     raise NotImplementedError
# =============================================================================

r = retrieve("rock")
print(r)

r = retrieve("colorless green ideas sleep furiously")
print(r)
