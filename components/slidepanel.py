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
from win32gui import GetWindowText, GetForegroundWindow
from nonstandardimports import *


class SlidePanel(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None, startcolumn=0, startrow=0, endrow=0, endcolumn=0, startcolumnspan=0, endcolumnspan=0, rowspan=0, columnspan=0, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN, name=None):
        super().__init__(parent, width=1, height=1, bg=TRANSPARENTGREEN, name=name)
        self.controller = controller
        gridGenerator(self, width, height, bg)
        self.grid(row=startrow, column=startcolumn, rowspan=rowspan,
                  columnspan=startcolumnspan, sticky=NSEW)
        self.tk.call("lower", self._w)
        self.grid_propagate(False)
        self.startcolumn = startcolumn
        self.endcolumn = endcolumn
        self.startcolumnspan = startcolumnspan
        self.endcolumnspan = endcolumnspan
        self.distance = endcolumn - startcolumn
        # animation logic
        self.pos = startcolumn
        self.at_start_pos = True
        hwnd = self.winfo_id()  # TRANSPARENTGREEN IS the default colorkey
        transparentcolor = self.controller.hex_to_rgb(TRANSPARENTGREEN)
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)
        win32gui.SetLayeredWindowAttributes(
            hwnd, transparentcolor, 255, win32con.LWA_COLORKEY)
        imagepaths = [
            (r"Assets\Dashboard\sidebar320x940.png", "sidebarimage"),
            (r"Assets\Dashboard\SidebarPfp200x200.png", "sidebarpfpimage"),
            (r"Assets\Dashboard\SignOutSidebar.png", "signoutbuttonimg"),
        ]
        for i in imagepaths:
            self.controller.createImageReference(i[0], i[1])
        self.sidebarimage = self.controller.imageDict["sidebarimage"]
        self.sidebarpfpimage = self.controller.imageDict["sidebarpfpimage"]
        self.signoutbuttonimg = self.controller.imageDict["signoutbuttonimg"]
        self.sidebarlabel = Label(self, image=self.sidebarimage,
                                  bg=TRANSPARENTGREEN, width=1, height=1, name="sidebar")
        self.sidebarlabel.grid(
            row=0, column=0, rowspan=rowspan, columnspan=16, sticky=NSEW)
        self.sidebarpfp = Button(self, image=self.sidebarpfpimage, bg=LIGHTYELLOW,
                                 name="sidebarpfp", command=lambda: print("pfp clicked"))
        self.sidebarpfp.place(x=60, y=40, width=200, height=200)
        self.signoutbutton = Button(self, image=self.signoutbuttonimg, bg=LIGHTYELLOW, name="signoutbutton",
                                    command=lambda: self.controller.widgetsDict["dashboard"].tk.call("lower", self.controller.widgetsDict["dashboard"]._w))
        self.signoutbutton.place(x=40, y=720, width=240, height=100)

    def animate(self):
        if self.at_start_pos:
            self.animate_forward()
        else:
            self.animate_backward()

    def animate_forward(self):
        self.grid()
        self.tkraise()
        self.sidebarlabel.tk.call('raise', self.sidebarlabel._w)
        self.sidebarpfp.tk.call('raise', self.sidebarpfp._w)
        self.signoutbutton.tk.call('raise', self.signoutbutton._w)
        # self.parseObjectsFromFrame(self)
        if self.startcolumnspan < self.endcolumnspan+1:
            self.grid(columnspan=self.startcolumnspan)
            # self.sidebarlabel.grid(columnspan=self.startcolumnspan)
            self.startcolumnspan += 1
            self.after(6, self.animate_forward)
        else:
            self.at_start_pos = False

    def animate_backward(self):
        if self.startcolumnspan > 1:
            self.grid(columnspan=self.startcolumnspan)
            # self.sidebarlabel.grid(columnspan=self.startcolumnspan)
            self.startcolumnspan -= 1
            self.after(15, self.animate_backward)
        else:
            self.at_start_pos = True
            self.grid_remove()