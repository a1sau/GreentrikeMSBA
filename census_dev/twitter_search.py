import pandas as pd
import snscrape.modules.twitter as sntwitter
import itertools
from icecream import ic

search = 'daycare -Biscuits -K9 geocode:47.243638319477576,-122.43750438929989,30km'

# the scraped tweets, this is a generator
scraped_tweets = sntwitter.TwitterSearchScraper(search).get_items()
# ic(len(scraped_tweets))
# slicing the generator to keep only the first 100 tweets
itertools.islice()
sliced_scraped_tweets = itertools.islice(scraped_tweets, 100)

# convert to a DataFrame and keep only relevant columns
df = pd.DataFrame(sliced_scraped_tweets)[['date', 'content']]

print(df)