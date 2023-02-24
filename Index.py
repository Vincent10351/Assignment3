from collections import defaultdict
import math
from bs4 import BeautifulSoup
import numpy as np
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import os, re, json
import tokenizer
from query import search, load_dict

"""
Structure of the Inverted Index
{ 
    Token : { 
        token_frequency: int                             # how many times the token appears in ALL docments 
        document_frequency: int                          # how many documents does the token appear in
        doc_ids: {                                       
            id1: {
                id: int,                                 #doc ID number
                term_frequency_in_doc: int,              # how many times the token appears in the document divided by total words in doc
                tf_idf: int                              # tf * idf, i don't know how to explain
            }
            id2: {
                id: int,
                term_frequency_in_doc: int,
                tf_idf: int
            }
    }
}
"""
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

document_count = 0
doc_id_dict = {}                                                #holds mapping of docID to the url

def ind(): return defaultdict(ind)
index = ind()                                                   # a dictionary of all tokens

def add_tokens(dict_tokens, doc_id):                            # adds the tokens from the doc_id to global index
    total_words = sum(dict_tokens.values())
    for token, frequency in dict_tokens.items():

        #term_frequency_in_doc is the ratio of how many times the word appears in the doc compared to the total words
        p = {'id': doc_id, 'term_frequency_in_doc': frequency/total_words, 'tf_idf': 0.0}    

        if token not in index:                                  #if the token does not exist in the index, add the token
            index[token] = {'token_frequency':0, 'document_frequency': 0, 'doc_ids':{}};    

        index[token]['document_frequency'] += 1                 #Document_frequency is how many documents does this token appear in
        index[token]['token_frequency'] += frequency            #Token_frequency is the total number of times the token appears OVERALL
        index[token]['doc_ids'][doc_id] = p                     #Adds a token to index, and creates a Posting object for that doc_id and adds to the doc_ids list

def nltk_tokenize(text : str):                                  #tokenizes the file and returns a list of tokens
    tokenizer = RegexpTokenizer(r'\w+')
    list_tokens = tokenizer.tokenize(text)                      
    return [stemmer.stem(token.strip()) for token in list_tokens]

def calculate_tf_idf_score():                                   #calculates the tf_idf score for each document for each token
    for token in index:
        for doc_id in index[token]['doc_ids']:
            idf = math.log(document_count / (1 + index[token]['doc_ids'][doc_id]['term_frequency_in_doc']), 10)
            tf = index[token]['doc_ids'][doc_id]['term_frequency_in_doc']
            index[token]['doc_ids'][doc_id]['tf_idf'] = tf * idf

def parse_files(root):
    global document_count
    for filename in os.listdir(root):                                                             #opens the root directory
        for json_files in os.listdir(os.path.join(root, filename)):                               #opens each file within the root directory
            with open(os.path.join(root, filename, json_files)) as json_file:                     #opens each json_file within the sub-directory
                if document_count == 10:

                    return
                loaded_json = json.load(json_file)                                      #loads each json_file 
                content = loaded_json['content']                                        #grabs content from json_file
                soup = BeautifulSoup(content, 'html.parser')

                cur_list_tokens = nltk_tokenize(soup.get_text())
                if cur_list_tokens:                                                     #computes word frequencies and adds to index
                    word_frequencies = tokenizer.computeWordFrequencies(cur_list_tokens)
                    add_tokens(word_frequencies, document_count)

                doc_id_dict[document_count] = loaded_json['url']                        #stores mapping of docID to url
                document_count += 1                                                     #keeps track of how many documents there are
    return 

def start():
    parse_files('DEV')
    calculate_tf_idf_score()      
    open('result.txt', 'w').close()
    if not os.path.exists('storage'):
        os.mkdir('storage')
                                           #calculate the tf_idf score of ALL tokens in index
    with open("storage/docID_mappings.json", "w+") as output_file:       #writes docID mappings to a file
        json.dump(doc_id_dict, output_file, indent = 4)

    with open('storage/index_mappings.json', 'w+') as output_file:       #writes the index to a json file
        json.dump(index, output_file, indent = 4)

    load_dict()
    search('cristina lopes')                              #performs the query on these terms
    search('machine learning')
    search('ACM')
    search('master of software engineering')

if __name__=='__main__':
    start()

