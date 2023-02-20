from Main import freq_dict, document_count

def print_unique_words():                                          #Prints the number of unique words to report.txt
    with open("report.txt", "a") as f:
        f.write("unique_words: " + str(len(freq_dict)) + "\n")
        f.write("-------------------------------" + "\n")

def print_document_count():                                        #Prints the document count to report.txt
    with open("report.txt", "a") as f:
        f.write("document_count: " + str(document_count)+ "\n")
        f.write("-------------------------------" + "\n")