## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.220 (20140928)                       ##
##                                                                            ##
##                           File: models/cache.py                            ##
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
import os
import pickle

#------------------------------------------------------------------------------#
class CoubletCacheFile:

    FILE = 'cache'
    PATH = '.coub_cache'
    DIRS = 'videos', 'thumbnails', 'avatars'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self):
        # Create path string of global cache folder and cache file
        self._path = path = os.path.join(os.path.expanduser('~'), self.PATH)
        self._file = os.path.join(path, self.FILE)
        os.makedirs(self._path, exist_ok=True)

        # Create folders for downloaded
        # cache data if it doesn`t exist
        self._folders = folders = []
        for folder_name in self.DIRS:
            folder_path = os.path.join(path, folder_name)
            folders.append(folder_path)
            os.makedirs(folder_path, exist_ok=True)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self, version, dimension):
        # Load previously saved data if exists
        try:
            with open(self._file, 'rb') as cache_file:
                # Deserialise cache data
                self._data = pickle.load(cache_file)
                # If cache file's version is not the same
                # as the app create new cache object and
                # store the version independent data
                if self._data['version'] < version:
                    dimension = self._data['dimension']
                    # Remove cached files
                    raise FileNotFoundError
        # If first run of app or app has been updated
        except (FileNotFoundError, EOFError):
            # Delete all previously cached files
            for folder in self._folders:
                for path in os.listdir(folder):
                    file = os.path.join(folder, path)
                    if os.path.isfile(file):
                        os.remove(file)
            # Create new cache file and set default data
            self._data = {'temporary': set(),
                          'dimension': dimension,
                          'folders'  : self._folders,
                          'version'  : version}


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __getitem__(self, key):
        return self._data[key]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __setitem__(self, key, value):
        self._data[key] = value


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _serialise(self):
        # Serialise data
        with open(self._file, 'wb') as cache_file:
            pickle.dump(self._data, cache_file, pickle.HIGHEST_PROTOCOL)
            print('Cache file serialised.')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def auto_save(self):
        # Public wrapper for saving data
        self._serialise()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def save(self):
        # Get local reference
        data = self._data

        # Clean up
        data.setdefault('latest', set())
        for file in data['latest'] - data['temporary']:
            try:
                os.remove(file)
            # The program was terminated before all files were downloaded,
            # but the file name is already in the temporary list
            except FileNotFoundError:
                pass

        # Update values
        data['latest'] = data['temporary']
        data['temporary'] = set()

        # Save data
        self._serialise()


#------------------------------------------------------------------------------#
# Global cache object
CACHE = CoubletCacheFile()
