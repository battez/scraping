''' twitter mongodb queries; py3
'''

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    # complete the aggregation pipeline
    pipeline = []
    pipeline.append({ "$group" : { "_id" : "$user_id", "total" : { "$sum" : 1} } })
    pipeline.append({ "$sort" : { "total" : -1 } })
    pipeline.append({ "$limit" : 50 })

    return pipeline

def tweet_sources(db, pipeline):
    # db.Tweets.aggregate({$group : {_id:"$user_id", count: {$sum:1}}}, {$sort: {count:-1}} 
    result = db.Tweets.aggregate(pipeline)
    
    return result

if __name__ == '__main__':
    db = get_db('Twitter')

    pipeline = make_pipeline()
    result = tweet_sources(db, pipeline)
    
    import pprint
    print ('top 50 users by count tweets')
    pprint.pprint(list(result))