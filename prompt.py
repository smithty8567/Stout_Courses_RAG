from openai import OpenAI
from RAG import *
import re
import os

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
    prompt_gpt = prompt("What are some required math courses for Applied Mathematics and Computer Science?", "prompts/fact.txt", 5, embedding_model, data_path="data/bulletinData.csv")
    print("Prompt: " + prompt_gpt)
    print("---------------------------------------------------------")

    # if "OPENAI_API_KEY" in os.environ:
    #     client = OpenAI()
    #
    #     response = client.responses.create(
    #         model="gpt-5-mini",
    #         input=prompt_gpt
    #     )
    #
    #     print(response.output_text)