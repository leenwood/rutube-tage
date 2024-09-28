import http
from time import time

import whisper

from service.reader import FileReader
from vendor.service.videodecoder import DataProcessor

# class MyHandler(http.server.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#         self.wfile.write(b"Hello, this is a response from the server!")
#         return
#
# # Функция для запуска HTTP сервера
# def run_http_server():
#     global server
#     with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
#         print(f"Serving HTTP on port {PORT}")
#         server = httpd
#         httpd.serve_forever()
#
# # Функция для обработки команд с терминала
# def run_terminal():
#     global server
#     while True:
#         command = input("Enter command: ").strip().lower()
#
#         if command == "stop":
#             print("Stopping server...")
#             if server:
#                 server.shutdown()
#             break
#         elif command == "status":
#             print(f"Server is running on port {PORT}")
#         else:
#             print(f"Unknown command: {command}. Try 'status' or 'stop'.")

def run():
    # spliter = Spliter("1dbc2732cedac20ab19cf7dbc17ce3b8")
    # spliter.SaveFiles()
    #
    # TranscriptionSpeech().stt("1dbc2732cedac20ab19cf7dbc17ce3b8")

    dp = DataProcessor('input', 'output')
    dp.RenderCsvFile()
    # fr = FileReader()
    # fr.GetTitleAndDescription('1')
    # results = fr.GetFileNames()
    # count = 0
    # for item in results:
    #     count += 1
    #     print(f'{count} id: {item}, state: {results[item]}')
    # result = dp.DecodeVideo('4a4dc53857b44464613052a331877a07')
    # print(result)
    return True

if __name__ == '__main__':
    # print(whisper.available_models())
    run()

    # # Запускаем HTTP сервер в отдельном потоке
    # server_thread = threading.Thread(target=run_http_server)
    # server_thread.daemon = True  # Поток завершится, если основной поток завершится
    # server_thread.start()
    #
    # # Запускаем ввод команд через терминал
    # run_terminal()