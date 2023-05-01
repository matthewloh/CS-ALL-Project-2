import ctypes
from ctypes import windll
from time import sleep
import time
from tkinter import *
from tkinter import messagebox
# A drop in replacement for ttk that uses bootstrap styles
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.validation import add_text_validation, add_regex_validation, validator, add_validation, add_option_validation
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from prisma import Prisma
from multiprocessing import Process
from elementcreator import gridGenerator
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Threading')
from System.Windows.Forms import Control
from System.Threading import Thread,ApartmentState,ThreadStart  
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

class Window(ttk.Window):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self,themename="minty", *args, **kwargs)
        self.widgetsDict = {} 
        self.imageDict = {}
        self.initializeWindow()
 
        self.labelSettingsParentFrame = [
        (r"Assets\LandingPage\BackgroundImage.png", 0, 0, "Background Image",self.parentFrame),
        (r"Assets\LandingPage\Landing Page Title.png", 0, 0, "Title Label", self.parentFrame),
        (r"Assets\Login Page with Captcha\LoginPageTeachers.png", 0, 0, "postselectframebg", self.postSelectFrame),
        ]
        self.settingsUnpacker(self.labelSettingsParentFrame, "label")
        self.loadedImgs = [
            ImageTk.PhotoImage(Image.open(r"Assets\Login Page with Captcha\LoginPageStudents.png")),
            ImageTk.PhotoImage(Image.open(r"Assets\Login Page with Captcha\LoginPageTeachers.png"))
        ]
        buttonSettingsForParentFrame = [
            (r"Assets\LandingPage\Student Button.png", 1080, 320, "Student Button", 
            self.parentFrame, lambda: self.signUpPage(student=True)),
            (r"Assets\LandingPage\Teacher Button.png", 240, 320, "Teacher Button",
            self.parentFrame, lambda: self.signUpPage(teacher=True)) 
        ]
        self.settingsUnpacker(buttonSettingsForParentFrame, "button")
        self.btnSettingsPostSelectFrame = [
        (r"Assets\Login Page with Captcha\BackButtonComponent.png", 0, 40, "Back Button", 
        self.postSelectFrame,
        lambda: self.postSelectFrame.grid_remove()),
        (r"Assets\Login Page with Captcha\Skip Button.png", 1680, 980, "Skip Button", 
        self.postSelectFrame,
        lambda: [
        self.show_frame(Dashboard), 
        self.show_canvas(DashboardCanvas), 
        self.get_page(Dashboard).loadSpecificAssets("student")])
        ]
        self.settingsUnpacker(self.btnSettingsPostSelectFrame, "button")
        
        def parseObjectsFromFrame(frame: Frame):
            for widgetname, widget in self.widgetsDict.items():
                # skip widgets that are children of labels in hostfr
                if widgetname.startswith("!la") and widget.winfo_parent().endswith("hostfr"):
                    continue
                # skip widgets related to teacherreg or studentreg
                parents = widget.winfo_parent().split(".")
                if any(p.endswith("reg") for p in parents[-3:]):
                    continue
                print(widget.winfo_parent(), widget.winfo_class(), widget.winfo_name())
                    
        self.opensDevWindow(parseObjectsFromFrame)
        
        self.frames = {}
        self.canvasInDashboard = {}
        for F in (
            Dashboard,
            # RegistrationPage, LoginPage, 
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
            studentform = UserForms(self.postSelectFrame, self, "studentreg")
            studentform.userReg()
            studentform.loadStudentReg()
        elif teacher:
            ref.configure(image=self.loadedImgs[1])
            teacherform = UserForms(self.postSelectFrame, self, "teacherreg")
            teacherform.userReg()
            teacherform.loadLecturerReg()

        self.postSelectFrame.grid(), self.postSelectFrame.tkraise()

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

    def opensDevWindow(self, parseObjectsFromFrame):
        self.new_method()
        # self.developerkittoplevel.attributes("-topmost", True)
        self.settingsUnpacker([(r"Assets\DeveloperKit\BG.png", 0, 0, "DevKitBG", self.developerkittoplevel)], "label")
        buttonSettingsDevKit = [
        (r"Assets\DeveloperKit\GetAllWidgets.png", 40, 40, "GetAllWidgetsBtn", self.developerkittoplevel,
        lambda: self.removeManyWidgets()),
        (r"Assets\DeveloperKit\GetSpecificWidget.png", 40, 240, "GetWidgetFromFrame", self.developerkittoplevel,
        lambda: self.removeAWidget().grid_remove()),
        (r"Assets\DeveloperKit\CollectAllWidgets.png", 520, 0, "CollectWidgets", self.developerkittoplevel, 
        lambda: parseObjectsFromFrame(self)),
        (r"Assets\DeveloperKit\xd1.png", 680, 0, "XD1 Button", self.developerkittoplevel, 
        lambda: self.start_webview()),
        (r"Assets\DeveloperKit\ToggleZoom.png", 680, 320, "Toggle Zoom Button", self.developerkittoplevel, 
        lambda: [self.deletethewindowbar(), self.state("zoomed")])
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
        ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())
    
    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
        ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())

    def get_page(self, classname):
        return self.frames[classname]

    def deletethewindowbar(self):
        hwnd: int = get_handle(self)
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
        xpos,
        ypos,
        classname=None,
        buttonFunction=None,
        root=None,
        relief=SUNKEN,
        overrideRelief=FLAT,
        text=None,
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
            text=text, font=font, wraplength=wraplength, compound=CENTER, fg=WHITE, justify=LEFT,
            autostyle=False,
        ).grid(
            row=rowarg,
            column=columnarg,
            rowspan=heightspan,
            columnspan=widthspan,
            sticky=NSEW,
            pady=pady)
        self.updateWidgetsDict(root=root)

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
        menubtnmenu.option_add('*Menu.fg', 'orange')
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
            if self.widgetsDict[f"{parentname}passent"].get() == self.widgetsDict[f"{parentname}confpassent"].get():
                return True
            elif self.widgetsDict[f"{parentname}passent"].get() == "":
                return False 
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

