#!/usr/bin/python3

import sys
import os
import json
import shutil
import platform
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QCheckBox, QSizePolicy, QMessageBox, QFrame, QTextEdit, QListWidget, QListWidgetItem, QHBoxLayout, QAbstractItemView, QSlider, QComboBox
from PyQt5.QtGui import QPixmap, QImageReader, QIcon, QImage
from PyQt5.QtCore import Qt
from PIL import Image

if platform.system() == "Windows":
    if os.getenv("LOCALAPPDATA"):
        baseDir = os.getenv("LOCALAPPDATA") + "\\cosmic-reach\\mods\\assets"
    else:
        baseDir = ".\\mods\\assets"
else:
    if os.getenv("XDG_DATA_HOME"):
        baseDir = os.getenv("XDG_DATA_HOME") + "/cosmic-reach/mods/assets"
    elif os.getenv("HOME"):
        baseDir = os.getenv("HOME") + "/.local/share/cosmic-reach/mods/assets"
    else:
        baseDir = "./mods/assets"


class NewEventWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('New Event')
        self.setWindowModality(Qt.WindowModal)
        self.layout = QVBoxLayout()

        self.new_event_button = QPushButton('New Event')
        self.new_event_button.clicked.connect(self.add_event)
        self.layout.addWidget(self.new_event_button)

        self.event_list = QListWidget()
        self.event_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.event_list.itemClicked.connect(self.expand_event)
        self.layout.addWidget(self.event_list)

        self.setLayout(self.layout)

    def add_event(self):
        item = QListWidgetItem('New Event')
        item.setSizeHint(QSize(0, 60))
        self.event_list.addItem(item)

    def expand_event(self, item):
        if item.sizeHint().height() == 60:
            item.setSizeHint(QSize(0, 120))

            dropdown1 = QComboBox()
            dropdown1.addItems(['on interact', 'on break'])

            dropdown2 = QComboBox()
            dropdown2.addItem('replace block')

            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.addWidget(dropdown1)
            layout.addWidget(dropdown2)

            self.event_list.setItemWidget(item, widget)
        else:
            item.setSizeHint(QSize(0, 60))
            self.event_list.setItemWidget(item, None)

def apply_transparency(image_path, transparency):
    img = Image.open(image_path)
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    for i in range(img.width):
        for j in range(img.height):
            r, g, b, a = img.getpixel((i, j))
            img.putpixel((i, j), (r, g, b, int(255 * (1 - transparency))))
    return img

