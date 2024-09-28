import cgi
import http.server
import os
import json
import socketserver
import threading

from .helper import extract_first_frame
from ..predictor2001 import Predictor
from ..videodecoder import DataProcessor

UPLOAD_DIR = 'input'
VIDEOS_JSON_PATH = 'videos.json'

def load_videos_data():
    """Загрузка данных видео из JSON-файла."""
    json_file_path = "./videos.json"
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

# Ваша функция для обработки видео
def process_video(video_id):
    # Здесь можно добавить любую логику обработки видео
    print(f"Начинается обработка видео: {video_id}")

    # Пример получения популярных слов
    dp = DataProcessor('input', 'output')
    words = dp.GetDecodeVideo(video_id)

    # Путь к файлу JSON
    json_file_path = 'videos.json'

    # Проверяем, существует ли файл
    if os.path.exists(json_file_path):
        # Загружаем существующие данные из файла
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            video_data = json.load(json_file)
    else:
        raise FileNotFoundError(f"Файл {json_file_path} не найден.")

    # Проверяем, есть ли уже запись для video_id, и обновляем ее
    if video_id in video_data:
        video_data[video_id]['popular_words'] = words
    else:
        print(f"Видео с ID {video_id} не найдено в JSON-файле.")
        return

    # Сохраняем обновленные данные обратно в JSON-файл
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(video_data, json_file, ensure_ascii=False, indent=4)

    print(f"Пытаемся получить tags")
    predictor = Predictor()
    tags = predictor.predict(video_data[video_id]['title'], video_data[video_id]['description'], video_data[video_id]['popular_words'])


    # Сохраняем теги в JSON
    video_data[video_id]['tags'] = tags

    # Сохраняем обновленные данные обратно в JSON-файл
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(video_data, json_file, ensure_ascii=False, indent=4)

    print(f"Обработка видео завершена: {video_id}")


class WebServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Отправляем статус 200 (OK)
        self.send_response(200)

        # Устанавливаем заголовок Content-Type на "text/html" для возврата HTML-страницы
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Определяем путь запроса
        path = self.path

        # Определяем пути для разных маршрутов
        if path == "/":
            file_path = "template/index.html"
        elif path.startswith("/video/"):
            print("tried find video")
            # Извлекаем имя видеофайла из запроса
            video_file_name = path.split("/video/")[1]

            # Полный путь до видеофайла
            file_path = os.path.join('./', UPLOAD_DIR, video_file_name)
            print(file_path)

            if os.path.exists(file_path):
                print("found")
                # Если файл существует, отдаем его
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(os.path.getsize(file_path)))
                self.end_headers()

                # Отправляем содержимое видеофайла
                with open(file_path, 'rb') as file:
                    self.wfile.write(file.read())
            else:
                print("not found")
                # Если файл не найден, возвращаем 404
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>404 Not Found</h1><p>The requested video file was not found.</p>")
        elif path == "/upload":
            file_path = "template/upload.html"
        elif path == "/videos":
            # Новый маршрут для /list
            file_path = "template/list.html"

            # Проверяем наличие файла videos.json
            videos_json_path = "videos.json"
            if os.path.exists(videos_json_path):
                # Чтение данных из videos.json
                with open(videos_json_path, 'r', encoding='utf-8') as json_file:
                    videos_data = json.load(json_file)

                # Формируем HTML для списка видео
                videos_list_html = ""
                for video_id, video_info in videos_data.items():
                    video_title = video_info.get('title', 'No Title')
                    video_description = video_info.get('description', 'No Description')
                    video_tags = ", ".join(video_info.get('tags', []))
                    video_link = f'/view/{video_id}'

                    # Добавляем каждое видео в HTML
                    videos_list_html += f'''
                    <div class="video-item">
                        <h2>{video_title}</h2>
                        <p>{video_description}</p>
                        <p><strong>Tags:</strong> {video_tags}</p>
                        <a href="{video_link}">Watch Video</a>
                    </div>
                    <hr>
                    '''

                # Чтение шаблона list.html
                with open(file_path, 'r', encoding='utf-8') as html_file:
                    html_content = html_file.read()

                # Вставка сгенерированного списка видео в HTML
                html_content = html_content.replace("{{videos_list}}", videos_list_html)

                # Отправляем сгенерированный HTML
                self.wfile.write(html_content.encode())
            else:
                # Если videos.json не существует, возвращаем сообщение
                self.send_response(404)
                self.wfile.write(b"<h1>No videos found</h1><p>No videos have been uploaded yet.</p>")
        elif path.startswith("/preview/"):
            print("tried find video preview")

            # Извлекаем имя видеофайла из запроса
            video_file_name = path.split("/video_preview/")[1]

            # Полный путь до видеофайла
            file_path = os.path.join('./', UPLOAD_DIR, video_file_name)
            print(file_path)

            if os.path.exists(file_path):
                print("found video for preview")

                # Извлекаем первый кадр видео
                image_data = extract_first_frame(file_path)

                if image_data:
                    # Если кадр успешно извлечен, возвращаем его в ответе
                    self.send_response(200)
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", str(len(image_data)))
                    self.end_headers()

                    # Отправляем содержимое изображения
                    self.wfile.write(image_data)
                else:
                    print("could not extract frame")
                    # Если не удалось извлечь кадр, возвращаем 500 ошибку
                    self.send_response(500)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<h1>500 Internal Server Error</h1><p>Could not extract the preview frame.</p>")
            else:
                print("video not found")
                # Если файл не найден, возвращаем 404
                self.send_response(404)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>404 Not Found</h1><p>The requested video file was not found.</p>")
        elif path.startswith("/view/"):
            # Извлекаем ID из пути, формат URL: /view/{id}
            video_id = path.split("/view/")[1]
            videos_data = load_videos_data()
            # Ищем данные видео в JSON
            video_info = videos_data.get(video_id)

            if video_info:
                file_path = "template/view.html"
                with open(file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()

                # Замена плейсхолдеров в шаблоне на данные из JSON
                html_content = html_content.replace("{{video_id}}", video_id)
                html_content = html_content.replace("{{video_title}}", video_info.get('title', 'Unknown Title'))
                tags = video_info.get('tags', [])
                # Преобразование списка тегов в строку. Если список пустой, выводим 'Empty tags'
                tags_str = ', '.join(tags) if tags else 'Empty tags'

                # Замена {{tags}} в html_content
                html_content = html_content.replace("{{tags}}", tags_str)
                html_content = html_content.replace("{{video_description}}",
                                                    video_info.get('description', 'No description available'))

                # Отправляем динамически сгенерированный HTML
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(html_content.encode())
            else:
                # Если видео не найдено в JSON, возвращаем 404
                self.send_response(404)
                error_message = b"<h1>404 Not Found</h1><p>The requested video was not found on the server.</p>"
                self.wfile.write(error_message)
            return
        else:
            # Если путь не найден, возвращаем 404
            self.send_response(404)
            error_message = b"<h1>404 Not Found</h1><p>The requested file was not found on the server.</p>"
            self.wfile.write(error_message)
            return

        # Чтение содержимого HTML-файла, если он существует
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                html_content = file.read()

            # Отправляем содержимое HTML-файла
            self.wfile.write(html_content)
        else:
            # Если файл не найден, отправляем сообщение об ошибке
            error_message = b"<h1>404 Not Found</h1><p>The requested file was not found on the server.</p>"
            self.wfile.write(error_message)

    def do_POST(self):
        # Устанавливаем заголовки ответа
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Получаем данные формы
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})

        # Проверяем наличие файла и полей title и description в форме
        if "file" in form and "title" in form and "description" in form:
            file_field = form["file"]
            title = form["title"].value
            description = form["description"].value

            if file_field.filename:
                # Получаем имя файла и путь для сохранения
                file_name = os.path.basename(file_field.filename)
                file_path = os.path.join(UPLOAD_DIR, file_name)

                # Сохраняем файл на диск
                with open(file_path, "wb") as output_file:
                    output_file.write(file_field.file.read())

                # Создаём уникальный videoId (например, используя имя файла)
                video_id = os.path.splitext(file_name)[0]

                # Сохраняем данные о видео в JSON
                if os.path.exists(VIDEOS_JSON_PATH):
                    with open(VIDEOS_JSON_PATH, "r", encoding="utf-8") as json_file:
                        videos_data = json.load(json_file)
                else:
                    videos_data = {}

                # Обновляем данные о видео
                videos_data[video_id] = {
                    "title": title,
                    "description": description
                }

                # Записываем обновлённые данные обратно в JSON
                with open(VIDEOS_JSON_PATH, "w", encoding="utf-8") as json_file:
                    json.dump(videos_data, json_file, ensure_ascii=False, indent=4)

                # Асинхронная обработка видео
                threading.Thread(target=process_video, args=(video_id,)).start()

                # Отправляем ответ об успешной загрузке
                self.wfile.write(f"Файл успешно загружен: {file_name}".encode("utf-8"))

                # Редирект на страницу просмотра файла (имитация с базовым ответом)
                self.wfile.write(f"<script>window.location.href = '/view/{video_id}';</script>".encode('utf-8'))
            else:
                # Если файл не выбран, возвращаем ошибку
                self.wfile.write("Файл не выбран".encode('utf-8'))
        else:
            # Если одного из полей не хватает, возвращаем ошибку
            self.wfile.write("Ошибка: файл, заголовок или описание не найдены в запросе".encode('utf-8'))


