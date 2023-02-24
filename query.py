import json, os

index = ""
docID_dict = ""

def load_dict():
    global index
    global docID_dict
    with open('storage/index_mappings.json', 'r+') as file:
        index = json.load(file)
    
    with open('storage/docID_mappings.json', 'r+') as file:
        docID_dict = json.load(file)

def search(query):
    
    list_of_list_of_urls = []

    for q in query.lower().split():                                  #gets all query terms
        if (q not in index):             
            #list_of_list_of_urls.append([])
            print ('hi')
            print (q)
            print (type(q))
            continue
        #sorts all documents that contain the query term by their tf_idf score
        sorted_docs = sorted(list(index[q]['doc_ids'].items()), key = lambda x: x[1]['tf_idf'], reverse=True) 

        list_of_urls = []                               #list_of_urls contains all the urls mapped from the docID's in sorted_docs [url1, url2, url3... etc.]
        for doc in sorted_docs:                      
            list_of_urls.append(docID_dict[str(doc[1]['id'])] + '\n')

        list_of_list_of_urls.append(list_of_urls)                    #this contains all list_of_urls from all the query terms, and will intersect them to find similar urls
    
    if len(list_of_list_of_urls) == 0:
        return
    resulting_list_of_urls = list_of_list_of_urls[0]

    for i in list_of_list_of_urls[1:]:                               #performs the intersection between all the list_of_urls in list_of_list_of_urls
        resulting_list_of_urls = list(set(resulting_list_of_urls).intersection(set(i)) )

    # with open('result.txt', 'a') as file:                            #writes all the docs associated with the query term to result.txt
    #     file.write(query + '\n')
    #     for doc in resulting_list_of_urls[0:5]:
    #         file.write(doc)
    #     file.write ('\n')
    for doc in resulting_list_of_urls[0:5]:
        print (doc.strip())
    print ('\n')

        