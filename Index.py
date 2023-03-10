from collections import defaultdict
import math
import sys
from bs4 import BeautifulSoup
import numpy as np
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import os, re, json
import tokenizer
from flask import Flask, render_template, url_for, request
import time


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
                id: int,                                 # doc ID number
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


importance_dict = \
{
    'title': 25,
    'h1': 10,
    'h2': 8,
    'h3': 6,
    'h4': 5,
    'b': 3,
    'strong': 3,
    'i': 2,
    'em': 2,
    'h5': 2,
    'h6': 2
}


stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

document_count = 0
doc_id_dict = {}                                                #holds mapping of docID to the url

MAX_INDEX_SIZE = 100 * 1024 * 1024  # 100 MB
total_index_size = 0
def ind(): return defaultdict(ind)
index = ind()                                                   # a dictionary of all tokens

    

def add_tokens(dict_tokens, doc_id):
    global index
    global total_index_size
    # Calculate the total number of words in the document
    total_words = sum(dict_tokens.values())
    if total_index_size >= MAX_INDEX_SIZE:
        dump_index_to_files()
        total_index_size = 0
    # Loop through each token and its frequency in the document
    for token, frequency in dict_tokens.items():
        # Get the first letter of the token (converted to lowercase)
        token_letter = token[0].lower()
        
        # Check if the first letter is an alphabetic character and the token is not just a number
        if re.match('[a-z]', token_letter) and not token.isnumeric():
            # Create a filename for the token based on its first letter
            filename = f'storage/partial/{token_letter}.json'
            
            # Check if the file data has already been loaded for this filename
            if filename not in index:
                # If the file doesn't exist, create it with an empty dictionary
                if not os.path.exists(filename):
                    with open(filename, 'w') as f:
                        json.dump({}, f)
                
                # Load the existing file data into the index dictionary
                with open(filename, 'r+') as f:
                    index[filename] = json.load(f)
            
            # Get the data dictionary for this token from the file data
            data = index[filename]
            
            # If the token is not in the data dictionary, add it with initial values
            if token not in data:
                data[token] = {'token_frequency': 0, 'document_frequency': 0, 'doc_ids': {}}
            
            # Increment the document frequency and token frequency for this token
            data[token]['document_frequency'] += 1
            data[token]['token_frequency'] += frequency
            
            # Add the document ID, term frequency, and TF-IDF values for this token in this document
            data[token]['doc_ids'][doc_id] = {'id': doc_id, 'term_frequency_in_doc': frequency / total_words, 'tf_idf': 0.0}

                        
            # Calculate the size of the token and its data in bytes
            token_size = sys.getsizeof(token)
            data_size = sys.getsizeof(data[token])
            
            # Increment the total size of the index
            total_index_size += token_size + data_size


            
def dump_index_to_files():
    print(total_index_size)
    print("dumping")
    global index
    for partial, data in index.items():
        with open(partial, 'w') as f:
            json.dump(data, f, indent=4)
    index = {}
    
                    

def nltk_tokenize(text : str):                                  #tokenizes the file and returns a list of tokens
    tokenizer = RegexpTokenizer(r'\w+')
    list_tokens = tokenizer.tokenize(text)                      
    return [stemmer.stem(token.strip()) for token in list_tokens]

def calculate_tf_idf_score():                                   #calculates the tf_idf score for each document for each token
    global index
    for token in index:
        for doc_id in index[token]['doc_ids']:
            idf = math.log(document_count / (1 + index[token]['doc_ids'][doc_id]['term_frequency_in_doc']), 10)
            tf = index[token]['doc_ids'][doc_id]['term_frequency_in_doc']
            index[token]['doc_ids'][doc_id]['tf_idf'] = tf * idf
    with open('storage/fullIndex/merged_data.json','w') as f:
        json.dump(index,f,indent = 4)

def calculate_importance(soup, doc_id):
    for header, base_weight in importance_dict.items():
        for tag in soup.find_all(header):   # for each tag that matches header 
            content = tag.text              # content of the tag
            
            #TODO : tokenize contents of tag
            tokens_in_tag = nltk_tokenize(content)          
            # Adds to weight of document according to header
            for tag_token in tokens_in_tag: # iterate through token list
                if tag_token in index and doc_id in index[tag_token]['doc_ids']:
                    index[tag_token]['doc_ids'][doc_id]['term_frequency_in_doc'] += base_weight   # add weight 
        
def parse_files(root):
    global document_count
    for filename in os.listdir(root):                                                             #opens the root directory
        for json_files in os.listdir(os.path.join(root, filename)):                               #opens each file within the root directory
            with open(os.path.join(root, filename, json_files)) as json_file:                     #opens each json_file within the sub-directory
                loaded_json = json.load(json_file)                                      #loads each json_file 
                content = loaded_json['content']                                        #grabs content from json_file
                soup = BeautifulSoup(content, 'html.parser')
                cur_list_tokens = nltk_tokenize(soup.get_text())
                if cur_list_tokens:                                                     #computes word frequencies and adds to index
                    word_frequencies = tokenizer.computeWordFrequencies(cur_list_tokens)
                    add_tokens(word_frequencies, document_count)
                                          
                
                doc_id_dict[document_count] = loaded_json['url']                        #stores mapping of docID to url
                document_count += 1
    dump_index_to_files()
    mergeIndices()
    return

