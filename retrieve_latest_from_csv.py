'''
Take a set of CSV URLs and open each, retrieving their last line
(which has water level inside)
'''
from urllib.request import urlopen
from io import StringIO
import csv
from collections import deque

stem = 'http://apps.sepa.org.uk/database/riverlevels/'
suffix = '-SG.csv'
# improve this to be dynamic? if URLs are cosnistent
urls = {
   '234151' :'http://apps.sepa.org.uk/database/riverlevels/234151-SG.csv',
   '14954' : 'http://apps.sepa.org.uk/database/riverlevels/14954-SG.csv'
}

def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

for id_url in urls:
    # set URL path to CSV
    csv_url = stem + id_url + suffix
    # open the CSV
    data = urlopen(csv_url).read().decode('ascii', 'ignore')
    # run into StringIO so we avoid saving it etc
    data_file = StringIO(data)
    csv_reader = csv.reader(data_file)
    # we only need the last line contents
    latest = deque(csv_reader, 1)
    latest = latest[0][1]
    if(is_float(latest)):
        # TODO: append to results
        print(latest)
    else:
        latest = 0

    