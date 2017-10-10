import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import re


class KNNClassifier:
    SENTIMENT = 0
    CATEGORY = 1

    def __init__(self, filename, k=2):
        self.sent_model = KNeighborsClassifier(n_neighbors=k)
        self.category_model = KNeighborsClassifier(n_neighbors=k)

        data = pd.read_csv(filename)
        sentiments = data.ix[:, 1]
        categories = data.ix[:, 3]
        text = data.ix[:, 2]
        self.stop_words = stopwords.words('english')
        self.tknzr = TweetTokenizer()
        self.word_list = set()

        # create the total word list
        # tokenize tweets and remove stop words
        tweets = []
        for tweet in text:
            tweet = self.convert(tweet)
            tokenized = [w for w in self.tknzr.tokenize(tweet.lower())
                         if w not in self.stop_words]
            tweets.append(tokenized)
            self.word_list.update(tokenized)

        # vectorize tweets
        vectors = []
        for tweet in tweets:
            vectors.append([1 if w in tweet else 0 for w in self.word_list])

        # train the sentiment and category models
        self.sent_model.fit(vectors, sentiments)
        self.category_model.fit(vectors, categories)

    def classify(self, tweet_text, model_type):
        # tokenize and vectorize tweet
        tokenized = [w for w in self.tknzr.tokenize(tweet_text.lower())
                     if w not in self.stop_words]
        vector = [1 if w in tokenized else 0 for w in self.word_list]

        if model_type == self.SENTIMENT:
            return self.sent_model.predict([vector])[0]
        elif model_type == self.CATEGORY:
            return self.category_model.predict([vector])[0]
        else:
            return -1

    def convert(self,tweet):
        #lowercase conversion
        tweet = tweet.lower()
        #remove URL formating
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',tweet)
        #clean up whitespace
        tweet = re.sub('[\s]+', ' ', tweet)
        #cleanup usernames
        tweet = re.sub('@[^\s]+','',tweet)
        #remove non letters
        tweet = re.sub('[^a-zA-Z]', ' ' , tweet)
        return self.replaceTwoOrMore(tweet)

    def replaceTwoOrMore(self,s):
        #look for 2 or more repetitions of character and replace with the character itself
        pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
        return pattern.sub(r"\1\1", s)


if __name__ == '__main__':
    knn = KNNClassifier('train.csv')
    data = pd.read_csv('train.csv')
    categories = data.ix[:, 3]
    text = [str(x) for x in data.ix[:, 2]]
    for i, tweet in enumerate(text):
        predicted = knn.classify(tweet, KNNClassifier.CATEGORY)
        print(predicted, categories[i])
