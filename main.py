import ctypes
import os
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

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    ssl_ca=os.getenv("SSL_CERT")
)
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
        self.button_dicts = {}
        self.labels_dicts = {}
        self.widgetslist = []

        self.parentFrame = Canvas(self, bg=LIGHTYELLOW, width=1, height=1, name="parentFrame")
        self.parentFrame.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=NSEW)

        elementcreator.gridGenerator(self.parentFrame, 96, 54, WHITE)

        self.labelSettingsParentFrame = [
            (r"Assets\LandingPage\BackgroundImage.png", 0, 0, "Background Image",self.parentFrame),
            (r"Assets\LandingPage\Landing Page Title.png", 0, 0, "Title Label", self.parentFrame)
        ]
        self.settingsUnpacker(self.labelSettingsParentFrame, "label")

        def parseDicts(dictionary):
            """
            Parses a dictionary of buttons and labels and formats them into human readable text
            {'Student Button': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 54, 'image': <PIL.ImageTk.PhotoImage object at 0x00000269EDEE0950>}, 'Teacher Button': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 12, 'image': <PIL.ImageTk.PhotoImage object at 0x00000269EDEE0F90>}, 'Back Button': {'columnspan': 12, 'rowspan': 4, 'row': 2, 'column': 0, 'image': <PIL.ImageTk.PhotoImage object at 0x00000269EDEE1410>}, 'Skip Button': {'columnspan': 12, 'rowspan': 4, 'row': 47, 'column': 84, 'image': <PIL.ImageTk.PhotoImage object at 0x00000269EDEE17D0>}, 'Captcha Button': {'columnspan': 18, 'rowspan': 5, 'row': 26, 'column': 63, 'image': <PIL.ImageTk.PhotoImage object at 0x00000269EDEE18D0>}}
            Breaks up each element in the dictionary example above into
            <Button> -> <Button Name> -> <Button Property> -> <Button Property Value>... continuing in a single line

            """
            for key, value in dictionary.items():
                print(key, value)
                for key2, value2 in value.items():
                    print(key2, value2)

        def parseObjectsFromFrame(frame: Frame):
            for widgetname, widget in frame.children.items():
                if isinstance(widget, Button) or (isinstance(widget, Label)and not widgetname.startswith("!la")):
                    widgethost = str(widget).split(".")[-2]
                    widget = str(widget).split(".")[-1]
                    if isinstance(widget, Label):
                        print(f"Label: {widget} & Label holder: {widgethost}")
                    else:
                        print(f"Button: {widget} & and Button holder: {widgethost}")
        def destroyObjectsFromFrame(frame: Frame):
            for widgetname, widget in self.children.items():
                if not (widgetname.startswith("!la")):
                    # print(frame, widgetname, widget)
                    self.widgetslist.append(widget)
            for widget in self.widgetslist:
                print("asdf", widget)
        def returnObjectsToFrame(frame: Frame):
            widgetlist = []
            for widgetname, widget in frame.children.items():
                if widgetname.startswith("!la"):
                    print(frame, widgetname, widget)
                    widgetlist.append(widget)
            for widgetname, widget in widgetlist:
                print(f"this is widget in{frame}", widgetname, widget)


        self.postSelectFrame = Frame(self.parentFrame, bg=LIGHTYELLOW, width=1, height=1, name="postSelectFrame")
        self.postSelectFrame.grid(row=0, column=0, rowspan=54, columnspan=96, sticky=NSEW)
        elementcreator.gridGenerator(self.postSelectFrame, 96, 54, WHITE) 
        self.postSelectFrame.grid_remove()
        self.postSelectFrame.grid_propagate(False)

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
        self.buttonSettingsForParentFrame = [
            # (imagepath, xpos, ypos, classname, buttonFunction, root),
            (r"Assets\LandingPage\Student Button.png", 1080, 320, "Student Button", 
            self.parentFrame, lambda: makeBgImageGrid(student=True)),
            (r"Assets\LandingPage\Teacher Button.png", 240, 320, "Teacher Button",
            self.parentFrame, lambda: makeBgImageGrid(teacher=True)) 
        ]
        for i in self.buttonSettingsForParentFrame:
            button_params = {
                "imagepath": i[0],
                "x": i[1],
                "y": i[2],
                "classname": i[3],
                "root": i[4],
                "buttonFunction": i[5],
            }
            self.buttonCreator(**button_params )
        self.settingsForPostSelectFrame = [
        (r"Assets\Login Page with Captcha\BackButtonComponent.png", 0, 40, "Back Button", 
        self.postSelectFrame,
        lambda: self.postSelectFrame.grid_remove()),
        (r"Assets\Login Page with Captcha\Skip Button.png", 1680, 940, "Skip Button", 
        self.postSelectFrame,
        lambda: [self.show_frame(Dashboard), self.loadPageAssetsStudents(Dashboard)]), 
        (r"Assets\Login Page with Captcha\CaptchaButton.png", 1260, 520, "Captcha Button", 
        self.postSelectFrame,
        lambda: [self.postSelectFrame.grid_remove()]), 
        ]

        self.opensDevWindow(parseObjectsFromFrame, destroyObjectsFromFrame, returnObjectsToFrame)
        self.settingsUnpacker(self.settingsForPostSelectFrame, "button")
        
        self.frames = {}
        for F in (
            Dashboard,
            # RegistrationPage, LoginPage, StudentPage, TeacherPage, ChatBot, HelpPage
        ):
            frame = F(parent=self.parentFrame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
            frame.grid_propagate(False)
            frame.grid_remove()

    def opensDevWindow(self, parseObjectsFromFrame, destroyObjectsFromFrame, returnObjectsToFrame):
        self.developerkittoplevel = Toplevel(
            self,
            bg=LIGHTYELLOW,
        )
        self.developerkittoplevel.title("Developer Kit")
        self.developerkittoplevel.bind("<Escape>", lambda e: self.destroy())
        elementcreator.gridGenerator(self.developerkittoplevel, 40, 40, ORANGE)
        self.developerkittoplevel.geometry(f"800x800+0+0")  
        self.developerkittoplevel.resizable(False, False)
        self.developerkittoplevel.attributes("-topmost", True)
        self.settingsUnpacker([(r"Assets\DeveloperKit\BG.png", 0, 0, "DevKitBG", self.developerkittoplevel)], "label")
        widgetssettingsfordevkit = [
        (r"Assets\DeveloperKit\XD.png", 520, 0, "XD Button", self.developerkittoplevel, 
        lambda: parseObjectsFromFrame(self.get_page(Dashboard))),
        (r"Assets\DeveloperKit\xd1.png", 680, 0, "XD1 Button", self.developerkittoplevel, 
        lambda: destroyObjectsFromFrame(self.get_page(Dashboard))),
        (r"Assets\DeveloperKit\xd1.png", 680, 160, "XD2 Button", self.developerkittoplevel, 
        lambda: returnObjectsToFrame(self.get_page(Dashboard))),
        (r"Assets\DeveloperKit\XD.png", 520, 160, "XD3 Button", self.developerkittoplevel, 
        lambda: self.destroyLabelsFromFrame(self.parentFrame)),
        (r"Assets\DeveloperKit\WidgetWorkings.png", 520, 320, "XD4 Button", self.developerkittoplevel, 
        lambda: [self.destroyLabelFromFrame(self.postSelectFrame), print("destroyed")],),
        (r"Assets\DeveloperKit\ToggleZoom.png", 680, 320, "Toggle Zoom Button", self.developerkittoplevel, 
        lambda: [self.deletethewindowbar(self), self.state("zoomed")])
        ]
        self.settingsUnpacker(widgetssettingsfordevkit, "button")

    def settingsUnpacker(self, listoftuples, typeoftuple):
        for i in listoftuples:
            if typeoftuple == "button":
                button_params = {
                    "imagepath": i[0],
                    "x": i[1],
                    "y": i[2],
                    "classname": i[3],
                    "root": i[4],
                    "buttonFunction": i[5],
                }
                self.buttonCreator(**button_params)
            elif typeoftuple == "label":
                label_params = {
                    "imagepath": i[0],
                    "x": i[1],
                    "y": i[2],
                    "classname": i[3],
                    "root": i[4],
                }
                self.labelCreator(**label_params)

    def destroyLabelsFromFrame(self, frame:Frame):
        for widgetname, widget in frame.children.items():
            print(widgetname)
            if isinstance(widget, Frame):
                print(widgetname)

    def destroyLabelFromFrame(self, frame:Frame):
        widgetlist = []
        for widgetname, widget in frame.children.items():
            print(widgetname)
            if isinstance(widget, Label):
                widgetlist.append(widget)

        for widget in widgetlist:
            widget.destroy()
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()

    def get_page(self, classname):
        return self.frames[classname]

    def loadPageAssetsStudents(self, page):
        """
        This function loads the assets for the page. Each page has its own assets only loaded during time of use.
        """
        reference = self.get_page(page)
        reference.loadAssetsStudents()

    def loadPageAssetsTeachers(self, page):
        """
        This function loads the assets for the page. Each page has its own assets only loaded during time of use.
        """
        reference = self.get_page(page)
        reference.loadAssetsTeachers()

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
        relief=FLAT,
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

        button_dict = elementcreator.createDictOfSettings(
                self, imagepath, x, y, classname
        )

        self.button_dicts.update(button_dict)
        button_dict = button_dict[classname]

        button_kwargs = {
            "root": root,
            "image": button_dict["image"],
            "command": lambda: buttonFunction()
            if buttonFunction
            else lambda: print(f"This is the {classname} button"),
            "relief": relief if not overrideRelief else FLAT,
            "width": 1,
            "height": 1,
            "cursor": "hand2",
            "state": NORMAL,
            "name": classname.replace(" ", "").lower(),
            "text": text,
        }
        # print(button_kwargs["command"])
        Button(
            button_kwargs["root"], image=button_kwargs["image"],
            command=button_kwargs["command"] if buttonFunction else print(f"This is the {classname} button"),  
            relief=button_kwargs["relief"] if relief else SUNKEN,
            bg=WHITE, width=1, height=1,
            cursor="hand2", state=button_kwargs["state"], 
            name=button_kwargs["name"],
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=WHITE, justify=LEFT,
        ).grid(
            row=button_dict["row"],
            column=button_dict["column"],
            rowspan=button_dict["rowspan"],
            columnspan=button_dict["columnspan"],
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
        will destroy the dictionary if not referenced to something. Thus, we pass it with an identifier string variable called classname.\n\n
        For example, :\n
        self.buttonCreator(r"Assets\Student Button.png", 240, 320, classname="StudentButton")
        will first return a dictionary with the following format:\n
        {'StudentButton': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 12, 'image': <PIL.ImageTk.PhotoImage object at 0x00000246A6976710>}}
        Then, we pass the classname to the inner dictionary, which gives us a label or button with the image we want.
        """
        label_dict = elementcreator.createDictOfSettings(
            self, imagepath, x, y, classname
        )
        self.labels_dicts.update(label_dict)
        label_dict = label_dict[classname]
        label_kwargs = {
            "root": root,
            "image": label_dict["image"],
            "relief":overrideRelief,
            "width": 1,
            "height": 1,
            "state": NORMAL,
            "name": classname.replace(" ", "").lower(),
            "text": text,
        }
        # print(text)
        Label(
            label_kwargs["root"], image=label_kwargs["image"], relief=FLAT, width=1, height=1, 
            cursor="", state=label_kwargs["state"], name=label_kwargs["name"], 
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=WHITE, justify=LEFT,
        ).grid(
            row=label_dict["row"],
            column=label_dict["column"],
            rowspan=label_dict["rowspan"],
            columnspan=label_dict["columnspan"],
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
        Frame(frame_kwargs["root"], width=1, height=1, bg=frame_kwargs["bg"], relief=frame_kwargs["relief"],
        name=frame_kwargs["name"].lower(),
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
        )
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

    def entryCreator(self, xpos,ypos,width, height, root=None, classname=None, bg=WHITE,relief=FLAT,fg=BLACK):
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
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)

        Entry(root, bg=bg, relief=SOLID,font=("Avenir Next Medium", 16),fg=fg, width=1,name=entry_params["classname"]).grid(pady=10, row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
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
  
class Dashboard(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, width=1, height=1, bg=WHITE)
        # gridGenerator(parent, 96, 54, LIGHTYELLOW)
        self.controller = controller
        self.parent = parent
        self.framereference = self
        gridGenerator(self, 96, 54, LIGHTYELLOW)

        self.labelImg_settings = [
        (r"Assets\Dashboard\StudentDashboard.png", 0, 80, "StudentDashboardLabel", self.framereference),
        (r"Assets\Dashboard\Top Bar.png", 0, 0, "TopBar", self.framereference)
        ]
        self.buttonImg_settings = [
        (r"Assets\Dashboard\HamburgerMenuTopBar.png", 0, 0, "HamburgerMenu", self.framereference, lambda: print("hello-1")),
        (r"Assets\Dashboard\searchbar.png", 100, 0, "SearchBar", self.framereference, lambda : self.searchBarLogic()),
        (r"Assets\Dashboard\BellTopBar.png", 1100, 20, "BellTopBar", self.framereference, lambda: print("hello-3")),
        (r"Assets\Dashboard\RibbonTopBar.png", 1160, 20, "RibbonTopBar", self.framereference, lambda: print("hello-4")),
        (r"Assets\Dashboard\01DashboardChip.png", 20, 1020, "DashboardChip", self.framereference, lambda: print("hello-5")),
        (r"Assets\Dashboard\02SearchChip.png", 160, 1020, "SearchChip", self.framereference, lambda: print("hello-6")),
        (r"Assets\Dashboard\03ChatbotChip.png", 300, 1020, "ChatbotChip", self.framereference, lambda: print("hello-7")),
        (r"Assets\Dashboard\04LearningHubChip.png", 440, 1020, "LearningHubChip", self.framereference, lambda: print("hello-8")),
        (r"Assets\Dashboard\05MyCoursesChip.png", 580, 1020, "MyCoursesChip", self.framereference, lambda: print("hello-9")),
        (r"Assets\Dashboard\06MyDiscussionsChip.png", 720, 1020, "MyDiscussionsChip", self.framereference, lambda: print("hello-10")),
        (r"Assets\Dashboard\07MyFavoritesChip.png", 860, 1020, "MyFavoritesChip", self.framereference, lambda: print("hello-11")),
        (r"Assets\Dashboard\08MyAppointmentsChip.png", 1000, 1020, "MyAppointmentsChip", self.framereference, lambda: print("hello-12")),
        (r"Assets\Dashboard\ChatbotButton.png", 1660, 820, "ChatbotButton", self.framereference, lambda: print("hello-13")),
        ]

    #TODO: Cleanup this function call chaining using self.controller.settingsUnpacker 
    #     by fixing the loading from post authentication
    def generateElements(self, button_settings, label_settings):
        self.generateLabels(label_settings)
        self.generateButtons(button_settings)
    def generateButtons(self, button_settings):
        self.controller.settingsUnpacker(button_settings, "button")
    def generateLabels(self, label_settings):
        self.controller.settingsUnpacker(label_settings, "label")
    def loadAllAssets(self, button_settings, label_settings):
        self.generateElements(button_settings, label_settings)
        self.controller.canvasCreator(40, 220, 800, 600, root=self, classname="StudentDashboardCanvas1", bgcolor=WHITE, isTransparent=True,
            imgSettings=[
                (r"Assets\Dashboard\bigangry.png", 80, 260, "bigangry", lambda: self.grid_remove()),
                (r"Assets\Dashboard\transparencytest28040.png", 280, 240, "nametest", lambda: self.grid_remove()),
                # (r"Assets\Dashboard\VALORANT.png", 1360, 240, "VALORANTCAT"),
            ],
        )
    def loadAssetsStudents(self):
        self.controller.labelCreator(
            r"Assets\Dashboard\StudentDashboard.png",
            0,
            80,
            classname="StudentDashboardLabel",
            root=self,
        )
        self.loadAllAssets(self.buttonImg_settings, self.labelImg_settings)
    def searchBarLogic(self):
        self.controller.entryCreator(160, 0, 580, 80, self, "SearchBarResults")
        try:
            for widgetname, widget in self.children.items():
                if widgetname == "searchbarentrycanvas":
                    widget.destroy()
        except RuntimeError:
            pass
        for widgetname, widget in self.children.items():
            # print(widgetname)
            if widgetname == "searchbarresults":
                # widget.grid_propagate(False)                
                widget.after(100, lambda: widget.focus_set())
                widget.bind("<Return>", lambda e: self.searchByQuery(widget.get()))
                widget.bind("<FocusIn>", lambda e: widget.delete(0, END))
                # on new letters being typed, the search bar logic will be called
                widget.bind("<FocusOut>", lambda e: self.searchBarLogic())
                widget.bind("<Tab>", lambda e: self.searchBarLogic())
            # if isinstance(widget, Canvas) or isinstance(widget, Entry):
            #     widgetstoremove.append(widgetname)
            #     for widgetname in widgetstoremove:
            #         self.children[widgetname].destroy()

    def searchByQuery(self, query):
        # global connection
        # user = prisma.user.find_many()
        # with connection:
        #     cursor = connection.cursor()
        #     cursor.execute("SELECT * FROM User;")
        #     results = cursor.fetchall()
        #     print(results)
        #calculating where the search bar is and creating a top level window there
        # print(user)
        print(query)
        self.controller.canvasCreator(160, 60, 580, 240, self, classname="SearchBarEntryCanvas", bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
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
                self.controller.labelCreator(
                    r"Assets\Dashboard\SearchResultsBg.png", 0, 180, "SearchResults4", widget, text=f"Search Results 4 for {query}", font=("Avenir Next", 20), wraplength=600
                )

def runGui():
    window = Window()
    window.mainloop()

if __name__ == "__main__":
    runGui()
