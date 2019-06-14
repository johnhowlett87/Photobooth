# Photobooth version 2
# Pulling together the components into a more coherent program
# 1. Port methods from other scripts
#   a request.py - remove flask server as not required anymore
#   b photoboothClass.py
#   c GUI.py - build into proper methods ?OOP style
# 2. Build central flow control loop

import os
import glob
import time
import datetime
from PIL import ImageTk, Image
import requests
from bs4 import BeautifulSoup
import json
import shutil
import os.path
import re
import operator
import sys
from math import floor, fmod

from PyQt5.QtCore import Qt, QRegExp, QRunnable, QThreadPool, QObject, pyqtSlot, pyqtSignal, QItemSelectionModel, QTimer
from PyQt5.QtGui import QIcon, QColor, QPalette, QIntValidator, QPixmap, QKeySequence
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QGroupBox, QHBoxLayout, QPushButton, QLineEdit, \
    QLabel, QShortcut, QComboBox, QCheckBox, QFileDialog, QTableWidget, QTableView, QTabWidget, \
    QTableWidgetItem, QStyleFactory, QListWidgetItem, QScrollArea


# This is the class for images. We'll to storing these in a photobooth object.
# each image object will have methods to call the full path, current view count and image name (for the dict key)
# We'll also need to increment the view count.
class image:
    'Image class'

    def __init__(self, name, path, view_count=0):
        self.name = name
        self.path = path
        self.view_count = view_count

    def getName(self):
        return self.name

    def getPath(self):
        return self.path

    def getViewCount(self):
        return self.view_count

    def incrementViewCount(self):
        self.view_count = self.view_count + 1


# Nice GUI from Eddie
class App(QWidget):

    def __init__(self):
        super().__init__()
        screen = app.primaryScreen()
        rect = screen.availableGeometry()

        self.width = rect.width()
        self.height = rect.height()
        self.showFullScreen()

        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout()
        self.window = QLabel()
        self.window.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.window)
        self.setLayout(self.layout)

        self.qTimer = QTimer()
        self.qTimer.setInterval(3000)

        self.p = photobooth()

        self.counter = 0
        #self.images = ["C:\\Users\\ebennett2\\PycharmProjects\\Analysis\\venv\\pgat\\ghd_icon.jpg",
        #          "C:\\Users\\ebennett2\\PycharmProjects\\Analysis\\venv\\pgat\\transco_icon.jpg"]
        self.images = ['./static/images\P1060868.JPG', './static/images\P1060869.JPG','./static/images\P1060870.JPG', './static/images\P1060871.JPG']
        self.qTimer.timeout.connect(lambda: self.update_image())
        self.qTimer.start()

    def select_image(self):
        pass

    def get_new_images(self):
        self.p.Collect_Existing_Images()

    def update_image(self):
        # self.p.PrintListPhotos()
        image = int(fmod(self.counter, 2))
        pixmap = QPixmap(self.images[image])
        self.window.setPixmap(pixmap.scaledToHeight(self.height))
        self.counter = self.counter + 1


class photobooth:
    'Photobooth class'

    def __init__(self):
        self.catalog = list()

    def addToCatalog(self, image):
        self.catalog.append(image)

    # There will be some existing images which we'll need to load in first.
    # This will also allow the restart of the application without losing images.
    def Collect_Existing_Images(self):
        for img in glob.glob('./static/images/*.jpg'):

            if img not in self.catalog.keys():
                self.addToCatalog(image(img.split('\\')[1], img, ))
            else:
                print("Got it mate", img)
        return True

    def PrintListPhotos(self):
        print("NAME\tPATH\tVIEWCOUNT\n")
        for img in self.catalog.keys():
            print(self.catalog[img].getName(), "\t", self.catalog[img].getPath(), "\t",
                  self.catalog[img].getViewCount())
        return True

    def SortCatalog(self):
        return min(sorted(self.catalog, key=operator.attrgetter('view_count')))

    # GetNewImages()
    # This method will make a request call to the wifi card and if a new image exists
    # stream the image down.
    # CHANGES NEEDED TO WORK IN NEW ENVIRONMENT AND TO USE NEW DATA STRUCTURES
    def GetNewImages(self, folder, save_path):
        r = requests.get('http://ezshare.card/photo?fdir=' + folder, allow_redirects=False)
        last = ''
        script = BeautifulSoup(r.text, 'lxml').find_all('title')
        bt_redirect = False
        if script:
            for s in script:
                app.logger.info("checking Title:%s, type %s", s, type(s))
                tmp = s.text
                if "Photo Gallery" not in tmp:
                    app.logger.info("BT redirect %s", tmp)
                    bt_redirect = True
                    break

        else:
            bt_redirect = False
            # Was the request successful, continue to start pull the images down.
            app.logger.info("status: %s, bt redirect %s", r.status_code, bt_redirect)
        if r.status_code == 200 and bt_redirect == False:
            app.logger.info("history: %s\n %s\n %s\n %s", r.history, r.headers, r.json, r.text)

            tags = BeautifulSoup(html, 'lxml').find_all('a')
            app.logger.info("tags: %s", tags)
            # Loop throught the 'a' tags to identify the download links.
            for t in tags:
                link = t.attrs['href']
                app.logger.info("link: %s", link)
                if ".JPG" in link:
                    if "download" in link:
                        # Once we have them, can we call them and save them.
                        url = SITE_BASE + link
                        # split and get the JPG name
                        path = save_path + url.split("=")[1].split("&")[0]
                        app.logger.info("PATH: %s", path)
                        if not os.path.isfile(path):
                            img = requests.get(url, stream=True)
                            # If we get a successful response, stream the image to the path.
                            if img.status_code == 200:
                                with open(path, 'wb') as f:
                                    img.raw.decode_content = True
                                    shutil.copyfileobj(img.raw, f)
                                    app.logger.info("found new image %s", path)
                                    last = path
        else:
            app.logger.info('looking for last image')
            last = str(max(glob.glob(save_path + '*.jpg'), key=os.path.getmtime))
            app.logger.info("no new images, here's the last one %s", last)
        return last


if __name__ == "__main__":
    app = QApplication(sys.argv)

    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.Base, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.AlternateBase, QColor(0, 0, 0))
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(dark_palette)

    ex = App()
    ex.show()
    sys.exit(app.exec_())