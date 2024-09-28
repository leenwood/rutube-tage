import os
import pickle
import nltk
from collections import Counter
import string
import pymorphy3


class KeywordsExtractor:
    def __init__(self, stopwords_file='russian_stopwords.pkl'):
        # Имя файла для хранения стоп-слов
        self.stopwords_file = stopwords_file
        # Получаем стоп-слова при инициализации класса
        self.russian_stopwords = self._get_russian_stopwords()
        self.morph = pymorphy3.MorphAnalyzer()

    def _get_russian_stopwords(self):
        """
        Загрузка стоп-слов. Если файл с сохранёнными стоп-словами существует, загружаем их,
        иначе загружаем стандартные стоп-слова из NLTK и сохраняем их в файл.
        """
        if os.path.exists(self.stopwords_file):
            with open(self.stopwords_file, 'rb') as f:
                russian_stopwords = pickle.load(f)
        else:
            # Загрузка стоп-слов
            nltk.download("stopwords")
            from nltk.corpus import stopwords
            # Иначе загружаем из интернета и сохраняем в файл
            russian_stopwords = set(stopwords.words('russian'))
            # Добавляем дополнительные стоп-слова
            additional_stopwords = {'всё', 'это', 'ещё', 'поэтому'}
            russian_stopwords.update(additional_stopwords)

            # Сохраняем в файл
            with open(self.stopwords_file, 'wb') as f:
                pickle.dump(russian_stopwords, f)

        return russian_stopwords

    def _preprocess_text(self, text: str) -> list:
        """
        Приведение текста к нижнему регистру, удаление знаков препинания, разбиение текста на слова,
        лемматизация и удаление стоп-слов.

        :param text: Исходный текст
        :return: Список отфильтрованных слов
        """
        # Приводим текст к нижнему регистру
        text = text.lower()

        # Удаляем знаки препинания
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)

        # Разбиваем текст на слова
        words = text.split()

        # Лемматизация слов
        lemmatized_words = [self.morph.parse(word)[0].normal_form for word in words]

        # Убираем стоп-слова
        filtered_words = [word for word in lemmatized_words if word not in self.russian_stopwords]

        return filtered_words

    def get_most_popular_words(self, text: str, top_n: int = 25) -> str:
        """
        Подсчет и получение наиболее популярных слов в тексте.

        :param text: Исходный текст
        :param top_n: Количество наиболее популярных слов
        :return: Строка с самыми популярными словами
        """
        filtered_words = self._preprocess_text(text)

        # Подсчитываем наиболее часто встречающиеся слова
        word_counts = Counter(filtered_words)

        # Преобразуем результат в строку
        result = ", ".join([f"{word}" for word, count in word_counts.most_common(top_n)])

        return result

    def compile_file(self, path: str) -> str:
        """
        Чтение текста из файла и создание краткого резюме на основе ключевых слов.

        :param path: Путь к исходному текстовому файлу
        :return: Резюме с ключевыми словами
        """
        # Открываем файл в кодировке UTF-8
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()  # Читаем содержимое файла

        # Получаем ключевые слова
        summary = self.get_most_popular_words(content)

        print(summary)
        return summary