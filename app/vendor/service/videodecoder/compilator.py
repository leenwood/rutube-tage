import os
import pickle
import nltk
from collections import Counter
import string
import pymorphy3



# Загрузка стоп-слов
nltk.download("stopwords")
from nltk.corpus import stopwords

# Инициализация лемматизатора
morph = pymorphy3.MorphAnalyzer()





def get_most_popular_words(text: str, top_n: int = 15) -> str:
    # Приводим текст к нижнему регистру
    text = text.lower()

    # Удаляем знаки препинания
    translator = str.maketrans("", "", string.punctuation)
    text = text.translate(translator)

    # Разбиваем текст на слова
    words = text.split()

    # Лемматизация слов
    lemmatized_words = [morph.parse(word)[0].normal_form for word in words]

    # Убираем стоп-слова и оставляем только значимые слова
    filtered_words = [word for word in lemmatized_words if word not in russian_stopwords]

    # Подсчитываем наиболее часто встречающиеся слова
    word_counts = Counter(filtered_words)

    # Преобразуем результат в строку
    # result = ", ".join([f"{word}: {count}" for word, count in word_counts.most_common(top_n)])
    result = ", ".join([f"{word}" for word, count in word_counts.most_common(top_n)])

    return result


def get_russian_stopwords():
    # Имя файла для хранения стоп-слов
    stopwords_file = 'russian_stopwords.pkl'

    # Если файл с сохранёнными стоп-словами существует, загружаем их
    if os.path.exists(stopwords_file):
        with open(stopwords_file, 'rb') as f:
            russian_stopwords = pickle.load(f)
    else:
        # Иначе загружаем из интернета и сохраняем в файл
        russian_stopwords = set(stopwords.words('russian'))
        # Добавляем дополнительные стоп-слова
        russian_stopwords.add('всё')
        russian_stopwords.add('это')
        russian_stopwords.add('ещё')
        russian_stopwords.add('поэтому')

        # Сохраняем в файл
        with open(stopwords_file, 'wb') as f:
            pickle.dump(russian_stopwords, f)

    return russian_stopwords

# Получаем список стоп-слов на русском языке
russian_stopwords = get_russian_stopwords()

def compiling_file(path: str) -> str:
    """
    Чтение текста из файла, создание краткого резюме и запись его в файл.

    :param path: Путь к исходному текстовому файлу
    """
    # Открываем файл в кодировке UTF-8
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()  # Читаем содержимое файла
    summary = get_most_popular_words(content)

    print(summary)
    return summary