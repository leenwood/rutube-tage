import os

from .KeywordsExtractor import KeywordsExtractor
from .MediaSplitter import MediaSplitter
from .normalizator import normalize_name
from .TranscriptionSpeech import TranscriptionSpeech

import pandas as pd

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



        # Проход по всем файлам в директории
        for filename in os.listdir(self.input_dir):
            # Читаем существующий CSV-файл в DataFrame
            df = pd.read_csv(f'{self.output_dir}/{name}.csv')
            if filename.endswith(f".{extension}"):  # Проверка на видеофайл
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


    def DecodeVideo(self, filename: str) -> str | None:
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


# import os
# import pandas as pd
# from concurrent.futures import ThreadPoolExecutor, as_completed
#
# from .keywordsextractor import KeywordsExtractor
# from .mediaspliter import MediaSplitter
# from .normalizator import normalize_name
# from .speech import TranscriptionSpeech
#
# class DataProcessor:
#     def __init__(self, input_dir: str, output_dir: str, max_workers: int = 4):
#         """
#         Инициализация класса DataProcessor.
#
#         :param input_dir: Базовая директория, в которой хранятся текстовые файлы
#         :param output_dir: Директория для сохранения результатов обработки
#         :param max_workers: Максимальное количество потоков для обработки
#         """
#         self.input_dir = input_dir
#         self.output_dir = output_dir
#         self.max_workers = max_workers
#
#     def process_file(self, filename, df, extractor, transSpeech):
#         """
#         Обработка одного видеофайла.
#
#         :param filename: Имя видеофайла
#         :param df: DataFrame с данными
#         :param extractor: Экземпляр KeywordsExtractor
#         :param transSpeech: Экземпляр TranscriptionSpeech
#         """
#         video_id = normalize_name(filename)  # ИД видео — название файла без расширения
#
#         # Проверка на существование обработки
#         if not df.loc[df['video_id'] == video_id, 'popular_words'].isnull().any():
#             print(f"Видео {video_id} уже обработано")
#             return
#
#         splitter = MediaSplitter(video_id)
#         video = splitter.open_file(self.input_dir)
#
#         if not splitter.split_files(video, self.output_dir):
#             return
#
#         transSpeech.stt(video_id)
#
#         with open(f'./{self.output_dir}/text/{video_id}.txt', 'r', encoding='utf-8') as file:
#             content = file.read()  # Читаем содержимое файла
#         words = extractor.get_most_popular_words(content)
#
#         # Находим строку с нужным video_id и обновляем поле popular_words
#         df.loc[df['video_id'] == video_id, 'popular_words'] = words
#
#         # Сохраняем обновленный DataFrame обратно в CSV
#         df.to_csv(f'{self.output_dir}/result.csv', index=False, encoding='utf-8')
#         print(f"Видео {video_id} обработано")
#
#     def RenderCsvFile(self, name: str = "result", extension: str = 'mp4'):
#         """
#         Обработка видеофайлов из директории и сохранение результатов в CSV с использованием многопоточности.
#
#         :param name: Название выходного CSV файла (без расширения)
#         :param extension: Расширение файлов для обработки (по умолчанию mp4)
#         """
#         transSpeech = TranscriptionSpeech()
#         extractor = KeywordsExtractor()
#
#         # Читаем существующий CSV-файл в DataFrame
#         df = pd.read_csv(f'{self.output_dir}/{name}.csv')
#
#         # Проход по всем файлам в директории с использованием многопоточности
#         with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
#             future_to_filename = {
#                 executor.submit(self.process_file, filename, df, extractor, transSpeech): filename
#                 for filename in os.listdir(self.input_dir) if filename.endswith(f".{extension}")
#             }
#
#             # Ожидаем завершения всех задач
#             for future in as_completed(future_to_filename):
#                 filename = future_to_filename[future]
#                 try:
#                     future.result()
#                 except Exception as exc:
#                     print(f"Ошибка при обработке файла {filename}: {exc}")
#
