import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import io
# import twitter keys and tokens
from config import *
try:
    from tqdm import tqdm
except:
    def tqdm(x):
        return x


class TweetStreamListener(StreamListener):

    def __init__(self, start_time, tweet_limit=250):
        self.time = start_time
        self.limit = tweet_limit
        self.tweet_count = 0

    # on success
    def on_data(self, data):

        try:
            dict_data = json.loads(data)
            if not dict_data.get("place"):
                return
            if 'https://t.co' not in dict_data['text']:
                if dict_data["place"]["country_code"] == "US":
                    saveFile = io.open('raw_tweets.txt', 'a', encoding='utf-8')
                    saveFile.write(dict_data["text"].replace('\n', ' '))
                    saveFile.write('\n')
                    saveFile.close()
                    self.tweet_count += 1
        except BaseException:
            print('failed ondata,', str(e))
            time.sleep(5)
            pass

        if (self.tweet_count >= self.limit):
            exit()

        print('Tweets gathered: {}'.format(self.tweet_count), end='\r')

    # on failure
    def on_error(self, status):
        print(status)

if __name__ == '__main__':

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener(time.time(), tweet_limit=750)

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Keywords for tracking:
    keywords = [line.strip() for line in open('keywords.txt')]
    # create instance of the tweepy stream
    start_time = time.time()
    stream = Stream(auth, listener)

    # search twitter for "congress" keyword
    stream.filter(track=keywords, languages=['en'])
