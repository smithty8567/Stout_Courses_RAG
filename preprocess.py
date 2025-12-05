from sentence_transformers import SentenceTransformer
import csv
import numpy as np

def read_data(path="data/data.csv"):
    with open(path, mode='r') as file:
        data = csv.reader(file)
        strings = []
        for row in data:
            string = row[0]
            strings.append(string)
        return strings

def preprocess(path="data/data.csv", output='data/embeddings.npy'):
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    strings = read_data(path)
    embeddings = embedding_model.encode(strings, normalize_embeddings=True)
    np.save(output, embeddings)
        
if __name__ == '__main__':
    preprocess()