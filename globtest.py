import glob
import os

tmp=max(glob.glob('./*.jpg'),key=os.path.getmtime)
print(tmp)
page="<html><body><img src='" +  tmp + "'></body></html>"
print(page)