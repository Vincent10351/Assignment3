from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
import os, re, json
import tokenizer

index_file = 'index_file'
document_count = 0
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))
unique_words = set()
freq_dict = defaultdict(int)  # a dictionary of all tokens and its frequencies

def add_tokens(dict_tokens):                                # adds the tokens from the current page into our global token dictionary
    for token, c in dict_tokens.items():
        freq_dict[token] += c

def print_unique_words():
    with open("report.txt", "a") as f:
        f.write("unique_words: " + str(len(unique_words)) + "\n")
        f.write("-------------------------------" + "\n")

def print_document_count():
    with open("report.txt", "a") as f:
        f.write("document_count: " + str(document_count)+ "\n")
        f.write("-------------------------------" + "\n")

def tokenize(soup):
    dict_tokens = defaultdict(int)
    text = soup.get_text()
    for token in re.sub("[^a-zA-Z0-9']+", ' ', text.lower()).split():
        token = stemmer.stem(token.strip()) 
        unique_words.add(token)
        dict_tokens[token] += 1
        return dict_tokens

def parse_files(root):
    global document_count
    file_token_counts = defaultdict(lambda: defaultdict(int)) #i don't think we need a defaultdict(int)
    token_files = defaultdict(set)
    for filename in os.listdir(root):                                                             #opens the root directory
        for json_files in os.listdir(os.path.join(root, filename)):                               #opens each file within the root directory
            with open(os.path.join(root, filename, json_files)) as json_file:                     #opens each json_file within the sub-directory
                loaded_json = json.load(json_file)                                                #loads each json_file 
                content = loaded_json['content']
                text = BeautifulSoup(content, 'lxml')

                cur_list_tokens = tokenize(text)
                if cur_list_tokens:
                    word_frequencies = tokenizer.computeWordFrequencies(cur_list_tokens)
                    add_tokens(word_frequencies)


                # file_token_counts[filename][json_files] = cur_list_tokens      #sets value of dictionary of each json file to the tokenized list
                # "{www_cs_uci_edu: {0a0056b9.json: {tokens}, 0a77b.json: {tokens}}}"
                # for token in cur_list_tokens.keys():                           #adds each json file that contain the token
                #     token_files[token].add(json_files)
                    #{ 'teacher': {json1, json2, json3, json4}}
                

                document_count += 1
    
    return file_token_counts, token_files

file_token_counts, token_files = parse_files('DEV')

open('report.txt', 'w').close()
print_unique_words()
print_document_count()
tokenizer.print_freq(freq_dict)
