import pandas as pd
import os
import numpy as np
import tweepy
from collections import defaultdict
import json

def load_keys(key_file):
    with open(key_file) as f:
        key_dict = json.load(f)
    return key_dict['api_key'], key_dict['api_secret'], key_dict['token'], key_dict['token_secret']

def iterate_files(path, subdir):
    KEY_FILE = "./twitter.json"
    api_key, api_secret, token, token_secret = load_keys(KEY_FILE)
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    # Don't worry about this file recursion
    for filename in os.listdir(path):
        filePath = path + "/" + filename
        if (os.path.isdir(filePath)):
            tempSubdir = ""
            if subdir: tempSubdir = subdir + "/" + filename
            else: tempSubdir = filename
            iterate_files(filePath, tempSubdir)
        else:
            filekey = subdir
            if subdir: file = subdir + "/" + filename
            else: file = filename
            tweet_content = defaultdict(list)

            if filename != 'process_tweets.py': # So it doesn't read itself
                tweet_ids = open(filePath, 'r')
                content = tweet_ids.read()[1:-1] #removes beginning and ending [ and  ]
                ids = np.fromstring(content, dtype=int, sep= ',')
                for id in ids: # Each tweet id
                    try:
                        tweet = api.get_status(id) #returns status object
                        """
                        TODO: After running throuhg all tweet ids in each file,
                        save as a csv file for each one. needs unique name
                        """
                        print(type(tweet))
                    except Exception as e: # It will throw an exception if twitter user has actually been suspended
                        print("Exception...")
                        continue#print(content)


def get_path():
    iterate_files(os.getcwd(), "")

if __name__ == "__main__":
    get_path()
