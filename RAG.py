# SentenceTransformer holds the embedding model
# Documentation on how to use the model to find similarity, embed,
# and to the retrieval process
# https://sbert.net/docs/sentence_transformer/usage/usage.html
from sentence_transformers import SentenceTransformer, SimilarityFunction
import torch
import numpy as np
from preprocess import *

def get_sim(input, return_num, embedding_model, data_path="data/data.csv", embeddings_path='data/embeddings.npy'):
    embeddings = np.load(embeddings_path)
    data = read_data(data_path)
    input_embedding = embedding_model.encode(input, normalize_embeddings=True)

    similarity = embedding_model.similarity(embeddings,input_embedding)
    similarity = torch.squeeze(similarity, dim=1)
    
    values, indices = torch.topk(similarity, k=return_num, largest=True)
    output = []
    for val, i in zip(values, indices):
        output.append([val.item(), data[i]])
    return output


if __name__ == '__main__':
    embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5", similarity_fn_name=SimilarityFunction.DOT_PRODUCT)
    print(get_sim("what are good courses to take in the applied math and computer science major", 5, embedding_model, data_path="data/bulletinData.csv"))