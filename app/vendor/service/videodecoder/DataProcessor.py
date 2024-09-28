import csv
import json
import os

from .KeywordsExtractor import KeywordsExtractor
from .MediaSplitter import MediaSplitter
from .normalizator import normalize_name
from .TranscriptionSpeech import TranscriptionSpeech

import pandas as pd

from ..predictor2001 import Predictor


class DataProcessor:
    def __init__(self, input_dir: str, output_dir: str):
        """
        Инициализация класса TextProcessor.

        :param input_dir: Базовая директория, в которой хранятся текстовые файлы
        :param output_dir: Директория для сохранения результатов обработки
        """
        self.input_dir = input_dir
        self.output_dir = output_dir

    def RenderCsvFile(self, name: str = "result", extension: str = 'mp4'):
        """
        Обработка видеофайлов из директории и сохранение результатов в CSV.

        :param extension: расширения файла который открывается (мп4)
        :param name: Название выходного CSV файла (без расширения)
        """

        transSpeech = TranscriptionSpeech()
        extractor = KeywordsExtractor()

        count = 0

        # Проход по всем файлам в директории
        for filename in os.listdir(self.input_dir):
            # Читаем существующий CSV-файл в DataFrame
            df = pd.read_csv(f'{self.output_dir}/{name}.csv')
            if filename.endswith(f".{extension}"):  # Проверка на видеофайл
                count += 1
                print(f'Цикл {count}')
                # file_path = os.path.join(self.input_dir, filename)

                # Извлекаем ИД (например, из названия файла)
                video_id = normalize_name(filename) # ИД видео — название файла без расширения

                # Проверка на существование обработки
                if not df.loc[df['video_id'] == video_id, 'popular_words'].isnull().any():
                    print(f"Видео {video_id} уже обработано")
                    continue

                splitter = MediaSplitter(video_id)
                video = splitter.open_file(self.input_dir)

                if not(splitter.split_files(video, self.output_dir)):
                    continue

                # Расшифровка видео
                transSpeech.stt(video_id)

                # Открываем файл с расшифровкой
                with open(f'./{self.output_dir}/text/{video_id}.txt', 'r', encoding='utf-8') as file:
                    content = file.read()  # Читаем содержимое файла
                words = extractor.get_most_popular_words(content)

                # Находим строку с нужным video_id и обновляем поле popular_words
                df.loc[df['video_id'] == video_id, 'popular_words'] = words

                # Сохраняем обновленный DataFrame обратно в CSV
                df.to_csv(f'{self.output_dir}/{name}.csv', index=False, encoding='utf-8')



    def RenderJsonFile(self, name: str = "result", extension: str = 'mp4'):
        transSpeech = TranscriptionSpeech()
        extractor = KeywordsExtractor()

        count = 0

        # Загружаем существующий JSON-файл или создаем пустой словарь
        json_file_path = os.path.join(self.output_dir, f'{name}.json')
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {}

        # Загружаем CSV файл с описаниями и названиями
        csv_file_path = os.path.join(self.input_dir, 'input.csv')
        video_metadata = {}
        if os.path.exists(csv_file_path):
            with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    video_metadata[row['video_id']] = {
                        'title': row['title'],
                        'description': row['description']
                    }

        # Проход по всем файлам в директории
        for filename in os.listdir(self.input_dir):
            if filename.endswith(f".{extension}"):  # Проверка на видеофайл
                count += 1
                print(f'Цикл {count}')

                # Извлекаем ИД (например, из названия файла)
                video_id = normalize_name(filename)  # ИД видео — название файла без расширения

                # Проверяем, существует ли видео в JSON и было ли уже обработано
                if video_id in data and data[video_id].get('popular_words'):
                    print(f"Видео {video_id} уже обработано")
                else:
                    # Открытие видео и разделение на части
                    splitter = MediaSplitter(video_id)
                    video = splitter.open_file(self.input_dir)

                    if not splitter.split_files(video, self.output_dir):
                        continue

                    # Расшифровка видео
                    transSpeech.stt(video_id)

                    # Открываем файл с расшифровкой
                    transcript_path = os.path.join(self.output_dir, 'text', f'{video_id}.txt')
                    with open(transcript_path, 'r', encoding='utf-8') as file:
                        content = file.read()  # Читаем содержимое файла

                    # Извлекаем популярные слова
                    words = extractor.get_most_popular_words(content)

                    # Если видео еще не было в JSON, добавляем новую запись
                    if video_id not in data:
                        # Получаем метаданные из CSV, если есть
                        title = video_metadata.get(video_id, {}).get('title', "")
                        description = video_metadata.get(video_id, {}).get('description', "")

                        data[video_id] = {
                            "title": title,  # Добавляем заголовок из CSV
                            "description": description,  # Добавляем описание из CSV
                            "tags": [],  # Можно добавить теги, если нужно
                            "popular_words": words
                        }
                    else:
                        # Обновляем популярные слова для уже существующего видео
                        data[video_id]['popular_words'] = words

                    # Сохраняем обновленные данные обратно в JSON
                    with open(json_file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                # predict tags
                print(f"Пытаемся получить tags")
                if video_id in data and data[video_id].get('tags'):
                    print(f"Видео {video_id} уже имеет теги")
                else:
                    predictor = Predictor()
                    tags = predictor.predict(data[video_id]['title'], data[video_id]['description'],
                                             data[video_id]['popular_words'])

                    # Сохраняем теги в JSON
                    data[video_id]['tags'] = tags

                    # Сохраняем обновленные данные обратно в JSON-файл
                    with open(json_file_path, 'w', encoding='utf-8') as json_file:
                        json.dump(data, json_file, ensure_ascii=False, indent=4)

                    print(f"Обработка видео завершена: {video_id}")

                print(f"Видео {video_id} успешно обработано")



    def SaveDecodeVideo(self, filename: str) -> str | None:
        if filename is None:
            return None

        # Читаем существующий CSV-файл в DataFrame
        df = pd.read_csv(f'{self.output_dir}/result.csv')
        # Извлекаем ИД (например, из названия файла)
        video_id = normalize_name(filename)  # ИД видео — название файла без расширения

        # Проверка на существование обработки
        if not df.loc[df['video_id'] == video_id, 'popular_words'].isnull().any():
            popular_words = df.loc[df['video_id'] == video_id, 'popular_words'].values[0]
            print(f"Видео {video_id} уже обработано, {popular_words}")
            return popular_words

        splitter = MediaSplitter(video_id)
        video = splitter.open_file(self.input_dir)

        if not (splitter.split_files(video, self.output_dir)):
            return None

        transSpeech = TranscriptionSpeech()
        extractor = KeywordsExtractor()

        # Расшифровка видео
        transSpeech.stt(video_id)

        # Открываем файл с расшифровкой
        with open(f'./{self.output_dir}/text/{video_id}.txt', 'r', encoding='utf-8') as file:
            content = file.read()  # Читаем содержимое файла
        words = extractor.get_most_popular_words(content)

        # Находим строку с нужным video_id и обновляем поле popular_words
        df.loc[df['video_id'] == video_id, 'popular_words'] = words

        # Сохраняем обновленный DataFrame обратно в CSV
        df.to_csv(f'{self.output_dir}/result.csv', index=False, encoding='utf-8')
        return words


    def GetDecodeVideo(self, filename: str) -> str | None:
        if filename is None:
            return None

        # Извлекаем ИД (например, из названия файла)
        video_id = normalize_name(filename)  # ИД видео — название файла без расширения


        splitter = MediaSplitter(video_id)
        video = splitter.open_file(self.input_dir)

        if not (splitter.split_files(video, self.output_dir)):
            return None

        transSpeech = TranscriptionSpeech()
        extractor = KeywordsExtractor()

        # Расшифровка видео
        transSpeech.stt(video_id)

        # Открываем файл с расшифровкой
        with open(f'./{self.output_dir}/text/{video_id}.txt', 'r', encoding='utf-8') as file:
            content = file.read()  # Читаем содержимое файла
        words = extractor.get_most_popular_words(content)

        return words