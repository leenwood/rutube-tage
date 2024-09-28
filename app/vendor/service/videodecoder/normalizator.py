import re

# Функция для нормализации имени в данном проекте
def normalize_name(name: str) -> str:
    name = re.sub(r"\.mp3$", "", name)
    name = re.sub(r"\.mp4$", "", name)
    name = re.sub(r"\.txt$", "", name)
    return name