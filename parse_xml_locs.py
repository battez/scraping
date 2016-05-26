''' take an XML file (from an RSS at SEPA) and parse out gauges and 
certain metadata of those gauges: locations etc. 

Use python builtin etree for simplicity.
'''
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import sys
TWITDIR = 'U:\Documents\Project\demoapptwitter'
sys.path.insert(0, TWITDIR)
import config

# configuration
xml_file = 'rssriver.xml' # this can be found from the RSS proxy url on SEPA site
# conn  = 'localhost:27017'
conn_remote = config.MONGO_URI
conn = conn_remote
database = 'Twitter'
collection = 'gauges'


def scrape_avg_level(url):
    '''
    Take the url of a gauge location and scrape for the avg level value given there
    using div#SEPAWATERLEVELS_detailsDiv 
            table.stationDetailsTable
                span#SEPAWATERLEVELS_dvStationDetails_lblMean
    '''
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    html = urlopen(url)
    bs_obj = BeautifulSoup(html)
    val = bs_obj.find('span', {'id':'SEPAWATERLEVELS_dvStationDetails_lblMean'})
    try:
        return float(val.get_text())
    except ValueError:
        print ("Not a float")
        return 0



# set XML root tag
e = ET.parse(xml_file).getroot()

# connect to db where we store the Gauge data:
from pymongo import MongoClient
client = MongoClient(conn)
db = client[database]

# Loop through and make a document for each <item> to insert to DB.
# elements = ['guid', 'description', 'link', 'georss:point']
for count, item in enumerate(e.iterfind('channel/item')):
    doc = {}
    for idx, elem in enumerate(list(item.iter())[1:]):

        # we want to grab the ID for ease of use later on, so do that:
        if idx == 1:
            doc['loc_id'] = (elem.text.rsplit('/', 1)[-1])
        
        # make a location with lat and lng, for GeoJSON tricks of mongodb
        # note check ensureIndex() is set to 2dsphere
        if idx == 4:
            coords = [float(num) for num in elem.text.split(' ')]
            
            # x is long and y is lat, mongo prefers this ordering
            doc['loc'] = { 'type' : 'Point', \
            'coordinates' : [coords[1] , coords[0]] }
          
        else: 
            doc[elem.tag] = elem.text

    db[collection].insert(doc)



# loop through all the db collection of gauges
docs = db[collection].find()
for doc in docs:

    # retrieve avg level
    val = scrape_avg_level(doc['link'])
   
    # update this record with this new attribute 
    db[collection].update({'loc_id': doc['loc_id']}, {'$set': {'avg_level':val}})