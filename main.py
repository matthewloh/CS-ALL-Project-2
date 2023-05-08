import ctypes
from ctypes import windll
import threading
from time import sleep
import time
from tkinter import *
from tkinter import messagebox
# A drop in replacement for ttk that uses bootstrap styles
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.validation import add_text_validation, add_regex_validation, validator, add_validation, add_option_validation
from pathlib import Path
from itertools import cycle
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from prisma import Prisma
from multiprocessing import Process
from elementcreator import gridGenerator
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
import clr
import bcrypt
import jwt
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Threading')
from System.Windows.Forms import Control
from System.Threading import Thread,ApartmentState,ThreadStart  
load_dotenv()

from static import *
from PIL import Image, ImageTk, ImageSequence

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
eventId = None

class Window(ttk.Window):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self,themename="minty", *args, **kwargs )
        self.widgetsDict = {} 
        self.imageDict = {}
        self.imagePathDict = {}
        self.initializeWindow()
        self.labelSettingsParentFrame = [
        (r"Assets\LandingPage\BackgroundImage.png", 0, 0, "Background Image",self.parentFrame),
        (r"Assets\LandingPage\Landing Page Title.png", 0, 0, "Title Label", self.parentFrame),
        (r"Assets\Login Page with Captcha\LoginPageTeachers.png", 0, 0, "postselectframebg", self.postSelectFrame),
        ]
        self.loadedImgs = [
            ImageTk.PhotoImage(Image.open(r"Assets\Login Page with Captcha\LoginPageStudents.png")),
            ImageTk.PhotoImage(Image.open(r"Assets\Login Page with Captcha\LoginPageTeachers.png")),
            ImageTk.PhotoImage(Image.open(r"Assets/Login Page with Captcha/Sign In Page.png")),
        ]

        buttonSettingsPSF = [
            (r"Assets\LandingPage\Student Button.png", 1080, 320, "Student Button", 
            self.parentFrame, lambda: self.signUpPage(student=True)),
            (r"Assets\LandingPage\Teacher Button.png", 240, 320, "Teacher Button",
            self.parentFrame, lambda: self.signUpPage(teacher=True)), 
            (r"Assets\Login Page with Captcha\BackButtonComponent.png", 0, 40, "Back Button", 
            self.postSelectFrame,
            lambda: self.postSelectFrame.grid_remove()),
            (r"Assets\LandingPage\GoFullScreen.png", 1620, 960, "GoFullScreenBtn", self.parentFrame, 
            lambda: [self.togglethewindowbar()]),
            (r"Assets\Login Page with Captcha\Skip Button.png", 1680, 980, "Skip Button", 
            self.postSelectFrame,
            lambda: self.loadSignIn())
        ]

        self.settingsUnpacker(self.labelSettingsParentFrame, "label")
        self.settingsUnpacker(buttonSettingsPSF, "button")
        
        self.openDevWindow()
        self.bind("<Configure>", self.resizeEvent)
        self.frames = {}
        self.canvasInDashboard = {}
        for F in (Dashboard, ):
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

    def initializeWindow(self):
        windll.shcore.SetProcessDpiAwareness(1)
        quarterofscreenwidth = int(int(user32.GetSystemMetrics(0) / 2) / 4)
        quarterofscreenheight = int(int(user32.GetSystemMetrics(1) / 2) / 4)
        gridGenerator(self, 1, 1, NICEPURPLE)
        if self.winfo_screenwidth() <= 1920 and self.winfo_screenheight() <= 1080:
            self.geometry(f"1920x1080+0+0")
        elif self.winfo_screenwidth() > 1920 and self.winfo_screenheight() > 1080:
            self.geometry(f"1920x1080+{quarterofscreenwidth}+{quarterofscreenheight}")
        self.title("INTI.ai Learning Client")
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self.destroy())
        self.parentFrame = Frame(self, bg=LIGHTYELLOW, width=1, height=1, name="parentframe", autostyle=False)
        self.parentFrame.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=NSEW)
        gridGenerator(self.parentFrame, 96, 54, WHITE)
        self.postSelectFrame = Frame(self.parentFrame, bg=LIGHTYELLOW, width=1, height=1, name="postselectframe", autostyle=False)
        self.postSelectFrame.grid(row=0, column=0, rowspan=54, columnspan=96, sticky=NSEW)
        gridGenerator(self.postSelectFrame, 96, 54, WHITE)

    def signUpPage(self, student=False, teacher=False):
        ref = self.widgetsDict["postselectframebg"]
        if student:
            ref.configure(image=self.loadedImgs[0])
            self.studentform = UserForms(self.postSelectFrame, self, "studentreg")
            self.studentform.userReg()
            self.studentform.loadStudentReg()
        elif teacher:
            ref.configure(image=self.loadedImgs[1])
            self.teacherform = UserForms(self.postSelectFrame, self, "teacherreg")
            self.teacherform.userReg()
            self.teacherform.loadLecturerReg()
        self.postSelectFrame.grid(), self.postSelectFrame.tkraise()

    def loadSignIn(self):
        ref = self.widgetsDict["postselectframebg"]
        ref.configure(image=self.loadedImgs[2])
        try:
            if self.studentform:
                self.widgetsDict["studentreg"].grid_remove()
                self.widgetsDict["studentregcompleteregbutton"].grid_remove()
                self.studentform.loadSignIn()
        except AttributeError:
            pass
        try:
            if self.teacherform:
                self.widgetsDict["teacherreg"].grid_remove()
                self.widgetsDict["teacherregcompleteregbutton"].grid_remove()
                self.teacherform.loadSignIn()
        except AttributeError:
            pass
        def reloadForm():
            try:
                if self.studentform:
                    self.studentform.grid()
                    self.widgetsDict["studentregcompleteregbutton"].grid()
                    self.widgetsDict["postselectframebg"].configure(image=self.loadedImgs[0])
            except AttributeError:
                pass
            try:
                if self.teacherform:
                    self.teacherform.grid()
                    self.widgetsDict["teacherregcompleteregbutton"].grid()
                    self.widgetsDict["postselectframebg"].configure(image=self.loadedImgs[1])
            except AttributeError:
                pass
            self.widgetsDict["signinform"].grid_remove()
            self.widgetsDict["backbutton"].configure(
                command=lambda: [
                    self.postSelectFrame.grid_remove(),
                ])
            self.widgetsDict["skipbutton"].configure(
                command=lambda: [
                    self.loadSignIn(),
                ])  
        self.widgetsDict["backbutton"].configure(
            command=lambda: [
                reloadForm(),
            ]
        )
        self.widgetsDict["skipbutton"].configure(
            command=lambda: [     
            self.show_frame(Dashboard), 
            self.show_canvas(DashboardCanvas), 
            self.get_page(Dashboard).loadSpecificAssets("student"),
            ]
        )

    def createImageReference(self, imagepath:str, classname:str):
        self.imagePathDict[classname] = imagepath #stores a key value pair of "classname" : "imagepath"
        image = ImageTk.PhotoImage(Image.open(imagepath)) #creates a Tkinter image object
        self.imageDict[classname] = image  # stores a key value pair of "classname" : "image" to prevent garbage collection
    def resize(self):
        # the ratio of 1080p to the current screen size TODO: add aspect ratio sensing
        currentdimensions= (self.winfo_width(), self.winfo_height())
        print(f"Current dimensions: {currentdimensions}")
        # how many times larger is the screensize than the original 1920 x 1080
        ratio = (currentdimensions[0] / 1920, 
                 currentdimensions[1] / 1080)
        print(f"Ratio: {ratio}")
        # take the original imagepath and resize it to the current screen size, then store it in the imageDict
        # only resize when the currentdimensions changes
        # do not constantly loop over the imageDict resizing the images
        if currentdimensions != (1920, 1080):
            for key, imagepath in self.imagePathDict.items():
                orgimg = Image.open(imagepath)
                orgimgwidth, orgimgheight = orgimg.size
                # print(f"Original image dimensions: {orgimgwidth} x {orgimgheight}, {key}")
                newimgwidth, newimgheight = int(orgimgwidth * ratio[0]), int(orgimgheight * ratio[1])
                # print(f"New image dimensions: {newimgwidth} x {newimgheight}, {key}")
                image = ImageTk.PhotoImage(Image.open(imagepath).resize((newimgwidth, newimgheight), Image.Resampling.LANCZOS))
                self.imageDict[key] = image
                try:
                    self.widgetsDict[key].configure(image=image)
                except KeyError:
                    print("yeah")
            print("this has triggered")
        else:
            print("the screen is working as intended")

    def resizeEvent(self, event):
        self.eventId = None
        if not (str(event.widget).split(".")[-1].startswith("!label")):
            if len(str(event.widget).split(".")) < 3:
                if event.widget == self:
                    self.resizeDelay = 100
                    if self.eventId:
                        self.after_cancel(self.eventId)
                    if self.state() == "zoomed":
                        self.eventId = self.after(self.resizeDelay, self.resize)
                    elif self.state() == "normal":
                        self.eventId = self.after(self.resizeDelay, self.resize)


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

    def openDevWindow(self):
        self.new_method()
        def parseObjectsFromFrame():
            for widgetname, widget in self.widgetsDict.items():
                # skip widgets that are children of labels in hostfr
                if widgetname.startswith("!la") and widget.winfo_parent().endswith("hostfr"):
                    continue
                # skip widgets related to teacherreg or studentreg
                parents = widget.winfo_parent().split(".")
                if any(p.endswith("reg") for p in parents[-3:]):
                    continue
                print(widget.winfo_parent(), widget.winfo_class(), widget.winfo_name())
        # self.developerkittoplevel.attributes("-topmost", True)
        self.settingsUnpacker([(r"Assets\DeveloperKit\BG.png", 0, 0, "DevKitBG", self.developerkittoplevel)], "label")
        buttonSettingsDevKit = [
        (r"Assets\DeveloperKit\GetAllWidgets.png", 40, 40, "GetAllWidgetsBtn", self.developerkittoplevel,
        lambda: self.removeManyWidgets()),
        (r"Assets\DeveloperKit\GetSpecificWidget.png", 40, 240, "GetWidgetFromFrame", self.developerkittoplevel,
        lambda: self.removeAWidget().grid_remove()),
        (r"Assets\DeveloperKit\CollectAllWidgets.png", 520, 0, "CollectWidgets", self.developerkittoplevel, 
        lambda: parseObjectsFromFrame()),
        (r"Assets\DeveloperKit\xd1.png", 680, 0, "XD1 Button", self.developerkittoplevel, 
        lambda: self.start_webview()),
        (r"Assets\DeveloperKit\ToggleZoom.png", 680, 320, "Toggle Zoom Button", self.developerkittoplevel, 
        lambda: [self.togglethewindowbar()]),
        ]
        self.settingsUnpacker(buttonSettingsDevKit, "button")
        self.entryCreator(40, 120, 360, 80, root=self.developerkittoplevel, classname="DevKitEntryGreen", bg="light green")
        self.entryCreator(40, 320, 360, 80, root=self.developerkittoplevel, classname="DevKitEntryOrange", bg=ORANGE)

    def new_method(self):
        self.developerkittoplevel = Toplevel(
            self,
            bg=LIGHTYELLOW,
            name="devkit"
        )
        self.developerkittoplevel.title("Developer Kit")
        self.developerkittoplevel.bind("<Escape>", lambda e: self.destroy())
        gridGenerator(self.developerkittoplevel, 40, 40, ORANGE)
        self.developerkittoplevel.geometry(f"800x800+0+0")  
        self.developerkittoplevel.resizable(False, False)
    def removeManyWidgets(self):
        widgetlist = []
        framename = self.widgetsDict["devkitentrygreen"].get()
        for widgetname, widget in self.widgetsDict.items():
            if widgetname.startswith(framename):
                if isinstance(widget, Frame):
                    widgetlist.append(widget)  
        print(widgetlist)
        for widget in widgetlist:
            widget.grid_remove()

    def removeAWidget(self):
        widgetname = self.widgetsDict["devkitentryorange"].get()
        return self.widgetsDict[widgetname]

    def tupleToDict(self, tup): #TODO: make this multipurpose
        if len(tup) == 5:
            return dict(zip(("imagepath", "xpos", "ypos", "classname","root"), tup))
        if len(tup) == 6:
            return dict(zip(("imagepath", "xpos", "ypos", "classname","root", "buttonFunction"), tup))

    def settingsUnpacker(self, listoftuples, typeoftuple):
        """
        format for labels: (imagepath, x, y, classname, root)\n
        format for buttons: (imagepath, x, y, classname, root, buttonFunction)\n
        tupletodict creates a dict mapping to the creator functions.
        TODO: enable styling within here
        """
        for i in listoftuples:
            if typeoftuple == "button":
                self.buttonCreator(**self.tupleToDict(i))
            elif typeoftuple == "label":
                self.labelCreator(**self.tupleToDict(i))

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()
        # ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())
    
    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
        # ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())

    def get_page(self, classname):
        return self.frames[classname]

    def togglethewindowbar(self):
        self.deletethewindowbar() if self.state() == "normal" else self.showthewindowbar()

    def deletethewindowbar(self):
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("zoomed")

    def showthewindowbar(self):
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style |= WS_CAPTION | WS_THICKFRAME
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("normal")

    def buttonCreator(
        self,
        imagepath,
        xpos,
        ypos,
        classname=None,
        buttonFunction=None,
        root=None,
        relief=SUNKEN,
        overrideRelief=FLAT,
        text=None,
        fg=WHITE,
        font=("Avenir Next Bold", 16),
        wraplength=None,
        pady=None,
        hasImage=True
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
        columnarg = int(xpos/20)
        rowarg = int(ypos/20)
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

        Button(
            root, image=image,
            command=lambda:buttonFunction () if buttonFunction else print(f"This is the {classname} button"),  
            relief=relief if not overrideRelief else overrideRelief,
            bg=WHITE, width=1, height=1,
            cursor="hand2", state=button_kwargs["state"], 
            name=button_kwargs["name"],
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=fg, 
            justify=LEFT,
            autostyle=False,
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
            pady=pady)
        
        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)

    def labelCreator(
        self, 
        imagepath, 
        xpos, 
        ypos, 
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
        columnarg = int(xpos/20)
        rowarg = int(ypos/20)

        Label(
            root, image=image, relief=FLAT, width=1, height=1, 
            cursor="", state=NORMAL, name=classname, 
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=WHITE, justify=LEFT,
            autostyle=False,
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW
        )

        self.updateWidgetsDict(root=root)

    def frameCreator(
        self,
        xpos,
        ypos,
        framewidth,
        frameheight,
        root=None,
        classname=None,
        bg=LIGHTYELLOW,
        relief=FLAT,
        imgSettings=None,
        ):
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)

        Frame(root, width=1, height=1, bg=bg, relief=relief,
        name=classname, autostyle=False,
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
        )
        self.updateWidgetsDict(root=root)
        if imgSettings:
            listofimages = list(enumerate(imgSettings)) 
        # imgBg is a list of tuples containing (imagepath, x, y, name)
        # example = [("Assets\Dashboard\Top Bar.png", 0, 0, "stringwhatever"),] -> 0 ('Assets\\Dashboard\\Top Bar.png', 0, 0, 'stringwhatever')
        for widgetname, widget in root.children.items():
            if widgetname == classname:
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
                            buttonFunction=j[4])

    def entryCreator(
        self, xpos, ypos,
        width, height, 
        root=None, classname=None, bg=WHITE,
        relief=FLAT, fg=BLACK, textvariable=None, pady=None,
        font=("Avenir Next Medium", 16)):

        classname= classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        self.updateWidgetsDict(root=root)
        Entry(root, bg=bg, relief=SOLID,
            font=font,fg=fg, width=1,
            name=classname, 
            autostyle=False,
            textvariable=textvariable).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
            pady=pady,
        )
        self.updateWidgetsDict(root=root)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                widget.grid_propagate(False)

    def canvasCreator(
        self, xpos, ypos, width, height, root, classname=None,
        bgcolor=WHITE, imgSettings=None,
        relief=FLAT, 
        isTransparent=False, transparentcolor=TRANSPARENTGREEN,
        ):
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)

        if imgSettings:
            listofimages = list(
                enumerate(imgSettings)
            ) 
        Canvas(root, bg=bgcolor, 
        highlightcolor=bgcolor, 
        relief=FLAT, width=1, height=1, 
        name=classname, highlightthickness=0, autostyle=False
        ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
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
                            j[1],
                            j[2],
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4]
                        )
        self.updateWidgetsDict(root=root)

    def menubuttonCreator(
        self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, #Essential
        bgcolor=WHITE, 
        relief=FLAT, font=("Helvetica", 16),
        text=None, variable=None, listofvalues=None, command=None,#Special Values
        ):
        """
        Takes in arguments xpos, ypos, width, height, from Figma, creates a frame,\n
        and places a menubutton inside of it. The menubutton is then returned into the global dict of widgets.\n
        Requires a var like StringVar() to be initialized and passed in.\n
        Feed in a list of values and command functions to be used in the menubutton.\n
        Styling handled by passing in a formatted classname and font to config a style.
        """
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        classname = classname.lower().replace(" ", "")
        themename = f"{str(root).split('.')[-1]}.TMenubutton"
        print(themename, classname)
        menustyle = ttk.Style().configure(
        style=themename, font=("Helvetica", 10),
        background="#F9F5EB", foreground=BLACK, bordercolor="#78c2ad", 
        relief="raised"
        )
        self.frameCreator(xpos, ypos, width, height, root, classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT)
        frameref = self.widgetsDict[f"{classname}hostfr"]
        menubutton = ttk.Menubutton(
        frameref, text=text.title(), 
        style=themename, 
        name=classname,
        # bootstyle=(DANGER)
        )
        menubutton.grid(row=0, column=0, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        menubtnmenu = Menu(
        menubutton, tearoff=0, name=f"{classname}menu", 
        bg=LIGHTPURPLE, relief=FLAT, font=("Helvetica", 12),
        )

        for x in listofvalues:
            menubtnmenu.add_radiobutton(label=x, variable=variable, value=x,
            command=lambda:[command(), menubutton.config(text=variable.get())])
        menubutton["menu"] = menubtnmenu
        self.widgetsDict[menubutton["menu"]] = menubtnmenu
        self.widgetsDict[classname] = menubutton
        self.updateWidgetsDict(root=root)

    def ttkEntryCreator(
        self, xpos=None, ypos=None, width=None, height=None, 
        root=None, classname=None,
        bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16),
        validation=False, passwordchar="*",
        isContactNo=False, isEmail=False,
        ):
        """
        Takes in arguments xpos, ypos, width, height, from Figma, creates a frame,\n
        and places a ttk.Entry inside of it. The ttk.Entry is then returned into the global dict of widgets.\n
        Requires a var like StringVar() to be initialized and passed in.\n
        Styling handled by passing in a formatted classname and font to config a style.
        """
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        # entrystyle = ttk.Style()
        # entrystyle.configure(f"{classname}.TEntry", font=font, background=bgcolor, foreground=WHITE)
        self.frameCreator(xpos, ypos, width, height, root, classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT)

        @validator
        def validatePassword(event):
            """
            Validates the password and confirms password entries.
            """
            parentname = str(root).split(".")[-1]
            if self.widgetsDict[f"{parentname}passent"].get() == "":
                return False 
            if self.widgetsDict[f"{parentname}passent"].get() == self.widgetsDict[f"{parentname}confpassent"].get():
                return True
            else:
                return False
            # pass
        frameref = self.widgetsDict[f"{classname}hostfr"]
        themename = f"{str(root).split('.')[-1]}.TEntry"
        entrystyle = ttk.Style().configure(
        style=themename, font=font, background=NICEBLUE, foreground=BLACK,
        )
        entry = ttk.Entry(frameref, 
                        #   style=themename, 
                        bootstyle=PRIMARY,
                            name=classname, font=font, background=bgcolor)
        entry.grid(row=0, column=0, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        if validation == "isPassword":
            entry.config(show=passwordchar)
            add_regex_validation(widget=entry, pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$")
        elif validation == "isConfPass":
            entry.config(show=passwordchar)
            add_validation(widget=entry, func=validatePassword)
        elif validation == "isEmail":
            add_regex_validation(widget=entry, pattern="^[a-zA-Z0-9._%+-]+@(?:student\.newinti\.edu\.my|newinti\.edu\.my)$")
        elif validation == "isContactNo":
            add_regex_validation(widget=entry, pattern="^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$")
        else:
            #just not blank
            add_regex_validation(widget=entry, pattern="^.*\S.*$")
            pass
     
            
            
        self.widgetsDict[classname] = entry
        self.updateWidgetsDict(root=root)

    def webview2creator(
        self, xpos=None, ypos=None, framewidth=None, frameheight=None, root=None, classname=None,
        bgcolor=WHITE, relief=FLAT, font=("Avenir Next", 16),
        url=None,
        ):
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        classname = classname.lower().replace(" ", "") 
        navigationbar = Frame(root, width=1, height=1, bg=bgcolor, relief=FLAT, name=f"{classname}navbar")
        gridGenerator(navigationbar, widthspan, 3, WHITE)
        navigationbar.grid(row=rowarg-3, column=columnarg, rowspan=3, columnspan=widthspan, sticky=NSEW)
        frame = WebView2(parent=root, width=1, height=1, url=url, name=classname, bg=bgcolor)
        frame.grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
        )
        #binding a callback button to go back in javascript
        def goBack():
            frame.evaluate_js("window.history.back();")
            defocus()
        #binding a callback button to go forward in javascript
        def goForward():
            frame.evaluate_js("window.history.forward();")
            defocus()
        def getUrlandGo():
            try:
                url = self.widgetsDict[f"{classname}urlentry"].get()
                frame.load_url(url)
            except: 
                url = f"https://www.google.com/search?q={self.widgetsDict[f'{classname}urlentry'].get()}"
                frame.load_url(url)
            defocus()
            ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())
        def gotoGoogle():
            frame.load_url("https://www.google.com/")
            defocus()
            ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())
        def toggleFullscreen():
            frame.evaluate_js("document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();")
            defocus()
        def defocus():
            # getting the current window using the window handle, then simulating a refocusing
            # frame.evaluate_js("document.activeElement.blur();")
            ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())
        def exitCompletely():
            widgetslist = [frame, navigationbar]
            for widget in widgetslist:
                widget.destroy()

        self.buttonCreator(r"Assets\Chatbot\Backbutton.png", 0, 0, classname=f"{classname}backbutton",
        buttonFunction=lambda: goBack(),
        root=navigationbar)
        self.buttonCreator(r"Assets\Chatbot\Forwardbutton.png", 80, 0, classname=f"{classname}forwardbutton", 
        buttonFunction=lambda: goForward(),
        root=navigationbar)
        self.entryCreator(160, 0, 760, 60, navigationbar, classname=f"{classname}urlentry",
        bg=bgcolor)
        self.widgetsDict[f"{classname}urlentry"].insert(0, url)
        self.widgetsDict[f"{classname}urlentry"].bind("<Return>", lambda event: getUrlandGo())
        self.buttonCreator(r"Assets\Chatbot\EnterAndGoButton.png", 920, 0, classname=f"{classname}enterandgobutton",
        buttonFunction=lambda: getUrlandGo(),
        root=navigationbar)
        self.buttonCreator(r"Assets\Chatbot\GoogleButton.png", 1060, 0, classname=f"{classname}googlebutton",
        buttonFunction=lambda: gotoGoogle(),
        root=navigationbar)
        self.buttonCreator(r"Assets\Chatbot\Togglefullscreen.png", 1120, 0, classname=f"{classname}fullscreenbutton",
        buttonFunction=lambda: toggleFullscreen(),
        root=navigationbar)

        self.updateWidgetsDict(root=root)

    def hex_to_rgb(self, hexstring):
        # Convert hexstring to integer
        hexint = int(hexstring[1:], 16)
        # Extract Red, Green, and Blue values from integer using bit shifting
        red = hexint >> 16
        green = (hexint >> 8) & 0xFF
        blue = hexint & 0xFF
        colorkey = win32api.RGB(red, green, blue)
        return colorkey

