# SentenceTransformer holds the embedding model
# Documentation on how to use the model to find similarity, embed,
# and to the retrieval process
# https://sbert.net/docs/sentence_transformer/usage/usage.html

from sentence_transformers import SentenceTransformer, SimilarityFunction

embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5", similarity_fn_name=SimilarityFunction.DOT_PRODUCT)

# Data after processing
sentences = ["Cats are gray.", "dogs are gray", "cats weigh 15 lbs"]
input = ["What color are cats?"]
embeddings = embedding_model.encode(sentences, normalize_embeddings=True)
input_embedding = embedding_model.encode(input, normalize_embeddings=True)

similarity = embedding_model.similarity(embeddings,input_embedding)

print(similarity[0:])
