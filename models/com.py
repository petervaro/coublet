## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.180 (20140816)                       ##
##                                                                            ##
##                            File: models/com.py                             ##
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

# Import Python modules
import json
import threading
import urllib.error
import urllib.request

# Module level constants
USER_AGENT = {}

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def set_user_agent(name, version):
    USER_AGENT['User-Agent'] = '{}/{}'.format(name.capitalize(),
                                              '.'.join(map(str, version)))


#------------------------------------------------------------------------------#
def _open_url(url, file=None):

    # TODO: handle connection errors, like:
    #       urllib.error.HTTPError: HTTP Error 403: Forbidden
    #       was it forbidden because the coub is private?

    # TODO: probably add some timeout, and try to reconnect or something..
    respond = urllib.request.urlopen(urllib.request.Request(url, headers=USER_AGENT))
    # If respond has to be saved
    if file:
        with open(file, 'wb') as destination:
            destination.write(respond.read())
    # Return file-like object
    return respond


#------------------------------------------------------------------------------#
class CoubletConnectionError(Exception): pass

#------------------------------------------------------------------------------#
class CoubletDownloadPacketThread(threading.Thread):

    FILE_KEYS = 'video', 'thumb', 'user'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, index, packet, queue):
        super().__init__()
        self._index = index
        self._queue = queue
        self._packet = packet

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        packet = self._packet
        # Download from URL to file
        for file_key in self.FILE_KEYS:
            url, file = packet[file_key]
            print('Dowloading {!r} => {!r}'.format(url, file))
            if url and file:
                try:
                    _open_url(url, file)
                except urllib.error.URLError as e:
                    packet['error'] = e.reason + ' @url'
            # TODO: what happens if not url or not file ???
            print('File {!r} has been downloaded.'.format(file))
        # Put packet into queue
        self._queue.put((self._index, packet))



#------------------------------------------------------------------------------#
class CoubletDownloadJsonThread(threading.Thread):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, url, queue):
        super().__init__()
        self._url = url
        self._queue = queue

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        print('Fetching JSON data ...')
        try:
            # Put JSON file into queue
            self._queue.put(json.loads(_open_url(self._url).read().decode('utf-8')))
        except urllib.error.URLError:
            self._queue.put(CoubletConnectionError)
        print('JSON data has been fetched.')
