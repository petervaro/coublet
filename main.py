## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.61.108 (20140801)                       ##
##                                                                            ##
##               File: /Users/petervaro/Documents/coub/main.py                ##
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
import pickle
import os.path
import urllib.request

# Import PyQt5 modules
from PyQt5.QtWidgets import QApplication

# Import coub modules
import ui
import api

# Module level constants
DEV = True
TEST_MP4 = ('http://cdn1.akamai.coub.com/coub/simple/cw_file/1e0af8db2af/'
            'b69e3f00cd68c8d07a3ea/mp4_small_size_1376204276_small.mp4')

#------------------------------------------------------------------------------#
class CoubApp:

    FILE = 'cache'
    PATH = '.coub_cache'

    def __init__(self):
        # Create cache folder and file
        self._path = os.path.join(os.path.expanduser('~'), self.PATH)
        self._file = os.path.join(self._path, self.FILE)
        os.makedirs(self._path, exist_ok=True)


        # If load previously saved data
        try:
            with open(self._file, 'rb') as cache:
                self._temp = pickle.load(cache)
        # If first run of app
        except (FileNotFoundError, EOFError):
            self._temp = {'temporary':[]}

        # Create API object
        self.source = api.CoubAPI()

        # Run base Qt Application
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setApplicationName('COUB')


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load_menu(self, index):
        print(('FEATURED', 'NEWEST', 'RANDOM', 'USER')[index])
        files = []
        # TODO: _load_stream(index) is a private method
        #       or that should be part of the public interface?
        for packet in self.source._load_stream(index):
            file = os.path.join(self._path, packet['id'] + '.mp4')
            urllib.request.urlretrieve(url=packet['video'], filename=file)
            files.append(file)
        self._temp['temporary'].extend(files)
        return files

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self, position, dimension):
        # Store info
        self._temp['startup_pos'] = position
        self._temp['startup_dim'] = dimension
        # Clean up
        for file in self._temp['temporary']:
            os.remove(file)
        with open(self._file, 'wb') as cache:
            pickle.dump(self._temp, cache, pickle.HIGHEST_PROTOCOL)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        # Get previous position and dimension
        x, y = self._temp.setdefault('startup_pos', (NotImplemented, 0))
        width, height = self._temp.setdefault('startup_dim', (320, 768))
        # Create CoubApp
        app = ui.CoubAppUI(self, x, y, width, height)
        app.show()
        return self.qt_app.exec_()



#==============================================================================#
if __name__ == '__main__':
    if DEV:
        # Import cutils modules
        from cutils.cver import version
        from cutils.ccom import collect
        from cutils.clic import header, EXCEPTIONS
        exceptions = ('clic.py', 'cver.py', 'ccom.py',
                      'comment.py', 'check.py', 'table.py')
        exceptions += EXCEPTIONS
        # Update version
        version(sub_max=9,
                rev_max=99,
                build_max=999)
        cwd = os.getcwd()
        # Collect all special comments
        collect('.', exceptions=exceptions)
        # Update header comments
        # ??? cwd or '.' ???
        header(cwd, exceptions=exceptions)
    # Run application
    sys.exit(CoubApp().run())
