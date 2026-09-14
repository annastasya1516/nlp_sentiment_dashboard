import pickle
import os

def load_model_assets():

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    model_path = os.path.join(
        base_dir,
        "models",
        "model_sentimen.pkl"
    )

    vectorizer_path = os.path.join(
        base_dir,
        "models",
        "vectorizer_tfidf.pkl"
    )

    with open(model_path, "rb") as f_model:
        model = pickle.load(f_model)

    with open(vectorizer_path, "rb") as f_vectorizer:
        vectorizer = pickle.load(f_vectorizer)

    return model, vectorizer