from src.metrics import calculate_episode_success, episode_sentiments
from src.scrape import get_episode_info, clean_poll_vote
import pandas as pd
import numpy as np
import os


class AnimeProfile:
    def __init__(self, base_url):
        self.base_url = base_url
        self.df_episode_info = pd.DataFrame()

    def fetch_episode_info(self):
        episode_info = get_episode_info(self.base_url)
        self.df_episode_info = pd.DataFrame(
            {
                'episode_num': np.arange(1, len(episode_info) + 1),
                'episode_title': [title for title, _, _, _ in episode_info],
                'episode_date': [date for _, date, _, _ in episode_info],
                'poll_vote': [vote for _, _, _, vote, in episode_info],
                'forum_link': [link for _, _, link, _ in episode_info],
            }
        )
        self.df_episode_info = clean_poll_vote(self.df_episode_info)

    def calculate_sentiments(self):
        self.df_episode_info['sentiments'] = self.df_episode_info.apply(
            lambda x: episode_sentiments(x['forum_link']), axis=1
        )

    def calculate_success_metrics(self):
        self.df_episode_info = calculate_episode_success(self.df_episode_info)

    def save_to_csv(self, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        self.df_episode_info.to_csv(file_path, index=False)

    def perform_etl(self, file_path):
        self.fetch_episode_info()
        self.calculate_sentiments()
        self.calculate_success_metrics()
        self.save_to_csv(file_path)
