import re
import ups_api
import usps_api
import os
import pickle
import datetime

crontable = []
outputs = []

crontable.append([60*60, "refresh_items"])

items = {}
FILE = 'plugins/wheresmyshit.data'
if os.path.isfile(FILE):
    items = pickle.load(open(FILE, 'rb'))

def process_message(data):
    print data
    if not data.has_key('text'):
        return

    if data.has_key('subtype'):
        return

    text = data['text']
    channel = data['channel']

    if channel.startswith("D") or channel.startswith("C"):
        if text == 'show':
            show_items(channel)
        elif text.startswith('track'):
            m = re.match('track\s+(ups|usps)\s+(\S+)', text)
            if m:
                carrier = m.group(1)
                tracking_id = m.group(2)
                item = items.get(tracking_id, {'carrier': carrier, 'tracking_id': tracking_id, 'user': data['user']})
                track_item(item)
                items[tracking_id] = item
                show_items(channel)
            else:
                outputs.append([channel, 'invalid tracking command'])
        elif text.startswith('remove'):
            m = re.match('remove\s+(\S+)', text)
            if m:
                tracking_id = m.group(1)
                if tracking_id in items:
                    items.pop(tracking_id)
                    outputs.append([channel, 'removed'])
                else:
                    outputs.append([channel, 'item does not exist'])
        else:
            help(channel)
    pickle.dump(items, open(FILE, 'wb'))

def track_item(item):
    try:
        if item['carrier'] == 'ups':
            item['progress'] = ups_api.fetch_progress(item['tracking_id'])
        elif item['carrier'] == 'usps':
            item['progress'] = usps_api.fetch_progress(item['tracking_id'])
        item['error'] = None
    except Exception as e:
        print e
        item['error'] = 'COULD NOT FETCH INFO'
    return item

def show_items(channel):
    if len(items) == 0:
        outputs.append([channel, 'no items are being tracked'])
    else:
        msg = '```'
        i = 1
        items_list = items.values()
        ed = datetime.datetime.now()
        items_list.sort(key=lambda x: x['error'] and ed or x['progress'][0]['datetime'], reverse=True)
        for item in items_list:
            if item.get('error', None):
                msg += '%3i) %5s %25s %90s\n' % (
                        i, 
                        item['carrier'].upper(), 
                        item['tracking_id'], 
                        item['error'])
            else:
                msg += '%3i) %5s %25s %35s %25s %30s\n' % (
                        i, 
                        item['carrier'].upper(), 
                        item['tracking_id'],
                        item['progress'][0]['loc'],
                        str(item['progress'][0]['datetime']),
                        item['progress'][0]['activity'])
            i += 1
        msg += '```'
        outputs.append([channel, msg])

def refresh_items():
    for _id, item in items.iteritems():
        if item['error']:
            next
        if 'delivered' in item['progress'][0]['activity']:
            next
        track_item(item)

def help(channel):
    msg = '```'
    msg += 'show                                // display all items\n'
    msg += 'track [ups|usps] [tracking_id]      // track an item\n'
    msg += 'remove [tracking_id]                // untrack an item\n'
    msg += '```'
    outputs.append([channel, msg])
