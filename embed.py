from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("intfloat/multilingual-e5-large")

texts = [
    "The cat is sitting on the mat.",
    "A cat is resting on a rug.",
    "There is a dog outside.",
]

# Important for E5 models: prefix with "query:" or "passage:"
embeddings = model.encode(
    ["passage: " + t for t in texts],
    normalize_embeddings=True  # critical for cosine similarity
)

embeddings = np.array(embeddings)

# 1. Compute centroid
centroid = np.mean(embeddings, axis=0)

# 2. Compute cosine similarity to centroid
def cosine_similarity(a, b):
    return np.dot(a, b)

scores = [cosine_similarity(e, centroid) for e in embeddings]

# 3. Pick best
best_index = np.argmax(scores)
best_text = texts[best_index]

print("Centermost text:", best_text)