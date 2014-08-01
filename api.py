## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.109 (20140801)                       ##
##                                                                            ##
##                File: /Users/petervaro/Documents/coub/api.py                ##
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
import urllib.request

PER_PAGE  = 5
EXPLORE   = 'http://coub.com/api/v1/timeline/{}.json?page={}&per_page={}'
TIMELINES = 'explore', 'hot'#, 'random'

#------------------------------------------------------------------------------#
def _ruby_format(string, **kwargs):
    for keyword, value in kwargs.items():
        string = string.replace('%{' + keyword + '}', value)
    return string


#------------------------------------------------------------------------------#
def _create_packet(source):
    packet = {}

    # Link to thumbnail image
    try:
        image = source['image_versions']
        if 'small' not in image['versions']:
            raise KeyError
        ifile = _ruby_format(image['template'], version='small')
    except KeyError:
        ifile = None
    packet['thumb'] = ifile

    # Perma link
    packet['perma'] = source.get('href', 'http://coub.com')

    # Set aspect ration
    try:
        width, height = source['dimensions']['small']
        ratio = float(width) / float(height)
    except (KeyError, ValueError):
        ratio = 0
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
    packet['video'] = vfile

    # Link to audio
    packet['audio'] = source.get('audio_file_url', None)

    # Number of likes
    packet['likes'] = source.get('likes_count', 0)

    # Number of recoubs
    packet['share'] = source.get('recoubs_count', 0)

    # Title of masterpiece ;)
    packet['title'] = source.get('title', '')

    # Creator of coub
    packet['user'] = source.get('user_id', None)

    # ID
    packet['id'] = str(source.get('id', 0))

    # Return new packet
    return packet



#------------------------------------------------------------------------------#
class CoubAPI:

    URL = 'http://coub.com/api/v1/timeline/explore{}.json?page={}&per_page={}'
    STREAMS = ('',  #explore
               '/random',
               '/newest')
    PER_PAGE = 5

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self):
        # Storage for streams
        self.streams = {}

        # [total_pages, current_page]
        self.counters = [[1, 1] for i in self.STREAMS]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _load_stream(self, index):
        counters = self.counters
        counter, limit = counters[index]
        if counter <= limit:
            url = self.URL.format(self.STREAMS[index], counter, self.PER_PAGE)
            data = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
            counters[index][0] = data.get('total_pages', 0)
            counters[index][1] += 1
            return [_create_packet(d) for d in data.get('coubs', ())]
        return []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def explore(self): return self._load_stream(0)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def random(self): return self._load_stream(1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def newest(self): return self._load_stream(2)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def reload(self):
        for timeline in TIMELINES:
            data = loads(urlopen(EXPLORE.format(timeline, 1, PER_PAGE)).read().decode('utf-8'))
            setattr(self, '_{}_pages'.format(timeline), data['total_pages'])
            setattr(self, '_{}_coubs '.format(timeline), data['coubs'])
            setattr(self, '_{}_page'.format(timeline), 1)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def more(self):
        for timeline in TIMELINES:
            page = getattr(self, '_{}_page') + 1
            if page > getattr(self, '_{}_pages'):
                #
                # DO SOMETHING
                #
                continue
            data = loads(urlopen(EXPLORE.format(timeline, page, PER_PAGE)).read().decode('utf-8'))
            setattr(self, '_{}_coubs'.format(timeline), data['total_pages'])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def user_liked(self, user):
        pass
