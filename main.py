import ctypes
import os
import sys
import threading
from ctypes import windll
from time import sleep
from tkinter import *
from tkinter import messagebox

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from prisma import Prisma

import elementcreator
from elementcreator import gridGenerator

load_dotenv()

from static import *
from PIL import Image, ImageTk

# connection = mysql.connector.connect(
#     host=os.getenv("DB_HOST"),
#     database=os.getenv("DB_DATABASE"),
#     user=os.getenv("DB_USERNAME"),
#     password=os.getenv("DB_PASSWORD"),
#     ssl_ca=os.getenv("SSL_CERT")
# )
# try:
#     if connection.is_connected():
#         c = connection.cursor()
#     with connection:
#         c.execute("select @@version ")
#         version = c.fetchone()
#         if version:
#             print('Running version: ', version)
#         else:
#             print('Not connected.')

#         c.execute("""
#                 SHOW TABLES
#                 """)
#         results = c.fetchall()
#         print(results)
#     # connection.close()
# except Error as e:
#     print("Error while connecting to MySQL", e)
# ~~~~~ The Ability to Make a Colorkey in a Canvas / Widget Transparent Using Windows Only ~~~~~ #
# https://stackoverflow.com/questions/53021603/how-to-make-a-tkinter-canvas-background-transparent
import win32api
import win32con
import win32gui

# https://stackoverflow.com/a/68621773
# This bit of code allows us to remove the window bar present in tkinter
# More information on the ctypes library can be found here:
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
# https://learn.microsoft.com/en-us/windows/win32/winmsg/window-styles

GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW

def get_handle(root) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)

user32 = windll.user32

