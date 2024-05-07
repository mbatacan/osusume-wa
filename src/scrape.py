import requests
from bs4 import BeautifulSoup
import pandas as pd
import dateparser


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

            # Extract episode date
            date_tag = episode.find('td', class_='episode-aired')
            date_str = date_tag.text.strip() if date_tag else 'No Date'
            date = dateparser.parse(date_str)

            if forum_link:
                episodes_info.append((title, date, forum_link, poll_vote))

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
