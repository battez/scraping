def strtr(strng, replace):
        '''equivalent method to PHP strtr() method to replace characters
        '''
        if replace and strng:
            s, r = replace.popitem()
            return r.join(strtr(subs, dict(replace)) for subs in strng.split(s))
        return strng
    # usage: strtr(somestring, {':':'.', ' ':'_', '#':'HASHTAG'})
    # j=strtr('aa-bb-cc', {'aa': 'bbz', 'bb': 'x', 'cc': 'y'})