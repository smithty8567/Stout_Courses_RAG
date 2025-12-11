from openai import OpenAI
from RAG import *
import re
import os

def prompt(input, prompt_path, return_num, embedding_model,
           major_description="data/majorDescriptions.csv",
           major_course="data/majorCourses.csv",
           course_data="data/coursesData.csv",
           major_des_embed='data/majorDescriptionEmbeddings.npy',
           major_course_embed='data/majorCourseEmbeddings.npy',
           course_embed='data/courseEmbeddings.npy'):
    with open(prompt_path, 'r') as file:
        full_text = file.read()
    major_desc = get_sim(input, return_num, embedding_model, major_description, major_des_embed)
    major_courses = get_sim(input, return_num+5, embedding_model, major_course, major_course_embed)
    courses = get_sim(input, return_num+5, embedding_model, course_data, course_embed)

    reg1 = ""
    reg2 = ""
    reg3 = ""

    for _, string in major_desc:
        reg3 += string + "\n"

    for _, string in major_courses:
        reg2 += string + "\n"

    for _, string in courses:
        reg1 += string + "\n"
    
    user_pattern = r"\{\{USER_QUESTION\}\}"
    rag_pattern1 = r"\{\{RAG_CONTEXT1\}\}"
    rag_pattern2 = r"\{\{RAG_CONTEXT2\}\}"
    rag_pattern3 = r"\{\{RAG_CONTEXT3\}\}"
    full_text = re.sub(user_pattern, input, full_text)
    full_text = re.sub(rag_pattern1, reg1, full_text)
    full_text = re.sub(rag_pattern2, reg2, full_text)
    full_text = re.sub(rag_pattern3, reg3, full_text)
    return full_text
    
if __name__ == '__main__':
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5", similarity_fn_name=SimilarityFunction.DOT_PRODUCT)
    prompt_gpt = prompt("What are all classes I need to take Advanced Machine Learning if I come in with 0 credits?", "prompts/detailedPromptInfo.txt", 5, embedding_model)
    print("Prompt: " + prompt_gpt)
    print("---------------------------------------------------------")

    if "OPENAI_API_KEY" in os.environ:
        client = OpenAI()

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt_gpt
        )

        print(response.output_text)