class Window(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        windll.shcore.SetProcessDpiAwareness(1)
        quarterofscreenwidth = int(int(user32.GetSystemMetrics(0) / 2) / 4)
        quarterofscreenheight = int(int(user32.GetSystemMetrics(1) / 2) / 4)
        elementcreator.gridGenerator(self, 1, 1, NICEPURPLE)
        if self.winfo_screenwidth() <= 1920 and self.winfo_screenheight() <= 1080:
            self.geometry(f"1920x1080+0+0")
        elif self.winfo_screenwidth() > 1920 and self.winfo_screenheight() > 1080:
            self.geometry(f"1920x1080+{quarterofscreenwidth}+{quarterofscreenheight}")
        self.title("INTI.ai Learning Client")
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self.destroy())
        self.widgetsDict = {} 
        self.imageDict = {}
        self.parentFrame = Canvas(self, bg=LIGHTYELLOW, width=1, height=1, name="parentFrame")
        self.parentFrame.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=NSEW)

        elementcreator.gridGenerator(self.parentFrame, 96, 54, WHITE)

        self.postSelectFrame = Frame(self.parentFrame, bg=LIGHTYELLOW, width=1, height=1, name="postSelectFrame")
        self.postSelectFrame.grid(row=0, column=0, rowspan=54, columnspan=96, sticky=NSEW)
        elementcreator.gridGenerator(self.postSelectFrame, 96, 54, WHITE) 
        self.postSelectFrame.grid_remove()
        self.postSelectFrame.grid_propagate(False)
        self.labelSettingsParentFrame = [
            (r"Assets\LandingPage\BackgroundImage.png", 0, 0, "Background Image",self.parentFrame),
            (r"Assets\LandingPage\Landing Page Title.png", 0, 0, "Title Label", self.parentFrame)
        ]
        self.settingsUnpacker(self.labelSettingsParentFrame, "label")


        self.bgimageplaceholder = ImageTk.PhotoImage(
            Image.open(r"Assets\Login Page with Captcha\LoginPageTeachers.png")
        )
        self.imageSettingsForPostSelectFrame = [ 
        (self.bgimageplaceholder, 0, 0, "postselectframebg"),]
        self.bgimage_label = Label(
            self.postSelectFrame,
            image=self.bgimageplaceholder,
            width=1,
            height=1,
            name="postselectframebg",
        )
        self.bgimage_label.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
        self.bgimage_label.grid_remove()
        self.loadedImg1 = ImageTk.PhotoImage(
            Image.open(r"Assets\Login Page with Captcha\LoginPageStudents.png")
        )
        self.loadedImg2 = ImageTk.PhotoImage(
            Image.open(r"Assets\Login Page with Captcha\LoginPageTeachers.png")
        )

        def makeBgImageGrid(student=False, teacher=False):
            if student:
                self.bgimage_label.configure(image=self.loadedImg1)
            elif teacher:
                self.bgimage_label.configure(image=self.loadedImg2)
            self.bgimage_label.grid(), self.postSelectFrame.grid(), self.postSelectFrame.tkraise()
        buttonSettingsForParentFrame = [
            # (imagepath, xpos, ypos, classname, buttonFunction, root),
            (r"Assets\LandingPage\Student Button.png", 1080, 320, "Student Button", 
            self.parentFrame, lambda: makeBgImageGrid(student=True)),
            (r"Assets\LandingPage\Teacher Button.png", 240, 320, "Teacher Button",
            self.parentFrame, lambda: makeBgImageGrid(teacher=True)) 
        ]
        self.settingsUnpacker(buttonSettingsForParentFrame, "button")
        self.btnSettingsPostSelectFrame = [
        (r"Assets\Login Page with Captcha\BackButtonComponent.png", 0, 40, "Back Button", 
        self.postSelectFrame,
        lambda: self.postSelectFrame.grid_remove()),
        (r"Assets\Login Page with Captcha\Skip Button.png", 1680, 940, "Skip Button", 
        self.postSelectFrame,
        lambda: [self.show_frame(Dashboard), self.show_canvas(DashboardCanvas), self.get_page(Dashboard).loadSpecificAssets("student")]), 
        (r"Assets\Login Page with Captcha\CaptchaButton.png", 1260, 520, "Captcha Button",
        self.postSelectFrame,
        lambda: [self.show_frame(Dashboard), self.show_canvas(DashboardCanvas), self.get_page(Dashboard).loadSpecificAssets("student")]),
        ]
        self.settingsUnpacker(self.btnSettingsPostSelectFrame, "button")
        
        def parseObjectsFromFrame(frame: Frame):
            for widgetname, widget in self.widgetsDict.items():
                if (not widgetname.startswith("!la")):
                    print(widget.winfo_parent(), widget.winfo_class(), widget.winfo_name())
                    
        self.opensDevWindow(parseObjectsFromFrame, self.widgetRef)
        
        self.frames = {}
        self.canvasInDashboard = {}
        for F in (
            Dashboard,
            # RegistrationPage, LoginPage, StudentPage, TeacherPage, ChatBot, HelpPage
        ):
            frame = F(parent=self.parentFrame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
            frame.grid_propagate(False)
            frame.controller.canvasCreator(0, 80, 1920, 920, root=frame, classname="maincanvas", bgcolor=WHITE, isTransparent=True, transparentcolor=LIGHTYELLOW)
            self.updateWidgetsDict(frame)
            frame.tk.call("raise", frame._w)
            frame.grid_remove()
        for FRAME in (DashboardCanvas, SearchPage, Chatbot, LearningHub, CourseView, DiscussionsView, FavoritesView, AppointmentsView):
            canvas = FRAME(parent=self.widgetsDict["maincanvas"], controller=self)
            self.canvasInDashboard[FRAME] = canvas
            self.updateWidgetsDict(canvas)
            canvas.grid(row=0, column=0, columnspan=96, rowspan=46, sticky=NSEW)
            canvas.grid_propagate(False)
            canvas.grid_remove()

            

        self.show_canvas(DashboardCanvas)
    def widgetRef(self, classname: str):
        classname.lower().replace(" ", "")
        return self.widgetsDict[classname]           
    def createImageReference(self, imagepath:str, classname:str):
        image = ImageTk.PhotoImage(Image.open(imagepath))
        self.imageDict[classname] = image

    def updateWidgetsDict(self, root: Frame):
        for widgetname, widget in self.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.parentFrame.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.postSelectFrame.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in root.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        try:
            for widgetname, widget in self.get_page(Dashboard).children.items():
                if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass
        try: 
            for widgetname, widget in self.widgetsDict["maincanvas"].children.items():
                if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass
        # for widgetname, widget in self.developerkittoplevel.children.items():
        #     if isinstance(widget, (Label, Button, Frame, Canvas, Entry)) and not widgetname.startswith("!la"):
        #         self.widgetsDict[widgetname] = widget

    def opensDevWindow(self, parseObjectsFromFrame, widgetRef):
        self.developerkittoplevel = Toplevel(
            self,
            bg=LIGHTYELLOW,
            name="devkit"
        )
        self.developerkittoplevel.title("Developer Kit")
        self.developerkittoplevel.bind("<Escape>", lambda e: self.destroy())
        elementcreator.gridGenerator(self.developerkittoplevel, 40, 40, ORANGE)
        self.developerkittoplevel.geometry(f"800x800+0+0")  
        self.developerkittoplevel.resizable(False, False)
        # self.developerkittoplevel.attributes("-topmost", True)
        self.settingsUnpacker([(r"Assets\DeveloperKit\BG.png", 0, 0, "DevKitBG", self.developerkittoplevel)], "label")
        widgetssettingsfordevkit = [
        (r"Assets\DeveloperKit\GetAllWidgets.png", 40, 40, "GetAllWidgetsBtn", self.developerkittoplevel,
        lambda: print(self.widgetsDict)),
        (r"Assets\DeveloperKit\GetSpecificWidget.png", 40, 240, "GetWidgetFromFrame", self.developerkittoplevel,
        lambda: widgetRef(widgetRef("devkitentryorange").get()).grid_remove()),
        (r"Assets\DeveloperKit\CollectAllWidgets.png", 520, 0, "XD Button", self.developerkittoplevel, 
        lambda: parseObjectsFromFrame(self.parentFrame)),
        (r"Assets\DeveloperKit\xd1.png", 680, 0, "XD1 Button", self.developerkittoplevel, 
        lambda: widgetRef("learninghubchip").grid_remove()),
        # (r"Assets\DeveloperKit\CollectAllWidgets.png", 520, 160, "XD3 Button", self.developerkittoplevel, 
        # lambda: parseObjectsFromFrame(self.get_page(Dashboard))),
        # (r"Assets\DeveloperKit\xd1.png", 680, 160, "XD2 Button", self.developerkittoplevel, 
        # lambda: widgetRef('learninghubchip')),
        # (r"Assets\DeveloperKit\WidgetWorkings.png", 520, 320, "XD4 Button", self.developerkittoplevel, 
        # lambda: [self.destroyLabelFromFrame(self.postSelectFrame)],),
        (r"Assets\DeveloperKit\ToggleZoom.png", 680, 320, "Toggle Zoom Button", self.developerkittoplevel, 
        lambda: [self.deletethewindowbar(self), self.state("zoomed")])
        ]
        self.settingsUnpacker(widgetssettingsfordevkit, "button")
        self.entryCreator(40, 120, 360, 80, root=self.developerkittoplevel, classname="DevKitEntryGreen", bg=LIGHTYELLOW)
        self.entryCreator(40, 320, 360, 80, root=self.developerkittoplevel, classname="DevKitEntryOrange", bg=LIGHTYELLOW)
 
    def settingsUnpacker(self, listoftuples, typeoftuple):
        # print((listoftuples))
        for i in listoftuples:
            if typeoftuple == "button":
                button_params = {
                    "imagepath": i[0],
                    "x": i[1],
                    "y": i[2],
                    "classname": i[3].lower().replace(" ", ""),
                    "root": i[4],
                    "buttonFunction": i[5],
                }
                self.buttonCreator(imagepath=i[0], x=i[1], y=i[2], classname=i[3].lower().replace(" ", ""), root=i[4], buttonFunction=i[5])
            elif typeoftuple == "label":
                label_params = {
                    "imagepath": i[0],
                    "x": i[1],
                    "y": i[2],
                    "classname": i[3].lower().replace(" ", ""),
                    "root": i[4],
                }
                self.labelCreator(**label_params)

    def destroyLabelFromFrame(self, frame:Frame):
        isRemoved = False
        for widgetname, widget in frame.children.items():
            if isinstance(widget, Label):
                if isRemoved:
                    widget.grid()
                    isRemoved = False
                else:
                    widget.grid_remove()
                    isRemoved = True
            else:
                widget.grid()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()
    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
    def get_page(self, classname):
        return self.frames[classname]

    def deletethewindowbar(self, windowInstance):
        hwnd: int = get_handle(windowInstance)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        # self.state("zoomed")

    def showthewindowbar(self):
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style |= WS_CAPTION | WS_THICKFRAME
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("normal")

    def buttonCreator(
        self,
        imagepath,
        x,
        y,
        classname=None,
        buttonFunction=None,
        root=None,
        relief=SUNKEN,
        overrideRelief=FLAT,
        text=None,
        font=("Avenir Next Bold", 16),
        wraplength=None,
    ):
        """
        This function takes in the image path, x and y coordinates and the classname, which is necessary because the garbage collector
        will destroy the dictionary if not referenced to something. Thus, we pass it with an identifier string variable called classname.\n\n
        For example, :\n
        self.buttonCreator(r"Assets\Student Button.png", 240, 320, classname="StudentButton")
        will first return a dictionary with the following format:\n
        {'StudentButton': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 12, 'image': <PIL.ImageTk.PhotoImage object at 0x00000246A6976710>}}
        Then, we pass the classname to the inner dictionary, which gives us a label or button with the image we want.
        """
        
        classname = classname.replace(" ", "").lower()
        self.createImageReference(imagepath, classname)
        image = self.imageDict[classname]
        widthspan = int(image.width()/20)
        # just the vertical length of the image divided by 20 to get rowspan
        heightspan = int(image.height()/20)
        # the W value of the image divided by 20 to get the column position
        columnarg = int(x/20)
        rowarg = int(y/20)
        button_kwargs = {
            "root": root,
            "image": image,
            "command": lambda: buttonFunction()
            if buttonFunction
            else lambda: print(f"This is the {classname} button"),
            "relief": overrideRelief,
            "width": 1,
            "height": 1,
            "cursor": "hand2",
            "state": NORMAL,
            "name": classname.replace(" ", "").lower(),
            "text": text,
        }
        # print(button_kwargs["command"])
        self.updateWidgetsDict(root=button_kwargs["root"])
        Button(
            button_kwargs["root"], image=button_kwargs["image"],
            command=button_kwargs["command"] if buttonFunction else print(f"This is the {classname} button"),  
            relief=button_kwargs["relief"],
            bg=WHITE, width=1, height=1,
            cursor="hand2", state=button_kwargs["state"], 
            name= button_kwargs["name"],
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=WHITE, justify=LEFT,
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
        )

    def labelCreator(
        self, 
        imagepath, 
        x, 
        y, 
        classname=None,
        root=None,
        overrideRelief=FLAT,
        text=None, #(defines image=, text=, font=, compound=, wraplength=, justify=, anchor=,)
        font=("Avenir Next Medium", 16),
        wraplength=None,
        ):
        """
        This function takes in the image path, x and y coordinates and the classname, which is necessary because the garbage collector
        will destroy the image if not referenced to something. Thus, we pass it with an identifier string variable called classname.\n\n
        For example, :\n
        self.buttonCreator(r"Assets\Student Button.png", 240, 320, classname="StudentButton")
        will first return a dictionary with the following format:\n
        {'StudentButton': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 12, 'image': <PIL.ImageTk.PhotoImage object at 0x00000246A6976710>}}
        """

        classname = classname.replace(" ", "").lower()
        self.createImageReference(imagepath, classname)
        image = self.imageDict[classname]
        widthspan = int(image.width()/20)
        # just the vertical length of the image divided by 20 to get rowspan
        heightspan = int(image.height()/20)
        # the W value of the image divided by 20 to get the column position
        columnarg = int(x/20)
        rowarg = int(y/20)
        label_kwargs = {
            "root": root,
            "image": image,
            "relief": overrideRelief,
            "width": 1,
            "height": 1,
            "state": NORMAL,
            "name": classname.replace(" ", "").lower(),
            "text": text,
        }
        self.updateWidgetsDict(root=label_kwargs["root"])
        Label(
            label_kwargs["root"], image=label_kwargs["image"], relief=FLAT, width=1, height=1, 
            cursor="", state=label_kwargs["state"], name=label_kwargs["name"], 
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=WHITE, justify=LEFT,
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW
        )

    def frameCreator(
        self,
        xpos,
        ypos,
        framewidth,
        frameheight,
        root=None,
        classname=None,
        bg=WHITE,
        relief=FLAT,
        imgSettings=None,
        ):
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)

        frame_kwargs = {
            "root": root,
            "bg": bg,
            "relief": relief,
            "name": classname.replace(" ", ""),
        }
        self.updateWidgetsDict(root=frame_kwargs["root"])
        Frame(frame_kwargs["root"], width=1, height=1, bg=frame_kwargs["bg"], relief=frame_kwargs["relief"],
        name=frame_kwargs["name"].lower(),
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
        )
        self.updateWidgetsDict(root=frame_kwargs["root"])
        if imgSettings:
            listofimages = list(enumerate(imgSettings)) 
        # imgBg is a list of tuples containing (imagepath, x, y, name)
        # example = [("Assets\Dashboard\Top Bar.png", 0, 0, "stringwhatever"),] -> 0 ('Assets\\Dashboard\\Top Bar.png', 0, 0, 'stringwhatever')
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                gridGenerator(widget, widthspan, heightspan, WHITE)
                widget.grid_propagate(False)
                if imgSettings:
                    for i, j in listofimages:
                        # print(j[1] / 20, j[2] / 20)
                        self.buttonCreator(
                            j[0],
                            j[1] - xpos,
                            j[2] - ypos,
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4]
                        )

    def entryCreator(
        self, xpos,ypos,width, height, root=None, classname=None, bg=WHITE,relief=FLAT,fg=BLACK, textvariable=None, pady=None,):
        entry_params = {
            "xpos":xpos,
            "ypos":ypos,
            "height":height,
            "width":width,
            "root":root,
            "classname":classname.lower().replace(" ", ""),
            "bg":bg,
            "relief":relief,
            "font": ("Avenir Next", 16),
            "fg":fg
        }
        # print(entry_params)
        classname= classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        self.updateWidgetsDict(root=entry_params["root"])
        Entry(root, bg=bg, relief=SOLID,font=("Avenir Next Medium", 16),fg=fg, width=1,name=entry_params["classname"], textvariable=textvariable).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
            pady=pady,
        )
        self.updateWidgetsDict(root=entry_params["root"])
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                widget.grid_propagate(False)

    def canvasCreator(self, 
        xpos, ypos, width, height, root, classname=None,
        bgcolor=WHITE, imgSettings=None,
        relief=FLAT, 
        isTransparent=False, transparentcolor=TRANSPARENTGREEN,
        ):
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        canvas_params = {
            "xpos":xpos,
            "ypos":ypos,
            "height":height,
            "width":width,
            "root":root,
            "classname":classname.lower().replace(" ", ""),
            "bg":bgcolor,
            "highlightcolor":bgcolor,
            "relief":relief
        }
        if imgSettings:
            listofimages = list(
                enumerate(imgSettings)
            ) 
        self.updateWidgetsDict(root=canvas_params["root"])
        Canvas(root, bg=canvas_params["bg"], highlightcolor=bgcolor, relief=FLAT, width=1, height=1, name=canvas_params["classname"], highlightthickness=0).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                gridGenerator(widget, widthspan, heightspan, bgcolor)
                widget.grid_propagate(False)
                if isTransparent:
                    hwnd = widget.winfo_id() #TRANSPARENTGREEN IS the default colorkey
                    transparentcolor = self.hex_to_rgb(transparentcolor)
                    wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
                    win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,new_exstyle)
                    win32gui.SetLayeredWindowAttributes(hwnd,transparentcolor,255,win32con.LWA_COLORKEY)
                if imgSettings:
                    for i, j in listofimages:
                        self.buttonCreator(
                            j[0],
                            j[1] - xpos,
                            j[2] - ypos,
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4]
                        )

    def hex_to_rgb(self, hexstring):
        # Convert hexstring to integer
        hexint = int(hexstring[1:], 16)
        # Extract Red, Green, and Blue values from integer using bit shifting
        red = hexint >> 16
        green = (hexint >> 8) & 0xFF
        blue = hexint & 0xFF
        colorkey = win32api.RGB(red, green, blue)
        return colorkey
  
