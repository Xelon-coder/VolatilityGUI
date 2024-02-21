import sys

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout ,QWidget, QLineEdit, QTreeView, QCheckBox, QPushButton, QFileDialog, QComboBox, QLabel, QTextEdit
from PySide2.QtGui import QPalette, QColor, QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, QModelIndex
from tools import *
from volatilityInfo import *
from io import StringIO

MEMORY_FILE = "dump"
VOLATILITY_PATH = "volatility/vol.py"

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(239,239,239))
        self.setPalette(palette)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.vi = VolatilityInfo(MEMORY_FILE,VOLATILITY_PATH)

        self.setWindowTitle("Volatility GUI")
        self.setFixedSize(QSize(1200, 800))

        widgets = [(self.createTreePanel(),0,1,2,1),(self.createGreenPanel(),1,0,1,1),(self.createBluePanel(),0,0,1,1),(self.createConsolePanel(),2,0,1,2)]

        self.currentFiles = None
        self.currentPid = None
        self.currentCommand = None

        # Main frame
        widget = QWidget()
        widget.setLayout(self.createMainPanel(widgets))
        self.setCentralWidget(widget)

    def createConsolePanel(self):
        console_widget = Color('black')

        self.commandFeild = QLineEdit()
        self.commandFeild.setPlaceholderText('Enter volatility plugin')
        self.commandFeild.textChanged.connect(self.updateCommand)
        self.commandContent = QTextEdit()
        self.commandContent.setReadOnly(True)
        self.commandButton = QPushButton("Execute")
        self.commandButton.clicked.connect(self.executeCommand)
    
        layout = QGridLayout()
        layout.addWidget(self.commandFeild,0,0,1,1)
        layout.addWidget(self.commandButton,0,1,1,1)
        layout.addWidget(self.commandContent,1,0,1,2)

        console_widget.setLayout(layout)

        return console_widget

    def createGreenPanel(self):
        green_widget = Color('green')

        self.dumpFilesButton = QPushButton("Dumpfiles")
        self.dumpFilesButton.setEnabled(False)
        self.dumpFilesButton.clicked.connect(self.dumpFiles)

        self.memDumpButton = QPushButton("Memdump")
        self.memDumpButton.setEnabled(False)
        self.memDumpButton.clicked.connect(self.memDump)
        self.procDumpButton = QPushButton("Procdump")
        self.procDumpButton.setEnabled(False)
        self.procDumpButton.clicked.connect(self.procDump)

        self.pidText = QLineEdit()
        self.pidText.setPlaceholderText("Set your pid here")
        self.pidText.textChanged.connect(self.updatePid)

        self.labelFileInfo = QLabel("File Information")

        layoutButton = QGridLayout()
        layoutButton.addWidget(self.labelFileInfo,0,0,1,1)
        layoutButton.addWidget(self.dumpFilesButton,0,1,1,2)
        layoutButton.addWidget(self.pidText,1,0,1,1)
        layoutButton.addWidget(self.memDumpButton,1,1,1,1)
        layoutButton.addWidget(self.procDumpButton,1,2,1,1)

        green_widget.setLayout(layoutButton)

        return green_widget
    
    def handleProfile(self,result):
        self.profilesButton.clear()
        self.profilesButton.addItems(result)
        if len(result) > 0:
            self.profilesButton.setCurrentIndex(0)

    def createBluePanel(self):
        blue_widget = Color('blue')

        button1 = QPushButton('Find profile',self)
        button1.clicked.connect(lambda: self.handleProfile(self.vi.determineProfile()))
        self.profilesButton = QComboBox(self)
        self.profilesButton.currentIndexChanged.connect(self.profileChanged)
        button2 = QPushButton('Select File', self)
        button3 = QPushButton('Select Folder', self)

        button2.clicked.connect(self.selectFile)
        button3.clicked.connect(self.selectDirectory)

        #self.labelProfile = QLabel("Aelect volatility profile", self)
        self.labelFile = QLabel("Selected file :", self)
        self.labelDump = QLabel("Selected dump folder :", self)


        layoutButton = QGridLayout()
        layoutButton.addWidget(button2,0,0,1,1)
        layoutButton.addWidget(self.labelFile,1,0,1,1)
        #layoutButton.addWidget(self.labelProfile)
        layoutButton.addWidget(button1,0,1,1,1)
        layoutButton.addWidget(self.profilesButton,1,1,1,1)
        layoutButton.addWidget(button3,2,0,1,1)
        layoutButton.addWidget(self.labelDump,3,0,1,1)

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

        self.tree.clicked.connect(self.on_tree_clicked)
        
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
        item.setData(node.name, Qt.UserRole)

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
        self.tree.clicked.connect(self.on_tree_clicked)
        
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
            if len(filename) > 20:
                filename = '...'+str(filename[len(filename)-20:])
            self.labelFile.clear()
            self.labelFile.setText("Selected file :"+str(filename))

    def selectDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Choisir un dossier", "",)
        if directory:
            self.vi.dumpDirectory = directory
            if len(directory) > 20:
                directory = '...'+str(directory[len(directory)-20:])
            self.labelDump.clear()
            self.labelDump.setText("Selected dump folder : "+str(directory))

    def on_tree_clicked(self, index: QModelIndex):
        item = self.model.itemFromIndex(index)
        self.dumpFilesButton.setEnabled(True)
        if item is not None:
            file_obj = item.data(Qt.UserRole)
            if file_obj is not None:
                self.currentFiles = file_obj
                self.labelFileInfo.setText("File Informations\nOffset: "+str(file_obj.offset)+"\nPtr: "+str(file_obj.ptr)+"\nHnd: "+str(file_obj.hnd)+"\nAccess: "+str(file_obj.access)+"\nName: "+str(file_obj.name))

    def dumpFiles(self):
        if self.currentFiles != None:
            self.vi.dumpFiles(self.currentFiles.offset,self.vi.dumpDirectory)

    def memDump(self):
        if self.currentPid != None:
            self.vi.memDump(self.currentPid,self.vi.dumpDirectory)

    def procDump(self):
        if self.currentPid != None:
            self.vi.procDump(self.currentPid,self.vi.dumpDirectory)

    def updatePid(self, pid):
        if len(pid) != 0:
            try:
                self.currentPid = str(int(pid))
                self.procDumpButton.setEnabled(True)
                self.memDumpButton.setEnabled(True)
            except:
                print("[!] Only numbers")
                self.procDumpButton.setEnabled(False)
                self.memDumpButton.setEnabled(False)

    def updateCommand(self,command):
        self.currentCommand = command

    def executeCommand(self):
        stdout,stderr = self.vi.runVolatilityCommand(self.currentCommand)
        self.commandContent.setText(stdout.decode('utf-8'))

    def profileChanged(self, index):
        self.vi.profile = self.profilesButton.currentText()

if __name__=="__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()