import requests
from bs4 import BeautifulSoup
import re
import dateutil.parser

def fetch_progress(tracking_id):
    url = 'https://tools.usps.com/go/TrackConfirmAction.action?tLabels=' + str(tracking_id)
    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36'
    r = requests.get(url, headers={'User-Agent': ua})
    soup = BeautifulSoup(r.content, 'lxml')
    rows = soup.find('table').find('tbody').find_all('tr', {'class': 'detail-wrapper'}, recursive=False)
    progress = []
    for row in rows:
        if 'status-summary-panel' in row.attrs['class']:
            next
        c1,c2,c3 = row.find_all('td') 
        t = dateutil.parser.parse(col2text(c1))
        activity = col2text(c2)
        loc = col2text(c3)
        progress.append({
            'loc': loc,
            'datetime': t,
            'activity': activity
        })
    return progress
    
def col2text(c):
    s = c.text.strip()
    return re.sub('[\s\xa0]+', ' ', s)

