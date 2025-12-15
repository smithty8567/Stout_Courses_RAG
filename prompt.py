from openai import OpenAI
from RAG import *
from tkhtmlview import HTMLScrolledText
import customtkinter as ctk
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


def run_gui():
    if "OPENAI_API_KEY" in os.environ:
        client = OpenAI()
        embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5",
                                              similarity_fn_name=SimilarityFunction.DOT_PRODUCT)

    # Set up the GUI sections
    root = ctk.CTk()
    root.title("Stout Bulletin RAG")
    root.geometry("900x600")
    top = ctk.CTkFrame(root, fg_color="transparent")
    top.pack(pady=10)
    middle = ctk.CTkFrame(root, fg_color="transparent")
    middle.pack(fill="both", expand=True, pady=(10, 0))
    middle.pack_propagate(False)
    bottom = ctk.CTkFrame(root, fg_color="transparent")
    bottom.pack(pady=10, anchor="center")

    previous_context = ""

    def run_query():
        nonlocal previous_context
        user_input = query_entry.get().strip()
        if previous_context:
            user_input = f"{previous_context}\nFollow-up question: {user_input}"

        output_box.set_html("<p><b>Thinking...</b></p>")
        root.update()

        ## Update model and prompt in this section
        prompt_gpt = prompt(user_input, "prompts/detailedPromptInfo.txt", 5, embedding_model)
        response = client.responses.create(model="gpt-5-mini", input=prompt_gpt)
        gpt_output = response.output_text

        previous_context += f"\nUser: {user_input}\nAssistant: {gpt_output}\n"
        output_box.set_html(gpt_output)

    def reset_query():
        nonlocal previous_context
        query_entry.delete(0, ctk.END)
        previous_context = ""
        output_box.set_html("<p><i>Response will appear here...</i></p>")
        query_entry.focus()

    def prepare_follow_up():
        query_entry.delete(0, ctk.END)
        query_entry.focus()

    # Adding in each of the GUI elements (fyi html view does not like to play nice)
    query_entry = ctk.CTkEntry(top, placeholder_text="Enter query", width=600, corner_radius=20)
    query_entry.pack(side="left", padx=(0, 10))

    ask_button = ctk.CTkButton(top, text="Ask", command=run_query, corner_radius=20)
    ask_button.pack(side="left")

    output_box = HTMLScrolledText(middle, html="<p><i>Response will appear here...</i></p>", width=500, height=300)
    output_box.pack(padx=10, pady=10, fill="both", expand=True)

    reset_button = ctk.CTkButton(bottom, text="New Query", corner_radius=20, width=200, command=reset_query)
    reset_button.pack(side="left", padx=10)

    follow_up_button = ctk.CTkButton(bottom, text="Follow Up Query", corner_radius=20, width=200,
                                     command=prepare_follow_up)
    follow_up_button.pack(side="left", padx=10)

    root.mainloop()


if __name__ == '__main__':
    run_gui()