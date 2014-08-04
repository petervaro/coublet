
import sys
import wdgt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout


qtapp = QApplication(sys.argv)

app = QWidget()

layout = QVBoxLayout()
layout.addWidget(wdgt.AnimatedGif('img/spinner.gif'))

app.setLayout(layout)
app.show()

qtapp.exec_()
