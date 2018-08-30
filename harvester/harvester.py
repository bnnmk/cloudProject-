#  -*- coding: utf-8 -*-

import couchdb
import tweepy
from textblob import TextBlob

import threading

import time
from datetime import datetime
import pytz

import json
import os
import sys

import geo_classifier
import profanityfilter

ABS_PATH = os.path.dirname(os.path.realpath(__file__))


def load_couchdb_credentials():
    with open(ABS_PATH + '/credentials/couchdb.json') as myfile:
        return json.load(myfile)


def get_couchdb_server(index):
    credential = load_couchdb_credentials()[index]

    couchdb_server = couchdb.Server(
        "http://%s:%s@%s:%d/" % (
            credential['username'],
            credential['password'],
            credential['hostname'],
            credential['port']
        )
    )

    return couchdb_server


couchdb_server_index = 0
dbname = "tweets"

couchdb_server = get_couchdb_server(couchdb_server_index)
if dbname in couchdb_server:
    db = couchdb_server[dbname]
else:
    db = couchdb_server.create(dbname)


def load_twitter_credentials():
    with open(ABS_PATH + '/credentials/twitter.json') as myfile:
        return json.load(myfile)


def get_twitter_api_list():
    credentials = load_twitter_credentials()

    api_list = []
    for credential in credentials:
        auth = tweepy.OAuthHandler(credential['consumer_key'], credential['consumer_secret'])
        # pass our access token and access secret to tweepy
        auth.set_access_token(credential['access_token'], credential['access_token_secret'])
        # Creating a twitter API wrapper using tweepy
        api_list.append(tweepy.API(auth))

    return api_list


users_cache = set()

API_LIST = get_twitter_api_list()


# function used to store the data to the database
def save_to_couchdb(tweet, text):
    # this tweet already exists
    if db.get(tweet['id_str']):
        return

    # local time
    if sys.version_info > (3, 0):
        dt = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')
    else:
        dt = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y').replace(tzinfo=pytz.utc)
    dt = dt.astimezone(pytz.timezone('Australia/Melbourne'))

    # sentiment analysis
    sentiment = TextBlob(text).sentiment.polarity

    # convert coordinates into postcode
    try:
        longitude = tweet['coordinates']['coordinates'][0]
        latitude = tweet['coordinates']['coordinates'][1]
        postcode = geo_classifier.get_postcode(longitude, latitude)
        lga_code = geo_classifier.get_lga(longitude, latitude)
    except:
        postcode = -9
        lga_code = -9

    doc = {
        '_id': tweet['id_str'],
        'text': text,
        'local_time': dt.replace(microsecond=0).isoformat(),
        'day': dt.strftime('%a'),
        'hour': dt.strftime('%H'),
        'sentiment': sentiment,
        'postcode': postcode,
        'lga_code': lga_code,
        'bad_words': profanityfilter.detect(text),
    }

    elements = [
        "id_str",
        "lang",
        "coordinates",
        "created_at",
    ]

    for element in elements:
        doc[element] = tweet[element]

    try:
        db.save(doc)
    except couchdb.http.ResourceConflict:
        print("duplicate tweet: %s" % tweet['id_str'])


# stream class
class StreamListener(tweepy.StreamListener):

    # filter out retweet
    def on_status(self, status, tweet_mode='extended'):
        user = status.user.screen_name

        users_cache.add(user)
        print("add user '%s' to the cache" % user)

        if not status.retweeted:
            if status.coordinates and status.lang == "en":
                try:
                    text = status.extended_tweet["full_text"]
                except AttributeError:
                    text = status.text
                save_to_couchdb(status._json, text)

    # method of stream listener to handle errors coming from the Twitter API properly
    def on_error(self, status_code):
        if status_code == 420:
            return False


def stream(thread_index):
    # pass authentication credentials
    stream = tweepy.Stream(
        API_LIST[thread_index].auth,
        StreamListener()
    )
    # filter tweets from Sydney
    stream.filter(locations=[144.762703, -38.106018, 145.402088, -37.673881])


def search(thread_index):
    while True:
        try:
            user = users_cache.pop()
        except KeyError:
            time.sleep(1)
            continue

        print("processing '%s'" % user)

        cursor = tweepy.Cursor(
            API_LIST[thread_index].user_timeline,
            id=user,
            geocode="-37.9726,145.4020,55km",
            wait_on_rate_limit=True,
            wait_on_rate_limit_notify=True,
            tweet_mode='extended'
        ).items(50)

        for tweet in cursor:
            if not tweet.retweeted:
                if tweet.coordinates and tweet.lang == "en":
                    try:
                        text = tweet.full_text
                    except AttributeError:
                        text = tweet.text
                    save_to_couchdb(tweet._json, text)


if __name__ == "__main__":
    STREAM_THREAD_COUNT = 4
    SEARCH_THREAD_COUNT = 2

    offset = 0
    for index in range(offset, offset + STREAM_THREAD_COUNT):
        thread = threading.Thread(target=stream, args=(index,))
        thread.start()
        print("stream worker%d starts" % index)

    SLEEP = 10
    print("sleep for %d seconds" % SLEEP)
    time.sleep(SLEEP)
    print("awakened")

    offset += STREAM_THREAD_COUNT
    for index in range(offset, offset + SEARCH_THREAD_COUNT):
        thread = threading.Thread(target=search, args=(index,))
        thread.start()
        print("search worker%d starts" % index)
