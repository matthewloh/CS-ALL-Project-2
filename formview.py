# This is an example of the structure for a page in the application.
from dotenv import load_dotenv
from elementcreator import gridGenerator
from main import AnimatedGif, SlidePanel, TopBar
from static import *
import ctypes
from ctypes import windll
import threading
from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.validation import add_text_validation, add_regex_validation, validator, add_validation, add_option_validation
from pathlib import Path
from itertools import cycle
from dotenv import load_dotenv
from prisma import Prisma
from multiprocessing import Process
from elementcreator import gridGenerator
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
import bcrypt
import pendulum
from pendulum import timezone
from nonstandardimports import *
from PIL import Image, ImageTk, ImageSequence, ImageFont, ImageDraw
from components.animatedstarbtn import AnimatedStarBtn
from basewindow import ElementCreator
from tkinter import filedialog
from PIL import ImageTk, Image
load_dotenv()

GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW


def get_handle(root) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)


user32 = windll.user32
eventId = None

# Once you load into VS Code, please hide the Window,
# Dashboard, DashboardCanvas classes by using the Ctrl + Shift + [
# keyboard shortcut. This will make it easier to navigate the code.
# You can also use the Ctrl + Shift + ] keyboard shortcut to unhide the classes.


class Window(ElementCreator):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self, themename="minty", *args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}
        self.initializeWindow()
        self.initMainPrisma()
        self.frames = {}
        self.canvasInDashboard = {}
        # self.prismaConnect()

        for F in (Dashboard, ):
            frame = F(parent=self.parentFrame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
            frame.grid_propagate(False)
            self.canvasCreator(0, 80, 1920, 920, root=frame, classname="maincanvas",
                               bgcolor=WHITE, isTransparent=True, transparentcolor=LIGHTYELLOW)
            self.updateWidgetsDict(frame)
            # frame.grid_remove()
        for FRAME in (DashboardCanvas, FavoritesView,):
            canvas = FRAME(
                parent=self.widgetsDict["maincanvas"], controller=self)
            self.canvasInDashboard[FRAME] = canvas
            self.updateWidgetsDict(canvas)
            canvas.grid(row=0, column=0, columnspan=96,
                        rowspan=46, sticky=NSEW)
            canvas.grid_propagate(False)
            canvas.grid_remove()
        self.show_canvas(FavoritesView)
        self.bind("<F11>", lambda e: self.togglethewindowbar())

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()

    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
        canvas.focus_force()

    def startPrisma(self):
        try:
            self.mainPrisma = Prisma()
            self.mainPrisma.connect()
            print("Successfully connected to Prisma client.")
        except Exception as e:
            print(e)

    def initMainPrisma(self):
        t = threading.Thread(target=self.startPrisma)
        t.daemon = True
        t.start()

    # def prismaConnect(self):
    #     def connect():
    #         self.prisma = Prisma()
    #         self.prisma.connect()
    #     self.prismaThread = threading.Thread(target=connect, daemon=True)
    #     self.prismaThread.start()

    def initializeWindow(self):
        windll.shcore.SetProcessDpiAwareness(1)
        quarterofscreenwidth = int(int(user32.GetSystemMetrics(0) / 2) / 4)
        quarterofscreenheight = int(int(user32.GetSystemMetrics(1) / 2) / 4)
        gridGenerator(self, 1, 1, NICEPURPLE)
        if self.winfo_screenwidth() <= 1920 and self.winfo_screenheight() <= 1080:
            self.geometry(f"1920x1080+0+0")
        elif self.winfo_screenwidth() > 1920 and self.winfo_screenheight() > 1080:
            self.geometry(
                f"1920x1080+{quarterofscreenwidth}+{quarterofscreenheight}")
        self.title("INTI.ai Learning Client")
        self.resizable(False, False)
        self.bind("<Escape>", lambda e: self.destroy())
        self.parentFrame = Frame(
            self, bg=LIGHTYELLOW, width=1, height=1, name="parentframe", autostyle=False)
        self.parentFrame.grid(row=0, column=0, rowspan=1,
                              columnspan=1, sticky=NSEW)
        gridGenerator(self.parentFrame, 96, 54, WHITE)
        self.postSelectFrame = Frame(
            self.parentFrame, bg=LIGHTYELLOW, width=1, height=1, name="postselectframe", autostyle=False)
        self.postSelectFrame.grid(
            row=0, column=0, rowspan=54, columnspan=96, sticky=NSEW)
        gridGenerator(self.postSelectFrame, 96, 54, WHITE)
        self.postSelectFrame.tkraise()

    def updateWidgetsDict(self, root: Frame):
        widgettypes = (Label, Button, Frame, Canvas, Entry,
                       Text, ScrolledFrame, ScrolledText)
        for widgetname, widget in self.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.parentFrame.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.postSelectFrame.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in root.children.items():
            if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        try:
            for widgetname, widget in self.get_page(Dashboard).children.items():
                if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass
        try:
            for widgetname, widget in self.widgetsDict["maincanvas"].children.items():
                if isinstance(widget, widgettypes) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass


class Dashboard(Frame):
    def __init__(self, parent, controller: Window):
        Frame.__init__(self, parent, width=1, height=1,
                       bg=LIGHTYELLOW, name="dashboard", autostyle=False)
        self.controller = controller
        self.parent = parent
        self.framereference = self
        gridGenerator(self, 96, 54, LIGHTYELLOW)
        self.animatedpanel = SlidePanel(self, self.controller, startcolumn=0, startrow=4, endrow=3, endcolumn=15, rowspan=46,
                                        startcolumnspan=1, endcolumnspan=16, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN, name="animatedpanel")
        topbar = TopBar(parent=self, controller=self.controller)
        # self.loadSpecificAssets(role="student")
        self.staticImgBtns = [
            (r"Assets\Dashboard\01DashboardChip.png", 20, 1020, "DashboardChip",
             self.framereference, lambda: self.controller.show_canvas(DashboardCanvas)),
            # (r"Assets\Dashboard\02SearchChip.png", 160, 1020, "SearchChip",
            #  self.framereference, lambda: [self.controller.show_canvas(SearchPage),]),
            # (r"Assets\Dashboard\03ChatbotChip.png", 300, 1020, "ChatbotChip", self.framereference,
            #     lambda: [self.controller.show_canvas(Chatbot), self.chatbottoast.show_toast()]),
            # (r"Assets\Dashboard\04LearningHubChip.png", 440, 1020, "LearningHubChip",
            #  self.framereference, lambda: self.controller.show_canvas(LearningHub)),
            # (r"Assets\Dashboard\05MyCoursesChip.png", 580, 1020, "MyCoursesChip",
            #  self.framereference, lambda: self.controller.show_canvas(CourseView)),
            # (r"Assets\Dashboard\06MyDiscussionsChip.png", 720, 1020, "MyDiscussionsChip",
            #  self.framereference, lambda: self.controller.show_canvas(DiscussionsView)),
            (r"Assets\Dashboard\07MyFavoritesChip.png", 860, 1020, "MyFavoritesChip",
             self.framereference, lambda: self.controller.show_canvas(FavoritesView)),
            # (r"Assets\Dashboard\08MyAppointmentsChip.png", 1000, 1020, "MyAppointmentsChip",
            #  self.framereference, lambda: self.controller.show_canvas(AppointmentsView)),
        ]
        self.controller.settingsUnpacker(self.staticImgBtns, "button")


    def postLogin(self, data: dict, prisma: Prisma = None):
        role = data["role"]
        id = data["id"]
        fullName = data["fullName"]
        email = data["email"]
        modules = data["modules"]



class DashboardCanvas(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1, bg=NICEBLUE,
                        name="dashboardcanvas", autostyle=False, relief=RAISED)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, NICEBLUE)
        self.threader(self.emulateLoggingIn, ())

    def threader(self, func, args):
        t = threading.Thread(target=func, args=args)
        t.start()

    def emulateLoggingIn(self):
        prisma = self.controller.mainPrisma
        user = prisma.userprofile.find_first(
            where={
                "email": "p21013568@student.newinti.edu.my"
            },
            include={
                "favoritePosts": {
                    "include": {
                        "author": True
                    }
                },
                "createdPosts": True,
                # If you are working with a student, this will return the field in the Student's table where the userid is found
                "student": {
                    "include": {
                        "modules": True
                    }
                },
                "lecturer": True,  # will return an empty list if the user is not a lecturer and vice versa
            }
        )
        infotup = (user.email, user.fullName, user.contactNo)
        # Where there could be multiple fields, like modules, favoritePosts, and posts
        # You can access them like this

        data = {
            "id": user.id,
            "fullName": user.fullName,
            "email": user.email,
        }
        # for k, v in data.items():
        #     print(f"{k}:{v}")
        favoritesview = self.controller.widgetsDict["favoritesview"]
        # favoritesview.postLogin()
        # print(f"User email:{user.email}")
        # print(f"User Details:\n{user.json(indent=2)}")