class SimpleApp(QWidget):
    def __init__(self):
        super().__init__()
        self.imagePath = None
        self.items = []
        self.selectedItemIndex = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.modNameLabel = QLabel('Mod Name:', self)
        layout.addWidget(self.modNameLabel)

        self.modNameInput = QLineEdit(self)
        layout.addWidget(self.modNameInput)

        self.blockNameLabel = QLabel('Block Name:', self)
        layout.addWidget(self.blockNameLabel)

        self.blockNameInput = QLineEdit(self)
        layout.addWidget(self.blockNameInput)

        self.imageFrame = QFrame(self)
        self.imageFrame.setFixedSize(64, 64)
        self.imageFrame.setFrameShape(QFrame.Box)
        self.imageFrame.setFrameShadow(QFrame.Sunken)
        layout.addWidget(self.imageFrame)

        self.imageLabel = QLabel(self.imageFrame)
        self.imageLabel.setFixedSize(64, 64)
        self.imageLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.browseButton = QPushButton('Browse', self)
        self.browseButton.clicked.connect(self.showDialog)
        layout.addWidget(self.browseButton)

        self.includeSlabsCheckbox = QCheckBox('Include Slabs?', self)
        layout.addWidget(self.includeSlabsCheckbox)

        self.transparencyLabel = QLabel('Transparency:', self)
        layout.addWidget(self.transparencyLabel)

        self.transparencySlider = QSlider(Qt.Horizontal, self)
        self.transparencySlider.setMinimum(0)
        self.transparencySlider.setMaximum(100)
        self.transparencySlider.setValue(0)
        self.transparencySlider.setTickPosition(QSlider.TicksBelow)
        self.transparencySlider.setTickInterval(10)
        self.transparencySlider.valueChanged.connect(self.updateTransparencyLabel)
        layout.addWidget(self.transparencySlider)

        self.transparencyValueLabel = QLabel('0', self)
        layout.addWidget(self.transparencyValueLabel)

        buttonLayout = QHBoxLayout()
        self.applyEditButton = QPushButton('Apply Edit', self)
        self.applyEditButton.clicked.connect(self.applyEdit)
        buttonLayout.addWidget(self.applyEditButton)

        self.addButton = QPushButton('+', self)
        self.addButton.clicked.connect(self.addItem)
        buttonLayout.addWidget(self.addButton)
        layout.addLayout(buttonLayout)

        self.exportButton = QPushButton('Export to Mod Folder', self)
        self.exportButton.clicked.connect(self.exportFiles)
        layout.addWidget(self.exportButton)

        self.deleteButton = QPushButton('Delete', self)
        self.deleteButton.clicked.connect(self.deleteItem)
        layout.addWidget(self.deleteButton)

        self.listWidget = QListWidget(self)
        self.listWidget.itemClicked.connect(self.editItem)
        layout.addWidget(self.listWidget)

        self.setLayout(layout)

        self.setWindowTitle('CR Block Maker')

    def showDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        filePath, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "~/Downloads", "Images (*.png)", options=options)
        if filePath:
            reader = QImageReader(filePath)
            if reader.size().width() == 16 and reader.size().height() == 16:
                pixmap = QPixmap(filePath).scaled(64, 64, Qt.IgnoreAspectRatio, Qt.FastTransformation)
                self.imageLabel.setPixmap(pixmap)
                self.imagePath = filePath
            else:
                QMessageBox.warning(self, "Invalid Image", "Please select a 16x16 image.")

    def addItem(self):
        modName = self.modNameInput.text()
        blockName = self.blockNameInput.text()
        includeSlabs = self.includeSlabsCheckbox.isChecked()
        transparency = self.transparencySlider.value()

        item = {
            "modName": modName,
            "blockName": blockName,
            "includeSlabs": includeSlabs,
            "imagePath": self.imagePath,
            "transparency": transparency
        }

        self.items.append(item)

        listWidgetItem = QListWidgetItem(QIcon(self.imagePath), f"{modName}:{blockName}")
        self.listWidget.addItem(listWidgetItem)

    def applyEdit(self):
        if self.selectedItemIndex is not None:
            modName = self.modNameInput.text()
            blockName = self.blockNameInput.text()
            includeSlabs = self.includeSlabsCheckbox.isChecked()
            transparency = self.transparencySlider.value()

            item = {
                "modName": modName,
                "blockName": blockName,
                "includeSlabs": includeSlabs,
                "imagePath": self.imagePath,
                "transparency": transparency
            }

            self.items[self.selectedItemIndex] = item

            self.listWidget.item(self.selectedItemIndex).setText(f"{modName}:{blockName}")
            self.listWidget.item(self.selectedItemIndex).setIcon(QIcon(self.imagePath))

    def editItem(self, item):
        index = self.listWidget.row(item)
        self.selectedItemIndex = index
        self.modNameInput.setText(self.items[index]["modName"])
        self.blockNameInput.setText(self.items[index]["blockName"])
        self.includeSlabsCheckbox.setChecked(self.items[index]["includeSlabs"])
        self.imagePath = self.items[index]["imagePath"]
        self.transparencySlider.setValue(self.items[index]["transparency"])
        pixmap = QPixmap(self.imagePath).scaled(64, 64, Qt.IgnoreAspectRatio, Qt.FastTransformation)
        self.imageLabel.setPixmap(pixmap)

    def deleteItem(self):
        if self.selectedItemIndex is not None:
            self.listWidget.takeItem(self.selectedItemIndex)
            del self.items[self.selectedItemIndex]
            self.selectedItemIndex = None

    def exportFiles(self):
        try:
            for item in self.items:
                modName = item["modName"]
                blockName = item["blockName"]
                includeSlabs = item["includeSlabs"]
                imagePath = item["imagePath"]
                transparency = item["transparency"] / 100

                blockDir = os.path.join(baseDir, modName, 'blocks')
                modelDir = os.path.join(baseDir, modName, 'models', 'blocks')
                textureDir = os.path.join(baseDir, modName, 'textures', 'blocks')

                os.makedirs(blockDir, exist_ok=True)
                os.makedirs(modelDir, exist_ok=True)
                os.makedirs(textureDir, exist_ok=True)

                blockData = {
                    "stringId": f"{modName}:{blockName}",
                    "blockStates": {
                        modName: {
                            "modelName": f"model_{blockName}",
                            "generateSlabs": includeSlabs
                        }
                    }
                }

                if transparency > 0:
                    blockData["blockStates"][modName]["isTransparent"] = True
                    blockData["blockStates"][modName]["isOpaque"] = False

                modelData = {
                    "parent": "cube",
                    "textures": {
                        "all": {
                            "fileName": f"{blockName}.png"
                        }
                    }
                }

                with open(os.path.join(blockDir, f'block_{blockName}.json'), 'w') as f:
                    json.dump(blockData, f, indent=4)

                with open(os.path.join(modelDir, f'model_{blockName}.json'), 'w') as f:
                    json.dump(modelData, f, indent=4)

                new_img = apply_transparency(imagePath, transparency)
                new_img.save(os.path.join(textureDir, f'{blockName}.png'))

            QMessageBox.information(self, "Export Successful", "Export successful.")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", f"An error occurred: {e}")

    def updateTransparencyLabel(self):
        self.transparencyValueLabel.setText(str(self.transparencySlider.value()))

    def open_new_event_window(self):
        new_event_window = NewEventWindow(self)
        new_event_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimpleApp()
    ex.show()
    sys.exit(app.exec_())

