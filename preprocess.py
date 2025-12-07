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

def chunk_data(path="bulletin2.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    chunking = True
    chunks = []
    course_split_num = 10
    description_length = 500
    description_check = 600

    for row in tqdm(data, desc="Chunking data"):
        if row["concentration"] is not None:
            # Remove "Go to program website " from the beginning of row["text"]
            description = row["text"].replace("Go to program website ", '')
            description_chunks = []
            while chunking:
                if len(description) > description_check:
                    description_chunks.append(description[:description_length])
                    description = description[description_length:]
                if len(description) < description_check:
                    chunking = False

            for chunked_description in description_chunks:
                chunks.append(row["concentration"] + " Description: " + chunked_description)


            courses_chunks = row["required_courses"].split(".")

            for chunked_course in courses_chunks:
                if len(chunked_course) > description_check:
                    split_courses = chunked_course.split(",")
                    courses = []
                    for i in range(0, len(split_courses), course_split_num):
                        course = ",".join(split_courses[i: i+course_split_num])
                        courses.append(course)
                    for course_chunk in courses:
                        chunks.append(row["concentration"] + " Required Courses: " + course_chunk)
                else:
                    chunks.append(row["concentration"] + " Required Courses: " + chunked_course)
        else:
            description = row["text"].replace("Go to program website ", '')
            description_chunks = []

            while chunking:
                if len(description) > description_check:
                    description_chunks.append(description[:description_length])
                    description = description[description_length:]
                if len(description) < description_check:
                    chunking = False

            for chunked_description in description_chunks:
                chunks.append(row["program_name"] + " Description: " + chunked_description)

            courses_chunks = row["required_courses"].split(".")

            for chunked_course in courses_chunks:
                if len(chunked_course) > description_check:
                    split_courses = chunked_course.split(",")
                    courses = []
                    for i in range(0, len(split_courses), course_split_num):
                        course = ",".join(split_courses[i: i + course_split_num])
                        courses.append(course)
                    for course_chunk in courses:
                        chunks.append(row["program_name"] + " Required Courses: " + course_chunk)
                else:
                    chunks.append(row["program_name"] + " Required Courses: " + chunked_course)

        with open("bulletinData.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for chunk in chunks:
                writer.writerow([chunk])

def preprocess(path="data/data.csv", output='data/embeddings.npy'):
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    strings = read_data(path)
    # longest_string = max(strings, key=len)
    # print("Longest string length in data:", len(longest_string))
    # print("Longest String: " + longest_string)
    # embedding = embedding_model.encode(longest_string, normalize_embeddings=True)
    # print("Embedding shape:", embedding.shape)
    embeddings = embedding_model.encode(strings, normalize_embeddings=True)
    np.save(output, embeddings)
        
if __name__ == '__main__':
    # chunk_data()
    preprocess(path="data/bulletinData.csv")