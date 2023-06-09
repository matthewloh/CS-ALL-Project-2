from tkinter import *
from static import *
from PIL import Image, ImageTk
from dotenv import load_dotenv
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification


def gridGenerator(root:Frame, width, height, color, overriderelief: bool = False, relief: str = FLAT, name=None):
    for x in range(width):
        root.columnconfigure(x, weight=1, uniform="row")
        if height > width:
            Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
                row=0, column=x, sticky=NSEW)
    for y in range(height):
        root.rowconfigure(y, weight=1, uniform="row")
        if width >= height:
            Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
                row=y, column=0, sticky=NSEW)
    return root
