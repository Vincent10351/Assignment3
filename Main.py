from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.stem import PorterStemmer
import os

index_file = 'index_file'

def parse_files(root):
    for filename in os.listdir(root):
        for json_file in os.listdir(filename):
            pass

parse_files('ANALYST')
