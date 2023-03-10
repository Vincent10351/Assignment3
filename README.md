# Assignment3 Search Engine
Vincent Nguyen & Justin Chan & Jay Makwana & Ashley Sun

Our search engine gathers data from approximately 56,000 pages from 88 different domains and organizes the data into an inverted index. In order to return query searches within 300ms and minimize memory , we implemented a partial index with separate files for each letter of the alphabet

To use the search engine, we implemented a local web GUI with Flask. The user types in a query into the "Vincenettes Search Engine" and clicks the submit box. Afterwards, the user will receive the top K (5 in this case) links in an unordered list. The user can click on the hyperlink in order to directly go to the webpage. 
(talk about flask/ui implementation)