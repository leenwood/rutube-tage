import numpy as np
import pandas as pd

import faiss


from sentence_transformers import SentenceTransformer

class FaissSearchSingleton:
    _instance = None

    def __new__(cls, model_path = './model', tags_path = './preprocessed_tags.csv', index_path = './index_file.index'):
        if cls._instance is None:
            cls._instance = super(FaissSearchSingleton, cls).__new__(cls)
            cls._instance.model = SentenceTransformer(model_path)
            cls._instance.tags = pd.read_csv(tags_path)
            cls._instance.index = faiss.read_index(index_path)
        return cls._instance

    def get_vectors(self, information):
        info_vector = self.model.encode(information, convert_to_tensor=True).cpu().numpy()
        return info_vector

    def get_predictions(self, vector, top_n=3) -> list:
        search_vectors = vector.astype('float32')
        faiss.normalize_L2(search_vectors)
        scores, predictions = self.index.search(search_vectors, top_n)
        for j, i in enumerate(predictions):
            print("SCORES", scores[j])
            print("PREDICTION_by_title", np.array(self.tags['full_name'].values.tolist())[predictions[j]])
            print("\n")
            return np.array(self.tags['full_name'].values.tolist())[predictions[j]]