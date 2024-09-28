import os
import pandas as pd

from service.videodecoder.normalizator import normalize_name


class FileReader:
    def __init__(self, input_dir: str = 'input', extension: str = 'mp4', output_dir: str = 'output'):
        self._input_dir = input_dir
        self._extension = extension
        self.output_dir = output_dir


    def GetFileNames(self) -> dict:
        result = {}
        for filename in os.listdir(self._input_dir):
            if filename.endswith(f".{self._extension}"):
                result[normalize_name(filename)] = {'title': '', 'description': '', 'popular_words': ''}
        return result

    def GetTitleAndDescription(self, id: str):
        df = pd.read_csv(os.path.join(f"./{self.output_dir}/", 'result.csv'))
        df.head()