class AnimatedGif(Frame):
    def __init__(self, parent=None, controller=None, 
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
        self.grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        # open the GIF and create a cycle iterator
        file_path = Path(__file__).parent / imagepath
        with Image.open(file_path) as im:
            # create a sequence
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.image_cycle = cycle(images)

            # length of each frame
            self.framerate = im.info["duration"]
        #getting the width and height of the image
        imagetogetdetails = ImageTk.PhotoImage(Image.open(file_path))
        self.imgwidth = imagetogetdetails.width()
        self.imgheight = imagetogetdetails.height()
        imgrow = int(imageypos / 20)
        imgcolumn = int(imagexpos / 20)
        imgrowspan = int(self.imgheight / 20)
        imgcolumnspan = int(self.imgwidth / 20)
        self.img_container = Label(self, image=next(self.image_cycle), width=1, bg="#344557")
        self.img_container.grid(
        column= imgcolumn, row=imgrow, columnspan=imgcolumnspan, rowspan=imgrowspan, sticky=NSEW)
        self.after(self.framerate, self.next_frame)
        self.controller.widgetsDict[classname] = self
    def next_frame(self):
        """Update the image for each frame"""
        try:
            self.img_container.configure(image=next(self.image_cycle))
            self.after(self.framerate, self.next_frame)
        except:
            #happens because when switching from student to lecturer, a new animatedgifinstance is created and the old one is destroyed
            print("gif error i will fix one day surely")

class UserForms(Frame):
    def __init__(self, parent=None, controller=None, name=None):
        super().__init__(parent, width=1, height=1, bg="#344557", name=name)
        self.controller = controller
        self.parent = parent
        self.name = name

    def tupleToDict(self, tup):
        if len(tup) == 6:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname"], tup))
        elif len(tup) == 7:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname", "validation"], tup))

    def prismaFormSubmit(self,  data:dict):
        #LECTURER OR STUDENT
        prisma = Prisma()
        prisma.connect()

        try:
            if data["role"] == "STUDENT":     
                prisma.student.create(
                    data={
                        "fullName": data["fullName"],
                        "email": data["email"],
                        "password": data["password"],
                        "contactNo": data["contactNo"],
                        "currEnrolledCourses": data["currentCourses"],
                        "currInstitution": data["institution"],
                        "currSchool": data["school"],
                        "currSession": data["session"],
                        "currProgram": data["programme"],
                    }
                )
                user = prisma.student.find_many()
                toast = ToastNotification(
                    title="Success",
                    message=f"{user}",
                    duration=3000
                )
                toast.show_toast()
                self.gif.grid_forget()
                messagebox.showinfo("success", f"{user}")
            elif data["role"] == "LECTURER":
                prisma.lecturer.create(
                    data={
                        "fullName": data["fullName"],
                        "email": data["email"],
                        "password": data["password"],
                        "contactNo": data["contactNo"],
                        "currTenure" : data["tenure"],
                        "currInstitution": data["institution"],
                        "currSchool" : data["school"],
                        "currProgram" : data["programme"],
                        "currTeachingCourses": data["currentCourses"],
                    }
                )
                user = prisma.lecturer.find_many()
                print(user)
                toast = ToastNotification(
                    title="Success",
                    message=f"{user}",
                    duration=3000
                )
                toast.show_toast()
                self.gif.grid_forget()
        except Exception as e:
            self.gif.grid_forget()
            toast = ToastNotification(
                    title="Error",
                    message=f"There was an error creating your account. Please try again. {e}",
                    duration=3000
                )
            toast.show_toast()
        prisma.disconnect()
    def send_data(self, data:dict):
        t = threading.Thread(target=self.prismaFormSubmit, args=(data,))
        self.gif = AnimatedGif(
            parent=self, controller=self.controller,
            xpos=0, ypos=0, bg="#344557",
            framewidth=800, frameheight=920, classname="loadingspinner",
            imagepath=r"Assets\spinners.gif", imagexpos=200, imageypos=300)
        self.controller.labelCreator(
            r"Assets/signinguplabel.png", 140, 620, "signinguplabel", self.gif)
        t.daemon = True
        t.start()

    def userReg(self):
        self.controller.frameCreator(
        xpos=1000, ypos=40, framewidth= 800, frameheight= 920,
        root=self.parent, classname=f"{self.name}", 
        )
        self.frameref = self.controller.widgetsDict[f"{self.name}"]
        self.imgLabels = [
            (r"Assets\Login Page with Captcha\Sign Up Form.png", 0, 0, f"{self.name}BG", self.frameref),
        ]
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, f"{self.name}fullname"),
            (40, 220, 720, 60, self.frameref, f"{self.name}email", "isEmail"), 
            (40, 320, 340, 60, self.frameref, f"{self.name}passent", "isPassword"),
            (40, 480, 340, 60, self.frameref, f"{self.name}confpassent", "isConfPass"),
            (420, 320, 340, 60, self.frameref, f"{self.name}contactnumber", "isContactNo"),
            (420, 500, 340, 40, self.frameref, f"{self.name}captcha"),
        ]
        self.controller.buttonCreator(
        r"Assets\Login Page with Captcha\BackButtonComponent.png", 0, 40, classname="Back Button", 
        root=self.parent,
        buttonFunction=lambda: self.parent.grid_remove())
    def loadLecturerReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\LecturerForm.png", 0 , 600, f"{self.name}Lecturer", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        # implementing the joining of the two lists
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOCAT", "SOE", "CEPS", "SOBIZ", "Unlisted"],
            "tenure": ["Full Time", "Part Time", "Unlisted"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course2": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course3": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        }
        self.institution = StringVar(name=f"{self.name}institution")
        self.school = StringVar(name=f"{self.name}school")
        self.tenure = StringVar(name=f"{self.name}tenure")
        self.programme = StringVar(name=f"{self.name}programme")
        self.course1 = StringVar(name=f"{self.name}course1")
        self.course2 = StringVar(name=f"{self.name}course2")
        self.course3 = StringVar(name=f"{self.name}course3")
        vars = {
            "institution": self.institution,
            "school": self.school,
            "tenure": self.tenure,
            "programme": self.programme,
            "course1": self.course1,
            "course2": self.course2,
            "course3": self.course3
        }
        positions = {
            "institution": {"x": 140, "y": 660},
            "school": {"x": 140, "y": 740},
            "tenure": {"x": 520, "y": 660},
            "programme": {"x": 520, "y": 740},
            "course1": {"x": 20, "y": 840},
            "course2": {"x": 280, "y": 840},
            "course3": {"x": 540, "y": 840}
        }
        for name, values in lists.items():
            self.controller.menubuttonCreator(
                xpos=positions[name]["x"], ypos=positions[name]["y"], width=240, height=40,
                root=self.frameref, classname=name, text=f"Select {name}", listofvalues=values,
                variable=vars[name], font=("Helvetica", 10), command=lambda name=name:[print(vars[name].get())]
            )
        entries = {
            "fullname": self.controller.widgetsDict[f"{self.name}fullname"],
            "email": self.controller.widgetsDict[f"{self.name}email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict[f"{self.name}contactnumber"],
            "captcha": self.controller.widgetsDict[f"{self.name}captcha"]
        }

        def foo():
            mainwindowcorners = self.controller.winfo_geometry().split("+")
            xval = int(mainwindowcorners[1])
            yval = int(mainwindowcorners[2])
            print(xval, yval)
            self.controller.mainwindowcorners = (xval, yval, "se")
            return self.controller.mainwindowcorners

        def foo_bar():
            details = []
            for name, entry in entries.items():
                details.append(entry.get())
            detailstoast = ToastNotification(
            title="Submission details",
            message=f"Full Name: {details[0]}\nEmail: {details[1]}\nPassword: {details[2]}\nContact Number: {details[4]}\nInstitution: {vars['institution'].get()}\nSchool: {vars['school'].get()}\nTenure: {vars['tenure'].get()}\nProgramme: {vars['programme'].get()}\nCourse 1: {vars['course1'].get()}\nCourse 2: {vars['course2'].get()}\nCourse 3: {vars['course3'].get()}",
            duration=3000,
            position=foo()
            )
            detailstoast.show_toast()
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
        buttonFunction=lambda:[foo_bar()],
        pady=5)

        self.controller.buttonCreator(
            r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
            classname=f"{self.name}completeregbutton", buttonFunction=
            lambda: self.send_data(
                data={
                    "fullName": entries["fullname"].get(),
                    "email": entries["email"].get(),
                    "password": self.encryptPassword(entries["password"].get()),
                    "contactNo": entries["contactnumber"].get(),
                    "tenure" : vars['tenure'].get(),
                    "institution" : vars['institution'].get(),
                    "school" : vars['school'].get(),
                    "programme" : vars['programme'].get(),
                    "currentCourses": f"{vars['course1'].get()}, {vars['course2'].get()}, {vars['course3'].get()}",
                    "role": "LECTURER"
                }
            ),
            root=self.parent
        )
        self.completeregbutton = self.controller.widgetsDict[f"{self.name}completeregbutton"]
        # self.completeregbutton.config(state=DISABLED)
    
    def loadStudentReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\StudentForm.png", 0 , 600, f"{self.name}Student", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOCAT", "SOE", "CEPS", "SOBIZ", "Unlisted"],
            "session": ["APR2023", "AUG2023", "JAN2024", "APR2024", "AUG2025"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course2": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course3": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        }
        self.institution = StringVar()
        self.school = StringVar()
        self.session = StringVar()
        self.programme = StringVar()
        self.course1 = StringVar()
        self.course2 = StringVar()
        self.course3 = StringVar()
        vars = {
            "institution": self.institution,
            "school": self.school,
            "session": self.session,
            "programme": self.programme,
            "course1": self.course1,
            "course2": self.course2,
            "course3": self.course3,
        }
        positions = {
            "institution": {"x": 140, "y": 660},
            "school": {"x": 140, "y": 740},
            "session": {"x": 520, "y": 660},
            "programme": {"x": 520, "y": 740},
            "course1": {"x": 20, "y": 840},
            "course2": {"x": 280, "y": 840},
            "course3": {"x": 540, "y": 840}
        }
        for name, values in lists.items():
            self.controller.menubuttonCreator(
                xpos=positions[name]["x"], ypos=positions[name]["y"], width=240, height=40,
                root=self.frameref, classname=name.capitalize(), text=f"Select {name.capitalize()}",
                listofvalues=values, variable=vars[name], font=("Helvetica", 10),
                command=lambda name=name: print(vars[name].get())
            )
        # TODO: add absolute positioning for the toast notification
        entries = {
            "fullname": self.controller.widgetsDict[f"{self.name}fullname"],
            "email": self.controller.widgetsDict[f"{self.name}email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict[f"{self.name}contactnumber"],
            "captcha": self.controller.widgetsDict[f"{self.name}captcha"]
        }
        def foo():
            mainwindowcorners = self.controller.winfo_geometry().split("+")
            xval = int(mainwindowcorners[1])
            yval = int(mainwindowcorners[2])
            print(xval, yval)
            self.controller.mainwindowcorners = (xval, yval, "se")
            return self.controller.mainwindowcorners
        def foo_bar():
            details = []
            for name, entry in entries.items():
                details.append(entry.get())
            detailstoast = ToastNotification(
            title="Submission details",
            message=f"Full Name: {details[0]}\nEmail: {details[1]}\nPassword: {details[2]}\nConfirm Password: {details[3]}\nContact Number: {details[4]}\nInstitution: {vars['institution'].get()}\nSchool: {vars['school'].get()}\nSession: {vars['session'].get()}\nProgramme: {vars['programme'].get()}\nCourse 1: {vars['course1'].get()}\nCourse 2: {vars['course2'].get()}\nCourse 3: {vars['course3'].get()}",
            duration=3000,
            position=foo()
            )
            detailstoast.show_toast()
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
        buttonFunction=lambda:[foo_bar()],
        pady=5)
        self.controller.buttonCreator(
            r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
            classname=f"{self.name}completeregbutton", buttonFunction=
            # lambda: messagebox.showinfo("success", f"this is the button for {self.name}"),
            lambda: self.send_data(
                data={
                    "fullName": entries["fullname"].get(),
                    "email": entries["email"].get(),
                    "password": self.encryptPassword(entries["password"].get()),
                    "contactNo": entries["contactnumber"].get(),
                    "currentCourses": f"{vars['course1'].get()}, {vars['course2'].get()}, {vars['course3'].get()}",
                    "institution": vars["institution"].get(),
                    "school": vars["school"].get(),
                    "session": vars["session"].get(),
                    "programme": vars["programme"].get(),
                    "role": "STUDENT"
                }
            ),
            root=self.parent
        )
    def encryptPassword(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def validatePassword(self, password: str, encrypted: str) -> str:
        return bcrypt.checkpw(password.encode("utf-8"), encrypted.encode("utf-8"))

    def loadSignIn(self):
        self.controller.frameCreator(
        xpos=1140, ypos=240, framewidth= 600, frameheight= 600,
        root=self.parent, classname="signinform", 
        )
        self.signinformref = self.controller.widgetsDict["signinform"]
        self.signInLabels = [
            (r"Assets\Login Page with Captcha\LoginForm.png", 0, 0, f"loginformbg", self.signinformref),
        ]
        self.signInButtons = [
            (r"Assets\Login Page with Captcha\SignInButton.png", 120, 360, "signinbutton", self.signinformref, lambda: print("test")),
            (r"Assets\Login Page with Captcha\GoToRegisterBtn.png", 40, 480, "gotoregisterbutton", self.signinformref, lambda: print("test")),
        ]
        self.userLoginEntries = [
            (60, 80, 480, 80, self.signinformref, "signinemail", "isEmail"),
            (60, 240, 480, 80, self.signinformref, "signinpassent", "isPassword"),
        ]
        self.controller.settingsUnpacker(self.signInLabels, "label")
        self.controller.settingsUnpacker(self.signInButtons, "button")
        for i in self.userLoginEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))

