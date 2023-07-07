import threading
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma import Prisma

from components.animatedgif import AnimatedGif
from components.animatedstarbtn import AnimatedStarBtn
from PIL import Image, ImageTk, ImageSequence


class TopBar(Frame):
    def __init__(self, parent, controller: ElementCreator, name="topbarframe"):
        super().__init__(parent, width=1, height=1, bg=WHITE, name=name)
        self.controller = controller
        self.parent = parent
        self.name = name
        self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=80,
            root=self.parent, classname=self.name, bg=WHITE,
        )
        self.framereference = self.controller.widgetsDict[f"{self.name}"]
        self.staticImgLabels = [
            (r"Assets\Dashboard\Top Bar.png", 0, 0, "TopBar", self.framereference),
        ]
        self.animatedpanel = self.controller.widgetsDict["animatedpanel"]
        self.buttonImgs = [
            (r"Assets\Dashboard\HamburgerMenuTopBar.png", 0, 0, "HamburgerMenu",
             self.framereference, lambda: self.animatedpanel.animate()),
            (r"Assets\Dashboard\HomeButton.png", 760, 0, "homebutton",
             self.framereference, lambda: [
                 self.controller.widgetsDict["dashboardcanvas"].tk.call(
                     'raise', self.controller.widgetsDict["dashboardcanvas"]._w),
             ]),
            (r"Assets\Dashboard\searchbar.png", 100, 0, "SearchBar",
             self.framereference, lambda: self.searchBarLogic()),
            (r"Assets\Dashboard\RibbonTopBar.png", 1760, 20,
             "RibbonTopBar", self.framereference, lambda: print("hello-4")),
            (r"Assets\Dashboard\BellTopBar.png", 1820, 20, "BellTopBar",
             self.framereference, lambda: print("hello-3")),
        ]
        self.load()
        self.openSearchSettings = [
            (r"Assets\Dashboard\TopbarSearchOpen.png",
             0, 0, "SearchBarOpen", self.framereference),
            (r"Assets\Dashboard\ExitSearch.png", 0, 0, "ExitSearchBtn",
             self.framereference, lambda: self.closeSearchBarLogic()),
        ]

    def load(self):
        self.controller.settingsUnpacker(
            listoftuples=self.staticImgLabels, typeoftuple="label"
        )
        self.controller.settingsUnpacker(
            listoftuples=self.buttonImgs, typeoftuple="button"
        )

    def closeSearchBarLogic(self):
        for widgetname, widget in self.parent.children.items():
            if widgetname in ["searchbaropen", "exitsearchbtn", "searchbarresults", "searchbarentrycanvas"]:
                widget.grid_remove()
            if widgetname in ["searchbar"]:
                widget.tk.call('raise', widget._w)
        for widgetname, widget in self.framereference.children.items():
            if widgetname in ["searchbaropen", "exitsearchbtn", "searchbarresults", "searchbarentrycanvas"]:
                widget.grid_remove()
            if widgetname in ["searchbar"]:
                widget.tk.call('raise', widget._w)

    # TODO: redo this from the ground up
    def searchBarLogic(self):
        searchbg = self.openSearchSettings[0]
        exitbtn = self.openSearchSettings[1]

        self.controller.labelCreator(**self.controller.tupleToDict(searchbg))
        self.controller.buttonCreator(**self.controller.tupleToDict(exitbtn))
        self.controller.entryCreator(
            160, 0, 940, 80, self.parent, "SearchBarResults", pady=10)
        try:
            for widgetname, widget in self.parent.children.items():
                if widgetname == "searchbarentrycanvas":
                    widget.destroy()
        except RuntimeError:
            print("no searchbarentrycanvas")
        for widgetname, widget in self.parent.children.items():
            if widgetname == "searchbarresults":
                widget.after(100, lambda: widget.focus_set())
                widget.bind(
                    "<Return>", lambda e: self.searchByQuery(widget.get()))
                widget.bind("<FocusIn>", lambda e: widget.delete(0, END))
                widget.bind("<Tab>", lambda e: self.closeSearchBarLogic())

    def searchByQuery(self, query):
        self.controller.canvasCreator(160, 60, 940, 240, self.parent, classname="SearchBarEntryCanvas",
                                      bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
        ref = self.controller.widgetsDict["searchbarentrycanvas"]
        ref.tk.call('raise', ref._w)
        for widgetname, widget in self.children.items():
            if widgetname == "searchbarentrycanvas":
                # dummy results
                self.controller.labelCreator(
                    r"Assets\Dashboard\SearchResultsBg.png", 0, 0, "SearchResults1", widget, text=f"Search Results 1 for {query}", font=("Avenir Next", 20), wraplength=600
                )
                self.controller.labelCreator(
                    r"Assets\Dashboard\SearchResultsBg.png", 0, 60, "SearchResults2", widget, text=f"Search Results 2 for {query}", font=("Avenir Next", 20), wraplength=600
                )
                # self.controller.labelCreator(
                #     r"Assets\Dashboard\SearchResultsBg.png", 0, 120, "SearchResults3", widget, text=f"Search Results 3 for {query}", font=("Avenir Next", 20), wraplength=1000
                # )
                self.controller.buttonCreator(
                    r"Assets\Dashboard\SearchResultsBg.png", 0, 180, "SearchResults4", root=widget, text=f"Press Tab to Exit", font=("Avenir Next", 20), wraplength=600
                )
