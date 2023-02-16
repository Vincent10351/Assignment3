from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
import os, re, json


index_file = 'index_file'
document_count = 0
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))
unique_words = set()


def parse_files(root):
    global document_count
    for filename in os.listdir(root):                                               #opens the root directory
        for json_files in os.listdir(os.path.join(root, filename)):                 #opens each file within the root directory
            if document_count == 100: #debugging purposes, only goes up to 100 json files
                print (document_count)
                exit()
            with open(os.path.join(root, filename, json_files)) as json_file:       #opens each json_file within the sub-directory
                loaded_json = json.load(json_file)                                  #loads each json_file 
                content = loaded_json['content']
                text = BeautifulSoup(content, 'lxml')

                cur_list_tokens = tokenize(text)
                document_count += 1


def tokenize(soup):
    dict_tokens = defaultdict(int)
    text = soup.get_text()
    for token in re.split("[^a-zA-Z']+", text.lower()):                    #tokenizes the text and returns a dictionary with each token and it's frequency
        token = stemmer.stem(token.strip())
        if is_valid_token(token):
            unique_words.add(token)                               
            dict_tokens[token] += 1
    return dict_tokens

def is_valid_token(token):
    return token not in stop_words and len(token) > 2
        
parse_files('ANALYST')

#Wednesday: All day 
#Thursday: 6pm - whenever
#Friday: All day 
