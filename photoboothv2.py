#Photobooth version 2
# Pulling together the components into a more coherent program
# 1. Port methods from other scripts
#   a request.py - remove flask server as not required anymore
#   b photoboothClass.py
#   c GUI.py - build into proper methods ?OOP style
# 2. Build central flow control loop

#Imports:
import os
import glob
import time
import datetime

# This is the class for images. We'll to storing these in a dict. 
# each object will have methods to call the full path, current view count and image name (for the dict key)
# We'll also need to increment the view count.
class image:
    'Image class'
    
    def __init__(self, name, path, view_count=0):
        self.name = name
        self.path = path
        self.view_count= view_count
    
    def getName(self):
        return self.name

    def getPath(self):
        return self.path

    def getViewCount(self):
        return self.view_count

    def incrementViewCount(self):
        self.view_count = self.view_count + 1
    

class photobooth:
    'Photobooth class'

    def __init__(self):
        self.catalog = dict()
    
    def getCatalog(self):
        return self.catalog
    
    def addToCatalog(self, image):
        self.catalog[image.getName()] = image

    # There will be some existing images which we'll need to load in first. 
    # This will also allow the restart of the application without losing images.
    def Collect_Existing_Images(self):
        for img in glob.glob('./static/images/*.jpg'):
            
            if img not in self.catalog.keys():
                self.addToCatalog(image(img.split('\\')[1], img,))
            else:
                print("Got it mate" , img)
        return True
        
    def PrintListPhotos(self):
        print("NAME\tPATH\tVIEWCOUNT\n")
        for img in self.catalog.keys():
            print(self.catalog[img].getName(), "\t" , self.catalog[img].getPath(), "\t" , self.catalog[img].getViewCount() )
        return True

    def FindNextPhoto(self):
        low_val=999999
        lowest=''
        for k in self.catalog.keys():
            vc= self.catalog[k].getViewCount()
            if vc >= low_val:
                pass
            else:
                lowest=k
                low_val= vc
            return lowest


if __name__=='__main__':
    p=photobooth()
    p.Collect_Existing_Images()
    p.PrintListPhotos()
    print(p.FindNextPhoto())

