'''
Take a set of CSV URLs and open each, retrieving their last line
(which has water level inside)
'''
from time import sleep 
from urllib.request import urlopen
from io import StringIO
import csv
from collections import deque


STEM = 'http://apps.sepa.org.uk/database/riverlevels/'
SUFFIX = '-SG.csv'

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def scrape_current_levels(urls = []):
    ''' usage: pass in list IDs so we can form URL now:
    '234151' will be 'http://apps.sepa.org.uk/database/riverlevels/234151-SG.csv' 
    '''
    results = {}
    for id_url in urls:
        # set URL path to CSV
        csv_url = STEM + id_url + SUFFIX
        # open the CSV
        time.sleep(0.5)

        try:
            data = urlopen(csv_url).read().decode('ascii', 'ignore')
            # run into StringIO so we avoid saving it etc
            data_file = StringIO(data)
            csv_reader = csv.reader(data_file)
            # we only need the last line contents
            latest = deque(csv_reader, 1)
            latest = latest[0][1]
        
            if(not is_float(latest)):
                latest = 0

            # append to results
            results[id_url] = latest
        except HTTPError as e:
            
            print("Error: " + e.code)

    return results

    