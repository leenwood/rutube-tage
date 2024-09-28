import http
from time import time

from vendor.service.videodecoder import TranscriptionSpeech, compiling_file
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

    return True

if __name__ == '__main__':
    run()

    # # Запускаем HTTP сервер в отдельном потоке
    # server_thread = threading.Thread(target=run_http_server)
    # server_thread.daemon = True  # Поток завершится, если основной поток завершится
    # server_thread.start()
    #
    # # Запускаем ввод команд через терминал
    # run_terminal()