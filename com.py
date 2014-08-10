## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.80.966 (20140810)                       ##
##                                                                            ##
##                                File: com.py                                ##
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
import urllib.request

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
def _header(name, version):
    return {'User-Agent': '{}/{}'.format(name.capitalize(),
                                         '.'.join(map(str, version)))}


#------------------------------------------------------------------------------#
def _open_url(url, headers, file=None):

    # TODO: handle connection errors, like:
    #       urllib.error.HTTPError: HTTP Error 403: Forbidden
    #       was it forbidden because the coub is private?

    # TODO: probably add some timeout, and try to reconnect or something..
    respond = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
    # If respond has to be saved
    if file:
        with open(file, 'wb') as destination:
            destination.write(respond.read())
    # Return file-like object
    return respond



#------------------------------------------------------------------------------#
class DownloadPacket(threading.Thread):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, index, packet, queue, data, app_name, app_version):
        super().__init__()
        self._data = data
        self._index = index
        self._queue = queue
        self._packet = packet
        self._header = _header(app_name, app_version)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        packet = self._packet
        # Download from URL to file
        for data_type in self._data:
            url, file = packet[data_type]
            print('Dowloading {!r} => {!r}'.format(url, file))
            if url and file:
                _open_url(url, self._header, file)
            print('File {!r} has been downloaded.'.format(file))
        # Put packet into queue
        self._queue.put((self._index, packet))



#------------------------------------------------------------------------------#
class DownloadJson(threading.Thread):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, url, queue, app_name, app_version,):
        super().__init__()
        self._url = url
        self._queue = queue
        self._header = _header(app_name, app_version)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        print('Fetching JSON data ...')
        # Put JSON file into queue
        self._queue.put(json.loads(_open_url(self._url, self._header).read().decode('utf-8')))
        print('JSON data has been fetched.')