def load_dict():
    global index
    global doc_ids
    with open('storage/fullIndex/merged_data.json', 'r+') as file: # loads the merged_index
        index = json.load(file)
    
    with open('storage/docID_mappings.json', 'r+') as file: # loads the docID mappings
        doc_ids = json.load(file)


def mergeIndices():                                  #merges all json file into merged_data.json
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


def search(query):
    print (query)
    start_time = time.time()
    # Tokenize the query
    query_tokens = nltk_tokenize(query.lower())
    # Create an empty dictionary to store scores
    scores = {}
    # Create an empty dictionary to keep track of the number of times each query token appears in a document
    query_token_count = {}
    start_time = time.time()        # Store the current time in a variable
    for token in query_tokens:      # Loop through each token in the query_tokens list
        with open('storage/partial/' + f'{token[0]}.json') as f:
            load_partial_index = json.load(f)           # Load the contents of the JSON file into a dictionary
        print(f'load_time: {time.time() - start_time}')         # Print the time it took to load the partial index
        query_time = time.time()        # Store the current time in a variable
        if token in load_partial_index:  # Check if the current token exists in the partial index
            for doc_id, posting in load_partial_index[token]['doc_ids'].items(): # Loop through each document ID and posting for the current token
                if doc_id not in scores:    # If the document ID is not already in the scores dictionary, add it with a score of 0.0
                    scores[doc_id] = 0.0
                scores[doc_id] += load_partial_index[token]['doc_ids'][doc_id]['tf_idf'] * posting['tf_idf'] # Add the product of the token's and posting's TF-IDF values to the document's score
                if doc_id not in query_token_count:     # If the document ID is not already in the query_token_count dictionary, add it with a count of 0
                    query_token_count[doc_id] = 0
                query_token_count[doc_id] += 1      # Increment the count of how many times the current token appears in the current document
    print (f'query_time: {round((time.time() - query_time) * 1000, 2)}') # Print the time it took to process the query
        
            
    sort_time = time.time()
    scores2 = sorted(scores.items(), key=lambda x: x[1], reverse = True)
    # Return the top 5 documents with the highest cosine similarity scores that contain all query tokens
    top_docs = [(doc_id, score) for doc_id, score in scores.items() if query_token_count[doc_id] == len(query_tokens)] # top all docs that contain christina lopes
    # If the query term contains a token that does not exist in our index, we return the top 5 documents with the highest cosine similarity score for each word.
    while len(top_docs) < 5:
        docs = [doc[0] for doc in top_docs]   #retrieves all the docIDS in top_docs
        for doc_id, score in scores2:         
            if doc_id not in docs:            #if the current doc_id in scores2 HASN"T been added to top_docs, add it
                top_docs.append((doc_id, score))
            if len(top_docs) == 5:             #once it reaches 5 documents, break
                break
        break                                  #if it reaches the end of scores but top_docs is still length < 5, break
    top_docs = sorted(top_docs, key=lambda x: x[1], reverse=True)[:5]
    print (f'sort_time: {round((time.time() - sort_time) * 1000, 2)}')

    write_time = time.time()
    search_results = list()
    with open('results.txt', 'a') as file:                                              #writes to result.txt
        file.write(f'{query}\n')
        for doc_id, score in top_docs:
            file.write(f'{doc_ids[doc_id]}\n')
            search_results.append(doc_ids[doc_id])
        file.write(f'Total taken: {round((time.time() - start_time) * 1000, 2)} in miliseconds')
        file.write('\n')
    print (f'write_time: {round((time.time() - write_time) * 1000, 2)}')
    print (f'total_start_time: {round((time.time() - start_time) * 1000, 2)}')
    print ('----')
    return search_results

def splity():
    with open('storage/fullIndex/merged_data.json', 'r') as f:                      # load the inverted index.json file
        inverted_index = json.load(f)
    partial_indexes = {}                                                            # create a dictionary to store the partial indexes
    for token in inverted_index:                                                    # iterate through the tokens in the inverted index
        first_letter = token[0]                                                     # get the first letter of the token
        if first_letter not in partial_indexes:                                     # create a new dictionary for the partial index if it doesn't exist yet
            partial_indexes[first_letter] = {}
        partial_indexes[first_letter][token] = inverted_index[token]                # add the token information to the partial index
    for letter in partial_indexes:                                                  # save each partial index to a separate .json file
        filename = f'storage/partial/{letter}.json'
        with open(filename, 'w') as f:
            json.dump(partial_indexes[letter], f, indent = 4)



def start():
    if not os.path.exists('storage'):
        os.mkdir('storage')
    if not os.path.exists('storage/partial'):
        os.mkdir('storage/partial')
    parse_files('DEV')
    with open("storage/docID_mappings.json", "w+") as output_file:       #writes docID mappings to a file
        json.dump(doc_id_dict, output_file, indent = 4)
    load_dict()
    calculate_tf_idf_score()
    #calculate the tf_idf score of ALL tokens in index

    
    


if __name__=='__main__':
    start()
    app.run(debug=True)