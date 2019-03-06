import requests
from bs4 import BeautifulSoup
import json
import shutil
import os.path
import time

#Make the request to the wifi card
# This is the full screen, we'll need to handle pagination later.
# Next steps:
# Need to build this as a server to allow for polling of the page for new images
# Also need to check if we already have that image to save downloading 


SITE_BASE='http://ezshare.card/'

def Get_Images():
    r = requests.get('http://ezshare.card/photo?fdir=106PANA')

    # Was the request successful, continue to start pull the images down.
    if r.status_code == 200:

        html=r.text
        tags = BeautifulSoup(html, 'lxml').find_all('a')

        #Loop throught the 'a' tags to identify the download links. 
        for t in tags:
            link=t.attrs['href']
            if ".JPG" in link:
                if "download" in link:
                    #Once we have them, can we call them and save them. 
                    url=SITE_BASE + link
                    #split and get the JPG name 
                    path=url.split("=")[1].split("&")[0]
                    if not os.path.isfile(path):
                        img=requests.get(url, stream=True)
                        # If we get a successful response, stream the image to the path.
                        if img.status_code == 200:
                            with open(path, 'wb') as f:
                                img.raw.decode_content = True
                                shutil.copyfileobj(img.raw, f)
                                print(path) 
 
def main():
    while(True):
        Get_Images()
        time.sleep(5)


if __name__ == "__main__":
   main()