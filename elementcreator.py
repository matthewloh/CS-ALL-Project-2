from tkinter import *
from static import *
from PIL import Image, ImageTk
from dotenv import load_dotenv


def gridGenerator(root, width, height, color, overriderelief: bool = False, relief: str = FLAT, name=None):
    for x in range(width):
        root.columnconfigure(x, weight=1, uniform="row")
        Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name).grid(
            row=0, column=x, sticky=NSEW)
    for y in range(height):
        root.rowconfigure(y, weight=1, uniform="row")
        Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name).grid(
            row=y, column=0, sticky=NSEW)
    return root

# The grid layout of the application is 96 x 54 to give each base grid a 20x20 pixel size

# Calculating the grid position of the is done through checking the W and H values of the image and then dividing it by 20
# i.e W : 960 H : 1080
#         960/20 = 48 1080/20 = 54
# The grid position is then set to 48,54
# Subject to offsetting the grid position by -1 to account for the 0 index of the grid
# Then, the rowspan and columnspan is set to the height and width of the image divided by 20


