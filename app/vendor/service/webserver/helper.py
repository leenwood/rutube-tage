import cv2
from PIL import Image
from io import BytesIO

def extract_first_frame(video_path):
    # Открываем видео с помощью opencv
    video_capture = cv2.VideoCapture(video_path)

    # Читаем первый кадр
    success, frame = video_capture.read()
    video_capture.release()

    if success:
        # Конвертируем изображение из формата OpenCV (BGR) в RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Преобразуем массив в изображение с использованием PIL
        pil_image = Image.fromarray(frame_rgb)

        # Сохраняем изображение в байтовый поток в формате JPEG
        byte_io = BytesIO()
        pil_image.save(byte_io, 'JPEG')
        byte_io.seek(0)

        return byte_io.getvalue()
    else:
        return None
