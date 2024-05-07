from src.profile import AnimeProfile

# Read the links from links.txt
with open('models/links.txt', 'r') as f:
    links = f.read().splitlines()

# Create an AnimeProfile for each link
for link in links:
    profile = AnimeProfile(link)
    anime_name = link.split('/')[-2]
    profile.perform_etl(f'../data/{anime_name}_episode_sentiments.csv')

# Print the success message
print('ETL process completed successfully!')
