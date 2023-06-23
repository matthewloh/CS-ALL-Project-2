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
        favoritesview.postLogin(data)
        # print(f"User email:{user.email}")
        # print(f"User Details:\n{user.json(indent=2)}")


class AnimatedStarButton(Canvas):
    def __init__(self, parent):
        Canvas.__init__(self, parent, width=54, height=50, bd=0,
                        highlightthickness=0, relief="ridge")
        self.parent = parent
        self.is_yellow = False  # Tracks the state of the star button

        # Load the star button images
        self.yellow_star_image = PhotoImage(
            file="Assets/FavoritesView/yellowstar.png")
        self.white_star_image = PhotoImage(
            file="Assets/FavoritesView/whitestar.png")

        # Create a button with the white star image
        self.star_button = self.create_image(30, 30, image=self.white_star_image,
                                             tags="star_button")
        self.tag_bind("star_button", "<Button-1>", self.toggle_star_color)

    def toggle_star_color(self, event):
        # Toggle the star color when the button is clicked
        self.is_yellow = not self.is_yellow
        if self.is_yellow:
            self.itemconfigure(self.star_button, image=self.yellow_star_image)
        else:
            self.itemconfigure(self.star_button, image=self.white_star_image)


class FavoritesView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=ORANGE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, ORANGE)
        self.staticImgs = [
            (r"Assets\FavoritesView\FavoritesViewBg.png", 0, 0, "favviewbg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")

        self.scrolledframe = ScrolledFrame(
            master=self, width=1680, height=580, autohide=True, bootstyle="bg-round"
        )
        self.scrolledframe.place(x=120, y=260, width=1680, height=580)

        # im = r"Assets\FavoritesView\Button.png"
        # _text = "Lab Work 1 Answer"
        # self.controller.textElement(imagepath=im, xpos=100, ypos=240, fg="#5975D7",
        #                             classname="exampleofawordelement", root=self, text=_text, size=34, font=INTERBOLD,
        #                             buttonFunction=lambda: self.controller.widgetsDict["exampleofawordelement"].grid_remove(
        #                             )
        #                             )

        # self.star_button = AnimatedStarButton(self)
        # self.star_button.place(x=1600, y=262)

    def postLogin(self, data: dict):
        self.prisma = self.controller.mainPrisma
        self.userId = data["id"]
        prisma = self.prisma
        # This returns a student
        user = prisma.userprofile.find_first(
            where={
                "email": "p21013568@student.newinti.edu.my"
            },
            include={
                "favoritePosts": {
                    "include": {
                        "author": True,
                        "module": True
                    }
                },
                "createdPosts": True,
                # If you are working with a student, this will return the field in the Student's table where the userid is found
                "lecturer": True,  # will return an empty list if the user is not a lecturer and vice versa
            }
        )
        favPosts = user.favoritePosts
        self.favPostList = []
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        timestrfmt = r"%A, %B %d %Y at %I:%M:%S %p"
        for favPost in favPosts:
            postModule = favPost.module
            postAuthor = favPost.author
            createdAt = kualalumpur.convert(favPost.createdAt).strftime(timestrfmt)
            postInfo = (
                favPost.id, favPost.title, 
                postAuthor.fullName,
                createdAt,
                postModule.moduleCode, postModule.moduleTitle,
            )
            self.favPostList.append(postInfo)
                
        IMAGEPATH = r"Assets\FavoritesView\Button.png"

        # Calculates the number of post, if heightofFrame needs to exceed 580:
        heightofFrame = len(self.favPostList) * 140
        if heightofFrame < 580:
            heightofFrame = 580
    
        self.scrolledframe.config(height=heightofFrame)

        initCoords = (20, 20)
        for post in self.favPostList:
            id, title, author, createdAt, moduleCode, moduleTitle = post
            fmttext = f"{title}\n{moduleCode} - {moduleTitle}"
            tipText = f"Created on {createdAt} by {author} in {moduleCode} - {moduleTitle}"
            t = self.controller.textElement(
                imagepath=IMAGEPATH, xpos=initCoords[0], ypos=initCoords[1], 
                classname=f"favpost{id}", root=self.scrolledframe,
                text=fmttext, fg="#5975D7", font=INTERBOLD, size=32,
                isPlaced=True, xoffset=-2, yIndex=-1/2
            )
            ToolTip(t, text=tipText, bootstyle=(INFO,INVERSE))
            AnimatedStarBtn(
                self.scrolledframe, xpos=initCoords[0]+1540, ypos=initCoords[1]+20,
                frameheight=60, framewidth=60,
                classname=f"favpost{id}star",
                prisma=self.controller.mainPrisma, postId=id, userId=self.userId,
                resizeWidth=60, resizeHeight=60,
                isPlaced=True, isFavorited=True,
            )
            initCoords = (initCoords[0], initCoords[1]+140)


def runGui():
    window = Window()
    window.mainloop()


if __name__ == "__main__":
    runGui()
