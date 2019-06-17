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


SITE_BASE='http://ezshare.card/'
DIR='./static/images/'
CAM='106PANA'
INTERVAL=500

# This is the class for images. We'll to storing these in a photobooth object.
# each image object will have methods to call the full path, current view count and image name (for the dict key)
# We'll also need to increment the view count.
class image:
    'Image class'

    def __init__(self, name, path, view_count=0):
        self.name = name
        self.path = path
        self.view_count = view_count

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
        self.qTimer.setInterval(INTERVAL)

        self.p = photobooth()
        self.p.Collect_Existing_Images()
        
        #self.p.GetNewImages()

        #self.counter = 0
        #self.images = ["C:\\Users\\ebennett2\\PycharmProjects\\Analysis\\venv\\pgat\\ghd_icon.jpg",
        #          "C:\\Users\\ebennett2\\PycharmProjects\\Analysis\\venv\\pgat\\transco_icon.jpg"]
        #self.images = ['./static/images\P1060868.JPG', './static/images\P1060869.JPG','./static/images\P1060870.JPG', './static/images\P1060871.JPG']
        self.qTimer.timeout.connect(lambda: self.update_image())
        self.qTimer.start()

    def select_image(self):
        pass

    def get_new_images(self):
        self.p.Collect_Existing_Images()

    def update_image(self):
        # self.p.PrintListPhotos()
        #image = int(fmod(self.counter, 2))
        self.p.GetNewImages(CAM, DIR)
        self.p.Collect_Existing_Images()
        # Let's sort the images by view count to see the next one to display. 
        # Potentially need a weighting to stop the same image appearing for too many consectutive runs. 
        # A comparison with the sorted 1 element will tell me how far away it is. 
        self.p.SortCatalog()
        image = self.p.catalog[0]
        print("Lowest after sort:" , self.p.catalog[0].name , " " , self.p.catalog[0].view_count)
        print("Second Lowest after sort:" , self.p.catalog[1].name , " " , self.p.catalog[1].view_count)
        lowest_vc=self.p.catalog[0].view_count
        second_lowest_vc=self.p.catalog[1].view_count
        if (( second_lowest_vc - lowest_vc) >= 3):
            #This operates as a bit of a rubberband to avoid new images staying on screen. 
            # suggest we use a recent images list to repick if the same images are appearing.
            self.p.catalog[0].view_count=self.p.catalog[1].view_count - 2
        
        self.p.catalog[0].incrementViewCount()
        pixmap = QPixmap(image.path)
        self.window.setPixmap(pixmap.scaledToHeight(self.height))
        #self.counter = self.counter + 1


class photobooth:
    'Photobooth class'

    def __init__(self):
        self.catalog = list()

    def addToCatalog(self, image):
        self.catalog.append(image)

    # There will be some existing images which we'll need to load in first.
    # This will also allow the restart of the application without losing images.
    def Collect_Existing_Images(self):
        for img in glob.glob(DIR +'*.jpg'):

            if(any(x.path == img for x in self.catalog )):
                pass
                #print("Got it mate", img)
            else:
                self.addToCatalog(image(img.split('\\')[1], img, ))
        return True

    def PrintListPhotos(self):
        print("NAME\tPATH\tVIEWCOUNT\n")
        for img in self.catalog:
            print(self.catalog[img].name, "\t", self.catalog[img].path, "\t",
                  self.catalog[img].view_count)
        return True

    def SortCatalog(self):
        #return min(sorted(self.catalog, key=operator.attrgetter('view_count')))
        self.catalog.sort(key=lambda x: x.view_count)

    # GetNewImages()
    # This method will make a request call to the wifi card and if a new image exists
    # stream the image down.
    def GetNewImages(self, folder, save_path):
        try:
            r = requests.get('http://ezshare.card/photo?fdir=' + folder, allow_redirects=False)

            if r.status_code == 200 :
                #print("history: %s\n %s\n %s\n %s", r.history, r.headers, r.json, r.text)

                tags = BeautifulSoup(r.text, 'lxml').find_all('a')
                # Loop throught the 'a' tags to identify the download links.
                for t in tags:
                    link = t.attrs['href']
                    #print("link:", link)
                    if ".JPG" in link:
                        if "download" in link:
                            # Once we have them, can we call them and save them.
                            url = SITE_BASE + link
                            # split and get the JPG name
                            path = save_path + url.split("=")[1].split("&")[0]
                            #print("PATH:", path)
                            if not os.path.isfile(path):
                                img = requests.get(url, stream=True)
                                # If we get a successful response, stream the image to the path.
                                if img.status_code == 200:
                                    with open(path, 'wb') as f:
                                        img.raw.decode_content = True
                                        shutil.copyfileobj(img.raw, f)
                                        print("found new image", path)
                                        #time.sleep(2)
            else:
                pass

        except:
            pass


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