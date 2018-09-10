import pymel.core as pm
import maya.cmds as cmds

from pprint import pprint

try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except:
    pass

class UI(QWidget):
    def __init__(self):

        self.window = QWidget()
        self.window.setGeometry(200,200,500,600)
        self.window.setWindowTitle("Connection Editor")

        self.attrConn = {"from": "", "to": "", "inverse": False}
        self.leftObject = []
        self.rightObject = []

        self.config_ui()

        self.window.show()

    def config_ui(self):

        #layouts
        self.mainLayout       = QVBoxLayout()
        self.topButtonsLayout = QHBoxLayout()
        self.topLabelsLayout  = QHBoxLayout()
        self.searchLayout     = QHBoxLayout()
        self.listLayout       = QHBoxLayout()
        self.closeButtonLayout= QHBoxLayout()

        #instances
        self.color_active       = QColor(200,200,200,255)
        self.color_inative      = QColor(100,100,100,255)
        self.color_connected    = QColor(237,241,30,255)

        self.reloadLeftButton   = QPushButton("Reload Left")
        self.reloadRightButton  = QPushButton("Reload Right")
        self.leftLabel          = QLabel("Outputs")
        self.changeDirectionBtn = QPushButton("from -> to")
        self.rightLabel         = QLabel("Inputs")
        self.leftSearch         = QLineEdit("Search...")
        self.rightSearch        = QLineEdit("Search...")
        self.leftList           = QTreeWidget()
        self.rightList          = QTreeWidget()
        self.breakAllConnections= QPushButton("Break all")
        self.breakSelConnections= QPushButton("Break selection")
        self.closeButton        = QPushButton("Close")

        # layout config
        self.window.setLayout(self.mainLayout)
        self.mainLayout.addLayout(self.topButtonsLayout)
        self.mainLayout.addLayout(self.topLabelsLayout)
        self.mainLayout.addLayout(self.searchLayout)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addLayout(self.closeButtonLayout)

        self.topButtonsLayout.addWidget(self.reloadLeftButton)
        self.topButtonsLayout.addWidget(self.reloadRightButton)
        self.topLabelsLayout.addWidget(self.leftLabel, 1)
        self.topLabelsLayout.addWidget(self.changeDirectionBtn, 1)
        self.topLabelsLayout.addWidget(self.rightLabel, 1)
        self.searchLayout.addWidget(self.leftSearch)
        self.searchLayout.addWidget(self.rightSearch)
        self.listLayout.addWidget(self.leftList)
        self.listLayout.addWidget(self.rightList)
        self.closeButtonLayout.addWidget(self.breakSelConnections)
        self.closeButtonLayout.addWidget(self.breakAllConnections)
        self.closeButtonLayout.addWidget(self.closeButton)

        # config
        self.leftLabel.setAlignment(Qt.AlignCenter)
        self.rightLabel.setAlignment(Qt.AlignCenter)

        self.reloadLeftButton.clicked.connect(self.setLeftList)
        self.reloadRightButton.clicked.connect(self.setRightList)

        self.leftSearch.textChanged.connect(self.leftSearchFilter)
        self.rightSearch.textChanged.connect(self.rightSearchFilter)

        self.leftList.itemClicked.connect(self.leftConnect)
        self.rightList.itemClicked.connect(self.rightConnect)

        self.changeDirectionBtn.clicked.connect(self.changeDirection)

        self.closeButton.clicked.connect(self.closeApp)

        self.breakSelConnections.clicked.connect(self.breakSel)
        self.breakAllConnections.clicked.connect(self.breakAll)

    def breakAll(self):
        attributes = []

        for obj in self.leftObjDict:
            for k in obj.keys():
                for attr in obj[k]:
                    node = pm.PyNode("{}.{}".format(k, attr["name"]))
                    attributes += [node]

        for obj in self.rightObjDict:
            for k in obj.keys():
                for attr in obj[k]:
                    node = pm.PyNode("{}.{}".format(k, attr["name"]))
                    attributes += [node]

        self.breakAttributes(attributes)

    def breakSel(self):
        leftAttr = [attr for attr in self.leftList.selectedItems() if attr.parent()]
        rightAttr = [attr for attr in self.rightList.selectedItems() if attr.parent()]
        attributes = leftAttr + rightAttr

        pyAttributes = [pm.PyNode("{}.{}".format(attr.parent().text(0), attr.text(0))) for attr in attributes]

        self.breakAttributes(pyAttributes)

    def breakAttributes(self, attributes):

        for attr in attributes:
            try:
                attr.disconnect()
            except Exception as e:
                raise e
                pass

        if self.leftSearch.text() != "Search...":
            filter = self.leftSearch.text()

        self.reloadLeftList(filter=filter)

        if self.rightSearch.text() != "Search...":
            filter = self.rightSearch.text()

        self.reloadRightList(filter=filter)

    def closeApp(self):
        self.window.close()

    def changeDirection(self):

        if self.attrConn["inverse"] == False:
            self.attrConn["inverse"] = True

            self.leftLabel.setText("Output")
            self.rightLabel.setText("Input")
            self.changeDirectionBtn.setText("to <- from")
        else:
            self.attrConn["inverse"] = False

            self.leftLabel.setText("Input")
            self.rightLabel.setText("Output")

            self.changeDirectionBtn.setText("from -> to")

    def leftConnect(self):

        attr = self.leftList.selectedItems()
        if attr:
            if attr[0].parent():
                self.attrConn["from"] = pm.PyNode("{}.{}".format(attr[0].parent().text(0), attr[0].text(0)))

                self.connectAttributes()

    def rightConnect(self):

        attr = self.rightList.selectedItems()
        if attr:
            if attr[0].parent():
                self.attrConn["to"] = pm.PyNode("{}.{}".format(attr[0].parent().text(0), attr[0].text(0)))

                self.connectAttributes()

    def connectAttributes(self):
        print self.attrConn
        if self.attrConn["from"] != "" and self.attrConn["to"] != "":
            try:
                if self.attrConn["inverse"] == False:
                    pm.connectAttr(self.attrConn["from"], self.attrConn["to"], force=True)
                else:
                    pm.connectAttr(self.attrConn["to"], self.attrConn["from"], force=True)

                self.leftSearchFilter()
                self.rightSearchFilter()

                printConnLog(self.attrConn)

                self.attrConn["from"] = ""
                self.attrConn["to"] = ""
            except Exception as e:
                raise e
                pass

    def setLeftList(self):
        self.leftObject = pm.ls(selection=True)
        filter = None
        if self.leftSearch.text() != "Search...":
            filter = self.leftSearch.text()

        self.reloadLeftList(filter=filter)

    def setRightList(self):
        self.rightObject = pm.ls(selection=True)
        filter = None
        if self.rightSearch.text() != "Search...":
            filter = self.rightSearch.text()
        self.reloadRightList(filter=filter)

    def leftSearchFilter(self):

        filter = self.leftSearch.text()
        self.reloadLeftList(filter=filter)

    def rightSearchFilter(self):

        filter = self.rightSearch.text()
        self.reloadRightList(filter=filter)

    def reloadLeftList(self, filter=None):

        self.leftObjDict = [{object: self.check_filter(object, pm.listAttr(object, connectable=True), filter)}
                           for object in self.leftObject]

        self.make_tree_list(self.leftList, self.leftObjDict)

    def reloadRightList(self, filter=None):

        self.rightObjDict = [{object: self.check_filter(object, pm.listAttr(object, connectable=True), filter)}
                           for object in self.rightObject]

        self.make_tree_list(self.rightList, self.rightObjDict)

    def check_filter(self, object, list, filter):

        attributes_list = [pm.PyNode("{}.{}".format(object, attr)) for attr in list]

        if filter != None:
            attr_dict = [{
                "name": attr.name().split('.')[-1],
                "type": self.check_type(attr),
                "connected": self.check_isConnected(attr)
            } for attr in attributes_list if filter in attr.name().split('.')[-1]]
        else:
            attr_dict = [{
                "name": attr.name().split('.')[-1],
                "type": self.check_type(attr),
                "connected": self.check_isConnected(attr)
            } for attr in attributes_list]

        return attr_dict

    def check_isConnected(self, attr):

        try:
            status = attr.isConnected()
        except:
            status = None

        return status

    def check_type(self, attr):

        try:
            t = attr.type()
        except:
            t = None

        return t


    def make_tree_list(self, listWidget, objDict):

        listWidget.clear()
        for object in objDict:
            parent_name = object.keys()[0].fullPath()
            parent = QTreeWidgetItem(listWidget)
            parent.setExpanded(1)
            parent.setText(0, parent_name)
            for attr in object[object.keys()[0]]:
                child = QTreeWidgetItem(parent)
                child.setText(0, attr['name'])
                if attr['connected'] == True:
                    child.setTextColor(0, self.color_connected)
                else:
                    child.setTextColor(0, self.color_active)


def printConnLog(attr_dict):

    if attr_dict["inverse"] == False:
        f = attr_dict["from"]
        t = attr_dict["to"]
    else:
        f = attr_dict["to"]
        t = attr_dict["from"]

    print "{:*^100}".format(" Connection Log ")
    print "{: ^100}".format(" The attribute %s was connected to %s with successfully." % (f, t))
    print "{:*^100}".format("")
