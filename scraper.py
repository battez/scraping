''' script to scrape tweets down from twitter historical via Web browser interface
-- adapted from py 2.x.x: Tom Dickinson script:
-- credit: https://github.com/tomkdickinson/Twitter-Search-API-Python/blob/master/TwitterScraper.py

'''
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import datetime
import string
import logging
FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(filename="scrapelog.txt", level=logging.INFO, format=FORMAT)

import os

import urllib2
import json
from abc import ABCMeta
from urllib import urlencode
from abc import abstractmethod
from urlparse import urlunparse
from bs4 import BeautifulSoup
from time import sleep

# utility library 
import jlpb, process_tweets


class TwitterSearch:

    __metaclass__ = ABCMeta

    def __init__(self, rate_delay, error_delay=5):
        '''
        :param rate_delay: How long to pause between calls to Twitter
        :param error_delay: How long to pause when an error occurs
        '''
        self.rate_delay = rate_delay
        self.error_delay = error_delay
        self.json_file = ['filename' ,'json']

    def search(self, query):
        '''
        Scrape items from twitter
        :param query:   Query to search Twitter with. Takes form of queries constructed with using Twitters
                        advanced search: https://twitter.com/search-advanced
        '''
        url = self.construct_url(query)
        # prepare filename
        self.json_file[0] = jlpb.strtr(query, {':':'.', ',':'_', ' ':'_', '#':'HASHTAG', '"':''})

        continue_search = True
        min_tweet = None
        response = self.execute_search(url)
        while response is not None and continue_search and response['items_html'] is not None:
            tweets = self.parse_tweets(response['items_html'])

            # If we have no tweets, then we can break the loop early
            if len(tweets) == 0:
                break

            # If we haven't set our min tweet yet, set it now
            if min_tweet is None:
                min_tweet = tweets[0]

            continue_search = self.save_tweets(tweets)

            # Our max tweet is the last tweet in the list
            max_tweet = tweets[-1]
            if min_tweet['tweet_id'] is not max_tweet['tweet_id']:
                max_position = "TWEET-%s-%s" % (max_tweet['tweet_id'], min_tweet['tweet_id'])
                url = self.construct_url(query, max_position=max_position)
                # Sleep for our rate_delay
                sleep(self.rate_delay)
                response = self.execute_search(url)

    def execute_search(self, url):
        '''
        Executes a search to Twitter for the given URL
        :param url: URL to search twitter with
        :return: A JSON object with data from Twitter
        '''
        
        try:
            # Specify a user agent to prevent Twitter from returning a profile card
            headers = {
                'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
                # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36'
            }
            req = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(req)
            data = json.loads(response.read())
            return data

        # If we get a ValueError exception due to a request timing out, we sleep for our error delay, then make
        # another attempt
        except ValueError as e:
            logging.error(e.message + ' ' + url)
            print e.message, url
            
            print "Sleeping for %i" % self.error_delay
            sleep(self.error_delay)
            return self.execute_search(url)


    @staticmethod
    def parse_tweets(items_html):
        '''
        Parses Tweets from the given HTML
        :param items_html: The HTML block with tweets
        :return: A JSON list of tweets
        '''
        soup = BeautifulSoup(items_html, "html.parser", from_encoding="utf-8")
        tweets = []
        for li in soup.find_all("li", class_='js-stream-item'):

            # If our li doesn't have a tweet-id, we skip it as it's not going to be a tweet.
            if 'data-item-id' not in li.attrs:
                continue

           
            tweet = {
                'tweet_id': li['data-item-id'],
                'text': None,
                'user_id': None,
                'user_screen_name': None,
                'user_name': None,
                'created_at': None,
                'retweets': 0,
                'favorites': 0
            }

            # Tweet Text
            text_p = li.find("p", class_="tweet-text")
            if text_p is not None:
                tweet['text'] = text_p.get_text()

            # Tweet User ID, User Screen Name, User Name
            user_details_div = li.find("div", class_="tweet")
            if user_details_div is not None:
                tweet['user_id'] = user_details_div['data-user-id']
                tweet['user_screen_name'] = user_details_div['data-user-id']
                tweet['user_name'] = user_details_div['data-name']

            # Tweet date
            date_span = li.find("span", class_="_timestamp")
            if date_span is not None:
                tweet['created_at'] = float(date_span['data-time-ms'])

            # Tweet Retweets
            retweet_span = li.select("span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount")
            if retweet_span is not None and len(retweet_span) > 0:
                tweet['retweets'] = int(retweet_span[0]['data-tweet-stat-count'])

            # Tweet Favourites
            favorite_span = li.select("span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount")
            if favorite_span is not None and len(retweet_span) > 0:
                tweet['favorites'] = int(favorite_span[0]['data-tweet-stat-count'])

            tweets.append(tweet)
        return tweets

    @staticmethod
    def construct_url(query, max_position=None):
        '''
        For a given query, will construct a URL to search Twitter with
        :param query: The query term used to search twitter
        :param max_position: The max_position value to select the next pagination of tweets
        :return: A string URL
        '''

        params = {
            # Type Param
            'f': 'tweets',
            # Query Param
            'q': query
        }

        # If our max_position param is not None, we add it to the parameters
        if max_position is not None:
            params['max_position'] = max_position

        url_tupple = ('https', 'twitter.com', '/i/search/timeline', '', urlencode(params), '')
        return urlunparse(url_tupple)

    @abstractmethod
    def save_tweets(self, tweets):
        '''
        An abstract method that's called with a list of tweets.
        When implementing this class, you can do whatever you want with these tweets.
        '''


