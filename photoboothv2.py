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
import tkinter as tk
from PIL import ImageTk, Image

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
        low_val=1
        lowest=''
        for k in self.catalog.keys():
            vc= self.catalog[k].getViewCount()
            if vc >= low_val:
                pass
            else:
                lowest=k
                low_val= vc
        return self.catalog[lowest]

win = tk.Tk()
win.geometry('800x500')  # set window size
win.resizable(0, 0)  # fix window
panel = tk.Label(win)
panel.pack()

def next_img():
    try:
        img =  p.FindNextPhoto() # get the next image
        img.incrementViewCount()
        path=img.path
    except StopIteration:
        return  # if there are no more images, do nothing

    # load the image and display it
    im=Image.open(path)
    sm_im=im.resize((400, 400) , Image.ANTIALIAS)
    img = ImageTk.PhotoImage(sm_im)
    print("Displaying " , path)
    panel.img = img  # keep a reference so it's not garbage collected
    panel['image'] = img
    win.after(1000,next_img)



p=photobooth()
p.Collect_Existing_Images()
p.PrintListPhotos()
next_img()

win.mainloop()

