from tweepy.streaming import StreamListener
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
from train.train import KNNClassifier
from tweepy import OAuthHandler
from tweepy import Stream
import os.path as path
from config import *
import pandas as pd
import threading
import random
import json

## Creating Flask app.  Setting Template location
app = Flask(__name__, template_folder="templates")
app.config['GOOGLEMAPS_KEY'] = google_token_key
GoogleMaps(app, key=google_token_key)

##Possible Marker Colors
icons = [icons.dots.brown, icons.dots.green, icons.dots.yellow, icons.dots.red, icons.dots.orange, icons.dots.blue, icons.dots.black]


class Markers(object):
    '''Marker Class:  A Singleton list of Markers for the map'''
    class __Markers:
        def __init__(self):
            self.val = [None]
        def __str__(self):
            return ('self' + '\n'.join(self.val))
    instance = None
    def __new__(cls): # __new__ always a classmethod
        if not Markers.instance:
            Markers.instance = Markers.__Markers()
        return Markers.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)


@app.route("/")
def fullmap():
    '''Full Map Flask Route function.  Loads Markers'''
    m = Markers()
    fullmap = Map(
        identifier="fullmap",
        varname="fullmap",
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "left:0;"
            "position:absolute;"
            "z-index:200;"
        ),
        lat=37.0902,
        lng=-98.35,
        markers= m.val,
        zoom = "5",
    )
    return render_template('example_fullmap.html', fullmap=fullmap)

@app.route("/statistics/<k>")
def statistics(k):
    '''Basic Statics Information Function.'''
    
    k = int(k)
    df = pd.read_csv("saved_data/stats.csv", names=["", "author", "city", "state", "lat", "lng", "text","sentiment", "category"])
    df = df.drop_duplicates()
    labels = []
    values = []
    limits = []
    
    ## City Count - Top k
    labs = list(df.city.unique())
    vals = []
    for label in labs:
        vals.append((df[df.city == label]).shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA")) ])
    labels.append([x for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))])
    limits.append(max([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))]))

    ## Author Count - Top k
    labs = list(df.author.unique())
    vals = []
    for label in labs:
        vals.append((df[df.author == label]).shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort])
    labels.append([x for x,y in sort])
    limits.append(max([y for x,y in sort]))

    ## States Count - Top k
    labs = list(df.state.unique())
    vals = []
    for label in labs:
        vals.append((df[df.state == label]).shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))])
    labels.append([x for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))])
    limits.append(max([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))]))
    ## City avg - Top k
    labs = list(df.city.unique())
    vals = []
    for label in labs:
        vals.append((df[df.city == label]).sentiment.mean())
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA")) ])
    labels.append([x for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))])
    limits.append(max([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))]))
    
    ## States avg - Top k
    labs = list(df.state.unique())
    vals = []
    for label in labs:
        vals.append((df[df.state == label]).sentiment.mean())
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))])
    labels.append([x for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))])
    limits.append(max([y for x,y in sort if not (y=="None" or (x=="None" or x =="USA"))]))

    ## Author avg - Top k
    labs = list(df.author.unique())
    vals = []
    for label in labs:
        vals.append((df[df.author == label]).sentiment.mean())
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort])
    labels.append([x for x,y in sort])
    limits.append(max([y for x,y in sort]))
    return render_template('statistics.html', values=values, labels=labels, limit=limits)

@app.route("/city_statistics/<city>/<k>")
def city_statistics(city, k):
    '''Statistics for a given City: Top -k most Negative and least Negative people'''
    
    k = int(k)
    df = pd.read_csv("saved_data/stats.csv", names=["", "author", "city", "state", "lat", "lng", "text","sentiment", "category"])
    df = df.drop_duplicates()
    labels = []
    values = []
    limits = []
    
    ## K Most negative people in City
    labs = list(df[df.city == city].author.unique())
    vals = []
    for label in labs:
        vals.append((df[df.author == label])[df.sentiment == 5].shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort])
    labels.append([x for x,y in sort])
    limits.append((max([y for x,y in sort])))

    ## K Most positive people in City
    labs = list(df[df.city == city].author.unique())
    vals = []
    for label in labs:
        vals.append((df[df.author == label])[df.sentiment == 1].shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort])
    labels.append([x for x,y in sort])
    limits.append((max([y for x,y in sort])))

    ## Pie Data Category Ratios

    labs = list(df[df.city == city].category.unique())
    vals = []
    r = lambda: random.randint(0,255)
    for label in labs:
        vals.append((df[df.city == city])[df.category == label].shape[0])
    values.append(vals)
    labels.append([typefind(l) for l in labs])
    limits.append(max(vals))
    return render_template('city_statistics.html', values=values, labels=labels, limit=limits)

