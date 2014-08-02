## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.170 (20140802)                       ##
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

#------------------------------------------------------------------------------#
class DownloadPacket(threading.Thread):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, packet, queue):
        super().__init__(self, daemon=True)
        self._queue = queue
        self._packet = packet

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        packet = self._packet
        # Download from URL to file
        for file in ('video', 'thumb'):
            # TODO: handle connection errors, like:
            #       urllib.error.HTTPError: HTTP Error 403: Forbidden
            #       was it forbidden because the coub is private?
            print('[{}] started:  {!r} => {!r}'.format(file.upper(), *packet[file]))
            # TODO: probably add some timeout, and try to reconnect or something..
            urllib.request.urlretrieve(*packet[file])
            print('[{}] finished: {!r} => {!r}'.format(file.upper(), *packet[file]))
        # Put packet into queue
        self._queue.put(packet)

#------------------------------------------------------------------------------#
class DownloadJson(threading.Thread):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, url, queue):
        super().__init__(self, daemon=True)
        self._url = url
        self._queue = queue

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        print('[JSON] downloading...')
        # Put JSON file into queue
        self._queue.put(
            json.loads(urllib.request.urlopen(self._url).read().decode('utf-8')))
        print('[JSON] finished')
