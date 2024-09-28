from moviepy.audio.io import AudioFileClip

from .normalizator import normalize_name
from moviepy.editor import VideoFileClip

#
# # Переименование класса на более осмысленное название
# class MediaSplitter:
#     """
#     Класс для разделения видео и аудио дорожек из медиафайла.
#     """
#
#     def __init__(self, filename: str):
#         self.filename = normalize_name(filename)
#
#     def open_file(self, path: str) -> VideoFileClip:
#         """
#         Открывает видеофайл и нормализует его имя для дальнейшего использования.
#
#         :param filename: Имя файла без расширения.
#         :return: Объект видеофайла и нормализованное имя файла.
#         """
#         # Загружаем видеофайл
#         input_video = VideoFileClip(f"./{path}/{self.filename}.mp4")
#
#         return input_video
#
#     def split_files(self, video: VideoFileClip, path: str) -> bool:
#         """
#         Сохраняет аудио в формате MP3 и видео без аудиодорожки в формате MP4.
#
#         :return: True при успешном сохранении.
#         """
#         try:
#             # Сохраняем аудиодорожку в формате MP3
#             video.audio.write_audiofile(f"./{path}/audios/{self.filename}.mp3")
#
#             # Сохраняем видеодорожку без звука в формате MP4
#             video.without_audio().write_videofile(f"./{path}/videos/{self.filename}.mp4")
#         except Exception as e:
#             print(f"An error occurred: {str(e)}")
#             return False
#
#         return True


class MediaSplitter:
    """
    Класс для обработки медиафайлов: разделения видео и аудио дорожек.
    """

    def __init__(self, filename: str):
        self.filename = normalize_name(filename)

    def open_file(self, path: str) -> VideoFileClip:
        """
        Открывает видеофайл и нормализует его имя для дальнейшего использования.

        :param path: Путь к файлу.
        :return: Объект видеофайла.
        """
        # Загружаем видеофайл
        input_video = VideoFileClip(f"./{path}/{self.filename}.mp4")
        return input_video

    def split_files(self, video: VideoFileClip, path: str) -> bool:
        """
        Сохраняет аудио и видео (только первые 5 минут) в соответствующих форматах.

        :param video: Объект видеофайла.
        :param path: Путь для сохранения.
        :return: True при успешном сохранении, иначе False.
        """
        try:
            # Определяем максимальную длительность в 5 минут (300 секунд)
            max_duration = 300

            # Обрезаем видео и аудио на первые 5 минут
            video_clip = video.subclip(0, min(max_duration, video.duration))

            # Если аудиодорожка есть, сохраняем её первые 5 минут
            if video.audio:
                audio_clip = video_clip.audio
                audio_clip.write_audiofile(f"./{path}/audios/{self.filename}.mp3")

            # Сохраняем видеодорожку (первые 5 минут) без звука в формате MP4
            video_clip.without_audio().write_videofile(f"./{path}/videos/{self.filename}.mp4")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

        return True