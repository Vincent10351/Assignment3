from collections import defaultdict
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
import re

def tokenize(TextFilePath):
    """
    This function opens a text file and tokenizes each word, returning a list of tokens.
    Because we're reading each line in the file, then each word within that line, it will 
    be O(m*n) time where n is the number of words in a file and m
    is the length of the regex string
    """
    res = []
    with open(TextFilePath, 'rb') as file:
        stopWords = set(stopwords.words('english'))   
        print (stopWords)
        for line in file:
            line = line.decode(encoding = 'utf-8').split(" ")
            for word in line:
                new_word = re.sub('[^0-9A-Za-z]', " ", word).lower().split()
                for word in new_word:
                    if word not in stopWords:
                        res.append(word)
    return res


def computeWordFrequencies(list_tokens):
    """
    This function counts the number of occurrences of each token within a list and returns
    a dictionary where the key is a token and the value is the number of occurrences.
    Will be O(n) time, where n is the number of tokens within the list of tokens, 
    and we're read one token at a time
    """
    my_dict = defaultdict(int)
    for token in list_tokens:
        my_dict[token] += 1
    return my_dict


def print_freq(freq):
    """
    This function sorts by value and then key, and prints each token and 
    its number of occurrences
    O(nlogn) time where n is the number of unique tokens in a dictionary, and the 
    sorted function has a time complexity of nlogn
    """
    freq = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    i_len = min(1000, len(freq))
    
    with open("report.txt", "a") as f:
        for i in range(i_len):
            f.write(freq[i][0] + " => " + str(freq[i][1]) + "\n")
        f.write("-------------------------------" + "\n")
            
