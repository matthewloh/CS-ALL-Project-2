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
from tkinter import filedialog

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

class Window(ttk.Window):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self, themename="minty", *args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}
        self.initializeWindow()
        self.frames = {}
        self.canvasInDashboard = {}
        self.prismaConnect()
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

    def prismaConnect(self):
        def connect():
            self.prisma = Prisma()
            self.prisma.connect()
        self.prismaThread = threading.Thread(target=connect, daemon=True)
        self.prismaThread.start()

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

    def signUpPage(self, student=False, teacher=False):
        ref = self.widgetsDict["postselectframebg"]
        # self.widgetsDict["backbutton"].grid()
        self.widgetsDict["skipbutton"].grid()
        if student:
            ref.configure(image=self.loadedImgs[0])
            self.studentform = UserForms(
                self.postSelectFrame, self, "studentreg")
            self.studentform.userReg()
            self.studentform.loadStudentReg()
        elif teacher:
            ref.configure(image=self.loadedImgs[1])
            self.teacherform = UserForms(
                self.postSelectFrame, self, "teacherreg")
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
                    self.widgetsDict["postselectframebg"].configure(
                        image=self.loadedImgs[0])
            except AttributeError:
                pass
            try:
                if self.teacherform:
                    self.teacherform.grid()
                    self.widgetsDict["teacherregcompleteregbutton"].grid()
                    self.widgetsDict["postselectframebg"].configure(
                        image=self.loadedImgs[1])
            except AttributeError:
                pass
            self.widgetsDict["signinform"].grid_remove()
            self.widgetsDict["backbutton"].configure(
                command=lambda: [
                    self.postSelectFrame.grid_remove(),
                ])
            self.widgetsDict["skipbutton"].grid()
            # self.widgetsDict["skipbutton"].configure(
            #     command=lambda: [
            #         self.loadSignIn(),
            #     ])
        self.widgetsDict["backbutton"].configure(
            command=lambda: [
                reloadForm(),
            ]
        )
        self.widgetsDict["skipbutton"].grid_remove()
        self.widgetsDict["skipbutton"].configure(
            command=lambda: [
                self.loadSignIn(),
            ]
        )

    def loadSignInPage(self):
        self.frameCreator(
            xpos=1140, ypos=240, framewidth=600, frameheight=600,
            root=self.postSelectFrame, classname="signinform",
        )
        self.signinformref = self.widgetsDict["signinform"]
        self.signInLabels = [
            (r"Assets\Login Page with Captcha\LoginForm.png",
             0, 0, f"loginformbg", self.signinformref),
        ]
        self.signInButtons = [
            (r"Assets\Login Page with Captcha\SignInButton.png", 120, 360, "signinbutton", self.signinformref,
             lambda: self.signInThreaded()),
            (r"Assets\Login Page with Captcha\GoToRegisterBtn.png", 40, 480, "gotoregisterbutton", self.signinformref,
             lambda: self.postSelectFrame.grid_remove()),
        ]
        self.userLoginEntries = [
            (60, 80, 480, 80, self.signinformref, "signinemail", "isEmail"),
            (60, 240, 480, 80, self.signinformref, "signinpassent", "isPassword"),
        ]

        self.settingsUnpacker(self.signInLabels, "label")
        self.settingsUnpacker(self.signInButtons, "button")
        for i in self.userLoginEntries:
            self.ttkEntryCreator(xpos=i[0], ypos=i[1], width=i[2],
                                 height=i[3], root=i[4], classname=i[5], validation=i[6])
        self.widgetsDict["signinpassent"].bind(
            "<Return>", lambda x: self.signInThreaded()
        )

    def signInThreaded(self):
        t = threading.Thread(target=self.signIn)
        t.daemon = True
        t.start()

    def validatePassword(self, password: str, encrypted: str) -> str:
        return bcrypt.checkpw(password.encode("utf-8"), encrypted.encode("utf-8"))

    def signIn(self):
        try:
            toast = ToastNotification(
                title="Signing in",
                message=f"Signing in...",
                bootstyle=INFO,
            )
            toast.show_toast()
            prisma = Prisma()
            prisma.connect()
            emailtext = self.widgetsDict["signinemail"].get()
            entrytext = self.widgetsDict["signinpassent"].get()
            user = prisma.userprofile.find_first(
                where={
                    "email": emailtext
                },
                include={
                    "student": True,
                    "lecturer": True,
                }
            )
            isTeacher = False
            isStudent = False
            if user.student == []:
                isTeacher = True
            else:
                isStudent = True

            validated = self.validatePassword(
                password=entrytext, encrypted=user.password)

            if not validated:
                toast.hide_toast()
                toast = ToastNotification(
                    title="Error",
                    message=f"Incorrect password",
                    duration=3000,
                )
                toast.show_toast()
                return
            print("Is teacher? ", isTeacher, "or is Student?", isStudent)
            if isStudent:
                student, moduleenrollments = self.setUserContext(
                    userId=user.id, role="student", prisma=prisma)
                modulesOfStudent = []
                lecturerinfo = []
                for i in range(len(moduleenrollments)):
                    mod = moduleenrollments[i]
                    module = mod.module
                    modtup = (module.moduleCode,
                              module.moduleTitle, module.moduleDesc)
                    modulesOfStudent.append(modtup)
                    try:
                        lecinfo = module.lecturer.userProfile
                        lecinfo = (lecinfo.fullName, lecinfo.email,
                                   lecinfo.contactNo)
                    except AttributeError:
                        print(
                            f"No lecturer for {module.moduleCode, module.moduleTitle}")
                        lecinfo = ("No lecturer", "No lecturer", "No lecturer")
                    lecturerinfo.append(lecinfo)
                data = {
                    "id": student.userProfile.id,
                    "fullName": student.userProfile.fullName,
                    "email": student.userProfile.email,
                    "modules": modulesOfStudent,
                    "lecturerinfo": lecturerinfo,
                    "role": "student",
                }
            elif isTeacher:
                lecturer, modules = self.setUserContext(
                    userId=user.id, role="lecturer", prisma=prisma)
                modulesOfLecturer = []
                studentinfo = []
                for mod in modules:
                    modtup = (mod.moduleCode, mod.moduleTitle, mod.moduleDesc)
                    modulesOfLecturer.append(modtup)
                    for me in mod.moduleEnrollments:
                        studentinfo.append(
                            (me.student.userProfile.fullName,
                             me.student.userProfile.email,
                             me.student.userProfile.contactNo)
                        )
                data = {
                    "id": lecturer.userProfile.id,
                    "fullName": lecturer.userProfile.fullName,
                    "email": lecturer.userProfile.email,
                    "modules": modulesOfLecturer,
                    "studentinfo": studentinfo,
                    "role": "lecturer",
                }
            toast.hide_toast()
            toast = ToastNotification(
                title="Success",
                message=f"Successfully logged in as {user.fullName}",
                duration=3000,
                bootstyle=SUCCESS,
            )
            toast.show_toast()
            self.show_frame(Dashboard)
            self.show_canvas(DashboardCanvas)
            dashboard = self.widgetsDict["dashboard"]
            dashboard.loadSpecificAssets(data["role"])
            dashboard.postLogin(data)
            favoritesview = self.widgetsDict["favoritesview"]
            favoritesview.postLogin(data, prisma)
        # prisma.disconnect()
        except Exception as e:
            print(e)

    def createImageReference(self, imagepath: str, classname: str):
        # stores a key value pair of "classname" : "imagepath"
        self.imagePathDict[classname] = imagepath
        # creates a Tkinter image object
        image = ImageTk.PhotoImage(Image.open(imagepath))
        # stores a key value pair of "classname" : "image" to prevent garbage collection
        self.imageDict[classname] = image

    def updateWidgetsDict(self, root: Frame):
        for widgetname, widget in self.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.parentFrame.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in self.postSelectFrame.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        for widgetname, widget in root.children.items():
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text)) and not widgetname.startswith("!la"):
                self.widgetsDict[widgetname] = widget
        try:
            for widgetname, widget in self.get_page(Dashboard).children.items():
                if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text)) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass
        try:
            for widgetname, widget in self.widgetsDict["maincanvas"].children.items():
                if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text)) and not widgetname.startswith("!la"):
                    self.widgetsDict[widgetname] = widget
        except:
            pass

    def tupleToDict(self, tup):  # TODO: make this multipurpose
        if len(tup) == 5:
            return dict(zip(("imagepath", "xpos", "ypos", "classname", "root"), tup))
        if len(tup) == 6:
            return dict(zip(("imagepath", "xpos", "ypos", "classname", "root", "buttonFunction"), tup))

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

    def buttonCreator(self, imagepath, xpos, ypos, classname=None, buttonFunction=None, root=None, relief=SUNKEN, overrideRelief=FLAT, pady=None, hasImage=True, bg=WHITE, isPlaced=False):
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
        if isPlaced:
            placedwidth = int(image.width())
            placedheight = int(image.height())
        button = Button(
            root, image=image, command=lambda: buttonFunction(
            ) if buttonFunction else print(f"This is the {classname} button"),
            relief=relief if not overrideRelief else overrideRelief, bg=bg, width=1, height=1,
            cursor="hand2", state=NORMAL,
            name=classname, autostyle=False
        )
        if isPlaced:
            button.place(x=xpos, y=ypos, width=placedwidth,
                         height=placedheight)
        else:
            button.grid(row=rowarg, column=columnarg,
                        rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)

    def labelCreator(self, imagepath, xpos, ypos, classname=None, root=None, overrideRelief=FLAT, isPlaced=False):
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
        placedwidth = int(image.width())
        placedheight = int(image.height())
        label = Label(
            root, image=image, relief=FLAT, width=1, height=1,
            state=NORMAL, name=classname,
            autostyle=False,
        )
        if isPlaced:
            label.place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
        else:
            label.grid(row=rowarg, column=columnarg,
                       rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)

    def frameCreator(self, xpos, ypos, framewidth, frameheight, root=None, classname=None, bg=LIGHTYELLOW, relief=FLAT, imgSettings=None):
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)

        Frame(root, width=1, height=1, bg=bg, relief=relief, name=classname, autostyle=False,).grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
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

    def entryCreator(self, xpos, ypos, width, height, root=None, classname=None, bg=WHITE, relief=FLAT, fg=BLACK, textvariable=None, pady=None, font=("Avenir Next Medium", 16)):
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        self.updateWidgetsDict(root=root)
        Entry(root, bg=bg, relief=SOLID, font=font, fg=fg, width=1, name=classname, autostyle=False, textvariable=textvariable).grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW, pady=pady)
        self.updateWidgetsDict(root=root)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                widget.grid_propagate(False)

    def canvasCreator(self, xpos, ypos, width, height, root, classname=None, bgcolor=WHITE, imgSettings=None, relief=FLAT, isTransparent=False, transparentcolor=TRANSPARENTGREEN):
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        if imgSettings:
            listofimages = list(enumerate(imgSettings))
        Canvas(root, bg=bgcolor, highlightcolor=bgcolor, relief=FLAT, width=1, height=1, name=classname, highlightthickness=0, autostyle=False
               ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                gridGenerator(widget, widthspan, heightspan, bgcolor)
                widget.grid_propagate(False)
                if isTransparent:
                    hwnd = widget.winfo_id()  # TRANSPARENTGREEN IS the default colorkey
                    transparentcolor = self.hex_to_rgb(transparentcolor)
                    wnd_exstyle = win32gui.GetWindowLong(
                        hwnd, win32con.GWL_EXSTYLE)
                    new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
                    win32gui.SetWindowLong(
                        hwnd, win32con.GWL_EXSTYLE, new_exstyle)
                    win32gui.SetLayeredWindowAttributes(
                        hwnd, transparentcolor, 255, win32con.LWA_COLORKEY)
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

    def menubuttonCreator(self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), text=None, variable=None, listofvalues=None, command=None):
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
        # print(themename, classname)
        menustyle = ttk.Style().configure(
            style=themename, font=("Helvetica", 10),
            background="#F9F5EB", foreground=BLACK, bordercolor="#78c2ad",
            relief="raised"
        )
        self.frameCreator(xpos, ypos, width, height, root,
                          classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT)
        frameref = self.widgetsDict[f"{classname}hostfr"]
        menubutton = ttk.Menubutton(
            frameref, text=text.title(),
            style=themename,
            name=classname,
            # bootstyle=(DANGER)
        )
        menubutton.grid(row=0, column=0, rowspan=heightspan,
                        columnspan=widthspan, sticky=NSEW)
        menubtnmenu = Menu(
            menubutton, tearoff=0, name=f"{classname}menu",
            bg=LIGHTPURPLE, relief=FLAT, font=("Helvetica", 12),
        )
        for x in listofvalues:
            menubtnmenu.add_radiobutton(label=x, variable=variable, value=x,
                                        command=lambda: [command(), menubutton.config(text=variable.get())])
        menubutton["menu"] = menubtnmenu
        self.widgetsDict[menubutton["menu"]] = menubtnmenu
        self.widgetsDict[classname] = menubutton
        self.updateWidgetsDict(root=root)

    def ttkEntryCreator(self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), validation=False, passwordchar="*", isContactNo=False, isEmail=False):
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
        self.frameCreator(xpos, ypos, width, height, root,
                          classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT)

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

        frameref = self.widgetsDict[f"{classname}hostfr"]
        themename = f"{str(root).split('.')[-1]}.TEntry"
        ttk.Style().configure(
            style=themename, font=font, background=NICEBLUE, foreground=BLACK,
        )
        entry = ttk.Entry(frameref, bootstyle=PRIMARY,
                          name=classname, font=font, background=bgcolor)
        entry.grid(row=0, column=0, rowspan=heightspan,
                   columnspan=widthspan, sticky=NSEW)

        if validation == "isPassword":
            entry.config(show=passwordchar)
            add_regex_validation(
                widget=entry, pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$")
        elif validation == "isConfPass":
            entry.config(show=passwordchar)
            add_validation(widget=entry, func=validatePassword)
        elif validation == "isEmail":
            add_regex_validation(
                widget=entry, pattern="^[a-zA-Z0-9._%+-]+@(?:student\.newinti\.edu\.my|newinti\.edu\.my)$")
        elif validation == "isContactNo":
            add_regex_validation(
                widget=entry, pattern="^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$")
        else:
            # just not blank
            add_regex_validation(widget=entry, pattern="^.*\S.*$")
            pass

        self.widgetsDict[classname] = entry
        self.updateWidgetsDict(root=root)

    def webview2creator(self, xpos=None, ypos=None, framewidth=None, frameheight=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Avenir Next", 16), url=None):
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        classname = classname.lower().replace(" ", "")
        navigationbar = Frame(root, width=1, height=1,
                              bg=bgcolor, relief=FLAT, name=f"{classname}navbar")
        gridGenerator(navigationbar, widthspan, 3, WHITE)
        navigationbar.grid(row=rowarg-3, column=columnarg,
                           rowspan=3, columnspan=widthspan, sticky=NSEW)
        frame = WebView2(parent=root, width=1, height=1,
                         url=url, name=classname, bg=bgcolor)
        frame.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                   columnspan=widthspan, sticky=NSEW)
        # binding a callback button to go back in javascript

        def goBack():
            frame.evaluate_js("window.history.back();")
            defocus()
        # binding a callback button to go forward in javascript

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
            ctypes.windll.user32.SetForegroundWindow(
                ctypes.windll.kernel32.GetConsoleWindow())

        def gotoGoogle():
            self.widgetsDict[f"{classname}urlentry"].focus_set()
            frame.load_url("https://www.google.com/")
            defocus()
            ctypes.windll.user32.SetForegroundWindow(
                ctypes.windll.kernel32.GetConsoleWindow())

        def toggleFullscreen():
            frame.evaluate_js(
                "document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();")
            defocus()
            self.widgetsDict[f"{classname}urlentry"].focus_set()

        def defocus():
            # getting the current window using the window handle, then simulating a refocusing
            # frame.evaluate_js("document.activeElement.blur();")
            ctypes.windll.user32.SetForegroundWindow(
                ctypes.windll.kernel32.GetConsoleWindow())
            self.widgetsDict[f"{classname}urlentry"].focus_set()
            self.focus_set()

        self.buttonCreator(r"Assets\Chatbot\Backbutton.png", 0, 0, classname=f"{classname}backbutton",
                           buttonFunction=lambda: goBack(),
                           root=navigationbar)
        self.buttonCreator(r"Assets\Chatbot\Forwardbutton.png", 80, 0, classname=f"{classname}forwardbutton",
                           buttonFunction=lambda: goForward(),
                           root=navigationbar)
        self.entryCreator(160, 0, 760, 60, navigationbar, classname=f"{classname}urlentry",
                          bg=bgcolor)
        self.widgetsDict[f"{classname}urlentry"].insert(0, url)
        self.widgetsDict[f"{classname}urlentry"].bind(
            "<Return>", lambda event: getUrlandGo())
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

    def setUserContext(self, userId=None, role="student", prisma: Prisma = None):
        if role == "student":
            student = prisma.student.find_first(
                where={
                    "userProfile": {
                        "id": userId,
                    }
                },
                include={
                    "userProfile": True,
                    "modules": {
                        "include": {
                            "module": True,
                        }
                    }
                }
            )
            moduleenrollments = prisma.moduleenrollment.find_many(
                where={
                    "studentId": student.id
                },
                include={
                    "module": {
                        "include": {
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            }
                        }
                    }
                }
            )
            return student, moduleenrollments
        elif role == "lecturer":
            lecturer = prisma.lecturer.find_first(
                where={
                    "userProfile": {
                        "id": userId,
                    }
                },
                include={
                    "userProfile": True,
                }
            )
            modules = prisma.module.find_many(
                where={
                    "lecturerId": lecturer.id
                },
                include={
                    "moduleEnrollments": {
                        "include": {
                            "student": {
                                "include": {
                                    "userProfile": True
                                }
                            }
                        }
                    },
                }
            )
            for m in modules:
                for me in m.moduleEnrollments:
                    me.student.userProfile.fullName
            return lecturer, modules
        # prisma.disconnect()

    def textElement(self, imagepath, xpos, ypos, classname=None,
                    buttonFunction=None, root=None, relief=FLAT,
                    fg=BLACK, bg=WHITE, font=SFPRO,
                    text=None, size=40, isPlaced=False,
                    index=0, xoffset=0):
        classname = classname.replace(" ", "").lower()
        # ~~~ ADD TEXT TO IMAGE FUNCTIONS ~~~
        h = fg.lstrip("#")
        textcolor = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        im = Image.open(imagepath)
        font = ImageFont.truetype(font, size)
        draw = ImageDraw.Draw(im)
        # print(im.size) # Returns (width, height) tuple
        xcoord, ycoord = im.size
        # push the text to the right by xoffset pixels
        xcoord = im.size[0]/20 + xoffset*20
        y_offset = size * index  # Vertical offset based on font size and index
        ycoord = ycoord/2 - (font.getbbox(text)[3]/2) + y_offset
        draw.text((xcoord, ycoord), text, font=font, fill=textcolor)
        self.imageDict[f"{classname}"] = ImageTk.PhotoImage(im)
        image = self.imageDict[f"{classname}"]
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        widthspan = int(image.width()/20)
        heightspan = int(image.height()/20)
        columnarg = int(xpos/20)
        rowarg = int(ypos/20)
        placedwidth = int(widthspan*20)
        placedheight = int(heightspan*20)

        if buttonFunction:
            if isPlaced:
                Button(root, image=image, cursor="hand2",
                       command=lambda: buttonFunction() if buttonFunction else print(
                           "No function assigned to button"),
                       relief=relief,
                       bg=bg, width=1, height=1, name=classname, autostyle=False).place(
                    x=xpos, y=ypos, width=placedwidth, height=placedheight
                )
            else:
                Button(root, image=image, cursor="hand2",
                       command=lambda: buttonFunction() if buttonFunction else print(
                           "No function assigned to button"),
                       relief=relief,
                       bg=bg, width=1, height=1, name=classname, autostyle=False).grid(
                    row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
                )
        else:
            if isPlaced:
                Label(root, image=image, relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False).place(
                    x=xpos, y=ypos, width=placedwidth, height=placedheight
                )
            else:
                Label(root, image=image, relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False).grid(
                    row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
                )
        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)
        return self.widgetsDict[classname]

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

    def loadSpecificAssets(self, role):
        self.controller.widgetsDict["dashboardcanvas"].tk.call(
            'raise', self.controller.widgetsDict["dashboardcanvas"]._w)
        if role == "student":
            self.controller.labelCreator(
                r"Assets\Dashboard\StudentDashboard.png", 0, 0,
                classname="StudentDashboardLabel", root=self.dashboardcanvasref)
        elif role == "lecturer":
            self.controller.labelCreator(r"Assets\Dashboard\TeacherDashboard.png", 0, 0,
                                         classname="TeacherDashboardLabel", root=self.dashboardcanvasref)
        self.gif = AnimatedGif(
            parent=self.controller.widgetsDict["dashboardcanvas"], controller=self.controller,
            xpos=180, ypos=460, bg="#344557",
            framewidth=400, frameheight=300, classname="cutebunny",
            imagepath=r"Assets\bunnygifresized400x300.gif", imagexpos=0, imageypos=0)

    def postLogin(self, data: dict, prisma: Prisma = None):
        role = data["role"]
        id = data["id"]
        fullName = data["fullName"]
        email = data["email"]
        modules = data["modules"]
        # modules = [(moduleCode, moduleTitle, moduleDesc), (moduleCode, moduleTitle, moduleDesc), (moduleCode, moduleTitle, moduleDesc)]
        cont = self.controller
        initialypos = 20
        print(f"The modules are {modules}")
        for m in modules:
            cont.textElement(
                imagepath=r"Assets\Dashboard\coursetitlebg.png", xpos=760, ypos=initialypos,
                classname=f"{m[0]}title", root=self.dashboardcanvasref, text=m[1], size=28, xoffset=-1,
                buttonFunction=lambda e=m[0]: print(f"clicked {e}")
            )
            initialypos += 300
        cont.textElement(
            imagepath=r"Assets\Dashboard\NameBg.png", xpos=160, ypos=120,
            classname="usernamedash", root=self.dashboardcanvasref, text=fullName, size=32, xoffset=-1
        )
        cont.textElement(
            imagepath=r"Assets\Dashboard\NameBg.png", xpos=160, ypos=160,
            classname="useremaildash", root=self.dashboardcanvasref, text=email, size=24, xoffset=-1
        )

class DashboardCanvas(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1, bg=NICEBLUE,
                        name="dashboardcanvas", autostyle=False, relief=RAISED)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, NICEBLUE)
        self.staticImgs = [
            (r"Assets\Dashboard\bigangry.png", 0, 0, "bigangry", self),
            (r"Assets\Dashboard\StudentDashboard.png", 0, 0,
             "StudentDashboardLabel", self),
        ]
        self.controller.settingsUnpacker(self.staticImgs, "label")
        self.threader(self.emulateLoggingIn, (self.controller.prisma,))

    def threader(self, func, args):
        t = threading.Thread(target=func, args=args)
        t.start()

    def emulateLoggingIn(self, prisma: Prisma):
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
        # we segregate finding student info at login
        student = prisma.student.find_first(
            where={
                "userProfile": {
                    "is": {
                        "id": user.id
                    }
                }
            },
            include={
                "modules": {
                    "include": {
                        "module": {
                            "include": {
                                "lecturer": True
                            }
                        }
                    }
                },
                "appointments": True,
            }
        )
        # You can access the userprofile details like this
        # Single fields like email, fullName, contactNo
        infotup = (user.email, user.fullName, user.contactNo)
        # Where there could be multiple fields, like modules, favoritePosts, and posts
        # You can access them like this
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        for post in user.createdPosts:
            details = (
                post.title, post.content, kualalumpur.convert(
                    post.createdAt).strftime("%d/%m/%Y %H:%M:%S"
                                             ),
            )
            # print(details)
            # print(f"Post title:{post.title}")
            # print(f"Post content:{post.content}")
        data = {
            "id": user.id,
            "fullName": user.fullName,
            "email": user.email,
            "modules": [(mod.module.moduleCode, mod.module.moduleTitle, mod.module.moduleDesc) for mod in student.modules]
        }
        for k, v in data.items():
            print(f"{k}:{v}")
        favoritesview = self.controller.widgetsDict["favoritesview"]
        favoritesview.postLogin(prisma, data)
        # print(f"User email:{user.email}")
        # print(f"User Details:\n{user.json(indent=2)}")

class FavoritesView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=ORANGE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, ORANGE)
        self.name_entry = Entry(self)
        self.name_entry.place(x=9, y=8)
        self.name_entry.grid(row=60, column=10)
        self.staticImgs = [(r"Assets\SearchView\background.png", 0, 0, "favviewbg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")

        

        

def runGui():
    window = Window()
    window.mainloop()


if __name__ == "__main__":
    runGui()