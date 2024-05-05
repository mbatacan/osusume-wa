# %% Notebook to develop functions to scrape reviews from MyAnimeList and calculate metrics
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')


# %%
def scrape_forum_comments(url):
    comments = []
    show = 0

    while True:
        page_url = f"{url}&show={show}"
        response = requests.get(page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        forum_messages = soup.find_all('div', class_='forum-topic-message')

        # If there are no forum messages on the page, break the loop
        if not forum_messages:
            break

        for message in forum_messages:
            content = message.find('table', class_='body clearfix')
            if content:
                comment_text = content.find('td').get_text(strip=True)
                comments.append(comment_text)

        # Increment the show parameter by 50 for the next page
        show += 50

    return comments


def analyze_sentiments(comments):
    sia = SentimentIntensityAnalyzer()
    sentiments = []
    for comment in comments:
        score = sia.polarity_scores(comment)
        sentiments.append(score)
    return sentiments


def summarize_sentiments(sentiments):
    positive = sum(1 for s in sentiments if s['compound'] > 0.05)
    neutral = sum(1 for s in sentiments if -0.05 <= s['compound'] <= 0.05)
    negative = sum(1 for s in sentiments if s['compound'] < -0.05)
    total = len(sentiments)
    return {
        'positive': positive / total * 100,
        'neutral': neutral / total * 100,
        'negative': negative / total * 100,
    }


def episode_sentiments(url):
    while True:
        try:
            comments = scrape_forum_comments(url)
            sentiments = analyze_sentiments(comments)
            summary = summarize_sentiments(sentiments)
            return (summary, len(comments))
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 405:
                print(
                    "HTTP 405 error occurred: Not Allowed. Waiting for 1 minute before retrying..."
                )
                time.sleep(60)  # Wait for 1 minute
            else:
                raise err  # If the error is not a 405 error, raise it


def get_episode_info(base_url):
    offset = 0
    episodes_info = []

    while True:
        url = f"{base_url}?offset={offset}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        episodes = soup.find_all('tr', class_='episode-list-data')
        if not episodes:
            break

        for episode in episodes:
            # Extract forum link
            forum_link_tag = episode.find('td', class_='episode-forum').find('a')
            forum_link = forum_link_tag['href'] if forum_link_tag else None

            # Extract episode title
            title_tag = episode.find('td', class_='episode-title').find('a')
            title = title_tag.text.strip() if title_tag else 'No Title Available'

            # Extract poll vote count
            poll_vote_tag = episode.find('td', class_='episode-poll')
            poll_vote = poll_vote_tag.text.strip() if poll_vote_tag else 'No Votes'

            if forum_link:
                episodes_info.append((title, forum_link, poll_vote))

        offset += 100

    return episodes_info


def clean_poll_vote(df):

    df['poll_vote'] = df['poll_vote'].str.replace('Voteaverage ', '')

    # Convert the 'poll_vote' column to numeric, replacing non-numeric values with NaN
    df['poll_vote'] = pd.to_numeric(df['poll_vote'], errors='coerce')

    # Identify the indices of the rows that have NaN in the 'poll_vote' column
    na_indices = df[df['poll_vote'].isna()].index

    # For each index that has NaN in 'poll_vote', calculate the average of the previous 3 'poll_vote' values and impute this average
    for idx in na_indices:
        avg_prev_3 = df.loc[max(0, idx - 3) : idx - 1, 'poll_vote'].mean()
        df.loc[idx, 'poll_vote'] = avg_prev_3

    return df


def calculate_episode_success(df):
    # Normalize poll_vote (assuming 1 to 5 scale, transform to 0 to 1 scale)
    df['normalized_poll_vote'] = (df['poll_vote'] - 1) / 4

    # Calculate weighted sentiment score
    def weighted_sentiment(sentiments):
        # Weights can be adjusted according to desired sensitivity
        weights = {'positive': 1, 'neutral': 0, 'negative': -1}
        score = sum(sentiments[0][sent] * weights[sent] for sent in sentiments[0])
        total_sentiments = sum(sentiments[0].values())
        return score / total_sentiments if total_sentiments != 0 else 0

    df['sentiment_score'] = df['sentiments'].apply(weighted_sentiment)

    # Normalize number of comments (logarithmic scale to reduce skew)
    df['normalized_comments'] = np.log1p(df['sentiments'].apply(lambda x: x[1]))

    # Weights for each component
    W_R = 0.25  # Weight for poll votes
    W_S = 0.25  # Weight for sentiment score
    W_C = 0.25  # Weight for comments
    W_P = 0.25  # Weight for previous episode's success

    # Initialize success metric column
    df['success_metric'] = 0.0

    # Calculate success metric iteratively to include previous episode metric
    for i in range(len(df)):
        if i == 0:
            previous_metric = 0.5  # Assuming neutral baseline for first episode
        else:
            previous_metric = df.loc[i - 1, 'success_metric']

        df.loc[i, 'success_metric'] = (
            W_R * df.loc[i, 'normalized_poll_vote']
            + W_S * df.loc[i, 'sentiment_score']
            + W_C * df.loc[i, 'normalized_comments']
            + W_P * previous_metric
        )

    return df


# %% Test scape_forum_comments
forum_url = 'https://myanimelist.net/forum/?topicid=124435'
comments = scrape_forum_comments(forum_url)

# Analyze sentiments
sentiments = analyze_sentiments(comments)
print(sentiments)

summary = summarize_sentiments(sentiments)
print(f"Sentiment Summary: {summary}")

# %% Testing get_forum_links_and_titles
base_url = 'https://myanimelist.net/anime/21/One_Piece/episode'
episode_info = get_episode_info(base_url)
print(episode_info)
# %% df_comments view
df_comments = pd.DataFrame(comments, columns=['comment'])
df_comments.head()
# %% data frame of forum links with episode number and title
df_episode_info = pd.DataFrame(
    {
        'episode_num': np.arange(1, len(episode_info) + 1),
        'episode_title': [title for title, _, _ in episode_info],
        'poll_vote': [vote for _, _, vote in episode_info],
        'forum_link': [link for _, link, _ in episode_info],
    }
)

df_episode_info = clean_poll_vote(df_episode_info)
df_episode_info.head()
# %%
# df_episode_info = df_episode_info.apply(
#     lambda x: episode_sentiments(x['forum_link']), axis=1
# )
# %%
df_sample = df_episode_info.head(100)
df_sample['sentiments'] = df_sample.apply(
    lambda x: episode_sentiments(x['forum_link']), axis=1
)
df_sample = calculate_episode_success(df_sample)
df_sample
# %%
df_sample.to_csv('../data/one_piece_episode_sentiments.csv', index=False)
# %%
