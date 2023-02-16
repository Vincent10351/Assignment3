from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
import os
import json


index_file = 'index_file'
document_count = 0


def parse_files(root):
    global document_count
    for filename in os.listdir(root):                                               #opens the root directory
        for json_files in os.listdir(os.path.join(root, filename)):                 #opens each file within the root directory
            with open(os.path.join(root, filename, json_files)) as json_file:       #opens each json_file within the sub-directory
                loaded_json = json.load(json_file)                                  #loads each json_file 
                content = loaded_json['content']
                text = BeautifulSoup(content, 'lxml')
                print (text)
                document_count += 1
    print (document_count)

parse_files('ANALYST')

#Wednesday: All day 
#Thursday: 6pm - whenever
#Friday: All day 
