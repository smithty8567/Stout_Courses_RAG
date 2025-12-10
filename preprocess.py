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

def chunk_data(path="stout_programs.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    major_descriptions = []
    major_courses = []
    course_split_num = 10
    description_check = 500

    for row in tqdm(data, desc="Chunking data"):
        # Remove "Go to program website " from the beginning of row["text"]
        description = row["text"].replace("Go to program website ", '')

        if row["concentration"] is not None:
            concentration = row["program_name"] + " (" + row["concentration"] + ")"
            if description.strip() != "":
                major_descriptions.append(concentration + " Description: " + description)

            courses_chunks = row["required_courses"].split(":.")

            for chunked_course in courses_chunks:
                # No leading whitespace
                chunked_course = chunked_course.lstrip()

                if len(chunked_course) > description_check:
                    split_courses = chunked_course.split(",")
                    courses = []
                    for i in range(0, len(split_courses), course_split_num):
                        course = ",".join(split_courses[i: i+course_split_num])
                        courses.append(course)
                    for course_chunk in courses:
                        # Cleaning leading whitespaces
                        course_chunk = course_chunk.lstrip()
                        if course_chunk.strip() != "":
                            major_courses.append(concentration + " Required Courses: " + course_chunk)
                else:
                    if chunked_course.strip() != "":
                        major_courses.append(concentration + " Required Courses: " + chunked_course)
        else:

            if description.strip() != "":
                major_descriptions.append(row["program_name"] + " Description: " + description)

            courses_chunks = row["required_courses"].split(":.")

            for chunked_course in courses_chunks:
                # Cleaning leading whitespaces
                chunked_course = chunked_course.lstrip()

                if len(chunked_course) > description_check:
                    split_courses = chunked_course.split(",")
                    courses = []
                    for i in range(0, len(split_courses), course_split_num):
                        course = ",".join(split_courses[i: i + course_split_num])
                        courses.append(course)
                    for course_chunk in courses:
                        # Cleaning leading whitespaces
                        course_chunk = course_chunk.lstrip()
                        if course_chunk.strip() != "":
                            major_courses.append(row["program_name"] + " Required Courses: " + course_chunk)
                else:
                    if chunked_course.strip() != "":
                        major_courses.append(row["program_name"] + " Required Courses: " + chunked_course)

        with open("data/majorCourses.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for major_course in major_courses:
                writer.writerow([major_course])

        with open("data/majorDescriptions.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for major_description in major_descriptions:
                writer.writerow([major_description])


def preprocess(path1="data/data.csv", path2="data/coursesData.csv",output1='data/embeddings.npy', output2='data/courseEmbeddings.npy'):
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    strings1 = read_data(path1)
    strings2 = read_data(path2)
    embeddings1 = embedding_model.encode(strings1, normalize_embeddings=True)
    embeddings2 = embedding_model.encode(strings2, normalize_embeddings=True)
    np.save(output1, embeddings1)
    np.save(output2, embeddings2)
        
if __name__ == '__main__':
    chunk_data()
    preprocess(path1="data/majorDescriptions.csv", path2="data/majorCourses.csv",output1='data/majorDescriptionEmbeddings.npy', output2='data/majorCourseEmbeddings.npy')
