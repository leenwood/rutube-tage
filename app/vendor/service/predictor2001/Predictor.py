from .Processor import FaissSearchSingleton


class Predictor:

    def __init__(self):
        # Создание экземпляра синглтона
        self._search_instance = FaissSearchSingleton()


    def predict(self, title: str = "", description: str = "", popular_words: str = "") -> list:
        # Получение вектора
        vector = self._search_instance.get_vectors([f"{title.lower()} {description.lower()} {popular_words}"])
        # Получение предсказаний
        return (self._search_instance.get_predictions(vector)).tolist()