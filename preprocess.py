from sentence_transformers import SentenceTransformer
import csv
import json
import numpy as np
from tqdm import tqdm

def read_data(path="data/data.csv"):
    with open(path, mode='r', encoding="utf-8") as file:
        data = csv.reader(file)
        strings = []
        for row in data:
            string = row[0]
            strings.append(string)
        return strings

def chunk_data(path="data/stout_programs_update.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    major_descriptions = []
    major_courses = []
    course_split_num = 10
    description_check = 1250

    for row in tqdm(data, desc="Chunking data"):
        # Remove "Go to program website " from the beginning of row["text"]
        description = row["text"].replace("Go to program website ", '')

        program_name = row["program_name"]

        if row["concentration"] is not None:
            program_name = row["program_name"] + " (" + row["concentration"] + ")"

        if description.strip() != "":
            major_descriptions.append(program_name + " Description: " + description + "url:" + row["url"])

        courses_chunks = row["required_courses"].split("Major Studies:")
        if len(courses_chunks) == 1:
            courses_chunks = row["required_courses"].split("Additional concentration courses:")

        # Stout core classes
        major_courses.append(program_name + " " + courses_chunks[0])

        # No leading whitespace
        major_studies = courses_chunks[1].lstrip()

        if len(major_studies) > description_check:
            split_courses = major_studies.split(":")

            if len(split_courses) < course_split_num:
                course_split_num = len(split_courses)//2

            courses = []
            for i in range(0, len(split_courses), course_split_num):
                course = ":".join(split_courses[i: i+course_split_num])
                courses.append(course)
            for course_chunk in courses:
                # Cleaning leading whitespaces
                course_chunk = course_chunk.lstrip()
                if course_chunk.strip() != "":
                    major_courses.append(program_name + " Major Required Courses: " + course_chunk)
        else:
            if major_studies.strip() != "":
                major_courses.append(program_name + " Major Required Courses: " + major_studies)

    with open("data/majorCourses.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for major_course in major_courses:
            writer.writerow([major_course])

    with open("data/majorDescriptions.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for major_description in major_descriptions:
            writer.writerow([major_description])


def preprocess(path1="data/majorDescriptions.csv", path2="data/majorCourses.csv",path3="data/coursesData.csv",output1='data/majorDescriptionsEmbeddings.npy',output2='data/majorCoursesEmbeddings', output3='data/courseEmbeddings.npy'):
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    strings1 = read_data(path1)
    strings = []
    for string in strings1:
        strings.append(string.split("url:")[0])
    strings2 = read_data(path2)
    strings3 = read_data(path3)

    embeddings1 = embedding_model.encode(strings, normalize_embeddings=True)
    embeddings2 = embedding_model.encode(strings2, normalize_embeddings=True)
    embeddings3 = embedding_model.encode(strings3, normalize_embeddings=True)

    np.save(output1, embeddings1)
    np.save(output2, embeddings2)
    np.save(output3, embeddings3)
        
if __name__ == '__main__':
    chunk_data()
    preprocess(path1="data/majorDescriptions.csv", path2="data/majorCourses.csv",output1='data/majorDescriptionEmbeddings.npy', output2='data/majorCourseEmbeddings.npy')
