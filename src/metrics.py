import requests
import time
import numpy as np
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from src.scrape import scrape_forum_comments

nltk.download('vader_lexicon')


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
