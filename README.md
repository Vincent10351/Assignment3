# Assignment3 Search Engine
### Vincent Nguyen & Justin Chan & Jay Makwana & Ashley Sun

## Overview
Our search engine gathers data from approximately 56,000 pages from 88 different domains and organizes the data into an inverted index. In order to return query searches within 300ms and minimize memory, we implemented a partial index with separate files for each letter of the alphabet

## Prerequisites and Dependencies
Python 3.9  
MacOS or Linux  
Flask micro web framework  
BeautifulSoup  

***First, open your machine's terminal. Then run these commands:***  
> pip install python3  
> pip install flask  
> pip install bs4  

## Set up  
1. Download our code from github via cloning the repository and navigate to said directory within your machine's terminal.   

    ***For Linux:***  
    > cd /home/user/my_project  

    ***For macOS:***  
    > cd /Users/user/my_project 

    ***Then run this command to clone the repository***   
    > git clone https://github.com/Vincent10351/Assignment3.git  

2. Set up the index by running python3 Index.py within your terminal. This should take approximately 2 hours to complete  

    ***Run this command to create the index:***
    > python3 Index.py  

3. Once the command has finished running, the index will have been successfully created. To make a query search, click on the link that is provided in the terminal after the completion of *"python3 Index.py"* or alternatively you can copy the link provided and paste it into your web browser.

## Using the UI
To use the search engine, we implemented a local web GUI with Flask. The user types in a query into the "Vincenettes Search Engine" and clicks the submit box. Afterwards, the user will receive the top K (5 in this case) links in an unordered list. 