class UserForms(Frame):
    def __init__(self, parent=None, controller=None, name=None):
        super().__init__(parent, width=1, height=1, bg=WHITE, name=name)
        self.controller = controller
        self.parent = parent
        self.name = name

    def on_submit(self):
        messagebox.showinfo("success", f"Welcome {self.fullname.get()}")
    def tupleToDict(self, tup):
        if len(tup) == 6:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname"], tup))
        elif len(tup) == 7:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname", "validation"], tup))

    def userReg(self):
        self.controller.frameCreator(
        xpos=1000, ypos=40, framewidth= 800, frameheight= 920,
        root=self.parent, classname=f"{self.name}", 
        )
        self.frameref = self.controller.widgetsDict[f"{self.name}"]
        self.imgLabels = [
            (r"Assets\Login Page with Captcha\Sign Up Form.png", 0, 0, f"{self.name}BG", self.frameref),
        ]
        passwordvar = StringVar(value="")
        confPassvar = StringVar(value="")
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, "fullname"),
            (40, 220, 720, 60, self.frameref, "email", "isEmail"), 
            (40, 320, 340, 60, self.frameref, f"{self.name}passent", "isPassword"),
            (40, 480, 340, 60, self.frameref, f"{self.name}confpassent", "isConfPass"),
            (420, 320, 340, 60, self.frameref, "contactnumber", "isContactNo"),
            (420, 500, 340, 40, self.frameref, "captcha"),
        ]
        self.completeRegButton = self.controller.buttonCreator(
            r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
            classname=f"{self.name}CompleteRegButton", buttonFunction=lambda: messagebox.showinfo("success", f"this is the button for {self.name}"),
            root=self.parent
        )
        # looping to get a variable for each entry
        self.entrylist = []
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
        institution = StringVar(name=f"{self.name}institution")
        school = StringVar(name=f"{self.name}school")
        tenure = StringVar(name=f"{self.name}tenure")
        programme = StringVar(name=f"{self.name}programme")
        course1 = StringVar(name=f"{self.name}course1")
        course2 = StringVar(name=f"{self.name}course2")
        course3 = StringVar(name=f"{self.name}course3")
        vars = {
            "institution": institution,
            "school": school,
            "tenure": tenure,
            "programme": programme,
            "course1": course1,
            "course2": course2,
            "course3": course3
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
        # fullname, email, password, confirmpassword, contactnumber
        entries = {
            "fullname": self.controller.widgetsDict["fullname"],
            "email": self.controller.widgetsDict["email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict["contactnumber"],
            "captcha": self.controller.widgetsDict["captcha"]
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
    
    def loadStudentReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\StudentForm.png", 0 , 600, f"{self.name}Student", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        self.studentRegEntries = [
            # (200, 660, 160, 40, self.frameref, "currentinstitution"),
            # (200, 740, 160, 40, self.frameref, "currentschool"),
            # (600, 660, 160, 40, self.frameref, "semester"),
            # (600, 740, 160, 40, self.frameref, "currentprogramme"),
            # (200, 820, 560, 40, self.frameref, "enrolledcourses"),
        ]
        #self.studentRegEntries extends self.userRegEntries        
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOCAT", "SOE", "CEPS", "SOBIZ", "Unlisted"],
            "session": ["APR2023", "AUG2023", "JAN2024", "APR2024", "AUG2025"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course2": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course3": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        }

        institution = StringVar()
        school = StringVar()
        session = StringVar()
        programme = StringVar()
        course1 = StringVar()
        course2 = StringVar()
        course3 = StringVar()

        vars = {
            "institution": institution,
            "school": school,
            "session": session,
            "programme": programme,
            "course1": course1,
            "course2": course2,
            "course3": course3,
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
            "fullname": self.controller.widgetsDict["fullname"],
            "email": self.controller.widgetsDict["email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict["contactnumber"],
            "captcha": self.controller.widgetsDict["captcha"]
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
            message=f"Full Name: {details[0]}\nEmail: {details[1]}\nPassword: {details[2]}\nConfirm Password: {details[3]}\nContact Number: {details[4]}\nInstitution: {institution.get()}\nSchool: {school.get()}\nSession: {session.get()}\nProgramme: {programme.get()}\nCourse 1: {course1.get()}\nCourse 2: {course2.get()}\nCourse 3: {course3.get()}",
            duration=3000,
            position=foo()
            )
            detailstoast.show_toast()
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
        buttonFunction=lambda:[foo_bar()],
        pady=5)

    def loginLecturer(self):
        print("hello")

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
        Frame.__init__(self, parent, width=1, height=1, bg=LIGHTYELLOW, name="dashboard", autostyle=False)
        # gridGenerator(parent, 96, 54, LIGHTYELLOW)
        self.controller = controller
        self.parent = parent
        self.framereference = self
        gridGenerator(self, 96, 54, LIGHTYELLOW)
        self.animatedpanel = SlidePanel(self, self.controller ,startcolumn=0, startrow=4, endrow=3, endcolumn=15, rowspan=46, startcolumnspan=1, endcolumnspan=16, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN, name="animatedpanel")
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
        
        (r"Assets\Dashboard\03ChatbotChip.png", 300, 1020, "ChatbotChip", self.framereference, 
        lambda: [self.controller.show_canvas(Chatbot), self.chatbottoast.show_toast(), 
        ctypes.windll.user32.SetForegroundWindow(ctypes.windll.kernel32.GetConsoleWindow())]),
        
        (r"Assets\Dashboard\04LearningHubChip.png", 440, 1020, "LearningHubChip", self.framereference, lambda: self.controller.show_canvas(LearningHub)),
        (r"Assets\Dashboard\05MyCoursesChip.png", 580, 1020, "MyCoursesChip", self.framereference, lambda: self.controller.show_canvas(CourseView)),
        (r"Assets\Dashboard\06MyDiscussionsChip.png", 720, 1020, "MyDiscussionsChip", self.framereference, lambda: self.controller.show_canvas(DiscussionsView)),
        (r"Assets\Dashboard\07MyFavoritesChip.png", 860, 1020, "MyFavoritesChip", self.framereference, lambda: self.controller.show_canvas(FavoritesView)),
        (r"Assets\Dashboard\08MyAppointmentsChip.png", 1000, 1020, "MyAppointmentsChip", self.framereference, lambda: self.controller.show_canvas(AppointmentsView)),
        # (r"Assets\Dashboard\ChatbotButton.png", 1660, 780, "ChatbotButton", self.framereference, lambda: print("hello-13"))
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
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\AppointmentsView\BGForAppointments1920x780+0+200.png", 0, 120, "AppointmentsBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")

def runGui():
    window = Window()
    window.mainloop()

if __name__ == "__main__":
    t = Thread(ThreadStart(runGui))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Join()