class TwitterSearchImpl(TwitterSearch):

    def __init__(self, rate_delay, error_delay, max_tweets):
        '''
        :param rate_delay: How long to pause between calls to Twitter
        :param error_delay: How long to pause when an error occurs
        :param max_tweets: Maximum number of tweets to collect for this example
        '''
        super(TwitterSearchImpl, self).__init__(rate_delay, error_delay)
        self.max_tweets = max_tweets
        self.counter = 0


    def save_tweets(self, tweets):
        '''
        Save tweets to json file
        :return:
        '''
        # store data in a subdirectory:
        script_dir =  os.path.join( os.path.dirname(__file__) , 'json') 

        # stringify the filename using the query
        output_file = '.'.join(self.json_file)
        output_path = os.path.join(script_dir, output_file)

        # write out the json data tweets to this file
        with open(output_path, "a+") as file:
            for tweet in tweets:
                
                # Lets add a counter so we only collect a max number of tweets
                self.counter += 1

                if tweet['created_at'] is not None:
                    t = datetime.datetime.fromtimestamp((tweet['created_at']/1000))
                    fmt = "%Y-%m-%d %H:%M:%S"
                    tweet['nice_created_at'] = t.strftime(fmt)
                    # file.write("%i [%s] - %s" % (self.counter, t.strftime(fmt), tweet['text']))
                    # print "%i [%s] - %s" % (self.counter, t.strftime(fmt), tweet['text'])

                
                j = json.dumps(tweet, indent=2)
                print >> file, j 

                
                # When we've reached our max limit, return False so collection stops
                if self.counter >= self.max_tweets:
                    logging.info(" tweets:" + str(self.counter))
                    return False

            logging.info(" tweets:" + str(self.counter))

        file.close()
        return True


# RUN TASKS:
if __name__ == '__main__':

    print 'processing...'
    exit()

    # set the max_tweets:
    max_tweets = 5000
    twit = TwitterSearchImpl(0, 5, max_tweets)
    directory = 'query'

    # defaults we will use in queries sometimes
    since = 'since:2014-05-01 '
    geocode = 'geocode:56.37655,-3.841994,170km '
    timelines = True

    if(timelines == True):
        # IMPORT USER IDS AND SCRAPE THEIR TIMELINES SINCE SOME DATE
        pass

    else: 
        # IMPORT QUERIES FROM A CSV FILE
        # loop through the log files and write out no comment lines as data
        # to relevant output file (ie with same no. of fields in its header, 
        # as the data)
        total_rows = 0
        # open folder
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.csv'):
                    # open each csv
                    with open(directory + '\\' + file) as text:
                        current = os.path.splitext(os.path.basename(file))[0]
                        # flood lcoation river storm
                        # loop through terms; combine into a query
                        q = ''
                        if current == 'location':
                            continue 
                            q = 'flood '
                            
                        elif current == 'river':
                            continue 
                            q = 'flood ' + current
                            
                        elif current == 'storm' :
                            pass
                            
                        elif current == 'flood':
                            q = since + geocode + current
                            pass
                        else:
                            pass
                        
                        for idx, line in enumerate(text):
                            if(idx > 0):
                                if current == 'flood':
                                    continue # temp dont try this.
                                elif current != 'storm':
                                    if line.strip() not in ['dee', 'deveron']:
                                        query = q + ' ' + line.strip()
                                
                                else:
                                    
                                    pieces = line.split(',')
                                    pieces[0] = datetime.datetime.strptime(pieces[0], '%d/%m/%Y').strftime('%Y-%m-%d')
                                    # add space
                                    pieces[2] = string.replace(pieces[2], 'storm', 'storm ')

                                    # disabled datewise, try geocode for search
                                    # query = pieces[2].strip() + ' since:' + pieces[0] 
                                    query = pieces[2].strip()  
                                
                                # run the query:
                                logging.info(query)
                                twit.search(query)
                                    
                        text.close

      

    # perform search
    # scratchpad queries:
    q = '-pee since:2015-10-01 dee flood' # use -pee
    # q = 'stormhenry since:2016-02-01 until:2016-02-02'
    # Crieff  lat long radius 170km
    # q = 'flood geocode:56.37655,-3.841994,170km'
    # logging.info(q)
    # q = since + geocode + ' flood'
    # print q
    # twit.search(q)
   
    
