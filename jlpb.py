import sys
def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').\
        decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)
        
def strtr(strng, replace):
        '''equivalent method to PHP strtr() method to replace characters
        '''
        if replace and strng:
            s, r = replace.popitem()
            return r.join(strtr(subs, dict(replace)) for subs in strng.split(s))
        return strng
    # usage: strtr(somestring, {':':'.', ' ':'_', '#':'HASHTAG'})
    # j=strtr('aa-bb-cc', {'aa': 'bbz', 'bb': 'x', 'cc': 'y'})

def get_dbc(db_name, collection):
    '''Convenience wrapper for a collection in mongoDB'''
    from pymongo import MongoClient
    try:
        client = MongoClient('localhost:27017')

    except pymongo.errors.ConnectionFailure as e:
        exit("Could not connect to MongoDB: %s" % e )

    db = client[db_name]

    return db[collection]
