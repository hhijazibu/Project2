# Project2
This is a repository for Project 2 for my software engineering class. I have selected the project of creating a smart Document analyzer. In order to complete this project, I will first need to be able to upload any supported document type. The document analyzer will then run on the file, extract all text and using NLP it will be able to understand the text, summarize it, and lastly provide a sentiment analysis. It has database integration using mongoDB, additionally queuing has been added to the project for certain apis.

# How to Run
Step 1: GitCLone This repository
Step 2: run the following command in terminal: docker build -t flask-app. (Ensure you have docker on your pc)
Step 3: docker run -p 5001:5001 flask-app
Step 4: go to localhost:5001

# User Flow
Upon entering the website you see the login page, the page allows new users to register if an account is not created. In order to ensure safety data sanitization techniques are employed to reduce chances of attacks.

After logging in the user can then upload a document (PDF or Image). The file which is uploaded has its text stripped and displayed in raw form. The sentiment analysis score is displayed indicating weather its positive or negative, or neutral. As you scroll more, a summary is shown highlighting the main points of the texts. Lastly keywords are extracted and redirect you to wikipedia pages showing the definitions of these words.

# DEMO VIDEO
https://drive.google.com/file/d/1NSwXZMqkERTMoXoD0tncL5OJLAEKN4N9/view?usp=sharing

# Files:
