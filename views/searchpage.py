import threading
from tkinter import *
from tkinter import filedialog
import uuid
import boto3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from components.animatedgif import AnimatedGif
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma import Prisma
from win32gui import GetWindowText, GetForegroundWindow

from views.discussionsview import DiscussionsView
from PIL import Image, ImageTk, ImageSequence
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime


class SearchPage(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="searchpage", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, ORANGE)

        self.createFrames()

        # Image
        self.staticImgs = [
            (r"Assets\SearchView\searchframe.png", 0, 0, "searchpagebg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")

        # Entry
        self.keywordEntry = self.controller.ttkEntryCreator(
            xpos=300, ypos=220, width=420, height=60, root=self, classname="keywordentry")

        self.keywordEntry.insert(0, "Enter Keyword Here")

        self.keywordEntry2 = self.controller.ttkEntryCreator(
            xpos=915, ypos=220, width=440, height=60, root=self, classname="keywordentry2")

        self.keywordEntry2.insert(0, "Enter Date Here")

        # Scrolled Frame
        self.scrolledframe = ScrolledFrame(
            master=self, width=1160, height=240, autohide=True, bootstyle="bg-round"
        )
        self.scrolledframe.place(x=140, y=540, width=1200, height=240)
        exampleOfSearchItems = [
            "This is Item 1",
            "This is another Item",
            "This is a third item"]
        h = len(exampleOfSearchItems) * 120
        if h < 240:
            h = 240
        self.scrolledframe.configure(height=h)
        initCoords = (20, 0)
        # Set your imagepath here
        IMAGEPATH = r"Assets\SearchView\Button.png"
        for i in exampleOfSearchItems:
            t = self.controller.textElement(
                imagepath=IMAGEPATH, xpos=initCoords[0], ypos=initCoords[1],
                classname=f"searchitem{i}", root=self.scrolledframe,
                text=i, fg="#000000", font=INTER, size=32,
                isPlaced=True, xoffset=-2, yIndex=-1/2,
                buttonFunction=lambda i=i: print(i)
            )
            initCoords = (initCoords[0], initCoords[1] + 120)

        # Button
        self.staticBtns = [
            (r"Assets\SearchView\Search.png", 660, 321, "searchbtncreation", self,
             lambda: print('test')),
            (r"Assets\SearchView\Click.png", 1540, 740, "loadhelpdeskbtn", self,
             lambda: [self.helpdeskFrame.grid(), self.helpdeskFrame.tkraise()]),
        ]
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def createFrames(self):
        self.helpdeskFrame = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="helpdeskframe",
        )
        self.helpdeskLabels = [
            (r"Assets\SearchView\HelpdeskBg.png", 0,
             0, "helpdeskbg", self.helpdeskFrame),
        ]
        self.controller.settingsUnpacker(self.helpdeskLabels, "label")
        self.helpdeskButtons = [
            (r"Assets\SearchView\helpdeskreturnbtn.png", 140, 780,
             "helpdeskreturnbtn", self.helpdeskFrame,
             lambda: self.helpdeskFrame.grid_remove()),
            (r"Assets\SearchView\helpdesksubmit.png", 1560, 780,
             "helpdesksubmit", self.helpdeskFrame,
             lambda: print("Submit")),
            (r"Assets\SearchView\imagebutton.png", 1200, 359,
             "helpdeskimage", self.helpdeskFrame,
             lambda: print("UploadImage"))
        ]
        self.controller.settingsUnpacker(self.helpdeskButtons, "button")
        self.helpdeskFrame.grid_remove()

        # Entry
        self.nameEntry = self.controller.ttkEntryCreator(
            xpos=340, ypos=260, width=520, height=60, root=self.helpdeskFrame, classname="helpdeskframe")

        self.nameEntry.insert(0, "Enter Name Here")

        self.emailEntry = self.controller.ttkEntryCreator(
            xpos=1080, ypos=260, width=600, height=60, root=self.helpdeskFrame, classname="emailentry")

        self.emailEntry.insert(0, "Enter E-mail Here")

        # Scrolled Text
        self.scrolledtext = ScrolledText(
            master=self.helpdeskFrame, width=630, height=330, autohide=True)
        self.scrolledtext.place(x=222, y=402, width=630, height=330)
        self.textArea = self.scrolledtext.text
        self.textArea.configure(font=(INTERBOLD, 20))