class SlidePanel(Frame):
    def __init__(self, parent=None, controller=None, startcolumn=0, startrow=0, endrow=0, endcolumn=0, startcolumnspan=0, endcolumnspan=0, rowspan=0, columnspan=0, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN, name=None):
        super().__init__(parent, width=1, height=1, bg=TRANSPARENTGREEN, name=name)
        self.controller = controller
        gridGenerator(self, width, height, bg)
        self.grid(row=startrow, column=startcolumn, rowspan=rowspan, columnspan=startcolumnspan, sticky=NSEW)
        self.tk.call("lower", self._w)
        self.grid_propagate(False)
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
        self.sidebarlabel = Label(self, image=self.sidebarimage, bg=TRANSPARENTGREEN,width=1,height=1, name="sidebar")
        self.sidebarlabel.grid(row=0, column=0, rowspan=rowspan, columnspan=16, sticky=NSEW)
        self.sidebarpfp = Button(self, image=self.sidebarpfpimage, bg=LIGHTYELLOW, name="sidebarpfp", command=lambda:print("pfp clicked"))
        self.sidebarpfp.place(x=60, y=40, width=200, height=200)
        self.signoutbutton = Button(self, image=self.signoutbuttonimg, bg=LIGHTYELLOW, name="signoutbutton", command=lambda:self.controller.widgetsDict["dashboard"].tk.call("lower", self.controller.widgetsDict["dashboard"]._w))
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
        Frame.__init__(self, parent, width=1, height=1, bg=LIGHTYELLOW, name="dashboard", autostyle=False)
        # gridGenerator(parent, 96, 54, LIGHTYELLOW)
        self.controller = controller
        self.parent = parent
        self.framereference = self
        gridGenerator(self, 96, 54, LIGHTYELLOW)
        self.animatedpanel = SlidePanel(self, self.controller ,startcolumn=0, startrow=4, endrow=3, endcolumn=15, rowspan=46, startcolumnspan=1, endcolumnspan=16, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN, name="animatedpanel")
        self.staticImgLabels = [
        (r"Assets\Dashboard\Top Bar.png", 0, 0, "TopBar", self.framereference),
        ]
        self.staticImgBtns = [
        (r"Assets\Dashboard\HamburgerMenuTopBar.png", 0, 0, "HamburgerMenu", self.framereference, lambda: self.animatedpanel.animate()),
        (r"Assets\Dashboard\searchbar.png", 100, 0, "SearchBar", self.framereference, lambda : self.searchBarLogic()),
        (r"Assets\Dashboard\RibbonTopBar.png", 1760, 20, "RibbonTopBar", self.framereference, lambda: print("hello-4")),
        (r"Assets\Dashboard\BellTopBar.png", 1820, 20, "BellTopBar", self.framereference, lambda: print("hello-3")),
        (r"Assets\Dashboard\01DashboardChip.png", 20, 1020, "DashboardChip", self.framereference, lambda: self.controller.show_canvas(DashboardCanvas)),
        (r"Assets\Dashboard\02SearchChip.png", 160, 1020, "SearchChip", self.framereference, lambda: [self.controller.show_canvas(SearchPage),]),
        (r"Assets\Dashboard\03ChatbotChip.png", 300, 1020, "ChatbotChip", self.framereference, 
        lambda: [self.controller.show_canvas(Chatbot), self.chatbottoast.show_toast()]),
        (r"Assets\Dashboard\04LearningHubChip.png", 440, 1020, "LearningHubChip", self.framereference, lambda: self.controller.show_canvas(LearningHub)),
        (r"Assets\Dashboard\05MyCoursesChip.png", 580, 1020, "MyCoursesChip", self.framereference, lambda: self.controller.show_canvas(CourseView)),
        (r"Assets\Dashboard\06MyDiscussionsChip.png", 720, 1020, "MyDiscussionsChip", self.framereference, lambda: self.controller.show_canvas(DiscussionsView)),
        (r"Assets\Dashboard\07MyFavoritesChip.png", 860, 1020, "MyFavoritesChip", self.framereference, lambda: self.controller.show_canvas(FavoritesView)),
        (r"Assets\Dashboard\08MyAppointmentsChip.png", 1000, 1020, "MyAppointmentsChip", self.framereference, lambda: self.controller.show_canvas(AppointmentsView)),
        ]
        self.chatbottoast = ToastNotification(
            title="You have entered the webbrowser view",
            message="You will not be able to use the keyboard for the application until you exit the webbrowser view. You can exit the webbrowser view by clicking the exit button on the top right corner of the webbrowser view.",
            duration=3000,
        )
        self.controller.canvasCreator(0, 80, 1920, 920, root=self.framereference, classname="maincanvas", bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.loadAllStaticAssets(self.staticImgBtns, self.staticImgLabels)
        self.maincanvasref = self.controller.widgetsDict["maincanvas"]
        self.controller.canvasCreator(0, 0, 1920, 920, root=self.maincanvasref, classname="dashboardcanvas", bgcolor=NICEBLUE, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.openSearchSettings = [
            (r"Assets\Dashboard\TopbarSearchOpen.png", 0, 0, "SearchBarOpen", self.framereference),
            (r"Assets\Dashboard\ExitSearch.png", 0, 0, "ExitSearchBtn", self.framereference, lambda : self.closeSearchBarLogic()),
        ]
        self.dashboardcanvasref = self.controller.widgetsDict["dashboardcanvas"]
    def loadAllStaticAssets(self, button_settings, label_settings):
        self.controller.settingsUnpacker(label_settings, "label")
        self.controller.settingsUnpacker(button_settings, "button")

    def loadSpecificAssets(self, role):
        self.controller.widgetsDict["dashboardcanvas"].tk.call('raise', self.controller.widgetsDict["dashboardcanvas"]._w)
        if role == "student":
            self.controller.labelCreator( r"Assets\Dashboard\StudentDashboard.png", 0, 0, classname="StudentDashboardLabel", root=self.controller.widgetsDict["dashboardcanvas"])
            self.gif = AnimatedGif(
            parent=self.controller.widgetsDict["dashboardcanvas"], controller=self.controller,
            xpos=180, ypos= 460, bg="#344557", 
            framewidth=400, frameheight=300, classname="cutebunny",
            imagepath=r"Assets\bunnygifresized400x300.gif", imagexpos=0, imageypos=0)
        elif role == "teacher":
            self.controller.labelCreator( r"Assets\Dashboard\TeacherDashboard.png", 0, 80, classname="TeacherDashboardLabel", root=self.controller.widgetsDict["dashboardcanvas"])
        # self.controller.widgetRef("dashboardcanvas").tk.call('raise', self.controller.widgetRef("dashboardcanvas")._w)
    def tupleToDict(self, tup):
        if len(tup) == 5:
            return dict(zip(("imagepath", "xpos", "ypos", "classname","root"), tup))
        if len(tup) == 6:
            return dict(zip(("imagepath", "xpos", "ypos", "classname","root", "buttonFunction"), tup))
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
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="dashboardcanvas", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
                
class SearchPage(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="searchpage", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Search Page", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")

class Chatbot(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="chatbot", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\Chatbot\ChatbotBg.png", 0, 0, "ChatbotBgLabel", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.webview2creator(xpos=60, ypos=160, framewidth=1200, frameheight=740, root=self, classname="chatbotwebview2", url="http://localhost:5555/")

class LearningHub(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="learninghub", autostyle=False)
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
        Canvas.__init__(self, parent, width=1, height=1, bg="#F6F5D7", name="courseview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\My Courses\CoursesBG.png", 0, 0, "CoursesBG", self),
        ]
        self.controller.canvasCreator(80, 100, 1760, 720, root=self, classname="coursescanvas", bgcolor="#F6F5D7",
            isTransparent=True, transparentcolor="#efefef")
        canvas = self.controller.widgetsDict["coursescanvas"]
        self.buttonImgLabels = [
                (r"Assets\My Courses\CompArch.png", 0, 0, "cancourse", canvas,lambda: self.grid_remove()),
                (r"Assets\My Courses\MathForCS.png", 0, 300, "csmathcourse", canvas,lambda: self.grid_remove()),
                (r"Assets\My Courses\ObjectOP.png", 920, 0, "oopcourse", canvas ,lambda: self.grid_remove()),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.buttonImgLabels, "button")
        self.controller.widgetsDict["coursescanvas"].tk.call("raise", self.controller.widgetsDict["coursescanvas"]._w)

            # if widgetname.endswith("course"):
                # buttonstoconfig.append(widget)
        # for widget in buttonstoconfig:
            # widget.bind("<Enter>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=RAISED))
            # widget.bind("<Leave>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=FLAT))
        # self.controller.widgetsDict[f"{widget}"].bind("<Enter>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=RAISED))
        # self.controller.widgetsDict[f"{widget}"].bind("<Leave>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=FLAT))
class AnimatedStarBtn(Frame):
    def __init__(self, 
        parent=None, controller=None, 
        xpos=0, ypos=0, framewidth=0, frameheight=0, 
        classname=None, imagepath=None, imagexpos=0,imageypos=0, bg=WHITE, ):
        super().__init__(parent, width=1, bg=bg, autostyle=False, name=classname) 
        self.controller = controller
        self.grid_propagate(False)
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        self.configure(bg=bg)
        gridGenerator(self, widthspan, heightspan, bg)
        self.grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        
        file_path = Path(__file__).parent / r"Assets\DiscussionsView\stargifs.gif"
        with Image.open(file_path) as im:
            #sequence
            sequence = ImageSequence.Iterator(im)
            self.images = [ImageTk.PhotoImage(sequence_frame) for sequence_frame in sequence]
            self.image_cycle = cycle(self.images)
            #length of each frame
            self.framerate = im.info['duration']
        
        self.frame_index = 0
        self.end_index = len(self.images) - 1 
        imagetogetdetails = ImageTk.PhotoImage(Image.open(file_path))
        self.imgwidth = 40
        self.imgheight = 40
        imgrow = int(imageypos / 20)
        imgcolumn = int(imagexpos / 20)
        imgrowspan = int(self.imgheight / 20)
        imgcolumnspan = int(self.imgwidth / 20)

        self.img_container = Button(self, image=next(self.image_cycle), width=1, bg="#344557",
                                    command=lambda: self.trigger_animation())
        self.img_container.grid(
        column= imgcolumn, row=imgrow, columnspan=imgcolumnspan, rowspan=imgrowspan, sticky=NSEW)
        self.animation_length = len(self.images)

        self.animation_status = StringVar(value="start")
        self.animation_status.trace('w', self.animate)

        # self.after(self.framerate, self.next_frame)

    def next_frame(self):
        self.img_container.configure(image=next(self.image_cycle))
        self.after(self.framerate, self.next_frame)

    def infinite_animate(self):
        self.frame_index += 1
        self.frame_index = 0 if self.frame_index > self.animation_length else self.frame_index
        self.img_container.configure(image=next(self.image_cycle))
        self.after(self.framerate, self.infinite_animate)
    def trigger_animation(self):
        print(self.animation_status.get())
        if self.animation_status.get() == "start":
            self.frame_index = 0
            self.animation_status.set("forward")
        if self.animation_status.get() == "end":
            self.frame_index = self.animation_length
            self.animation_status.set("backward")
    def animate(self, *args):
        if self.animation_status.get() == "forward":
            self.frame_index += 1
            self.img_container.configure(image=self.images[self.frame_index - 1])
            
            if self.frame_index < self.animation_length:
                self.after(20, self.animate)
            else:
                self.animation_status.set("end")
        
        if self.animation_status.get() == "backward":
            self.frame_index -= 1 
            self.img_container.configure(image=self.images[self.frame_index])
            if self.frame_index > 0:
                self.after(20, self.animate)
            else:
                self.animation_status.set("start")

class DiscussionsView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="discussionsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\DiscussionsView\DiscussionsViewBG.png", 0, 0, "DiscussionsBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.loadDiscussionTopics()
    def loadDiscussionTopics(self):
        # ~~~~ BACKEND FUNCTIONALITY ~~~~
        # TODO: add this database functionality
        # posting a request to the database and getting the credentials
        # searching for discussions where user is present in
        discussiontitlesList = ["This is sample discussion topic 1", "This is sample discussion topic 2", "This is a sample discussion topic 3"]
        initialcoordinates = (100, 320)
        for number, discussiontitle in list(enumerate(discussiontitlesList)):
        # ~~~~ FRONTEND FUNCTIONALITY ~~~~
            def toggleStarImage(number, state:bool):
                imgpaths = [
                    r"Assets\DiscussionsView\Deactivated Star.png",
                    r"Assets\DiscussionsView\ActivatedStar.png",
                ]
                loaded = [
                    ImageTk.PhotoImage(Image.open(imgpaths[0])),
                    ImageTk.PhotoImage(Image.open(imgpaths[1])),
                ]
                ref = self.controller.widgetsDict[f"discresult{number}star"]
                # true = activated, false = deactivated
                if state:
                    ref.config(image=loaded[1])
                else:
                    ref.config(image=loaded[0])
                state = not state
            discResultsSettings = {
                "imagepath": r"Assets\DiscussionsView\discussionstitlecomponentbg.png",
                "xpos": initialcoordinates[0],
                "ypos": initialcoordinates[1],
                "classname": f"discresult{number}",
                "buttonFunction": lambda number=number: messagebox.showinfo("Discussion", f"This is a sample discussion {number+1}"),
                "root": self,
                "text": discussiontitle,
                "fg": "black",
            }
            self.controller.buttonCreator(**discResultsSettings)
            starBtn = AnimatedStarBtn(
                parent=self, xpos=initialcoordinates[0] + 740, ypos=initialcoordinates[1] + 20,
                framewidth=40, frameheight=40, classname=f"discresult{number}star",
                imagexpos=0, imageypos=0
            )
            # discResultsStarBtn = {
            #     "imagepath": r"Assets\DiscussionsView\Deactivated Star.png",
            #     "xpos": initialcoordinates[0] + 740,
            #     "ypos": initialcoordinates[1] + 20,
            #     "classname": f"discresult{number}star",
            #     "buttonFunction": lambda number=number: 
            #     [print("Favorited", f"This is favorite button {number+1}"),
            #     # toggleStarImage(number, state=False)
            #     ],
            #     "root": self,
            #     "overrideRelief": "raised",
            # }
            # self.controller.buttonCreator(**discResultsStarBtn)
            initialcoordinates = (initialcoordinates[0], initialcoordinates[1] + 100)



class FavoritesView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
class AppointmentsView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="appointmentsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        self.name = "appointmentsview"
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\AppointmentsView\BGForAppointments1920x780+0+200.png", 0, 0, "AppointmentsBG", self),
            (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.frameCreator(
            xpos=120, ypos=580,
            framewidth=1160, frameheight=180,
            root=self, classname="appointmentsmenuframe", bg="#F6F5D7", 
        )
        buttontoloadmenubutton = ttk.Button(self.controller.widgetsDict["appointmentsmenuframe"], text="Appointments", command=lambda: self.loadmenubuttons())
        buttontoloadmenubutton.place(x=0, y=0, width=200, height=60)
        self.controller.frameCreator(120, 580, 1160, 180, self, classname="hostfr", bg=WHITE, relief=FLAT)
        self.controller.widgetsDict["appointmentsmenuframe"].tk.call("raise", self.controller.widgetsDict["appointmentsmenuframe"]._w)
        self.coursebuttonvar = StringVar()
        self.lecturerbuttonvar = StringVar()
        self.purposebuttonvar = StringVar()
        ttk.Style().configure("TMenubutton", font=("Helvetica", 16, "bold"),
        background=NICEBLUE, foreground=BLACK, relief=FLAT)
        self.coursebuttonvar = StringVar()
        self.coursemenubutton, self.coursemenubtnmenu, _ = self.create_menubutton(
            parent=self.controller.widgetsDict["appointmentsmenuframe"],
            text="Courses",
            values=["Computer Architecture", "Mathematics for Computer Science", "Object Oriented Programming"],
            variable=self.coursebuttonvar,
            xpos=40,ypos=80
        )
        self.lecturerbuttonvar = StringVar()
        self.lecturermenubutton, self.lecturermenubtnmenu, _ = self.create_menubutton(
            parent=self.controller.widgetsDict["appointmentsmenuframe"],
            text="Lecturers",
            values=["Dr. John Doe", "Dr. Jane Doe", "Dr. John Smith"],
            variable=self.lecturerbuttonvar,
            xpos=420,ypos=80
        )
        self.purposebuttonvar = StringVar()
        self.purposemenubutton, self.purposemenubtnmenu, _ = self.create_menubutton(
            parent=self.controller.widgetsDict["appointmentsmenuframe"],
            text="Purpose",
            values=["Consultation", "Discussion", "Other"],
            variable=self.purposebuttonvar,
            xpos=800,ypos=80
        )
        self.controller.widgetsDict["coursemenubutton"] = self.coursemenubutton
        self.controller.widgetsDict["lecturermenubutton"] = self.lecturermenubutton
        self.controller.widgetsDict["purposemenubutton"] = self.purposemenubutton

    def create_menubutton(self, parent, text, values, variable, xpos=0,ypos=0, command=None):
        menubutton_var = StringVar()
        style = ttk.Style()
        style.configure("TMenubutton", font=("Helvetica", 16, "bold"), background="#e9d0c3", foreground=BLACK, relief=FLAT)
        menubutton = ttk.Menubutton(parent, width=320, text=text, name=text.lower() + "menubutton")
        menubutton.place( x=xpos, y=ypos,
             width=320, height=60)
        menubutton_menu = Menu(menubutton, tearoff=0)
        for value in values:
            menubutton_menu.add_radiobutton(label=value, variable=menubutton_var, value=value,
                command=lambda: self.loadmenubuttons(menubutton, menubutton_var))
        if command:
            menubutton.config(command=command)
        menubutton.config(menu=menubutton_menu)
        variable.set(menubutton_var.get())
        return menubutton, menubutton_menu, menubutton_var
    
    def loadmenubuttons(self, menubutton, menubutton_var):
        # retrieve the course name from the coursemenubutton
        menubutton.config(text=menubutton_var.get())
        course = self.controller.widgetsDict["coursemenubutton"].cget("text")
        if course.startswith("Computer"):
            messagebox.showerror("Error", "Please select a course")
        else:
            # if the course is not empty, load the buttons
            print(course)
def runGui():
    window = Window()
    window.mainloop()

if __name__ == "__main__":
    runGui()
    # try:
    #     t = Thread(ThreadStart(runGui))
    #     t.ApartmentState = ApartmentState.STA
    #     t.Start()
    #     t.Join()
    # except Exception as e:
    #     runGui()