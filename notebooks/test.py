# %%
# notebooks/test.py
from src.profile import AnimeProfile
from src.scrape import get_episode_info

# %%
friren = AnimeProfile('https://myanimelist.net/anime/52991/Sousou_no_Frieren/episode')
# %%
friren.perform_etl('../data/friren_episode_sentiments.csv')
friren.df_episode_info.head()
# %%
df = get_episode_info('https://myanimelist.net/anime/52991/Sousou_no_Frieren/episode')
# %%
df[0]
# %%
