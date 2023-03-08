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
from flask import Flask, render_template, url_for


app = Flask(__name__)
@app.route('/', methods =['GET','POST'])
def searchFlask():
    search_results = list()
    if request.method == 'POST':
        query = request.form['query']
        search_results = search(query)
    return render_template('index.html',links=search_results)


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

def add_tokens(dict_tokens, doc_id): # Modified add_tokens to create .json file for each alphanumeric character. 
    total_words = sum(dict_tokens.values())
    for token, frequency in dict_tokens.items():
        token_letter = token[0].lower()
        reg = re.compile(r'[a-z0-9]')
        if reg.match(token_letter):
            if not token.isnumeric(): # checks if the token is just a number ex. "1" , "100" , "1000", if so does not add to token file.
                # Check if a file already exists for this token's first letter
                filename = f'storage/partial/{token_letter}.json'
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        json.dump({}, f)
                
                # Open the file for this token's first letter
                with open(filename, 'r+') as f:
                    data = json.load(f)
                    
                    # If the token is not in the file, add it
                    if token not in data:
                        data[token] = {'token_frequency': 0, 'document_frequency': 0, 'doc_ids': {}}
                    
                    # Update the token's information in the file
                    data[token]['document_frequency'] += 1
                    data[token]['token_frequency'] += frequency
                    data[token]['doc_ids'][doc_id] = {'id': doc_id, 'term_frequency_in_doc': frequency / total_words, 'tf_idf': 0.0}
                    
                    # Write the updated data back to the file
                    f.seek(0)
                    json.dump(data, f)
                    f.truncate()
                    
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
                                                                                                    #keeps track of how many documents there are
                    mergeIndices()
                    return
                loaded_json = json.load(json_file)                                      #loads each json_file 
                content = loaded_json['content']                                        #grabs content from json_file
                soup = BeautifulSoup(content, 'html.parser')

                cur_list_tokens = nltk_tokenize(soup.get_text())
                if cur_list_tokens:                                                     #computes word frequencies and adds to index
                    word_frequencies = tokenizer.computeWordFrequencies(cur_list_tokens)
                    add_tokens(word_frequencies, document_count)

                doc_id_dict[document_count] = loaded_json['url']                        #stores mapping of docID to url
                document_count += 1
    return 


def mergeIndices():
    partial_index_directory = 'storage/partial'
    if not os.path.exists('storage/fullIndex'):
        os.makedirs('storage/fullIndex')
    merged_data = {}
    for filename in os.listdir(partial_index_directory):
        with open(os.path.join(partial_index_directory,filename)) as f:
            partial_index_data = json.load(f)

        merged_data.update(partial_index_data)
    with open('storage/fullIndex/merged_data.json','w') as f:
        json.dump(merged_data,f)
    return

def load_dict():
    global index
    global doc_ids
    with open('storage/fullIndex/merged_data.json', 'r+') as file: # loads the merged_index
        index = json.load(file)
    
    with open('storage/docID_mappings.json', 'r+') as file: # loads the docID mappings
        doc_ids = json.load(file)

def mergeIndices():
    partial_index_directory = 'storage/partial'
    if not os.path.exists('storage/fullIndex'):
        os.makedirs('storage/fullIndex')
    merged_data = {}
    for filename in os.listdir(partial_index_directory):
        with open(os.path.join(partial_index_directory,filename)) as f:
            partial_index_data = json.load(f)

        merged_data.update(partial_index_data)
    with open('storage/fullIndex/merged_data.json','w') as f:
        json.dump(merged_data,f)
    return


def search(query):
    # Tokenize the query
    query_tokens = nltk_tokenize(query.lower())
    # Calculate the tf-idf score for each query token
    query_tf_idf = {}
        
    for token in query_tokens:
        if token in index:
            idf = math.log(document_count / index[token]['document_frequency'], 10)
            tf = 1 + math.log(query_tokens.count(token), 10)
            query_tf_idf[token] = tf * idf

    # Calculate the cosine similarity between the query and each document in the posting lists
    scores = {}
    query_token_count = {}
    for token in query_tokens:
        if token in index:
            for doc_id, posting in index[token]['doc_ids'].items():
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                scores[doc_id] += query_tf_idf[token] * posting['tf_idf']
                if doc_id not in query_token_count:
                    query_token_count[doc_id] = 0
                query_token_count[doc_id] += 1

    # Return the top 5 documents with the highest cosine similarity scores that contain all query tokens
    top_docs = [(doc_id, score) for doc_id, score in scores.items() if query_token_count[doc_id] == len(query_tokens)]
    top_docs = sorted(top_docs, key=lambda x: x[1], reverse=True)[:5]

    search_results = list()
    with open('results.txt', 'a') as file:
        file.write(f'{query}\n')
        for doc_id, score in top_docs:
            file.write(f'{doc_ids[doc_id]}\n')
            search_results.append(doc_ids[doc_id])
        file.write('\n')

    return search_results

def start(): 
    if not os.path.exists('storage'):
        os.mkdir('storage')
    if not os.path.exists('storage/partial'):
        os.makedirs('storage/partial')
    parse_files('DEV')
    calculate_tf_idf_score()     
                                           #calculate the tf_idf score of ALL tokens in index
    with open("storage/docID_mappings.json", "w+") as output_file:       #writes docID mappings to a file
        json.dump(doc_id_dict, output_file, indent = 4)

    with open('storage/index_mappings.json', 'w+') as output_file:       #writes the index to a json file
        json.dump(index, output_file, indent = 4)

    load_dict()
    #search('cristina lopes')                              #performs the query on these terms
    #search('machine learning')
    #search('ACM')
    #search('master of software engineering')



if __name__=='__main__':
    start()
    app.run(debug=True)


