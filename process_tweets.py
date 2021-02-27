import pandas as pd
import os
import numpy as np
import tweepy
from collections import defaultdict
import json
import time

max_num_records = 5000

"""
Methodology we covered in class to just load the twitter credentials into appropriate objects.
This assumes a file with your Twitter developer credentials are in a file named 'twitter.json' 
and is in the same directory as the program when it's being run.
"""
def load_keys(key_file):
    with open(key_file) as f:
        key_dict = json.load(f)
    return key_dict['api_key'], key_dict['api_secret'], key_dict['token'], key_dict['token_secret']


"""
Recursive method to navigate through many directories.
"""
def iterate_files(path, subdir):
    KEY_FILE = "./twitter.json" # Twitter credentials. See def load_keys(key_file):
    api_key, api_secret, token, token_secret = load_keys(KEY_FILE)
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    
    # File recursion portion. Not pertinent to the actual data collection.
    for filename in os.listdir(path):
        filePath = path + "/" + filename
        # If folder, recursively call.
        if filename == 'scraped_data': # Skip folder containing the scraped data.
            continue
        if (os.path.isdir(filePath)):
            tempSubdir = ""
            if subdir: tempSubdir = subdir + "/" + filename
            else: tempSubdir = filename
            iterate_files(filePath, tempSubdir)
        # Otherwise, process the file.
        else:
            filekey = subdir
            if subdir: file = subdir + "/" + filename
            else: file = filename
            tweet_content = defaultdict(list)
            
            """
            TODO: Refactor to detect .txt and .csv to know which dataset it came from. 
            """
            # So it doesn't read itself or the credentials file
            #if filename not in ['process_ieee.py', 'process_tweets.py', 'twitter.json']: 
            print(filename)
            if filename.endswith('.csv'):
                # NOTE: This version of the program is assuming .csv files -- IEEE data. 
                # Samples 5000 records from the data set, takes only the column values, then ravels into a np array
                tweet_ids = pd.read_csv(filePath).sample(n=max_num_records).iloc[:,0].values.ravel()
                print("Collecting from file: {}".format(filename))
                # Iterates through each of the tweet ids we sampled.
                for id in tweet_ids: 
                    """
                    Must be in a try-catch structure. If a twitter user is banned or suspended, the tweet_id
                    refers to data that doesn't exist. The Tweepy api will return a 400-level HTTP status code
                    due to the resource not being found - which is considered an exception.
                    """
                    try: 
                        print(num_records) # Debugging. Just to see that the program wasn't stalling.
                        tweet = api.get_status(id) #returns status object
                    except tweepy.RateLimitError:
                        print("Rate Limit hit. Sleeping for 15 minutes.")
                        time.sleep(900)
                        print("Resuming...\n")
                        continue
                    except Exception as e: # It will throw an exception if twitter user has actually been suspended
                        continue
                    if tweet is None:
                        print("Should never be reached. If seen, something went wrong.")
                    
                    # Features we're extracting.
                    tweet_content['id'].append(tweet.id)
                    tweet_content['username'].append(tweet.user.name)
                    tweet_content['text'].append(tweet.text)
                    tweet_content['entities'].append(tweet.entities)
                    tweet_content['retweet_count'].append(tweet.retweet_count)
                    tweet_content['favorite_count'].append(tweet.favorite_count)
                    tweet_content['created_at'].append(tweet.created_at)
                result_filename = './scraped_data/' + filename
                """
                We control how many records we want from each day. It'll either run through the entire file
                or run based on how many records we want sampled.
                """
                pd.DataFrame(tweet_content).to_csv(result_filename)
                print("Done processing: {}".format(result_filename))


def get_path():
    iterate_files(os.getcwd(), "")

if __name__ == "__main__":
    get_path()
