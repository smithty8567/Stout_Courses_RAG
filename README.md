# Stout_Courses_RAG
This was a 3 week project conducted as a last project for the Advanced Machine Learning course at UW-Stout. The goal of the project was to create a Retieval Augmented Generator which is capable of answering questions utilizing documents specific to UW-Stout. 

Authors: Tyler Smith, Kyler Nikolai, Matthew Peplinski, Aaron Smith

## What is a RAG
A RAG leverages existing word imbedding models and LLM's for qurey reasoning and response. External information which an LLM was not trained on is stored in an embedding space using an existing embedding model, which will be accessed by a query. When a query is made, it too is ran through the same embedding model as the external data in order to directly compare embedded information. External information whose embedding is simmilar to the query is retireved, and the information is proveded as an augmentation to the users original query. The then sends the user query and simmilar information to an LLM where the RAG limits the LLM to utilizing only external information provided for response generation. This is used to limit the LLM from halucinating responses, or pulling information from non-authoritative sources. The Response is then provided to the user.

## Data
For this project, a major section of the work went into collecting and processing the data. To do this we utilized Beautifulsoup, response, and Selenium for webscraping the UW-Stout bulletin. We collected several types of data which was uitlized by the RAG, and seperated for the purposes of embedding. Data collection for programs was non-trivial due to inconsitent website layout and inconsistent program requirements.

[Stout Courses](https://bulletin.uwstout.edu/content.php?catoid=29&navoid=774):
 - Course name and number
 - Course Description
 - Prerequisites

[Stout Programs](https://bulletin.uwstout.edu/content.php?catoid=29&navoid=773):
 - Program name (Majors, Minors, Concentrations)
 - Program description
 - Stout Core requirements
 - Major Studies requirements

## Using Existing Models
Embedding Model:
- [BGE v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5)
- Made specifically for use with RAG's
- 512 token length limit for embedding
- - Data chunking is required to adhere to this limit

LLM
- gpt 5 mini
- requires use of an OpenAI API key
- Queries costed less than 1 cent per query

## GUI
The base GUI has three main sections;
1. Search Bar: Allows user to enter a question (response is generated after pressing the "Ask" button)
2. Response Section: Displays the HTML formated output for better visual clarity
3. New Query/ Follow up section: Allows user to clear all previous context to ask a new question, or retain previous questions and answers as additional information sent with the API call to the gpt model.

![Base GUI](https://github.com/smithty8567/Stout_Courses_RAG/blob/main/gui_pictures/base_gui.png)

### Asking about courses
![Course Query](https://github.com/smithty8567/Stout_Courses_RAG/blob/main/gui_pictures/graph_theory_query.png)

### Asking general questions
![Art and Math](https://github.com/smithty8567/Stout_Courses_RAG/blob/main/gui_pictures/math_and_art_query.png)

### More complex question
In this query we ask to compare the Applied Math and Computer Science program and the Computer Science program.
![AMCS vs CS](https://github.com/smithty8567/Stout_Courses_RAG/blob/main/gui_pictures/amcs_vs_cs.png)


