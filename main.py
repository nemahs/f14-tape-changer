# This Python file uses the following encoding: utf-8
import sys
import os
import logging
from typing import List, Set, Optional
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QListWidgetItem as ListItem

SONGTITLES = [f"Song{x}.ogg" for x in range(1,11)]

class Main(QtWidgets.QMainWindow):
    """Main class for the Qt front end"""

    def __init__(self):
        """
        Constructor.

        Also displays the window once constructed,
        """
        super(Main, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.loadedTape: Optional[ListItem] = None

        self.folderPicker: QtWidgets.QToolButton = self.findChild(QtWidgets.QToolButton, 'folderPicker')
        self.folderPicker.clicked.connect(self.findDCS)

        self.folderDisplay: QtWidgets.QLineEdit = self.findChild(QtWidgets.QLineEdit, 'folderDisplay')

        self.tapePicker: QtWidgets.QListWidget = self.findChild(QtWidgets.QListWidget, 'tapePicker')

        self.tapeLoad: QtWidgets.QPushButton = self.findChild(QtWidgets.QPushButton, 'tapeLoad')
        self.tapeLoad.clicked.connect(self.loadTape)

        self.show()

    def updateLoadedTape(self, tape: ListItem) -> None:
        """
        Updates the loaded tape display.

        @param tape Currently loaded tape
        """
        logging.info(f"Setting {tape.path} as the selected tape")
        tape.setText(f"* {tape.path}")
        if self.loadedTape:
            self.loadedTape.setText(f"  {self.loadedTape.name}")
        self.loadedTape = tape
        

    def findDCS(self) -> None:
        """
        Gets the DCS folder.

        Allows the user to select the DCS folder and finds the walkman subdirectory.
        """
        dialog = QtWidgets.QFileDialog(self, 'DCS Folder')
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            os.chdir(f"{dialog.selectedFiles()[0]}/Mods/aircraft/F14/Sounds/Walkman/")
            self.folderDisplay.setText(dialog.selectedFiles()[0])

            for fd in os.scandir():
                if fd.is_dir(follow_symlinks=False):
                    logging.info("Found {fd.name}")
                    newItem = QtWidgets.QListWidgetItem()
                    newItem.setText(f"  {fd.name}")
                    newItem.path = fd.name
                    
                    self.tapePicker.addItem(newItem)

            self.updateLoadedTape(self.determineLoadedTape())

    def determineLoadedTape(self) -> ListItem:
        """
        Determines the currently loaded tape by checking the symlink paths

        @warn This only works if the folder is configured properly
        @return loaded tape
        """
        tapes: Set[str] = set()
        
        for song in SONGTITLES:
            if os.path.islink(song):
                tape, __ = os.readlink(song).split('\\')
                tapes.add(tape)

        if len(tapes) == 1:
            selectedTape: List[ListItem] = self.tapePicker.findItems(f"[\*, ] {tapes.pop()}", QtCore.Qt.MatchRegularExpression)
            return selectedTape[0]
        return None

    def loadTape(self) -> None:
        """
        Loads the currently selected tape into the F14.
        """
        tapeToLoad = self.tapePicker.currentItem()

        if not tapeToLoad:
            logging.warn("No tape was selected to load!")
            return


        # TODO Check for symlinks to make sure we don't clobber anything. Needs a convert function though
        for song in SONGTITLES:
            logging.info(f"Replacing {song}")
            if os.path.exists(song):
                os.remove(song)
            os.symlink(f"{tapeToLoad.path}\\{song}", song)

        self.updateLoadedTape(tapeToLoad)
       

if __name__ == "__main__":
    logging.basicConfig(filename='TapeChanger.log', level=logging.DEBUG)
    app = QApplication([])
    window = Main()
    # ...
    sys.exit(app.exec_())
