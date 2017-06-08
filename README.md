# Various scraping scripts, including:

## functions for Scottish river levels polling - uses SEPA river levels scraping
**retrieve_latest_from_csv.py** will build URLs from IDs and then visit each latest river level CSV at: http://apps.sepa.org.uk/database/riverlevels/ IDGOESHERE

NB Call from another script with a set of IDs of river gauges you want to call ***scrape_current_levels()***

## For scraping Twitter via web search - Twitter-Search-API-Python
A python implementation of the Twitter Search Example

This Python script is an implementation of it's Java version https://github.com/tomkdickinson/TwitterSearchAPI.

It's suitable as an example of how you can extract Tweets from Twitter, without going through their API and obtaining
theoretically much large datasets.

While written for the Java version, the associated blog post for pagination on Twitter can be found
[here](http://tomkdickinson.co.uk/2015/08/scraping-tweets-directly-from-twitters-search-update/)

### Required Libraries
* BeautifulSoup 4
