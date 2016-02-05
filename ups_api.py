import requests
from bs4 import BeautifulSoup
import re
import dateutil.parser

def fetch_progress(tracking_id):
    url = 'http://wwwapps.ups.com/WebTracking/track?loc=en_US&track.x=Track&trackNums=' + str(tracking_id)
    c = requests.get(url).content
    soup = BeautifulSoup(c, 'lxml')
    progress = []

    if 'Delivered On' in c:
        t = soup.find('label', text='Delivered On:').find_parent('dl').find('dd')
        t = col2text(t)
        t = t.replace('P.M.', 'PM').replace('A.M.', 'AM')
        t = dateutil.parser.parse(t)
        loc = soup.find('label', text='Left At:').find_parent('dl').find('dd')
        loc = col2text(loc)
        progress.append({
            'loc': loc,
            'datetime': t,
            'activity': 'Delivered'
        })
    elif 'Label Created On' in c:
        t = soup.find('label', text='Label Created On:').find_parent('dl').find('dd')
        t = col2text(t)
        t = t.replace('P.M.', 'PM').replace('A.M.', 'AM')
        t = dateutil.parser.parse(t)
        progress.append({
            'loc': '',
            'datetime': t,
            'activity': 'Label Created'
        })
    else:
        rows = soup.find('table').find_all('tr')[1:]
        for row in rows:
            c1,c2,c3,c4 = row.find_all('td')
            loc = col2text(c1)
            t = col2text(c2) + ' ' + col2text(c3)
            t = t.replace('P.M.', 'PM').replace('A.M.', 'AM')
            t = dateutil.parser.parse(t)
            activity = col2text(c4)
            progress.append({
                'loc': loc,
                'datetime': t,
                'activity': activity
            })
    return progress
    
def col2text(c):
    s = c.text.strip()
    return re.sub('[\s\xa0]+', ' ', s)
