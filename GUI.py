import tkinter as tk
from PIL import ImageTk, Image

win = tk.Tk()
win.geometry('800x500')  # set window size
win.resizable(0, 0)  # fix window

panel = tk.Label(win)
panel.pack()

images = ['./static/images\P1060868.JPG', './static/images\P1060869.JPG','./static/images\P1060870.JPG', './static/images\P1060871.JPG']
images = iter(images)  # make an iterator

def next_img():
    try:
        img = next(images)  # get the next image from the iterator
    except StopIteration:
        return  # if there are no more images, do nothing

    # load the image and display it
    im=Image.open(img)
    sm_im=im.resize((200, 200) , Image.ANTIALIAS)
    img = ImageTk.PhotoImage(sm_im)
    
    panel.img = img  # keep a reference so it's not garbage collected
    panel['image'] = img
    win.after(1000,next_img)

# btn = tk.Button(text='Next image', command=next_img)
# btn.pack()

# show the first image
next_img()

win.mainloop()

#Notes for John- this GUI works for the selected images on a 1 sec wait. 
# Next I need to integrate this code with the method's I've developed. #
# Once I've got a cobbled together method, I should organise things and potentially make it OO. 
# Need to dust off the methods for the camera and build functions/methods for them
