import torch
import numpy as np
from RAG import *
import re

def prompt(input, prompt_path, return_num, embedding_model, data_path="data/data.csv", embeddings_path='data/embeddings.npy'):
    with open(prompt_path, 'r') as file:
        full_text = file.read()
    strings = get_sim(input, return_num, embedding_model, data_path, embeddings_path)
    reg = ""
    for _, string in strings:
        reg += string + "\n"
    
    user_pattern = r"\{\{USER_QUESTION\}\}"
    rag_pattern = r"\{\{RAG_CONTEXT\}\}"
    full_text = re.sub(user_pattern, input, full_text)
    full_text = re.sub(rag_pattern, reg, full_text)
    return full_text
    
if __name__ == '__main__':
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5", similarity_fn_name=SimilarityFunction.DOT_PRODUCT)
    print(prompt("What is a good major for using art and math", "prompts/fact.txt", 5, embedding_model, data_path="data/bulletinData.csv"))