## INFO ########################################################################
##                                                                            ##
##                                  COUBLET                                   ##
##                                  =======                                   ##
##                                                                            ##
##          Cross-platform desktop client to follow posts from COUB           ##
##                       Version: 0.6.93.172 (20140814)                       ##
##                                                                            ##
##                          File: widgets/handler.py                          ##
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

# Import PyQt5 modules
from PyQt5.QtCore import Qt, QTimer

f = lambda *args, **kwargs: None

#------------------------------------------------------------------------------#
class CoubletMouseEventHandler:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, interval=300, l_single=f, l_double=f, r_single=f, r_double=f):
        # Create Timer objects, set them and connect events
        self.l_timer = l_timer = QTimer()
        self.r_timer = r_timer = QTimer()
        for i, side in enumerate((l_timer, r_timer)):
            side.setInterval(interval)
            side.setSingleShot(True)
            side.timeout.connect(lambda s=i: self._on_timeout(s))

        # Click counter
        self._counters = [0, 0]

        # Set callbacks
        self._singles = [l_single, r_single]
        self._doubles = [l_double, r_double]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _on_timeout(self, index):
        if self._counters[index] > 1:
            self._doubles[index]()
        else:
            self._singles[index]()
        # Reset counter
        self._counters[index] = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def click(self, button):
        # Clicked by left mouse button
        if button == Qt.LeftButton:
            self._counters[0] += 1
            if not self.l_timer.isActive():
                self.l_timer.start()

        # Clicked by right mouse button
        if button == Qt.RightButton:
            self._counters[1] += 1
            if not self.r_timer.isActive():
                self.r_timer.start()
