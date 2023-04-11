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


def createDictOfSettings(root, imagepath: str, wval: int, hval: int, classname: str):
    """
    Accepts the root, imagepath, and the W and H values of the image obtainable through Figma\n
    Returns a unique dictionary identified by classname of the widthspan, heightspan, rowarg, columnarg, and image in a dictionary\n\n
    Example output:\n
    {"columnspan": widthspan, "rowspan": heightspan, "row": rowarg, "column": columnarg, "image": image}
    Accepts a classname that is used to create a unique dictionary, so that the program can distinguish keys.
    Returns a dictionary, used in the creation of Labels, Buttons, and Frames.
    """
    image = ImageTk.PhotoImage(Image.open(imagepath))
    # just the horizontal length of the image divided by 20 to get columnspan
    widthspan = int(image.width()/20)
    # just the vertical length of the image divided by 20 to get rowspan
    heightspan = int(image.height()/20)
    # the W value of the image divided by 20 to get the column position
    columnarg = int(wval/20)
    rowarg = int(hval/20)
    # print(wval, hval)
    # print("Column: ", columnarg, "Row: ", rowarg)
    # the classname is used to create a unique dictionary, so that the program can distinguish keys.
    classname = classname
    # print(classname)
    ret_dict = {classname: {'columnspan': widthspan, 'rowspan': heightspan, 'row': rowarg, 'column': columnarg, 'image': image}}
    # Holding object reference with the root
    return ret_dict
