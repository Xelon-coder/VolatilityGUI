import sys

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout ,QWidget, QLineEdit, QTreeView, QCheckBox, QPushButton, QFileDialog, QComboBox, QLabel
from PySide2.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, QModelIndex
from tools import *
from volatilityInfo import *

MEMORY_FILE = "dump"
VOLATILITY_PATH = "volatility/vol.py"

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.vi = VolatilityInfo(MEMORY_FILE,VOLATILITY_PATH)

        self.setWindowTitle("Volatility GUI")
        self.setFixedSize(QSize(1200, 800))

        widgets = [(self.createTreePanel(),0,1,2,2),(self.createGreenPanel(),1,0,1,1),(self.createBluePanel(),0,0,1,1)]

        # Main frame
        widget = QWidget()
        widget.setLayout(self.createMainPanel(widgets))
        self.setCentralWidget(widget)

    def createGreenPanel(self):
        green_widget = Color('green')
        return green_widget
    
    def handleProfile(self,result):
        self.profilesButton.clear()
        self.profilesButton.addItems(result)

    def createBluePanel(self):
        blue_widget = Color('blue')

        button1 = QPushButton('Find profile',self)
        button1.clicked.connect(lambda: self.handleProfile(self.vi.determineProfile()))
        self.profilesButton = QComboBox(self)
        button2 = QPushButton('Select File', self)
        button3 = QPushButton('Select Folder', self)

        button2.clicked.connect(self.selectFile)
        button3.clicked.connect(self.selectDirectory)

        self.labelProfile = QLabel("Select volatility profile", self)
        self.labelFile = QLabel("Selected file :", self)
        self.labelDump = QLabel("Selected dump folder :", self)


        layoutButton = QVBoxLayout()
        layoutButton.addWidget(button2)
        layoutButton.addWidget(self.labelFile)
        layoutButton.addWidget(self.labelProfile)
        layoutButton.addWidget(button1)
        layoutButton.addWidget(self.profilesButton)
        layoutButton.addWidget(button3)
        layoutButton.addWidget(self.labelDump)

        blue_widget.setLayout(layoutButton)

        return blue_widget

    def createTreePanel(self):

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Nom du fichier'])

        #_,root = self.vi.filterFiles('')

        #self.add_node(root,self.model)

        self.tree = QTreeView()
        #self.tree.setModel(self.model)
        #self.tree.show()
        
        # Tree Ps and Files Widget
        self.searchbar = QLineEdit()
        self.checkbox = QCheckBox("Expand All")
        self.checkbox.stateChanged.connect(self.expand_tree)
        self.searchbar.textChanged.connect(self.filter_tree)  # Connect the slot

        treePanel = Color('red')
        treeLayout = QHBoxLayout()

        layoutFilter = QVBoxLayout()
        layoutFilter.addWidget(self.searchbar,1)
        layoutFilter.addWidget(self.checkbox)
        layoutFilter.addWidget(self.tree,2)

        treeLayout.addLayout(layoutFilter)
        treePanel.setLayout(treeLayout)

        return treePanel

    def createMainPanel(self,widgets):
        layout = QGridLayout()
        for wid,row,col,spanRow,spanCol in widgets:
            layout.addWidget(wid, row, col, spanRow, spanCol)
        return layout

    def add_node(self,node, parent):
        
        item = QStandardItem(node.name.name)

        existing_items = self.model.findItems(node.name.name, Qt.MatchExactly | Qt.MatchRecursive)
        if existing_items:
            item = existing_items[0]
        else:
            parent.appendRow(item)

        for child in node.children:
            self.add_node(child, item)

    def filter_tree(self, text):
        _, root = self.vi.filterFiles(text)
        self.model.clear()  # Clear the existing model
        self.model.setHorizontalHeaderLabels(['Nom du fichier'])
        self.add_node(root, self.model)
        self.tree.setModel(self.model)  # Update the model of the tree
        
        if self.checkbox.isChecked():
            self.tree.expandAll()

    def expand_tree(self, state):
        if state == Qt.Checked:
            self.tree.expandAll()
        else:
            self.tree.collapseAll()

    def selectFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Choisir un fichier", "", "Tous les fichiers (*)")
        if filename:
            self.vi.memoryFile = filename
            self.labelFile.clear()
            self.labelFile.setText("Selected file :"+str(filename))

    def selectDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir un dossier", "",)
        if directory:
            self.vi.dumpDirectory = directory
            self.labelDump.clear()
            self.labelDump.setText("Selected dump folder :"+str(directory))

if __name__=="__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()