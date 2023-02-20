from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import os, re, json
import tokenizer
from print_functions import *
from classes import *

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()


index_file = 'index_file'
document_count = 0
doc_id_dict = {}                            #holds mapping of docID to the url

def ind(): return defaultdict(ind)
index = ind()                               # a dictionary of all tokens and its frequencies

def add_tokens(dict_tokens, doc_id):                        # adds the tokens from the doc_id to global index
    for token, frequency in dict_tokens.items():
        p = Posting(doc_id, frequency)
        index[token]['doc_ids'][doc_id] = p                 #adds a token to index, and creates a Posting object for that doc_id and adds to the doc_ids list

def nltk_tokenize(text : str):
    tokenizer = RegexpTokenizer(r'\w+')
    list_tokens = tokenizer.tokenize(text)                  # tokenizes the file and returns a list of tokens
    return [stemmer.stem(token.strip()) for token in list_tokens]

def parse_files(root):
    global document_count
    for filename in os.listdir(root):                                                             #opens the root directory
        for json_files in os.listdir(os.path.join(root, filename)):                               #opens each file within the root directory
            with open(os.path.join(root, filename, json_files)) as json_file:                     #opens each json_file within the sub-directory
                if document_count == 10:
                    #print (index)
                    print (index['artifici']['doc_ids'])
                    exit()
                loaded_json = json.load(json_file)                                                #loads each json_file 
                content = loaded_json['content']
                soup = BeautifulSoup(content, 'html.parser')

                cur_list_tokens = nltk_tokenize(soup.get_text())
                if cur_list_tokens:
                    word_frequencies = tokenizer.computeWordFrequencies(cur_list_tokens)
                    add_tokens(word_frequencies, document_count)

                doc_id_dict[document_count] = loaded_json['url']                        #stores mapping of docID to url
                document_count += 1
    
    return file_token_counts, token_files


file_token_counts, token_files = parse_files('DEV')
open('report.txt', 'w').close()
print_unique_words()
print_document_count()
tokenizer.print_freq(freq_dict)
