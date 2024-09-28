import pandas as pd


class Processor:
    def __init__(self, filename_tags: str, filename_dataset: str):
        self.filename_tags = filename_tags
        self.filename_dataset = filename_dataset
        self.tags_df = None
        self.dataset = None

    def compile(self):
        self.tags_df = self.process_tags(self.filename_tags)
        self.dataset = self.process_dataset(self.filename_dataset)

    def process_dataset(self, filename_dataset):
        dataset = pd.read_csv(filename_dataset)
        dataset = dataset[~dataset['tags'].isna()]

        dataset['clean_tags'] = dataset['tags'].apply(self.clean_tags)

        dataset['meta_info'] = dataset['title'] + ' ' + dataset['description']
        dataset['tags'] = dataset['tags'].apply(lambda x: x.replace('\n', ''))

        return dataset

    def process_tags(self, filename_tags):
        df = pd.read_csv(filename_tags)
        df.dropna(subset=['Уровень 1 (iab)'], inplace=True)
        df['full_name'] = df.apply(self.get_full_tag, axis=1)
        return df

    def get_full_tag(self,tag):
        tag_1, tag_2, tag_3 = tag['Уровень 1 (iab)'], tag['Уровень 2 (iab)'], tag['Уровень 3 (iab)']

        if isinstance(tag_1, str) and isinstance(tag_2, str) and isinstance(tag_3, str):
            return tag_1 + ': ' + tag_2 + ': ' + tag_3
        elif isinstance(tag_1, str) and isinstance(tag_2, str) and not isinstance(tag_3, str):
            return tag_1 + ': ' + tag_2
        elif isinstance(tag_1, str) and not isinstance(tag_2, str):
            return tag_1
        return
    def clean_tags(self, tags):
        if not isinstance(tags, str):
            return
        tags = tags.split(',')
        new_tags = []
        for tag in tags:
            splited_tags = tag.split(':')
            splited_tags = list(map(lambda x: x.strip().capitalize(), splited_tags))
            new_tags.append(': '.join(splited_tags))
        return new_tags



