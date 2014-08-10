## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.5.80.956 (20140810)                       ##
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
import itertools
import urllib.request

# Import PyQt5 modules
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication

# Import coub modules
import api
import com
from ui.app import CoubAppUI

# Module level constants
# TODO: read version from file (where will VERSION file be in the final app?)
VERSION = 0, 5, 80
DEV = 1

#------------------------------------------------------------------------------#
class CoubApp:

    NAME = 'COUBLET'
    MENU = 'featured', 'newest', 'random', 'hot'
    PAGE = 5  # per-page count

    CACHE_FILE = 'cache'
    CACHE_PATH = '.coub_cache'
    CACHE_DATA = 'video', 'thumb', 'user'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, version):
        # Store static values
        self._version = version

        # Create path string of global cache folder and cache file
        self._cache_path = os.path.join(os.path.expanduser('~'), self.CACHE_PATH)
        self._cache_file = os.path.join(self._cache_path, self.CACHE_FILE)
        os.makedirs(self._cache_path, exist_ok=True)

        # Create folders for downloaded
        # cache data if it doesn`t exist
        self._cache_folders = cache_folders = []
        for folder_name in self.CACHE_DATA:
            folder_path = os.path.join(self._cache_path, folder_name)
            cache_folders.append(folder_path)
            os.makedirs(folder_path, exist_ok=True)

        # Default values
        dimension = NotImplemented, 0, 350, 768

        # Load previously saved data if exists
        try:
            with open(self._cache_file, 'rb') as cache:
                # Deserialise cache data
                self._cache = pickle.load(cache)
                # If cache file's version is not the same
                # as the app create new cache object and
                # store the version independent data
                if self._cache['version'] < self._version:
                    dimension = self._cache['dimension']
                    # Remove cached files
                    raise FileNotFoundError
        # If first run of app or app has been updated
        except (FileNotFoundError, EOFError):
            # Delete all previously cached files
            for folder in self._cache_folders:
                for path in os.listdir(folder):
                    file = os.path.join(folder, path)
                    if os.path.isfile(file):
                        os.remove(file)
            # Create new cache file and set default data
            self._cache = {'temporary': set(),
                           'dimension': dimension}

        # Queue for JSON file communication
        self._json_queues = [queue.Queue() for menu_label in self.MENU]

        # Create the Coub API object
        self._coub_api = api.CoubAPI(per_page=self.PAGE,
                                     app_name=self.NAME,
                                     app_version=version)

        # Run base Qt Application
        self._qt_app = QApplication(sys.argv)
        self._qt_app.setApplicationName(self.NAME)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, dimension):
        # Get local reference
        cache = self._cache

        # Store info
        cache['dimension'] = dimension
        cache['version'] = self._version

        # Clean up
        cache.setdefault('latest', set())
        for file in cache['latest'] - cache['temporary']:
            try:
                os.remove(file)
            # The program was terminated before all files were downloaded,
            # but the file name is already in the temporary list
            except FileNotFoundError:
                pass

        # Update values
        cache['latest'] = cache['temporary']
        cache['temporary'] = set()

        # Serialise new data
        with open(self._cache_file, 'wb') as cache_file:
            pickle.dump(cache, cache_file, pickle.HIGHEST_PROTOCOL)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        # Create CoubApp
        app = CoubAppUI(self, self._cache['dimension'], self.NAME, self.MENU, self.PAGE)
        app.show()
        # Enter event-loop
        return self._qt_app.exec_()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def start_loading_posts(self, index, packets_queue):
        # If there is more data to fetch
        try:
            self._coub_api.fetch_data_to_queue(index, self._json_queues[index])
            self._process_fetched_data(index, packets_queue)
        # If no more data
        except api.NoMoreDataToFetch:
            # TODO: indicate this to the user somehow
            pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _process_fetched_data(self, index, packets_queue):
        # If data fetched to queue
        try:
            # Translate fetched data into a coublet-packet
            fetched = self._json_queues[index].get_nowait()
            packets = self._coub_api.translate_fetched_data(fetched, index)

            # Process each coublet-packet
            files = set()
            path_video, path_thumb, path_user = self._cache_folders
            for i, packet in enumerate(packets):
                # Get unique coub ID
                id = packet['id']

                # Create and store video file name
                video_file = os.path.join(path_video, id + '.mp4')
                files.add(video_file)

                # Create and store thumbnail file name
                thumb_file = os.path.join(path_thumb, id + '.jpg')
                files.add(thumb_file)

                # Create and store avatar file name
                avatar_url = packet['user'][0]
                if avatar_url:
                    ext = os.path.splitext(avatar_url)[1]
                    user_file = os.path.join(path_user, packet['user_id'] + ext)
                    files.add(user_file)
                else:
                    user_file = None

                # Add file names to packet
                packet['video'].append(video_file)
                packet['thumb'].append(thumb_file)
                packet['user'].append(user_file)

                # If video file not already cached then
                # download it and push it to the queue
                if not os.path.isfile(video_file):
                    com.DownloadPacket(i, packet, packets_queue, self.CACHE_DATA,
                                       self.NAME, self._version).start()
                # If cached, pushed it to queue
                else:
                    packets_queue.put((i, packet))
            # Store files
            self._cache['temporary'].update(files)
        # If data didn't arrived yet
        except queue.Empty:
            # Schedule next processing
            QTimer.singleShot(300, lambda i=index, q=packets_queue:
                                       self._process_fetched_data(i, q))



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
    # TODO: catch all exceptions, store it to a log file, write that into
    #       the cache file and ask the user if he wants to send it to us
    sys.exit(CoubApp(v).run())

    # Print all module dependencies
    # CoubApp(v).run()
    # print(*['{}: {}'.format(k, v) for k, v in sys.modules.items()], sep='\n')
