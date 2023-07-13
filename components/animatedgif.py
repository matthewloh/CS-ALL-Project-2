from itertools import cycle
from pathlib import Path
from tkinter import *
from ttkbootstrap.constants import *
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from PIL import Image, ImageTk, ImageSequence


class AnimatedGif(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None,
                 xpos=0, ypos=0, framewidth=0, frameheight=0,
                 classname=None, imagepath=None, imagexpos=0, imageypos=0,
                 bg=WHITE,
                 *args, **kwargs):
        super().__init__(parent, width=1, bg=bg, autostyle=False, name=classname)
        self.controller = controller
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        self.configure(bg=bg)
        gridGenerator(self, widthspan, heightspan, bg)
        self.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                  columnspan=widthspan, sticky=NSEW)
        # open the GIF and create a cycle iterator
        file_path = Path(__file__).parent.parent / imagepath
        with Image.open(file_path) as im:
            # create a sequence
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.image_cycle = cycle(images)
            # length of each frame
            self.framerate = im.info["duration"]
        # getting the width and height of the image
        imagetogetdetails = ImageTk.PhotoImage(Image.open(file_path))
        self.imgwidth = imagetogetdetails.width()
        self.imgheight = imagetogetdetails.height()
        imgrow = int(imageypos / 20)
        imgcolumn = int(imagexpos / 20)
        imgrowspan = int(self.imgheight / 20)
        imgcolumnspan = int(self.imgwidth / 20)
        self.img_container = Label(self, image=next(
            self.image_cycle), width=1, bg="#344557")
        self.img_container.grid(
            column=imgcolumn, row=imgrow, columnspan=imgcolumnspan, rowspan=imgrowspan, sticky=NSEW)
        self.after(self.framerate, self.next_frame)
        self.controller.widgetsDict[classname] = self

    def next_frame(self):
        """Update the image for each frame"""
        try:
            self.img_container.configure(image=next(self.image_cycle))
            self.after(self.framerate, self.next_frame)
        except:
            # happens because when switching from student to lecturer, a new animatedgifinstance is created and the old one is destroyed
            print("gif error i will fix one day surely")