class SlidePanel(Frame):
    def __init__(self, parent=None, controller=None, startcolumn=0, startrow=0, endrow=0, endcolumn=0, startcolumnspan=0, endcolumnspan=0, rowspan=0, columnspan=0, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN):
        super().__init__(parent, width=1, height=1, bg=TRANSPARENTGREEN)
        self.controller = controller
        gridGenerator(self, width, height, bg)
        self.grid(row=startrow, column=startcolumn, rowspan=rowspan, columnspan=startcolumnspan, sticky=NSEW)
        self.tk.call("lower", self._w)
        self.grid_propagate(False)
        # self.startposition = startposition
        # self.endposition = endposition
        self.startcolumn = startcolumn
        self.endcolumn = endcolumn
        self.startcolumnspan = startcolumnspan
        self.endcolumnspan = endcolumnspan
        self.distance = endcolumn - startcolumn
        #animation logic
        self.pos = startcolumn
        self.at_start_pos = True
        hwnd = self.winfo_id() #TRANSPARENTGREEN IS the default colorkey
        transparentcolor = self.controller.hex_to_rgb(TRANSPARENTGREEN)
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd,transparentcolor,255,win32con.LWA_COLORKEY)
        self.controller.sidebarimage = ImageTk.PhotoImage(Image.open(r"Assets\Dashboard\sidebar320x940.png"))
        self.sidebarlabel = Label(self, image=self.controller.sidebarimage, bg=TRANSPARENTGREEN,width=1,height=1, name="sidebar")
        self.sidebarlabel.grid(row=0, column=0, rowspan=rowspan, columnspan=16, sticky=NSEW)
        self.controller.sidebarpfpimage = ImageTk.PhotoImage(Image.open(r"Assets\Dashboard\SidebarPfp200x200.png"))
        self.sidebarpfp = Button(self, image=self.controller.sidebarpfpimage, bg=LIGHTYELLOW, name="sidebarpfp", command=lambda:print("pfp clicked"))
        self.sidebarpfp.place(x=60, y=40, width=200, height=200)
        self.controller.signoutbuttonimg = ImageTk.PhotoImage(Image.open(r"Assets\Dashboard\SignOutSidebar.png"))
        self.signoutbutton = Button(self, image=self.controller.signoutbuttonimg, bg=LIGHTYELLOW, name="signoutbutton", command=lambda:self.controller.widgetsDict["dashboard"].tk.call("lower", self.controller.widgetsDict["dashboard"]._w))
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

