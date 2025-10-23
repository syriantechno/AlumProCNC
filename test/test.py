from PyQt5.QtWidgets import QApplication, QMainWindow
from pyvistaqt import QtInteractor
import pyvista as pv
import sys

app = QApplication(sys.argv)
win = QMainWindow()
plotter = QtInteractor(win)
win.setCentralWidget(plotter.interactor)
plotter.add_mesh(pv.Cube(), color="skyblue")
win.show()
sys.exit(app.exec_())