class FavoritesView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=ORANGE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, ORANGE)

        self.createFrames()

        # Image
        self.staticImgs = [(r"Assets\SearchView\searchframe.png", 0, 0, "favviewbg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")

        # Entry
        self.keywordEntry=self.controller.ttkEntryCreator(
            xpos=300, ypos=220, width=420, height=60, root=self, classname="keywordentry")
        
        self.keywordEntry.insert(0,"Enter Keyword Here")
        
        self.keywordEntry2=self.controller.ttkEntryCreator(
            xpos=915, ypos=220, width=440, height=60, root=self, classname="keywordentry2")
        
        self.keywordEntry2.insert(0,"Enter Date Here")

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
                buttonFunction=lambda i = i: print(i)
            )
            initCoords = (initCoords[0], initCoords[1] + 120)
    
        # Button
        self.staticBtns = [
            (r"Assets\SearchView\Search.png", 660, 321, "postbtncreation", self,
             lambda: self.controller.widgetsDict["exampleofawordelement"].grid_remove()),
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

        #Entry
        self.nameEntry=self.controller.ttkEntryCreator(
            xpos=340, ypos=260, width=520, height=60, root=self.helpdeskFrame, classname="helpdeskframe")
        
        self.nameEntry.insert(0,"Enter Name Here")
        
        self.emailEntry=self.controller.ttkEntryCreator(
            xpos=1080, ypos=260, width=600, height=60, root=self.helpdeskFrame, classname="emailentry")
        
        self.emailEntry.insert(0,"Enter E-mail Here")
        
        #Scrolled Text
        self.scrolledtext = ScrolledText( master=self.helpdeskFrame, width=630, height=330,autohide=True)
        self.scrolledtext.place(x=222,y=402,width=630,height=330)
        self.textArea = self.scrolledtext.text 
        self.textArea.configure(font=(INTERBOLD,20))

   
       
def runGui():
    window = Window()
    window.mainloop()


if __name__ == "__main__":
    runGui()