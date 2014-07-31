## INFO ########################################################################
##                                                                            ##
##                                  COUB App                                  ##
##                                  ========                                  ##
##                                                                            ##
##      Cross-platform desktop application for following posts from COUB      ##
##                       Version: 0.5.50.015 (20140731)                       ##
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
import urllib.request
from sys import argv, exit
from os.path import join, expanduser
from os import remove, makedirs, getcwd

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

    def __init__(self):
        # Create cache folder
        self.folder = join(expanduser('~'), '.coub_cache')
        makedirs(self.folder, exist_ok=True)
        # Create list for temporary files
        self._temp = []
        # Run base Qt Application
        self.qt_app = QApplication(argv)
        self.qt_app.setApplicationName('COUB')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def on_exit(self):
        # Clean up
        for file in self._temp:
            remove(file)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def load(self, app):
        file = join(self.folder, 'test_coub.mp4')
        urllib.request.urlretrieve(url=TEST_MP4, filename=file)
        self._temp.append(file)
        app.append(file, file, file)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        # Create CoubApp
        app = ui.CoubAppUI(self)
        app.show()
        self.load(app)
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
        cwd = getcwd()
        # Collect all special comments
        collect('.', exceptions=exceptions)
        # Update header comments
        header(cwd, exceptions=exceptions)
    # Run application
    exit(CoubApp().run())
