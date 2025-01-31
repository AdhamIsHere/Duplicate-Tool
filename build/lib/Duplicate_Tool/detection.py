import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .embedding import get_embedding
from .preprocessing import preprocess_code, handle_overlapping_chunks

def detect_duplicate_groups(java_code, threshold=0.95):
    chunks = preprocess_code(java_code)  # This includes formatting and chunk extraction
    filtered_chunks = handle_overlapping_chunks(chunks)
    embeddings = [get_embedding(chunk) for chunk in filtered_chunks]

    # Compute similarity matrix between all pairs of filtered_chunks
    similarity_matrix = np.zeros((len(filtered_chunks), len(filtered_chunks)))
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = cosine_similarity(embeddings[i].numpy(), embeddings[j].numpy())[0][0]
            similarity_matrix[i, j] = similarity
            similarity_matrix[j, i] = similarity  # Symmetric matrix

    # Find groups of similar filtered_chunks using a simple threshold for similarity
    visited = set()
    duplicate_groups = []

    for i in range(len(filtered_chunks)):
        if i not in visited:
            group = [i]  # Start a new group
            visited.add(i)
            # Explore the group by checking similarities
            for j in range(i + 1, len(filtered_chunks)):
                if similarity_matrix[i, j] > threshold and j not in visited:
                    group.append(j)
                    visited.add(j)
            if len(group) > 1:  # If a group has more than one chunk, it's a duplicate group
                duplicate_groups.append([filtered_chunks[index] for index in group])

    return duplicate_groups