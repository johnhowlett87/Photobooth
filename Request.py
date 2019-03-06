import requests
from bs4 import BeautifulSoup
import json
import shutil

#Make the request to the wifi card
# This is the full screen, we'll need to handle pagination later.

SITE_BASE='http://ezshare.card/'
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
                print(url)
                #split and get the JPG name 
                path=url.split("=")[1].split("&")[0]
                img=requests.get(url, stream=True)
                # If we get a successful response, stream the image to the path.
                if img.status_code == 200:
                    with open(path, 'wb') as f:
                        img.raw.decode_content = True
                        shutil.copyfileobj(img.raw, f) 
 
#print(table_data)

#print(json.dumps(dict(table_data)))