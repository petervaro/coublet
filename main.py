## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.231 (20140802)                       ##
##                                                                            ##
##                               File: main.py                                ##
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
import os
import sys
import queue
import shutil
import pickle
import os.path
import itertools
import urllib.request

# Import PyQt5 modules
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

# Import coub modules
import ui
import api
import com

# Module level constants
# TODO: read version from file (where will VERSION file be in the final app?)
VERSION = 0, 5, 61
DEV = True

#------------------------------------------------------------------------------#
class CoubApp:

    FILE = 'cache'
    PATH = '.coub_cache'
    MENU = 'featured', 'newest', 'random', 'user'

    def __init__(self, version):
        self._version = version
        # Create global cache folder and file
        self._path = os.path.join(os.path.expanduser('~'), self.PATH)
        self._file = os.path.join(self._path, self.FILE)
        os.makedirs(self._path, exist_ok=True)

        # Create cache folder for videos
        self._path_video = path_video = os.path.join(self._path, 'video')
        os.makedirs(path_video, exist_ok=True)

        # Create cache folder for thumbnails
        self._path_thumb = path_thumb = os.path.join(self._path, 'thumb')
        os.makedirs(path_thumb, exist_ok=True)

        # If load previously saved data
        try:
            with open(self._file, 'rb') as cache:
                self._temp = pickle.load(cache)
                # If cache file's version is not the same
                # as the app create the empty cache object
                if self._temp['version'] < self._version:
                    raise FileNotFoundError
        # If first run of app or update
        except (FileNotFoundError, EOFError):
            # Delete all previous videos
            for file in os.listdir(path_video):
                path = os.path.join(path_video, file)
                if os.path.isfile(path):
                    os.remove(path)
            # Delete all previous thumbnails
            for file in os.listdir(path_thumb):
                path = os.path.join(path_thumb, file)
                if os.path.isfile(path):
                    os.remove(path)
            self._temp = {'temporary': set()}

        # Queue for JSON file communication
        self._json = [queue.Queue() for m in self.MENU]

        # Create API object
        self.source = api.CoubAPI()

        # Run base Qt Application
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName('COUB')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load_menu(self, index, packets_queue):
        # TODO: _load_stream(index) is a private method
        #       or that should be part of the public interface?
        #       and what about the user stream? search?
        self.source._open_stream(index, self._json[index])
        self.process_menu(index, packets_queue)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def process_menu(self, index, packets_queue):
        try:
            packets = self.source._load_stream(self._json[index].get_nowait(), index)
            files = set()
            path_video = self._path_video
            path_thumb = self._path_thumb
            for packet in packets:
                # Create file names
                id = packet['id']
                video_file = os.path.join(path_video, id + '.mp4')
                thumb_file = os.path.join(path_thumb, id + '.jpg')
                # Store file names in temporary cache
                files.add(video_file)
                files.add(thumb_file)
                # Add file names to packet
                packet['video'].append(video_file)
                packet['thumb'].append(thumb_file)
                # If file not cached download it
                if not os.path.isfile(video_file):
                    com.DownloadPacket(packet, packets_queue).start()
                # If cached, pushed it to queue
                else:
                    packets_queue.put(packet)
            self._temp['temporary'].update(files)
        except queue.Empty:
            pass
        finally:
            QTimer.singleShot(300, lambda i=index, q=packets_queue: self.process_menu(i, q))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, position, dimension):
        temp = self._temp
        # Store info
        temp['startup_pos'] = position
        temp['startup_dim'] = dimension
        temp['version'] = self._version

        # Clean up
        temp.setdefault('latest', set())
        for file in temp['latest'] - temp['temporary']:
            os.remove(file)

        # Update values
        temp['latest'] = temp['temporary']
        temp['temporary'] = set()

        # Update cache file
        with open(self._file, 'wb') as cache:
            pickle.dump(temp, cache, pickle.HIGHEST_PROTOCOL)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        # Get previous position and dimension
        x, y = self._temp.setdefault('startup_pos', (NotImplemented, 0))
        width, height = self._temp.setdefault('startup_dim', (340, 768))
        # Create CoubApp
        app = ui.CoubAppUI(self, x, y, width, height, self.MENU)
        app.show()
        return self.qt_app.exec_()



#==============================================================================#
if __name__ == '__main__':
    v = VERSION
    if DEV:
        # Import cutils modules
        from cutils.cver import version
        from cutils.ccom import collect
        from cutils.clic import header, EXCEPTIONS
        exceptions = ('clic.py', 'cver.py', 'ccom.py',
                      'comment.py', 'check.py', 'table.py')
        exceptions += EXCEPTIONS
        # Update version
        v = version(sub_max=9, rev_max=99, build_max=999)[:3]
        # Collect all special comments
        collect('.', exceptions=exceptions)
        # Update header comments
        header('.', exceptions=exceptions)
    # Run application
    sys.exit(CoubApp(v).run())
