from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

model = SentenceTransformer("intfloat/multilingual-e5-large")
translations_dir = Path("translations")

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

def visualize_embeddings(embeddings, texts=None, folder=None, xlim=(-0.15, 0.15), ylim=(-0.15, 0.15)):
    embeddings = np.array(embeddings)

    # Compute centroid in original space
    centroid = np.mean(embeddings, axis=0)

    # Project to 2D
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(embeddings)
    centroid_2d = pca.transform([centroid])[0]

    # Plot
    plt.figure(figsize=(6,6))
    x = reduced[:, 0]
    y = reduced[:, 1]

    plt.scatter(x, y, label="Translations")
    plt.scatter(centroid_2d[0], centroid_2d[1], marker='x', color='red', label="Centroid")

    # Optional labels
    if texts:
        for i, txt in enumerate(texts):
            plt.text(x[i], y[i], str(i), fontsize=8)

    plt.title("Embedding Visualization (PCA)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.legend()

    # Force manual axis limits
    plt.xlim(xlim)
    plt.ylim(ylim)

    # Save plot to file
    if folder is None:
        folder = Path("translations")
    folder.mkdir(exist_ok=True)
    save_path = folder / "embedding_plot.png"
    plt.savefig(save_path)
    plt.close()
    print(f"Saved embedding plot to: {save_path}")


def create_file_with_text(file_path, content):
    translations_dir.mkdir(exist_ok=True)
    with file_path.open("w", encoding="utf-8") as f:
        f.write(content)

def get_centermost_text():
    for folder in Path("translations").iterdir():
        if folder.is_dir():
            texts = []
            for file in folder.glob("*.txt"):
                file_name = file.stem + "_centermost.txt"
                content = file.read_text(encoding="utf-8")
                texts.append(content)

            embeddings = model.encode(
                ["passage: " + t for t in texts],
                normalize_embeddings=True  
            )

            visualize_embeddings(embeddings, texts, folder=folder, xlim=(-0.15, 0.15), ylim=(-0.15, 0.15))

            # for i, emb in enumerate(embeddings):
            #     print(f"\nVector {i} (length {len(emb)}):")
            #     print(emb)

            embeddings = np.array(embeddings)

            centroid = np.mean(embeddings, axis=0)

            def cosine_similarity(a, b):
                return np.dot(a, b)

            scores = [cosine_similarity(e, centroid) for e in embeddings]

            best_index = np.argmax(scores)
            best_text = texts[best_index]

            # print("Centermost text:", best_text)
            create_file_with_text(translations_dir / file_name, best_text)

if __name__ == "__main__":
    get_centermost_text()