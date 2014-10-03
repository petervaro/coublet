#!/usr/bin/env python3
## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.95.240 (20141003)                       ##
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
import sys

# Import PyQt5 modules
from PyQt5.QtWidgets import QApplication

# Import Coublet modules
from models.cache import CACHE
from models.app import CoubletAppModel
from models.com import set_user_agent
from presenters.window import CoubletWindowPresenter
from views.vars import set_gui_constants, DEFAULT_WINDOW_POS_DIM

# Module level constants
# TODO: read version from file (where will VERSION file be in the final app?)
VERSION = 0, 6, 95
DEV = 1

#------------------------------------------------------------------------------#
class CoubletApp(QApplication):

    NAME = 'coublet'

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, version, *args, **kwargs):
        super().__init__(sys.argv, *args, **kwargs)
        # Set name of app
        self.setApplicationName(self.NAME)

        # Set global GUI constants
        set_gui_constants(self)

        # HACK: find an elegant way to solve these global variables
        set_user_agent(self.NAME, version)
        CACHE.load(version, DEFAULT_WINDOW_POS_DIM)

        self._model = CoubletAppModel()
        self._presenter = CoubletWindowPresenter(self._model, self.NAME)

        # Start auto-saving
        self._presenter.set_auto_save(CACHE.auto_save)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def run(self):
        # TODO: catch all exceptions, store it to a log file, write that into
        #       the cache file and ask the user if he wants to send it to us
        self._presenter.show_view()
        return self.exec_()
        # # Print all module dependencies
        # print(*['{}: {}'.format(k, v) for k, v in sys.modules.items()], sep='\n')



#==============================================================================#
if __name__ == '__main__':
    version = VERSION
    if DEV:
        # Import cutils modules
        import cutils.ccom
        import cutils.clic
        import cutils.cver
        # Extend exceptions
        exceptions = cutils.clic.EXCEPTIONS + ('clic.py', 'cver.py', 'ccom.py',
                                               'comment.py', 'check.py', 'table.py')
        # Update version
        version = cutils.cver.version('.', sub_max=9, rev_max=99, build_max=999)[:3]
        # Collect all special comments
        cutils.ccom.collect('.', exceptions=exceptions)
        # Update header comments
        cutils.clic.header('.', exceptions=exceptions)
    # Run application
    sys.exit(CoubletApp(version).run())
