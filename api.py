## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.70.660 (20140806)                       ##
##                                                                            ##
##                                File: api.py                                ##
##                                                                            ##
##           Designed and written by Peter Varo. Copyright (c) 2014           ##
##             License agreement is provided in the LICENSE file              ##
##           For more info visit: https://github.com/petervaro/coub           ##
##                                                                            ##
##      Copyright (c) 2014 Coub Ltd and/or its suppliers and licensors,       ##
##    5 Themistokli Dervi Street, Elenion Building, 1066 Nicosia, Cyprus.     ##
##         All rights reserved. COUB (TM) is a trademark of Coub Ltd.         ##
##                              http://coub.com                               ##
##                                                                            ##
######################################################################## INFO ##

# Import python modules
import json
import queue
import urllib.request

# Import coub modules
import com

#------------------------------------------------------------------------------#
def _ruby_format(string, **kwargs):
    for keyword, value in kwargs.items():
        string = string.replace('%{' + keyword + '}', value)
    return string



#------------------------------------------------------------------------------#
def _create_packet(source):
    # Create new packet
    packet = {}

    # Link to thumbnail image
    try:
        image = source['image_versions']
        if 'small' not in image['versions']:
            raise KeyError
        ifile = _ruby_format(image['template'], version='small')
    except KeyError:
        ifile = None
    packet['thumb'] = [ifile]

    # Perma link
    try:
        perma = 'http://coub.com/view/' + source['permalink']
    except KeyError:
        perma = 'http://coub.com'
    packet['perma'] = perma

    # Set aspect ration
    try:
        width, height = source['dimensions']['small']
        ratio = float(height) / float(width)
    except (KeyError, ValueError):
        ratio = 1
    packet['ratio'] = ratio

    # Link to video
    try:
        video = source['file_versions']['web']
        if ('small' not in video['versions'] and
            'mp4' not in video['types']):
                raise KeyError
        vfile = _ruby_format(video['template'], version='small', type='mp4')
    except KeyError:
        vfile = None
    packet['video'] = [vfile]

    # Link to audio
    packet['audio'] = source.get('audio_file_url', None)
    # Number of likes
    packet['likes'] = str(source.get('likes_count', 0))
    # Number of recoubs
    packet['share'] = str(source.get('recoubs_count', 0))
    # Title of masterpiece ;)
    packet['title'] = source.get('title', '')

    # Avatar of creator of coub
    try:
        user = source['user']['small_avatar']
    except KeyError:
        user = None
    packet['user'] = [user]

    # Name of creator of coub
    try:
        name = source['user']['name']
    except KeyError:
        name = '—'
    packet['name'] = name

    # ID of user
    try:
        user_id = source['user']['id']
    except KeyError:
        user_id = 0
    packet['user_id'] = str(user_id)

    # Perma-link to user
    try:
        user_perma = source['user']['permalink']
    except KeyError:
        user_perma = None
    packet['user_perma'] = user_perma

    # ID of coub
    packet['id'] = str(source.get('id', 0))

    # Return new packet
    return packet



#------------------------------------------------------------------------------#
class NoMoreDataToFetch(Exception): pass


#------------------------------------------------------------------------------#
class CoubAPI:
    URL = 'http://coub.com/api/v1/timeline/{}?page={}&per_page={}'
    STREAMS = ['explore.json',
               'explore/newest.json',
               'explore/random.json',
               'hot.json']

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, per_page):
        self.per_page = per_page
        # counter => [total_pages, current_page]
        self.counters = [[1, 1] for i in self.STREAMS]
        self.user_counter = [1, 1]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def fetch_data_to_queue(self, index, queue):
        self._fetch_data_to_queue(self.counters[index], self.STREAMS[index], queue)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def fetch_user_data_to_queue(self, user, queue):
        self._fetch_data_to_queue(self.user_counter, 'user/' + user, queue)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def translate_fetched_data(self, data, index):
        self.counters[index][0] = data.get('total_pages', 0)
        self.counters[index][1] += 1
        return [_create_packet(d) for d in data.get('coubs', ())]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _fetch_data_to_queue(self, counter, url, queue):
        # If given stream has more pages to load
        total, current = counter
        if current <= total:
            # Format URL and start downloading JSON file
            url = self.URL.format(url, current, self.per_page)
            com.DownloadJson(url, queue).start()
        else:
            raise NoMoreDataToFetch
