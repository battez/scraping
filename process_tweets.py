'''Process and clean functions for tweet data.

Todo: mentions improved; extract keywords (non hashtags) using stopwords etc.; 
improve normalise:remove URL patterns
'''
import re
from collections import Counter


def extract_tags(text):
    ''' find all strings with # then use a regex on that; returns set hashtags'''
    hashtags = set([re.sub(r"(\W+)$", "", j) for j in set([i for i in text.split() if i.startswith("#")])])
        
    # normalise hashtags
    return set([re.sub('#+', '#', x.lower()) for x in hashtags])

def extract_mentions(text):
    ''' find all strings with @ then use a regex on that; returns set hashtags'''
    mentions = set(re.findall(r"@(\w+)", text))
    return mentions

def get_dbc(db_name, collection):
    '''Convenience wrapper for a collection in mongoDB'''
    from pymongo import MongoClient
    try:
        client = MongoClient('localhost:27017')
    except pymongo.errors.ConnectionFailure, e:
        print "Could not connect to MongoDB: %s" % e

    db = client[db_name]

    return db[collection]


if __name__ == '__main__':
    ''' extract hashtags and summarise; store to file/db'''
    # MongoDB data is from scraped tweets, so no hashtag entities
    dbc = get_dbc('Twitter', 'rawtweets')
    dbstore = get_dbc('Twitter', 'scrapedtags')

    # add set of tags to a list, so then we can get the frequency
    count_all = Counter()

    blacklisted = ['aberdeenfc','android', 'BBCSportsound', 'celtic','dons', 'ge16','yemen','billcosby', \
     'iOs', 'donslive', 'followchess', 'nowplaying', 'mikeenriquez', 'hibees', 'retweet', 'europaleague', \
    'football', 'GreaseLive','Hearts','Hibs', 'IowaCaucus', 'news','newyearsresolutionin5words', 'got' \
     'sports', 'BlackTwitterTheBestTwitter', 'Lemmy', 'Thanks1DForAnAmazing2015', 'Remember1D2015', \
     'rotherham', 'christmas','thearchers', 'justsaying', 'fitba', 'happynewyear','newyearseve','sports',\
     'spl', 'twitter','coyr', 'earthquake','scotland','iraq','blackhistorymonth']
    blacklisted = [x.lower() for x in blacklisted]
    # noted: waterlogged, staysafe, crisiscomms
    
    # we just need the text field
    tweet_cursor = dbc.find({}, {'text':1})

    for tweet in tweet_cursor:
        
        # hashtags & put in a set
        text = extract_tags(tweet['text'])   

        # remove blacklisted
        output = [tag for tag in text if tag.lower()[1:] not in blacklisted]
       
        # tally these
        count_all.update(output)

    # find frequent:
    frequent_tags = count_all.most_common()
    for tag in frequent_tags:
        
        dbstore.insert_one({'tag':tag[0][1:], 'count':tag[1]})
    print (len(frequent_tags), ' inserted docs')  
    # print(frequent_tags[1:10]) # tuple list
    