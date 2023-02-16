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

def tokenize(soup):
    dict_tokens = defaultdict(int)
    text = soup.get_text()
    for token in re.split("[^a-zA-Z']+", text.lower()):
        token = stemmer.stem(token.strip()) # current issue at stemmer, tokens not fully spelled out.
        if is_valid_token(token):
            unique_words.add(token)
            dict_tokens[token] += 1
    return dict_tokens

def is_valid_token(token):
    return token not in stop_words and len(token) > 2

def parse_files(root):
    global document_count
    file_token_counts = defaultdict(lambda: defaultdict(int))
    token_files = defaultdict(set)
    for filename in os.listdir(root):
        for json_files in os.listdir(os.path.join(root, filename)):
            with open(os.path.join(root, filename, json_files)) as json_file:
                if document_count == 1000: # added stop at 1000 documents to create test inverted_index
                    return file_token_counts, token_files
                loaded_json = json.load(json_file)
                content = loaded_json['content']
                text = BeautifulSoup(content, 'lxml')

                cur_list_tokens = tokenize(text)
                file_token_counts[filename][json_files] = cur_list_tokens
                for token in cur_list_tokens.keys():
                    token_files[token].add(json_files)
                document_count += 1
    return file_token_counts, token_files

file_token_counts, token_files = parse_files('DEV')

with open('inverted_index_test.txt', 'a') as f:
    f.write(f"Total Documents: '{document_count}'\nTotal Unique Words: '{len(unique_words)}'\n")
    for filename, files in file_token_counts.items():
        for file_name, tokens in files.items():
            for token, count in tokens.items():
                file_containing_token = file_name
                f.write(f"Token: '{token}' | Frequency: {count} | Found in file: {file_containing_token}\n")

#Wednesday: All day 
#Thursday: 6pm - whenever
#Friday: All day 