class Dashboard(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, width=1, height=1, bg=LIGHTYELLOW, name="dashboard")
        # gridGenerator(parent, 96, 54, LIGHTYELLOW)
        self.controller = controller
        self.parent = parent
        self.framereference = self
        gridGenerator(self, 96, 54, LIGHTYELLOW)
        self.animatedpanel = SlidePanel(self, self.controller ,startcolumn=0, startrow=4, endrow=3, endcolumn=15, rowspan=46, startcolumnspan=1, endcolumnspan=16, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN)
        self.staticImgLabels = [
        # (r"Assets\Dashboard\StudentDashboard.png", 0, 80, "StudentDashboardLabel", self.framereference),
        (r"Assets\Dashboard\Top Bar.png", 0, 0, "TopBar", self.framereference),
        ]
        self.staticImgBtns = [
        (r"Assets\Dashboard\HamburgerMenuTopBar.png", 0, 0, "HamburgerMenu", self.framereference, lambda: self.animatedpanel.animate()),
        (r"Assets\Dashboard\searchbar.png", 100, 0, "SearchBar", self.framereference, lambda : self.searchBarLogic()),
        (r"Assets\Dashboard\RibbonTopBar.png", 1760, 20, "RibbonTopBar", self.framereference, lambda: print("hello-4")),
        (r"Assets\Dashboard\BellTopBar.png", 1820, 20, "BellTopBar", self.framereference, lambda: print("hello-3")),
        (r"Assets\Dashboard\01DashboardChip.png", 20, 1020, "DashboardChip", self.framereference, lambda: self.controller.show_canvas(DashboardCanvas)),
        (r"Assets\Dashboard\02SearchChip.png", 160, 1020, "SearchChip", self.framereference, lambda: [self.controller.show_canvas(SearchPage),]),
        (r"Assets\Dashboard\03ChatbotChip.png", 300, 1020, "ChatbotChip", self.framereference, lambda: self.controller.show_canvas(Chatbot)),
        (r"Assets\Dashboard\04LearningHubChip.png", 440, 1020, "LearningHubChip", self.framereference, lambda: self.controller.show_canvas(LearningHub)),
        (r"Assets\Dashboard\05MyCoursesChip.png", 580, 1020, "MyCoursesChip", self.framereference, lambda: self.controller.show_canvas(CourseView)),
        (r"Assets\Dashboard\06MyDiscussionsChip.png", 720, 1020, "MyDiscussionsChip", self.framereference, lambda: self.controller.show_canvas(DiscussionsView)),
        (r"Assets\Dashboard\07MyFavoritesChip.png", 860, 1020, "MyFavoritesChip", self.framereference, lambda: self.controller.show_canvas(FavoritesView)),
        (r"Assets\Dashboard\08MyAppointmentsChip.png", 1000, 1020, "MyAppointmentsChip", self.framereference, lambda: self.controller.show_canvas(AppointmentsView)),
        # (r"Assets\Dashboard\ChatbotButton.png", 1660, 780, "ChatbotButton", self.framereference, lambda: print("hello-13"))
        ]
        self.controller.canvasCreator(0, 80, 1920, 920, root=self.framereference, classname="maincanvas", bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.loadAllStaticAssets(self.staticImgBtns, self.staticImgLabels)
        self.maincanvasref = self.controller.widgetsDict["maincanvas"]
        self.controller.canvasCreator(0, 0, 1920, 920, root=self.maincanvasref, classname="dashboardcanvas", bgcolor=NICEBLUE, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.openSearchSettings = [
            (r"Assets\Dashboard\TopbarSearchOpen.png", 0, 0, "SearchBarOpen", self.framereference),
            (r"Assets\Dashboard\ExitSearch.png", 0, 0, "ExitSearchBtn", self.framereference, lambda : self.closeSearchBarLogic()),
        ]
    def loadAllStaticAssets(self, button_settings, label_settings):
        self.controller.settingsUnpacker(label_settings, "label")
        self.controller.settingsUnpacker(button_settings, "button")
        # self.controller.canvasCreator(0, 0, 800, 600, root=self.maincanvasref, classname="StudentDashboardCanvas1", bgcolor=WHITE, isTransparent=True, transparentcolor="#FF3F3E",
        #     imgSettings=[
        #         (r"Assets\Dashboard\bigangry.png", 80, 240, "bigangry", lambda: self.grid_remove()),
        #         (r"Assets\Dashboard\transparencytest28040.png", 280, 240, "nametest", lambda: self.grid_remove()),
        #         # (r"Assets\Dashboard\VALORANT.png", 1360, 240, "VALORANTCAT"),
        #     ])
        # self.controller.canvasCreator(0, 0, 660, 600, root=self.maincanvasref, classname="StudentDashboardCanvas2", bgcolor=WHITE, isTransparent=True, transparentcolor="#FFBC5A",
        #     imgSettings=[
        #         (r"Assets\Dashboard\Frame2.png", 860, 220, "Frame2", lambda: [self.grid_remove(), ]),
        #     ])
    def loadSpecificAssets(self, role):
        self.controller.widgetsDict["dashboardcanvas"].tk.call('raise', self.controller.widgetsDict["dashboardcanvas"]._w)
        if role == "student":
            self.controller.labelCreator( r"Assets\Dashboard\StudentDashboard.png", 0, 0, classname="StudentDashboardLabel", root=self.controller.widgetsDict["dashboardcanvas"])
        elif role == "teacher":
            self.controller.labelCreator( r"Assets\Dashboard\TeacherDashboard.png", 0, 80, classname="TeacherDashboardLabel", root=self.controller.widgetsDict["dashboardcanvas"])
        # self.controller.widgetRef("dashboardcanvas").tk.call('raise', self.controller.widgetRef("dashboardcanvas")._w)
    def tupleToDict(self, tup):
        if len(tup) == 5:
            return dict(zip(("imagepath", "x", "y", "classname","root"), tup))
        if len(tup) == 6:
            return dict(zip(("imagepath", "x", "y", "classname","root", "buttonFunction"), tup))
    def closeSearchBarLogic(self):
        for widgetname, widget in self.children.items():
            if widgetname in ["searchbaropen", "exitsearchbtn", "searchbarresults", "searchbarentrycanvas"]:
                widget.grid_remove()
            if widgetname in ["searchbar"]:
                widget.tk.call('raise', widget._w)

    def searchBarLogic(self):
        searchbg = self.openSearchSettings[0]
        exitbtn = self.openSearchSettings[1]

        self.controller.labelCreator(**self.tupleToDict(searchbg))
        self.controller.buttonCreator(**self.tupleToDict(exitbtn))
        self.controller.entryCreator(160, 0, 940, 80, self, "SearchBarResults", pady=10)
        try:
            for widgetname, widget in self.children.items():
                if widgetname == "searchbarentrycanvas":
                    widget.destroy()
        except RuntimeError:
            pass
        for widgetname, widget in self.children.items():
            if widgetname == "searchbarresults":
                widget.after(100, lambda: widget.focus_set())
                widget.bind("<Return>", lambda e: self.searchByQuery(widget.get()))
                widget.bind("<FocusIn>", lambda e: widget.delete(0, END))
                widget.bind("<Tab>", lambda e: self.closeSearchBarLogic())

    def searchByQuery(self, query):
        print(query)
        self.controller.canvasCreator(160, 60, 940, 240, self, classname="SearchBarEntryCanvas", bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
        for widgetname, widget in self.children.items():
            if widgetname == "searchbarentrycanvas":
                #dummy results
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
class DashboardCanvas(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="dashboardcanvas")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
                

class SearchPage(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="searchpage")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Search Page", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")


class Chatbot(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="chatbot")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Chatbot", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")



class LearningHub(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="learninghub")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Learning Hub", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\LearningHub\LearningHubBG.png", 0, 0, "LearningHubBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")



class CourseView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="courseview")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="CourseView", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")




class DiscussionsView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="discussionsview")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Discussions", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\DiscussionsView\DiscussionsViewBG.png", 0, 0, "DiscussionsBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")



class FavoritesView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="favoritesview")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Favorites", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")



class AppointmentsView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="appointmentsview")
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Appointments", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")
        self.staticImgLabels = [
            (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\AppointmentsView\BGForAppointments1920x780+0+200.png", 0, 120, "AppointmentsBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")



def runGui():
    window = Window()
    window.mainloop()

if __name__ == "__main__":
    runGui()
