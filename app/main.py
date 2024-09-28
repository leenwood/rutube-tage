import argparse
import cgi
import http.server
import json
import os
import socketserver
import threading

from vendor.service.predictor2001 import Predictor
from vendor.service.videodecoder import DataProcessor
from vendor.service.webserver import WebServerHandler

PORT = 8000
UPLOAD_DIR = "input"  # Директория для сохранения файлов

# Проверяем, существует ли директория, и создаем её, если нет
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# Функция для запуска HTTP сервера
def run_http_server():
    global server
    with socketserver.TCPServer(("", PORT), WebServerHandler) as httpd:
        print(f"Serving HTTP on port {PORT}")
        server = httpd
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopping...")
        finally:
            httpd.server_close()
            print("Server closed")


def run():
    from vendor.service.videodecoder import DataProcessor
    dp = DataProcessor('input', 'output')
    dp.RenderCsvFile()
    return True


# Ваша функция для обработки видео
def process_video():
    video_id = '0ac7ed0507b2364e40030d11bf52ee5d'

    # Путь к файлу JSON
    json_file_path = 'videos.json'

    # Проверяем, существует ли файл
    if os.path.exists(json_file_path):
        # Загружаем существующие данные из файла
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            video_data = json.load(json_file)
    else:
        raise FileNotFoundError(f"Файл {json_file_path} не найден.")

    print(f"Пытаемся получить tags")
    predictor = Predictor()
    tags = predictor.predict(video_data[video_id]['title'], video_data[video_id]['description'], video_data[video_id]['popular_words'])


    # Сохраняем теги в JSON
    video_data[video_id]['tags'] = tags

    # Сохраняем обновленные данные обратно в JSON-файл
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(video_data, json_file, ensure_ascii=False, indent=4)

    print(f"Обработка видео завершена: {video_id}")

def predict_all_videos_from_input():
    dp = DataProcessor('input', 'output')
    dp.RenderJsonFile()

def run_console_app():
    predict_all_videos_from_input()
    # Здесь ваш код для консольного приложения
    print("console ending")

if __name__ == '__main__':
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description='Start either HTTP server or console application.')
    parser.add_argument('mode', choices=['server', 'console'], help='Mode to run: server or console')
    args = parser.parse_args()

    if args.mode == 'server':
        # Запускаем HTTP сервер в отдельном потоке
        server_thread = threading.Thread(target=run_http_server)
        server_thread.daemon = True  # Поток завершится, если основной поток завершится
        server_thread.start()

        # Выводим лог запуска сервера в консоль
        print(f"Server started on port {PORT}. Waiting for requests...")

        # Добавляем обработку завершения работы через KeyboardInterrupt
        try:
            server_thread.join()  # Ожидание завершения потока
        except KeyboardInterrupt:
            print("Shutting down the server.")

    elif args.mode == 'console':
        # Запускаем консольное приложение
        run_console_app()
