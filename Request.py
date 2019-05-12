import requests
from bs4 import BeautifulSoup
import json
import shutil
import os.path
import time
import glob
import os
import re


from flask import Flask, render_template, url_for

app = Flask(__name__)

#Make the request to the wifi card
# This is the full screen, we'll need to handle pagination later.
# Next steps:
# Need to build this as a server to allow for polling of the page for new images
# Also need to check if we already have that image to save downloading 


SITE_BASE='http://ezshare.card/'
DIR='/static/images/'
#os.path.dirname(os.path.realpath(__file__))


@app.route('/')
def serve():
    #while(True):
    last_img=Get_Images()
    #path=DIR.join(last_img)
    app.logger.info("passing image to render %s", last_img)
    full_filename = last_img
    app.logger.info("serving %s", full_filename)
    return render_template("index.html", filename = full_filename)

# Get_Images()
# This method will make a request call to the wifi card and if a new image exists 
# stream the image down.
def Get_Images():
    r = requests.get('http://ezshare.card/photo?fdir=106PANA',allow_redirects=False)
    last=''
    app.logger.info("Checking for new images:%s", r.url )
    html=r.text
    script = BeautifulSoup(html, 'lxml').find_all('title')
    bt_redirect=False
    app.logger.info("Title %s", script)
    if script:   
        for s in script:
            app.logger.info("checking Title:%s, type %s", s, type(s))
            tmp=s.text
            if "Photo Gallery" not in tmp:
                app.logger.info("BT redirect %s" , tmp)
                bt_redirect=True
                break
      
    else:
        bt_redirect=False

    # Was the request successful, continue to start pull the images down.
        app.logger.info("status: %s, bt redirect %s" , r.status_code, bt_redirect)
    if r.status_code == 200 and bt_redirect== False:
        app.logger.info("history: %s\n %s\n %s\n %s" , r.history, r.headers, r.json, r.text)

        tags = BeautifulSoup(html, 'lxml').find_all('a')
        app.logger.info("tags: %s", tags)
        #Loop throught the 'a' tags to identify the download links. 
        for t in tags:
            link=t.attrs['href']
            app.logger.info("link: %s" , link)
            if ".JPG" in link:
                if "download" in link:
                    #Once we have them, can we call them and save them. 
                    url=SITE_BASE + link
                    #split and get the JPG name 
                    path="/static/images/" + url.split("=")[1].split("&")[0]
                    app.logger.info("PATH: %s", path)
                    if not os.path.isfile(path):
                        img=requests.get(url, stream=True)
                        # If we get a successful response, stream the image to the path.
                        if img.status_code == 200:
                            with open(path, 'wb') as f:
                                img.raw.decode_content = True
                                shutil.copyfileobj(img.raw, f)
                                app.logger.info("found new image %s", path)
                                last=path
    else:
        app.logger.info('looking for last image')
        last=str(max(glob.glob('./static/images/*.jpg'),key=os.path.getmtime))
        app.logger.info("no new images, here's the last one %s" , last)
    return last
 
with app.test_request_context():
    print(url_for('serve'))

if __name__=='__main__':
    app.run(debug=True)