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
from elementcreator import gridGenerator
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
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Search Page",
                          font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96,
                       rowspan=5, sticky="nsew")
        self.staticImgs = [
            (r"Assets\SearchView\background.png", 0, 0, "searchpagebg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")