@app.route("/state_statistics/<state>/<k>")
def state_statistics(state, k):
    '''Statistics for a given State: Top -k most Negative and least Negative people'''

    k = int(k)
    df = pd.read_csv("saved_data/stats.csv", names=["", "author", "city", "state", "lat", "lng", "text", "sentiment", "category"])
    df = df.drop_duplicates()
    labels = []
    values = []
    limits = []
    ## K Most negative people in City
    labs = list(df[df.state == state].author.unique())
    vals = []
    for label in labs:
        vals.append((df[df.author == label])[df.sentiment == 5].shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort])
    labels.append([x for x,y in sort])
    limits.append((max([y for x,y in sort])))

    ## K Most positive people in City
    labs = list(df[df.state == state].author.unique())
    vals = []
    for label in labs:
        vals.append((df[df.author == label])[df.sentiment == 1].shape[0])
    zipped = list(zip(labs,vals))
    sort = sorted(zipped, key=lambda x: x[1])
    if k < len(labs):
        sort = sort[-k:]
    values.append([y for x,y in sort])
    labels.append([x for x,y in sort])
    limits.append((max([y for x,y in sort])))

    return render_template('state_statistics.html', values=values, labels=labels, limit = limits)

def typefind(val):
    if(val == 1):
        return("Religion")
    elif(val == 2):
        return("Gender")
    elif(val == 3):
        return("Racial")
    elif(val == 4):
        return("Sexual Orientation")
    elif(val == 5):
        return("Disability")
    elif(val == 6):
        return("Political")
    elif(val == 7):
        return("Other")
    
class TweetStreamListener(StreamListener):

    def __init__(self):
        self.classifier = KNNClassifier('train/train.csv')

    # on success
    def on_data(self, data):
        # decode json
        dict_data = json.loads(data)

        #Must have a place object, must have a text object
        if "text" not in dict_data:
            return
        if not dict_data.get("place"):
            return
        #print(json.dumps(dict_data, indent=4, sort_keys=True))

        m = Markers() #Get the Markers instance

        #Use full_name if exists, otherwise, set None, None - May need changing
        if dict_data["place"]["full_name"]:
            c1 = dict_data["place"]["full_name"]
            c1 = c1.strip().split(", ")
        else:
            c1 = ["None","None"]
        #User info
        author = [dict_data["user"]["screen_name"]]

        #City from full_name
        city = [c1[0]]
        try:
            #Due to how full_name is weirdly set up, sometimes a place can be Region, Country rather than City, Region, may need to handle that as well
            state = [c1[1]]
        except IndexError:
            state = 'None'

        # Use the average of the lat/lngs of the bounding box for the marker coordinates.
        lng = [(dict_data["place"]["bounding_box"]["coordinates"][0][0][0] + dict_data["place"]["bounding_box"]["coordinates"][0][1][0] + dict_data["place"]["bounding_box"]["coordinates"][0][2][0] + dict_data["place"]["bounding_box"]["coordinates"][0][3][0])/4]
        lat = [(dict_data["place"]["bounding_box"]["coordinates"][0][0][1] + dict_data["place"]["bounding_box"]["coordinates"][0][1][1] + dict_data["place"]["bounding_box"]["coordinates"][0][2][1] + dict_data["place"]["bounding_box"]["coordinates"][0][3][1])/4]
        text = [(dict_data["text"])]
        
        #Only US tweets
        if(dict_data["place"]["country_code"] == "US"):
            sentiment = self.classifier.classify(dict_data['text'], KNNClassifier.SENTIMENT)
            category = self.classifier.classify(dict_data['text'], KNNClassifier.CATEGORY)
            #Append to Makers list for display purposes
            m.val.append({'icon': icons[sentiment], 'lng': lng, 'lat': lat, 'infobox':  typefind(category) + ": " + text[0]  })
            d = {'author': author, 'city': city, 'state':state, 'lat':lat, 'lng': lng, 'text': text, 'sentiment': sentiment, 'category': category}
            df = pd.DataFrame(data=d, columns=["author", "city", "state", "lat", "lng", "text", "sentiment", "category"])
            with open('saved_data/stats.csv', 'a') as f:
                if not path.exists("saved_data/stats.csv"):
                    df.to_csv(f, header = True)
                else:
                    df.to_csv(f, header = False)

        return True

    # on failure
    def on_error(self, status):
        print (status)


def begin_stream():

    # create instance of the tweepy tweet stream listener
    listener = TweetStreamListener()

    # set twitter keys/tokens
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Keywords for tracking:
    keywords = [line.strip() for line in open('keywords.txt')]
    # create instance of the tweepy stream
    stream = Stream(auth, listener)

    #Apply filter on keywords
    stream.filter(track=keywords, languages = ['en'])

if __name__ == '__main__':

    m = Markers() #Load Markers singleton class
    
    old = pd.read_csv('saved_data/stats.csv')
    old = old.drop_duplicates() # Handle duplication behavior
    ## Load up previously pulled tweets into Marker Singleton
    for index, row in old.iterrows():
        lat = row[4]
        lng = row[5]
        text = row[6]
        sent = row[7]
        typ = row[8]
        m.val.append({'icon': icons[sent], 'lng': lng, 'lat': lat, 'infobox': typefind(typ) + ": " + text})

    threading.Thread(target=begin_stream).start()
    app.run(debug=True, use_reloader=True, host= '0.0.0.0')
