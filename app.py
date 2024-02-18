import sys

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QApplication, QMainWindow, QGridLayout, QVBoxLayout, QHBoxLayout ,QWidget, QLineEdit, QTreeView, QCheckBox
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
        self.vi.profile = "Win7SP1x86_23418"

        self.setWindowTitle("Volatility GUI")
        self.setFixedSize(QSize(1200, 800))

        layout = QGridLayout()

        # DrawTree
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Nom du fichier'])

        _,root = self.vi.filterFiles('')

        self.add_node(root,self.model)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.show()
        
        # Tree Ps and Files Widget
        self.searchbar = QLineEdit()
        self.checkbox = QCheckBox("Expand All")
        self.checkbox.stateChanged.connect(self.expand_tree)
        self.searchbar.textChanged.connect(self.filter_tree)  # Connect the slot

        red_widget = Color('red')
        treeLayout = QHBoxLayout()

        layoutFilter = QVBoxLayout()
        layoutFilter.addWidget(self.searchbar,1)
        layoutFilter.addWidget(self.checkbox)
        layoutFilter.addWidget(self.tree,2)

        treeLayout.addLayout(layoutFilter)
        red_widget.setLayout(treeLayout)

        layout.addWidget(red_widget, 0, 1, 2, 2)  # Row 0, Col 0, Span 1 Row, 2 Co

        # Green Widget
        green_widget = Color('green')
        layout.addWidget(green_widget, 1, 0, 1, 1)  # Row 1, Col 0, Span 1 Row, 1 Col

        # Blue Widget
        green_widget = Color('blue')
        layout.addWidget(green_widget, 0, 0, 1, 1)  # Row 1, Col 0, Span 1 Row, 1 Col

        # Main frame
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

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

if __name__=="__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()