## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.50.061 (20140801)                       ##
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
from json import loads
from urllib.request import urlopen

PER_PAGE  = 5
EXPLORE   = 'http://coub.com/api/v1/timeline/{}.json?page={}&per_page={}'
TIMELINES = 'explore', 'hot'#, 'random'

#------------------------------------------------------------------------------#
def _ruby_format(string, **kwargs):
    for keyword, value in kwargs.items():
        string = string.replace('%{' + keyword + '}', value)
    return string

#------------------------------------------------------------------------------#
class CoubAPI:

    # {'thumb': None,
    #  'perma': None,
    #  'ratio': 0,
    #  'video': None,
    #  'audio': None,
    #  'likes': 0}

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self):
        self.reload()


    # methods: explore_random(), user_id(), etc...


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def explore(self):
        for coub in self._explore_coubs:
            link = coub['permalink']
            web  = coub['file_versions']['web']
            # Check if coub has mp4 version
            if 'mp4' not in web['types']:
                #
                # DO SOMETHING
                #
                continue
            # Check if coub has small type
            if 'small' not in web['versions']:
                #
                # DO SOMETHING
                #
                continue
            print(_ruby_format(web['template'], type='mp4', version='small'))

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
