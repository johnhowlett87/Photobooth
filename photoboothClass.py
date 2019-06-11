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
    
#import photoboothClass
import os
import glob
import time
import datetime

# There will be some existing images which we'll need to load in first. 
# This will also allow the restart of the application without losing images.
def Collect_Existing_Images(photolist):
    for img in glob.glob('./static/images/*.jpg'):
        #print(img)
        if img not in photolist.keys():
            photolist[img]=(image(img.split('\\')[1], img,))
        else:
            print("Got it mate" , img)
    return True
        
def PrintListPhotos(photolist):
    print("NAME\tPATH\tVIEWCOUNT\n")
    for img in photolist.keys():
        print(photolist[img].getName(), "\t" , photolist[img].getPath(), "\t" , photolist[img].getViewCount() )
    
    return True

def FindNextPhoto(photolist):
    low_val=999999
    lowest=''
    for k in photolist.keys():
        vc= photolist[k].getViewCount()
        if vc >= low_val:
            pass
        else:
            lowest=k
            low_val= vc
        return lowest

if __name__=='__main__':
    photolist= dict()
    Collect_Existing_Images(photolist)
    PrintListPhotos(photolist)