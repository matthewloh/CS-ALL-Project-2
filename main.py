import time
from static import *
import ctypes
from ctypes import windll
import threading
from tkinter import *
from tkinter import messagebox
# A drop in replacement for ttk that uses bootstrap styles
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
from datetime import datetime, timedelta, timezone
# TODO: please stop formatting my imports you're breaking my code
# this contains my pywin32 imports, PIL imports, pythonnet
from nonstandardimports import *
import pendulum
from pendulum import timezone
from chatbot import Chatbot
load_dotenv()

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
        ttk.Window.__init__(self, themename="minty", *args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}
        self.initializeWindow()
        self.frames = {}
        self.canvasInDashboard = {}

        self.labelSettingsParentFrame = [
            (r"Assets\LandingPage\BackgroundImage.png",
             0, 0, "Background Image", self.parentFrame),
            (r"Assets\LandingPage\Landing Page Title.png",
             0, 0, "Title Label", self.parentFrame),
            (r"Assets\Login Page with Captcha\LoginPageTeachers.png",
             0, 0, "postselectframebg", self.postSelectFrame),
        ]
        self.loadedImgs = [
            ImageTk.PhotoImage(Image.open(
                r"Assets\Login Page with Captcha\LoginPageStudents.png")),
            ImageTk.PhotoImage(Image.open(
                r"Assets\Login Page with Captcha\LoginPageTeachers.png")),
            ImageTk.PhotoImage(Image.open(
                r"Assets/Login Page with Captcha/Sign In Page.png")),
        ]

        buttonSettingsPSF = [
            (r"Assets\LandingPage\Student Button.png", 1080, 320, "Student Button",
             self.parentFrame, lambda: self.signUpPage(student=True)),
            (r"Assets\LandingPage\Teacher Button.png", 240, 320, "Teacher Button",
             self.parentFrame, lambda: self.signUpPage(teacher=True)),
            (r"Assets\Login Page with Captcha\BackButtonComponent.png", 0, 40, "Back Button",
             self.postSelectFrame,
             lambda: self.postSelectFrame.grid_remove()),
            (r"Assets\LandingPage\GoFullScreen.png", 1620, 960, "GoFullScreenBtn", self.postSelectFrame,
             lambda: [self.togglethewindowbar()]),
            (r"Assets\Login Page with Captcha\Skip Button.png", 1680, 980, "Skip Button",
             self.postSelectFrame,
             lambda: [
                 # Uncomment this out and then comment out the three lines below to enable the sign in page
                 #  self.loadSignIn(),
                 self.show_frame(Dashboard),
                 self.show_canvas(DashboardCanvas),
                 self.get_page(Dashboard).loadSpecificAssets("student"),
             ])
        ]

        self.settingsUnpacker(self.labelSettingsParentFrame, "label")
        self.settingsUnpacker(buttonSettingsPSF, "button")

        self.openDevWindow()
        self.bind("<Configure>", self.resizeEvent)

        for F in (Dashboard, ):
            frame = F(parent=self.parentFrame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
            frame.grid_propagate(False)
            self.canvasCreator(0, 80, 1920, 920, root=frame, classname="maincanvas",
                               bgcolor=WHITE, isTransparent=True, transparentcolor=LIGHTYELLOW)
            self.updateWidgetsDict(frame)
            frame.grid_remove()
        for FRAME in (DashboardCanvas, SearchPage, Chatbot, LearningHub, CourseView, DiscussionsView, FavoritesView, AppointmentsView):
            canvas = FRAME(
                parent=self.widgetsDict["maincanvas"], controller=self)
            self.canvasInDashboard[FRAME] = canvas
            self.updateWidgetsDict(canvas)
            canvas.grid(row=0, column=0, columnspan=96,
                        rowspan=46, sticky=NSEW)
            canvas.grid_propagate(False)
            canvas.grid_remove()
        self.postSelectFrame.tkraise()
        self.loadSignInPage()
        ref = self.widgetsDict["postselectframebg"]
        ref.configure(image=self.loadedImgs[2])
        self.widgetsDict["backbutton"].grid_remove()
        # self.widgetsDict["skipbutton"].grid_remove()  # Comment to bypass login

        self.bind("<F11>", lambda e: self.togglethewindowbar())

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

    def signUpPage(self, student=False, teacher=False):
        ref = self.widgetsDict["postselectframebg"]
        self.widgetsDict["gofullscreenbtn"].grid_remove()
        self.widgetsDict["backbutton"].grid()
        self.widgetsDict["skipbutton"].grid()
        if student:
            ref.configure(image=self.loadedImgs[0])
            self.studentform = UserForms(
                self.postSelectFrame, self, "studentreg")
            # self.studentform.userReg()
            self.studentform.loadStudentReg()
        elif teacher:
            ref.configure(image=self.loadedImgs[1])
            self.teacherform = UserForms(
                self.postSelectFrame, self, "teacherreg")
            # self.teacherform.userReg()
            self.teacherform.loadLecturerReg()
        self.postSelectFrame.grid()
        self.postSelectFrame.tkraise()

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
            self.widgetsDict["gofullscreenbtn"].grid_remove()
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
        self.widgetsDict["gofullscreenbtn"].grid()

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
            self.prisma = Prisma()
            self.prisma.connect()
            emailtext = self.widgetsDict["signinemail"].get()
            entrytext = self.widgetsDict["signinpassent"].get()
            user = self.prisma.userprofile.find_first(
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
                    userId=user.id, role="student", prisma=self.prisma)
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
                    userId=user.id, role="lecturer", prisma=self.prisma)
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
                    "phone": lecturer.userProfile.contactNo,
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
            courseview = self.widgetsDict["courseview"]
            courseview.postLogin(data)
            discussionsview = self.widgetsDict["discussionsview"]
            discussionsview.postLogin(data, self.prisma)
            appointmentsview = self.widgetsDict["appointmentsview"]
            appointmentsview.postLogin(data, self.prisma)
        except Exception as e:
            print(e)

    def createImageReference(self, imagepath: str, classname: str):
        # stores a key value pair of "classname" : "imagepath"
        self.imagePathDict[classname] = imagepath
        # creates a Tkinter image object
        image = ImageTk.PhotoImage(Image.open(imagepath))
        # stores a key value pair of "classname" : "image" to prevent garbage collection
        self.imageDict[classname] = image

    def resize(self):
        # the ratio of 1080p to the current screen size TODO: add aspect ratio sensing
        currentdimensions = (self.winfo_width(), self.winfo_height())
        # print(f"Current dimensions: {currentdimensions}")
        # how many times larger is the screensize than the original 1920 x 1080
        ratio = (currentdimensions[0] / 1920,
                 currentdimensions[1] / 1080)
        # take the original imagepath and resize it to the current screen size, then store it in the imageDict
        # only resize when the currentdimensions changes
        # do not constantly loop over the imageDict resizing the images
        if currentdimensions != (1920, 1080):
            for key, imagepath in self.imagePathDict.items():
                orgimg = Image.open(imagepath)
                orgimgwidth, orgimgheight = orgimg.size
                print(
                    f"Original image dimensions: {orgimgwidth} x {orgimgheight}, {key}")
                newimgwidth, newimgheight = int(
                    orgimgwidth * ratio[0]), int(orgimgheight * ratio[1])
                print(
                    f"New image dimensions: {newimgwidth} x {newimgheight}, {key}")
                image = ImageTk.PhotoImage(Image.open(imagepath).resize(
                    (newimgwidth, newimgheight), Image.Resampling.LANCZOS))
                self.imageDict[key] = image
                try:
                    self.widgetsDict[key].configure(image=image)
                except KeyError:
                    pass
        else:
            pass

    def resizeEvent(self, event):
        self.eventId = None
        if not (str(event.widget).split(".")[-1].startswith("!label")):
            if len(str(event.widget).split(".")) < 3:
                if event.widget == self:
                    self.resizeDelay = 100
                    if self.eventId:
                        self.after_cancel(self.eventId)
                    if self.state() == "zoomed":
                        self.eventId = self.after(
                            self.resizeDelay, self.resize)
                    elif self.state() == "normal":
                        self.eventId = self.after(
                            self.resizeDelay, self.resize)

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
                print(widget.winfo_parent(),
                      widget.winfo_class(), widget.winfo_name())
        # self.developerkittoplevel.attributes("-topmost", True)
        self.settingsUnpacker(
            [(r"Assets\DeveloperKit\BG.png", 0, 0, "DevKitBG", self.developerkittoplevel)], "label")
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
        self.entryCreator(40, 120, 360, 80, root=self.developerkittoplevel,
                          classname="DevKitEntryGreen", bg="light green")
        self.entryCreator(40, 320, 360, 80, root=self.developerkittoplevel,
                          classname="DevKitEntryOrange", bg=ORANGE)

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

    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
        canvas.focus_set()
        canvas.focus_force()

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
        return self.widgetsDict[classname]

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

    def hex_to_rgb(self, hexstring):
        # Convert hexstring to integer
        hexint = int(hexstring[1:], 16)
        # Extract Red, Green, and Blue values from integer using bit shifting
        red = hexint >> 16
        green = (hexint >> 8) & 0xFF
        blue = hexint & 0xFF
        colorkey = win32api.RGB(red, green, blue)
        return colorkey

    # DATABASE FUNCTIONS
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

    def textElement(self, imagepath, xpos, ypos, classname=None, buttonFunction=None, root=None, relief=FLAT, fg=BLACK, bg=WHITE, font=SFPRO, text=None, size=40, isPlaced=False, index=0, xoffset=0):
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
                Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                       relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                       ).place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
            else:
                Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                       relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                       ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        else:
            if isPlaced:
                Label(root, image=image, relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                      ).place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
            else:
                Label(root, image=image, relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                      ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)

        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)
        return self.widgetsDict[classname]


class AnimatedGif(Frame):
    def __init__(self, parent=None, controller: Window = None,
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
        self.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                  columnspan=widthspan, sticky=NSEW)
        # open the GIF and create a cycle iterator
        file_path = Path(__file__).parent / imagepath
        with Image.open(file_path) as im:
            # create a sequence
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.image_cycle = cycle(images)
            # length of each frame
            self.framerate = im.info["duration"]
        # getting the width and height of the image
        imagetogetdetails = ImageTk.PhotoImage(Image.open(file_path))
        self.imgwidth = imagetogetdetails.width()
        self.imgheight = imagetogetdetails.height()
        imgrow = int(imageypos / 20)
        imgcolumn = int(imagexpos / 20)
        imgrowspan = int(self.imgheight / 20)
        imgcolumnspan = int(self.imgwidth / 20)
        self.img_container = Label(self, image=next(
            self.image_cycle), width=1, bg="#344557")
        self.img_container.grid(
            column=imgcolumn, row=imgrow, columnspan=imgcolumnspan, rowspan=imgrowspan, sticky=NSEW)
        self.after(self.framerate, self.next_frame)
        self.controller.widgetsDict[classname] = self

    def next_frame(self):
        """Update the image for each frame"""
        try:
            self.img_container.configure(image=next(self.image_cycle))
            self.after(self.framerate, self.next_frame)
        except:
            # happens because when switching from student to lecturer, a new animatedgifinstance is created and the old one is destroyed
            print("gif error i will fix one day surely")


class UserForms(Frame):
    def __init__(self, parent=None, controller: Window = None, name=None):
        super().__init__(parent, width=1, height=1, bg="#344557", name=name)
        self.controller = controller
        self.parent = parent
        self.name = name

    def tupleToDict(self, tup):
        if len(tup) == 6:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname"], tup))
        elif len(tup) == 7:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname", "validation"], tup))

    def userReg(self):
        self.controller.frameCreator(
            xpos=1000, ypos=40, framewidth=800, frameheight=920,
            root=self.parent, classname=f"{self.name}",
        )
        self.frameref = self.controller.widgetsDict[f"{self.name}"]
        self.imgLabels = [
            (r"Assets\Login Page with Captcha\Sign Up Form.png",
             0, 0, f"{self.name}BG", self.frameref),
        ]
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, f"{self.name}fullname"),
            (40, 220, 720, 60, self.frameref, f"{self.name}email", "isEmail"),
            (40, 320, 340, 60, self.frameref,
             f"{self.name}passent", "isPassword"),
            (40, 480, 340, 60, self.frameref,
             f"{self.name}confpassent", "isConfPass"),
            (420, 320, 340, 60, self.frameref,
             f"{self.name}contactnumber", "isContactNo"),
            (420, 500, 340, 40, self.frameref, f"{self.name}captcha"),
        ]

    def loadLecturerReg(self):
        self.userReg()
        self.imgLabels.append(
            (r"Assets\Login Page with Captcha\LecturerForm.png",
             0, 600, f"{self.name}lecturer", self.frameref)
        )
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        # implementing the joining of the two lists
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOC", "SOE", "CEPS", "SOBIZ"],
            "tenure": ["FULLTIME", "PARTTIME"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture and Networks", "Object-Oriented Programming", "Mathematics for Computer Science", "Computer Science Activity Led Learning Project 2", ""],
            "course2": ["Computer Architecture and Networks", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning Project 2", ""],
            "course3": ["Computer Architecture and Networks", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning Project 2", ""]
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
                variable=vars[name], font=("Helvetica", 10), command=lambda name=name: [print(vars[name].get())]
            )
        entries = {
            "fullname": self.controller.widgetsDict[f"{self.name}fullname"],
            "email": self.controller.widgetsDict[f"{self.name}email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict[f"{self.name}contactnumber"],
            "captcha": self.controller.widgetsDict[f"{self.name}captcha"]
        }

        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
                                      buttonFunction=lambda: [
                                          print("validate")],
                                      pady=5)

        self.controller.buttonCreator(
            r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
            classname=f"{self.name}completeregbutton", buttonFunction=lambda: self.send_data(
                data={
                    "fullName": entries["fullname"].get(),
                    "email": entries["email"].get(),
                    "password": self.encryptPassword(entries["password"].get()),
                    "contactNo": entries["contactnumber"].get(),
                    "tenure": vars['tenure'].get(),
                    "institution": vars['institution'].get(),
                    "school": vars['school'].get(),
                    "programme": vars['programme'].get(),
                    "currentCourses": [f"{vars['course1'].get()}", f"{vars['course2'].get()}", f"{vars['course3'].get()}"],
                    "role": "LECTURER"
                }
            ),
            root=self.parent
        )
        self.completeregbutton = self.controller.widgetsDict[f"{self.name}completeregbutton"]
        # self.completeregbutton.config(state=DISABLED)

    def loadStudentReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\StudentForm.png",
                              0, 600, f"{self.name}Student", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOC", "SOE", "CEPS", "SOBIZ", "Unlisted"],
            "session": ["APR2023", "AUG2023", "JAN2024", "APR2024", "AUG2025"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture and Networks", "Object-Oriented Programming", "Mathematics for Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course2": ["Computer Architecture and Networks", "Object-Oriented Programming", "Mathematics for Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course3": ["Computer Architecture and Networks", "Object-Oriented Programming", "Mathematics for Computer Science", "Computer Science Activity Led Learning 2", "None"]
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
                listofvalues=values, variable=vars[name], font=(
                    "Helvetica", 10),
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

        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
                                      buttonFunction=lambda: [
                                          print("validate")],
                                      pady=5)
        self.controller.buttonCreator(
            r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
            classname=f"{self.name}completeregbutton", buttonFunction=# lambda: messagebox.showinfo("success", f"this is the button for {self.name}"),
            lambda: self.send_data(
                data={
                    "fullName": entries["fullname"].get(),
                    "email": entries["email"].get(),
                    "password": self.encryptPassword(entries["password"].get()),
                    "contactNo": entries["contactnumber"].get(),
                    "currentCourses": [f"{vars['course1'].get()}", f"{vars['course2'].get()}", f"{vars['course3'].get()}"],
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

    def prismaFormSubmit(self,  data: dict):
        # LECTURER OR STUDENT
        prisma = Prisma()
        try:
            if data["role"] == "STUDENT":
                school = prisma.school.find_first(
                    where={
                        "schoolCode": data["school"]
                    }
                )
                prisma.moduleenrollment.delete_many(
                    where={
                        "student": {"is": {"userProfile": {"is": {"email": data["email"]}}}}})
                prisma.student.delete_many(
                    where={
                        "userProfile": {"is": {"email": data["email"]}}})
                prisma.userprofile.delete_many(
                    where={
                        "email": data["email"]
                    }
                )
                student = prisma.student.create(
                    data={
                        "userProfile": {
                            "create": {
                                "fullName": data["fullName"],
                                "email": data["email"],
                                "password": data["password"],
                                "contactNo": data["contactNo"],
                            }
                        },
                        "school": {
                            "connect": {
                                "id": school.id
                            }
                        },
                        "session": data["session"],
                    }
                )
                modulestoenroll = []
                for module in data["currentCourses"]:
                    module = prisma.module.find_first(
                        where={
                            "moduleTitle": module
                        }
                    )
                    modulestoenroll.append(module.id)
                for i in range(len(modulestoenroll)):
                    student = prisma.student.find_first(
                        where={
                            "userProfile": {
                                "is": {
                                    "email": data["email"]
                                }
                            }
                        }
                    )
                    update = prisma.student.update(
                        where={
                            "id": student.id
                        },
                        data={
                            "modules": {
                                "create": {
                                    "enrollmentGrade": 0,
                                    "moduleId": modulestoenroll[i]
                                }
                            }
                        },
                        include={
                            "userProfile": True,
                            "modules": True,
                        }
                    )
                welcomemessage = f"Welcome, {update.userProfile.fullName}!"
                toast = ToastNotification(
                    title="Success",
                    message=welcomemessage,
                    duration=3000
                )
                toast.show_toast()
                self.gif.grid_forget()
            elif data["role"] == "LECTURER":
                school = prisma.school.find_first(
                    where={
                        "schoolCode": data["school"]
                    }
                )
                modules = prisma.module.find_many(
                    where={
                        "lecturer": {
                            "is": {
                                "userProfile": {
                                    "is": {
                                        "email": data["email"]
                                    }
                                }
                            }
                        }
                    }
                )
                for module in modules:
                    if modules == "":
                        continue
                    prisma.module.update(
                        where={
                            "id": module.id
                        },
                        data={
                            "lecturer": {
                                "disconnect": True
                            }
                        }
                    )
                prisma.userprofile.delete_many(
                    where={
                        "email": data["email"]
                    }
                )
                lecturer = prisma.lecturer.create(
                    data={
                        "userProfile": {
                            "create": {
                                "fullName": data["fullName"],
                                "email": data["email"],
                                "password": data["password"],
                                "contactNo": data["contactNo"],
                                "isAdmin": True,
                            }
                        },
                        "school": {
                            "connect": {
                                "id": school.id
                            }
                        },
                        "tenure": data["tenure"],
                    }
                )
                for modules in data["currentCourses"]:
                    if modules == "":
                        continue
                    module = prisma.module.find_first(
                        where={
                            "moduleTitle": modules
                        }
                    )
                    newmodule = prisma.module.update(
                        where={
                            "id": module.id
                        },
                        data={
                            "lecturer": {
                                "connect": {
                                    "id": lecturer.id
                                }
                            }
                        },
                        include={
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            },
                            "moduleEnrollments": {
                                "include": {
                                    "student": {
                                        "include": {
                                            "userProfile": {
                                                "include": {
                                                    "student": True
                                                }
                                            }
                                        }
                                    },
                                }
                            },
                        }
                    )
                print(f"Lecturer:\n{lecturer.json(indent=2)}\n")
                print(f"Modules:\n{newmodule.json(indent=2)}\n")
                toast = ToastNotification(
                    title="Success",
                    message=f"{newmodule.json(indent=2), lecturer.json(indent=2)}",
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
        self.controller.loadSignIn()

    def send_data(self, data: dict):
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

    def loadSignIn(self):
        self.controller.loadSignInPage()
        self.controller.widgetsDict["signinform"].tkraise()


class SlidePanel(Frame):
    def __init__(self, parent=None, controller: Window = None, startcolumn=0, startrow=0, endrow=0, endcolumn=0, startcolumnspan=0, endcolumnspan=0, rowspan=0, columnspan=0, relief=FLAT, width=1, height=1, bg=TRANSPARENTGREEN, name=None):
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
        self.staticImgBtns = [
            (r"Assets\Dashboard\01DashboardChip.png", 20, 1020, "DashboardChip",
             self.framereference, lambda: self.controller.show_canvas(DashboardCanvas)),
            (r"Assets\Dashboard\02SearchChip.png", 160, 1020, "SearchChip",
             self.framereference, lambda: [self.controller.show_canvas(SearchPage),]),
            (r"Assets\Dashboard\03ChatbotChip.png", 300, 1020, "ChatbotChip", self.framereference,
                lambda: [self.controller.show_canvas(Chatbot), self.chatbottoast.show_toast()]),
            (r"Assets\Dashboard\04LearningHubChip.png", 440, 1020, "LearningHubChip",
             self.framereference, lambda: self.controller.show_canvas(LearningHub)),
            (r"Assets\Dashboard\05MyCoursesChip.png", 580, 1020, "MyCoursesChip",
             self.framereference, lambda: self.controller.show_canvas(CourseView)),
            (r"Assets\Dashboard\06MyDiscussionsChip.png", 720, 1020, "MyDiscussionsChip",
             self.framereference, lambda: self.controller.show_canvas(DiscussionsView)),
            (r"Assets\Dashboard\07MyFavoritesChip.png", 860, 1020, "MyFavoritesChip",
             self.framereference, lambda: self.controller.show_canvas(FavoritesView)),
            (r"Assets\Dashboard\08MyAppointmentsChip.png", 1000, 1020, "MyAppointmentsChip",
             self.framereference, lambda: self.controller.show_canvas(AppointmentsView)),
        ]
        self.chatbottoast = ToastNotification(
            title="You have entered the webbrowser view",
            message="You will not be able to use the keyboard for the application until you exit the webbrowser view. You can exit the webbrowser view by clicking the exit button on the top right corner of the webbrowser view.",
            duration=3000,
        )
        self.controller.canvasCreator(0, 80, 1920, 920, root=self.framereference, classname="maincanvas",
                                      bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.maincanvasref = self.controller.widgetsDict["maincanvas"]
        self.controller.canvasCreator(0, 0, 1920, 920, root=self.maincanvasref, classname="dashboardcanvas",
                                      bgcolor=NICEBLUE, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.dashboardcanvasref = self.controller.widgetsDict["dashboardcanvas"]
        self.controller.settingsUnpacker(self.staticImgBtns, "button")

    def loadSpecificAssets(self, role):
        self.controller.widgetsDict["dashboardcanvas"].tk.call(
            'raise', self.controller.widgetsDict["dashboardcanvas"]._w)
        if role == "student":
            self.controller.labelCreator(r"Assets\Dashboard\StudentDashboard.png", 0, 0,
                                         classname="StudentDashboardLabel", root=self.dashboardcanvasref)
        elif role == "lecturer":
            self.controller.labelCreator(r"Assets\Dashboard\TeacherDashboard.png", 0, 0,
                                         classname="TeacherDashboardLabel", root=self.dashboardcanvasref)
        # self.gif = AnimatedGif(
        #     parent=self.controller.widgetsDict["dashboardcanvas"], controller=self.controller,
        #     xpos=180, ypos=460, bg="#344557",
        #     framewidth=400, frameheight=300, classname="cutebunny",
        #     imagepath=r"Assets\bunnygifresized400x300.gif", imagexpos=0, imageypos=0)

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


class TopBar(Frame):
    def __init__(self, parent: Dashboard, controller: Window, name="topbarframe"):
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
                 self.controller.show_canvas(DashboardCanvas)
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


class DashboardCanvas(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1, bg=WHITE,
                        name="dashboardcanvas", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)


class SearchPage(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="searchpage", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Search Page",
                          font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96,
                       rowspan=5, sticky="nsew")


class LearningHub(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="learninghub", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\LearningHub\LearningHubBG.png", 0, 0, "LearningHubBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")


class CourseView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg="#F6F5D7", name="courseview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()
        self.canvas = self.controller.widgetsDict["coursescanvas"]

    def postLogin(self, data: dict, prisma: Prisma = None):
        modules = data["modules"]
        self.role = data["role"]
        if self.role == "student":
            lecturerinfo = data["lecturerinfo"]
            modulecodes = []
            for i in range(len(modules)):
                modulecode = modules[i][0]
                moduletitle = modules[i][1]
                moduledesc = modules[i][2]
                lecturername = lecturerinfo[i][0]
                lectureremail = lecturerinfo[i][1]
                lecturerphone = lecturerinfo[i][2]
                self.detailsCreator(modulecode, moduletitle, moduledesc,
                                    lecturername, lectureremail, lecturerphone)
                modulecodes.append(modulecode.lower())
            self.loadcoursebuttons(modulecodes)
        elif self.role == "lecturer":
            studentinfo = data["studentinfo"]
            modulecodes = []
            lecturername = data["fullName"]
            lectureremail = data["email"]
            lecturerphone = data["phone"]
            for i in range(len(modules)):
                modulecode = modules[i][0]
                moduletitle = modules[i][1]
                moduledesc = modules[i][2]
                modulecodes.append(modulecode.lower())
                self.detailsCreator(modulecode, moduletitle, moduledesc,
                                    lecturername, lectureremail, lecturerphone)
            for i in range(len(studentinfo)):
                studentname = studentinfo[i][0]
                studentemail = studentinfo[i][1]
                studentphone = studentinfo[i][2]
                print(studentname, studentemail, studentphone)
            # lecturer specific functions here like show student info
            # and upload course files and upload schedule
            self.loadcoursebuttons(modulecodes)

    def createFrames(self):
        self.controller.frameCreator(root=self,
                                     xpos=0, ypos=0,
                                     framewidth=1920, frameheight=920, classname="singlecourseviewframe"
                                     )
        self.mainframe = self.controller.widgetsDict["singlecourseviewframe"]
        self.controller.frameCreator(
            xpos = 0, ypos = 120, framewidth=1920, frameheight=800,
            root=self.mainframe, classname="viewuploadsframe"
        )
        self.viewUploadsFrame = self.controller.widgetsDict["viewuploadsframe"]
        self.staticImgLabels = [
            (r"Assets\My Courses\CoursesBG.png", 0, 0, "courseviewbg", self),
            (r"Assets\My Courses\loadedcoursebg.png",
             0, 0, "loadedcoursebg", self.mainframe),
            (r"Assets\My Courses\moduleuploadsbg.png", 0, 0, "moduleuploadsbg", self.viewUploadsFrame),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.canvasCreator(0, 100, 1920, 820, root=self,
                                      classname="coursescanvas", bgcolor="#F6F5D7",
                                      isTransparent=True, transparentcolor="#efefef"
                                      )
        self.viewUploadsFrame.grid_remove()

    def loadCourses(self, coursecode: str):
        self.canvas.grid_remove()
        self.mainframe.grid()
        self.mainframe.tkraise()
        buttonsList = [
            (r"Assets\My Courses\exitbutton.png", 1820, 20, "exitbutton",
            self.mainframe, lambda:[
                self.exitMainFrame(),
                self.focus_force()]),
            (r"Assets\My Courses\exituploadsview.png", 1780, 20, "exituploadsview",
            self.viewUploadsFrame, lambda:[
                self.exitUploadsView(),
                self.focus_force()]),
        ]

        self.controller.settingsUnpacker(buttonsList, "button")
        coursecode = coursecode.lower()
        staticBtns = ["checkschedule", "gotolearninghub",
                      "viewcoursefiles", "exitbutton"]
        self.viewUploadsFrame.grid_remove()
        for widgetname, widget in self.mainframe.children.items():
            if isinstance(widget, Label) and not widgetname.startswith("!la"):
                if not widgetname.startswith(f"{coursecode}") and not widgetname.startswith("loadedcoursebg"):
                    # print("Getting removed", widgetname)
                    widget.grid_remove()
                if widgetname.startswith(f"{coursecode}"):
                    # print("Getting loaded", widgetname)
                    widget.grid()
            if isinstance(widget, Button):
                if not widgetname.startswith(f"{coursecode}") and widgetname not in staticBtns:
                    # print("Getting removed", widgetname)
                    widget.grid_remove()
                if widgetname.startswith(f"{coursecode}"):
                    # print("Getting loaded", widgetname)
                    widget.grid()
    
    def detailsCreator(self, modulecode, moduletitle, moduledesc, lecturername, lectureremail, lecturerphone):
        tupleofinfo = (modulecode, moduletitle, moduledesc,
                       lecturername, lectureremail, lecturerphone)
        positions = [
            (f"{modulecode}_title", moduletitle, 60, -4, 20,
             20, r"Assets\My Courses\coursetitlebg.png"),
            (f"{modulecode}_lecname", lecturername, 32, -1, 220,
             240, r"Assets\My Courses\whitebgtextfield.png"),
            (f"{modulecode}_lecemail", lectureremail, 26, -1,
             220, 300, r"Assets\My Courses\whitebgtextfield.png"),
            (f"{modulecode}_lecphone", lecturerphone, 28, -1,
             220, 360, r"Assets\My Courses\whitebgtextfield.png")
        ]
        for classname, text, size, xoffset, xpos, ypos, imagepath in positions:
            self.controller.textElement(imagepath=imagepath, xpos=xpos, ypos=ypos,
                                        classname=classname, root=self.mainframe, text=text, size=size, xoffset=xoffset)

        buttons = [
            (f"{modulecode}checkschedule", r"Assets\My Courses\checklecschedule.png", 1060, 280,
             lambda m=(lectureremail): print(f"Check Schedule {m}")),
            (f"{modulecode}_gotolearninghub", r"Assets\My Courses\gotolearninghub.png", 1340, 280,
             lambda m=(modulecode): print(f"Go to Learning Hub {m}")),
            (f"{modulecode}_viewcoursefiles", r"Assets\My Courses\loadcoursefiles.png", 1620, 280,
             lambda m=(modulecode): self.loadModuleUploadsView(m)),
            (f"{modulecode}_discussions", r"Assets\My Courses\go_to_discussions.png", 700, 780,
             lambda: self.loadDiscussionsView(modulecode, moduletitle)),
        ]
        for classname, imagepath, xpos, ypos, buttonFunction in buttons:
            self.controller.buttonCreator(imagepath=imagepath, xpos=xpos, ypos=ypos,
                                          classname=classname, root=self.mainframe, buttonFunction=buttonFunction)
        self.controller.buttonCreator(imagepath=r"Assets\My Courses\go_to_discussions.png", xpos=700, ypos=780,
                                      classname=f"{modulecode}_discussions", root=self.mainframe, buttonFunction=lambda: self.loadDiscussionsView(modulecode, moduletitle))

    def exitMainFrame(self):
        self.mainframe.grid_remove()
        self.canvas.grid()

    def loadcoursebuttons(self, modulecodes: list = None):
        print(f"The modulecodes list is {modulecodes}")
        btnDict = {
            "int4004cem": (r"Assets\My Courses\CompArch.png", 40, 0,
                           "int4004cem", self.canvas, lambda: self.loadCourses("INT4004CEM")),
            "int4068cem": (r"Assets\My Courses\MathForCS.png", 40, 0,
                           "int4068cem", self.canvas, lambda: self.loadCourses("INT4068CEM")),
            "int4003cem": (r"Assets\My Courses\ObjectOP.png", 40, 0,
                           "int4003cem", self.canvas, lambda: self.loadCourses("INT4003CEM")),
            "int4009cem": (r"Assets\My Courses\ALL2.png", 40, 0,
                    "int4009cem", self.canvas, lambda: self.loadCourses("INT4009CEM")),
        }
        c = self.controller
        btnCount = 0
        yCount = 0
        for code in modulecodes:
            yCount += 1 if btnCount == 2 else 0  # increment yCount if btnCount reaches 2
            btnCount = btnCount if btnCount < 2 else 0
            c.buttonCreator(
                imagepath=btnDict[code][0],
                xpos=btnDict[code][1] + (btnCount * 1000),
                ypos=btnDict[code][2] + (yCount * 300),
                classname=btnDict[code][3],
                root=btnDict[code][4],
                buttonFunction=btnDict[code][5]
            )
            btnCount += 1
        try:
            for i in ["int4004cem", "int4068cem", "int4003cem", "int4009cem"]:
                if i not in modulecodes:
                    c.widgetsDict[i].grid_remove()
        except:
            pass
    def exitUploadsView(self):
        self.viewUploadsFrame.grid_remove()
        self.webview.grid_remove()
    def loadModuleUploadsView(self, modulecode):
        self.viewUploadsFrame.grid()
        self.viewUploadsFrame.tkraise()
        col = int(820/20)
        row = int(180/20)
        w = int(1060/20)
        h = int(580/20)
        defaulturl = r"https://newinti.edu.my/campuses/inti-international-college-penang/"
        self.webview = WebView2(parent=self.viewUploadsFrame, width=1, height=1,
            url=defaulturl)
        self.webview.grid(row=row, column=col, rowspan=h, columnspan=w, sticky=NSEW)
        print(f"Loading uploads for {modulecode}")
        urlbar = self.controller.entryCreator(
            xpos=820, ypos=120, width=980, height=40,
            root=self.viewUploadsFrame, classname=f"uploadssearchbar",
        )
        urlbar.insert(0, f"{defaulturl}")

        toast = ToastNotification(
            title="Focus was automatically regained",
            message="The focus was automatically regained to the search bar",
            duration=5000,
            bootstyle=INFO
        )
        # timer to reload the urlbar
        def regainFocus():
            if self.controller.focus_get() == None:
                urlbar.focus_force()
                toast.show_toast()
            self.viewUploadsFrame.after(15000, regainFocus)
        def updateUrlbar():
            if self.webview.get_url() != urlbar.get():
                urlbar.delete(0, END)
                urlbar.insert(0, f"{self.webview.get_url()}")
            self.viewUploadsFrame.after(100, updateUrlbar)
        updateUrlbar()
        regainFocus()
        # nvm this freezes the app lol
        # while True:
        #     urlbar.delete(0, END)
        #     urlbar.insert(0, f"{self.webview.get_url()}")
        #     time.sleep(0.5)
        

    def loadDiscussionsView(self, modulecode, moduletitle):
        toast = ToastNotification(
            title=f"Loading Discussions for {modulecode}",
            message="Please wait while we load the discussions for this module",
            bootstyle="info"
        )
        toast.show_toast()
        discview = self.controller.widgetsDict["discussionsview"]
        discview.callLoadLatestPosts(modulecode)
        toast.hide_toast()
        toast2 = ToastNotification(
            title=f"Discussions for {modulecode} loaded",
            message="The discussions for this module have been loaded",
            bootstyle="success",
            duration=500,
        )
        discview.creationframe.grid_remove()
        discview.postviewframe.grid_remove()
        discview.modulecodevar.set(modulecode)
        discview.menubutton.configure(text=f"{modulecode} - {moduletitle}")
        toast2.show_toast()
        self.controller.show_canvas(DiscussionsView)
class AnimatedStarBtn(Frame):
    def __init__(self,
                 parent=None, controller: Window = None,
                 xpos=0, ypos=0, framewidth=0, frameheight=0, isPlaced=False,
                 classname=None, imagexpos=0, imageypos=0, bg=WHITE,
                 prisma: Prisma = None, postId=None, userId=None,
                 isFavorited=False, postTitle=None):
        super().__init__(parent, width=1, bg=bg, autostyle=False, name=classname)
        self.controller = controller
        self.grid_propagate(False)
        self.postId = postId
        self.userId = userId
        self.prisma = prisma
        self.isFavorited = isFavorited
        self.postTitle = postTitle
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        self.configure(bg=bg)
        gridGenerator(self, widthspan, heightspan, bg)
        if isPlaced:
            self.place(x=xpos, y=ypos, width=framewidth, height=frameheight)
        else:
            self.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                      columnspan=widthspan, sticky=NSEW)

        file_path = Path(__file__).parent / \
            r"Assets\DiscussionsView\stargifs.gif"
        if self.isFavorited:
            with Image.open(file_path) as im:
                sequence = ImageSequence.Iterator(im)
                reversedsequence = [frame.copy() for frame in sequence]
                reversedsequence.reverse()
                self.images = [ImageTk.PhotoImage(
                    sequence_frame) for sequence_frame in reversedsequence]
                self.image_cycle = cycle(self.images)
                self.framerate = im.info['duration']
        else:
            with Image.open(file_path) as im:
                # sequence
                sequence = ImageSequence.Iterator(im)
                self.images = [ImageTk.PhotoImage(
                    sequence_frame) for sequence_frame in sequence]
                self.image_cycle = cycle(self.images)
                # length of each frame
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

        self.img_container = Button(self, image=next(self.image_cycle), width=1, bg="#344557", cursor="hand2",
                                    command=lambda: self.trigger_animation())

        if isPlaced:
            self.img_container.place(
                x=0, y=0, width=self.imgwidth, height=self.imgheight
            )
        else:
            self.img_container.grid(
                column=imgcolumn, row=imgrow, columnspan=imgcolumnspan, rowspan=imgrowspan, sticky=NSEW)
        self.animation_length = len(self.images)

        self.animation_status = StringVar(value="start")
        self.animation_status.trace('w', self.animate)

        # self.after(self.framerate, self.next_frame)
        if self.isFavorited:
            self.tooltip = ToolTip(
                self.img_container, f"Click to unfavorite {self.postTitle}", bootstyle=(DANGER, INVERSE))
        else:
            self.tooltip = ToolTip(
                self.img_container, f"Click to favorite {self.postTitle}", bootstyle=(INFO, INVERSE))

    def next_frame(self):
        self.img_container.configure(image=next(self.image_cycle))
        self.after(self.framerate, self.next_frame)

    def trigger_animation(self):
        if self.animation_status.get() == "start":
            self.frame_index = 0
            self.animation_status.set("forward")
            if self.isFavorited:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUnfavoritePost(userId=self.userId, postId=self.postId)
            else:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUpdateUser(userId=self.userId, postId=self.postId)
        if self.animation_status.get() == "end":
            self.frame_index = self.animation_length
            self.animation_status.set("backward")
            if self.isFavorited:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUpdateUser(userId=self.userId, postId=self.postId)
            else:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUnfavoritePost(userId=self.userId, postId=self.postId)

    def callUpdateUser(self, userId=None, postId=None):
        prisma = self.prisma

        def updateuser():
            toast = ToastNotification(
                title="Please be patient...",
                message="We are updating your favorite posts",
                bootstyle=(INFO)
            )
            toast.show_toast()
            userprofile = prisma.userprofile.update(
                where={
                    "id": userId
                },
                data={
                    "favoritePosts": {
                        "connect": {
                            "id": postId
                        }
                    }
                },
                include={
                    "favoritePosts": True
                }
            )
            toast.hide_toast()
            newtoast = ToastNotification(
                title="Success",
                message="Post added to your favorites",
                bootstyle=(SUCCESS),
                duration=500,
            )
            newtoast.show_toast()
            self.tooltip.hide_tip()
            self.tooltip = ToolTip(
                self.img_container, f"Click to unfavorite post {self.postTitle}", bootstyle=(DANGER, INVERSE))
            self.tooltip.show_tip()

        t = threading.Thread(target=updateuser)
        t.daemon = True
        t.start()

    def callUnfavoritePost(self, userId=None, postId=None):
        prisma = self.prisma

        def updateuser():
            toast = ToastNotification(
                title="Please be patient...",
                message="We are updating your favorite posts",
                bootstyle=(INFO)
            )
            userprofile = prisma.userprofile.update(
                where={
                    "id": userId
                },
                data={
                    "favoritePosts": {
                        "disconnect": {
                            "id": postId
                        }
                    }
                },
                include={
                    "favoritePosts": True
                }
            )
            toast.hide_toast()
            newtoast = ToastNotification(
                title="Success",
                message="Post removed from your favorites",
                bootstyle=(SUCCESS),
                duration=500,
            )
            newtoast.show_toast()
            self.tooltip.hide_tip()
            self.tooltip = ToolTip(
                self.img_container, f"Click to favorite {self.postTitle}", bootstyle=(INFO, INVERSE))
            self.tooltip.show_tip()
        t = threading.Thread(target=updateuser)
        t.daemon = True
        t.start()

    def animate(self, *args):
        if self.animation_status.get() == "forward":
            self.frame_index += 1
            self.img_container.configure(
                image=self.images[self.frame_index - 1])

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
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1, bg=WHITE,
                        name="discussionsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()
        self.creationframe = self.controller.widgetsDict["postcreation"]
        self.postviewframe = self.controller.widgetsDict["postview"]

        self.createElements()

        # self.creationframe.tkraise()
        self.controller.ttkEntryCreator(
            xpos=900, ypos=160, width=920, height=40, root=self.creationframe, classname="posttitleent"
        )
        textxpos, textypos, textcolumnspan, textrowspan = int(
            900/20), int(340/20), int(920/20), int(360/20)
        self.postcontenttext = Text(
            master=self.creationframe, width=1, height=1, font=("Helvetica", 18), wrap="word", name="postcontenttext"
        )
        self.postcontenttext.grid(
            column=textxpos, row=textypos, columnspan=textcolumnspan, rowspan=textrowspan, sticky=NSEW
        )

        self.creationframe.grid_remove()
        self.postviewframe.grid_remove()

    def createElements(self):
        self.staticImgLabels = [
            (r"Assets\DiscussionsView\DiscussionsViewBG.png",
             0, 0, "DiscussionsBG", self),
            (r"Assets\DiscussionsView\postcreationbg.png",
             0, 0, "postcreationbg", self.creationframe),
            (r"Assets\DiscussionsView\postviewbg.png",
             0, 0, "postviewbg", self.postviewframe),
        ]
        self.staticBtns = [
            (r"Assets\DiscussionsView\creatediscussion.png", 80, 120, "creatediscussionbtn", self,
             lambda: self.loadPostCreation()),
            (r"Assets\DiscussionsView\refreshbutton.png", 860, 220, "refreshbtn", self,
             lambda: self.callLoadLatestPosts(self.modulecodevar.get())),
            (r"Assets\DiscussionsView\cancelbuttondisc.png", 40, 760, "cancelbtncreation", self.creationframe,
             lambda: self.unloadPostCreation()),
            (r"Assets\DiscussionsView\createpostbuttondisc.png", 480, 760, "postbtncreation", self.creationframe,
             lambda: self.threadStart()),
            (r"Assets\My Courses\exitbutton.png", 1840, 0, "cancelbtnview", self.postviewframe,
             lambda: self.unloadPostView()),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def createFrames(self):
        self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="postcreation",
        )
        self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="postview",
        )
    # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors

    def loadPostCreation(self):
        self.creationframe.grid()
        self.creationframe.tkraise()
        self.controller.widgetsDict["posttitleent"].delete(0, END)
        self.postcontenttext.delete("1.0", END)
        self.controller.widgetsDict["posttitleent"].focus_set()
        self.controller.widgetsDict["posttitleent"].bind(
            "<Return>", lambda event: self.postcontenttext.focus_set()
        )

    def postLogin(self, data: dict = None, prisma: Prisma = None):
        self.prisma = prisma
        self.userId = data["id"]
        print(f"User ID: {self.userId}")
        # posts = self.prisma.modulepost.find_many(
        #     order={
        #         "createdAt": "desc"
        #     },
        #     take=2,
        #     include={
        #         "replies": {
        #             "include": {
        #                 "author": True
        #             }
        #         },
        #         "author": True,
        #         "favoritedBy": True,
        #     },
        # )
        # kualalumpur = timezone("Asia/Kuala_Lumpur")
        # for post in posts:
        #     print(
        #         f"Time of post: {kualalumpur.convert(post.createdAt).strftime(r'%A %B %e %Y %I:%M %p')}")
        #     print(f"Post:\n{post.json(indent=2)}")
        # for post in posts:
        #     # print(f"Post found:\n{post.json(indent=2)}, {post.id}")
        #     createdat = post.createdAt
        #     # string representation using Monday, 01 January 2021 00:00:00 would be %A, %d %B %Y %H:%M:%S
        #     formattedtime = kualalumpur.convert(
        #         createdat).strftime(r'%A %d %B %Y %H:%M:%S %z')
        #     # print("Local time in Malaysia", formattedtime)
        #     # print("UTC Time, from Prisma", post.createdAt.strftime(r'%A %d %B %Y %H:%M:%S %z'))
        #     # print("Current time:",datetime.now().strftime(r'%A %d %B %Y %H:%M:%S %z'))
        #     try:
        #         if len(post.replies) == 0:
        #             pass  # no posts
        #         for reply in post.replies:
        #             print(reply.author)
        #             print(reply.json(indent=2))
        #     except:
        #         print("no replies")
        postContentList = self.loadLatestPosts(prisma=self.prisma)
        self.controller.frameCreator(
            xpos=560, ypos=120, framewidth=400, frameheight=80, root=self,
            classname="modulecodeframe", bg=WHITE
        )
        self.frameref = self.controller.widgetsDict["modulecodeframe"]
        self.menubutton = ttk.Menubutton(
            self.frameref, text="INT4004CEM", name="modulecodemenubtn", style="info.TMenubutton"
        )
        self.menubutton.grid(column=0, row=0,
                             columnspan=int(400/20), rowspan=int(80/20), sticky=NSEW)
        self.menubuttonmenu = Menu(
            self.menubutton, tearoff=0, font=("Helvetica", 12))
        self.modulecodevar = StringVar()
        modules = prisma.module.find_many()
        listofvalues = []
        self.valueDict = {}
        for module in modules:
            self.valueDict[f"{module.moduleCode}"] = f"{module.moduleCode} - {module.moduleTitle}"
            listofvalues.append(module.moduleCode)
        for value in listofvalues:
            _text = self.valueDict[f"{value}"]
            self.menubuttonmenu.add_radiobutton(
                label=_text,
                variable=self.modulecodevar,
                value=value,
                command=lambda: [
                    self.menubutton.config(
                        text=self.valueDict[self.modulecodevar.get()]),
                    self.callLoadLatestPosts(self.modulecodevar.get()),
                ]
            )
        self.modulecodevar.set("INT4004CEM")
        self.menubutton["menu"] = self.menubuttonmenu
        self.menubutton.config(text=self.valueDict[self.modulecodevar.get()])
        heightofframe = len(postContentList) * 100
        # minimum height of frame is 500 for 5 posts
        if heightofframe < 500:
            rowspanofFrame = int(500/20)
        else:
            rowspanofFrame = int(heightofframe/20)

        self.postscrolledframe = ScrolledFrame(
            self, width=840, height=heightofframe, name="postsframescrollable", autohide=True,
        )
        gridGenerator(self.postscrolledframe, int(
            840/20), rowspanofFrame, WHITE)
        self.postscrolledframe.grid_propagate(False)
        self.postscrolledframe.place(x=100, y=320, width=840, height=500)
        self.loadDiscussionTopics(postContentList)
        print("In discussionview, userid is: ", self.userId)

    def threadStart(self):
        t = threading.Thread(target=self.createPost)
        self.gif = AnimatedGif(
            parent=self.creationframe, controller=self.controller,
            xpos=280, ypos=400, bg="#344557",
            framewidth=320, frameheight=320, classname="creatingpostspinner",
            imagepath=r"Assets\200x200spinner.gif", imagexpos=60, imageypos=60)
        t.daemon = True
        t.start()

    def createPost(self):
        # ~~~~ BACKEND FUNCTIONALITY ~~~~
        prisma = self.controller.prisma
        title = self.controller.widgetsDict["posttitleent"].get()
        content = self.postcontenttext.get("1.0", 'end-1c')
        findmodule = prisma.module.find_first(
            where={
                "moduleCode": self.modulecodevar.get()
            }
        )
        module = prisma.modulepost.create(
            data={
                "authorId": self.userId,
                "moduleId": findmodule.id,
                "title": title,
                "content": content,
            }
        )
        self.gif.grid_forget()
        postContentList = self.loadLatestPosts(
            prisma=prisma, moduleCode=self.modulecodevar.get())
        heightofframe = len(postContentList) * 100
        # minimum height of frame is 500 for 5 posts
        if heightofframe < 500:
            rowspanofFrame = int(500/20)
        else:
            rowspanofFrame = int(heightofframe/20)
        self.postscrolledframe = ScrolledFrame(
            self, width=840, height=heightofframe, name="postsframescrollable", autohide=True,
        )
        gridGenerator(self.postscrolledframe, int(
            840/20), rowspanofFrame, WHITE)
        self.postscrolledframe.grid_propagate(False)
        self.postscrolledframe.place(x=100, y=320, width=840, height=500)
        self.loadDiscussionTopics(postContentList)
        self.unloadPostCreation()

    def unloadPostCreation(self):
        self.creationframe.grid_remove()

    def loadDiscussionTopics(self, postidtitles: list = []):
        # ~~~~ BACKEND FUNCTIONALITY ~~~~
        # size of frame needed is postidtitles * 100, 80 for the post and 20 for the gap below
        heightframe = len(postidtitles) * 100
        self.postscrolledframe.configure(height=heightframe)
        initialcoordinates = (0, 0)
        for tupleofcontent in postidtitles:
            postId = tupleofcontent[0]
            discussiontitle = tupleofcontent[1]
            content = tupleofcontent[2]
            author = tupleofcontent[3]
            email = tupleofcontent[4]
            createdat = tupleofcontent[5]
            posteditedAt = tupleofcontent[6]
            repliesList = tupleofcontent[7]
            authorId = tupleofcontent[8]
            favoritedPostIds = tupleofcontent[9]
            imagepath = r"Assets\DiscussionsView\discussionstitlecomponentbg.png"
            xpos = initialcoordinates[0]
            ypos = initialcoordinates[1]
            cont = self.controller
            cont.textElement(
                imagepath=imagepath, xpos=xpos, ypos=ypos,
                classname=f"post{postId}title",
                buttonFunction=lambda num=tupleofcontent: self.loadPostView(
                    num),
                root=self.postscrolledframe, text=discussiontitle, fg=BLACK, size=28, xoffset=-1, isPlaced=True,
            )
            if postId in favoritedPostIds:
                AnimatedStarBtn(
                    parent=self.postscrolledframe, xpos=initialcoordinates[0] + 760,
                    ypos=initialcoordinates[1] + 20, frameheight=40, framewidth=40,
                    classname=f"post{postId}favoritestar", imagexpos=0, imageypos=0,
                    isPlaced=True, prisma=self.prisma, postId=postId, userId=self.userId,
                    isFavorited=True, postTitle=discussiontitle,
                )
            else:
                AnimatedStarBtn(
                    parent=self.postscrolledframe,
                    xpos=initialcoordinates[0] + 760,
                    ypos=initialcoordinates[1] + 20,
                    framewidth=40, frameheight=40, classname=f"post{postId}favoritestar",
                    imagexpos=0, imageypos=0, isPlaced=True,
                    prisma=self.prisma, postId=postId, userId=self.userId,
                    postTitle=discussiontitle,
                )
            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 100)

    def unloadPostView(self):
        self.postviewframe.grid_remove()

    def loadPostView(self, tupleofcontent: tuple = ()):
        self.postviewframe.grid()
        self.postviewframe.tkraise()
        postId = tupleofcontent[0]
        discussiontitle = tupleofcontent[1]
        content = tupleofcontent[2]
        author = tupleofcontent[3]
        email = tupleofcontent[4]
        createdat = tupleofcontent[5]
        posteditedAt = tupleofcontent[6]
        repliesList = tupleofcontent[7]
        authorId = tupleofcontent[8]

        self.controller.frameCreator(
            root=self.postviewframe, framewidth=1100, frameheight=660,
            classname="scrolledframehostframe", xpos=100, ypos=180, bg=NICEBLUE
        )
        self.scrolledframehost = self.controller.widgetsDict["scrolledframehostframe"]
        self.scrolledframe = ScrolledFrame(
            self.scrolledframehost, width=1, height=1, name="postviewcontent", autohide=True, padding=0,
        )
        self.scrolledframe.grid_propagate(False)
        self.scrolledframe.place(
            x=0, y=0, width=1100, height=660
        )
        # TITLE OF THE POST
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\titleofthepost.png", xpos=60, ypos=40,
            classname="titleofthepost", root=self.postviewframe, isPlaced=True,
            text=f"{discussiontitle}", fg=BLACK, size=34, xoffset=-2
        )
        # MODULE CODE
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\modulecode.png", xpos=100, ypos=120,
            classname="modulecode", root=self.postviewframe, isPlaced=True,
            text=f"SOC / BCSCU / {self.modulecodevar.get()}", fg=BLACK, size=36, xoffset=-1
        )
        # REFRESH BUTTON
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\refreshbutton.png", xpos=1160, ypos=20,
            classname="repliesrefreshbtn", root=self.postviewframe, isPlaced=True,
            buttonFunction=lambda: self.callLoadLatestReplies(
                postId, moduleCode=self.modulecodevar.get())
        )
        # PURPLE BG
        # Normal size is 1100 x 660
        self.controller.labelCreator(
            imagepath=r"Assets\DiscussionsView\scrolledframebg.png", xpos=0, ypos=0,
            classname="scrolledframebg", root=self.scrolledframe, isPlaced=True
        )
        totalheight = (1 + len(repliesList)) * 280
        numberofverticalsquares = int(totalheight/21)
        if totalheight > 660:
            gridGenerator(self.scrolledframe, int(int(1100/20)),
                          numberofverticalsquares, "#acbcff")
            image = self.controller.imagePathDict["scrolledframebg"]
            image = Image.open(image)
            image = image.resize((1100, totalheight),
                                 Image.Resampling.LANCZOS)
            self.controller.imageDict["scrolledframebg"] = ImageTk.PhotoImage(
                image)
            newimage = self.controller.imageDict["scrolledframebg"]
            self.controller.widgetsDict["scrolledframebg"].configure(
                image=newimage, bg=ORANGE)
            self.controller.widgetsDict["scrolledframebg"].place(
                x=0, y=0, width=1100, height=totalheight
            )
        else:
            gridGenerator(self.scrolledframe, int(
                1100/20), int(640/20), "#acbcff")
        # POST BG
        self.controller.labelCreator(
            imagepath=r"Assets\DiscussionsView\exampleofapost.png", xpos=0, ypos=0,
            classname="exampleofapost", root=self.scrolledframe, isPlaced=True,
            # buttonFunction=lambda: print(f"{tupleofcontent} was clicked")
        )
        # AUTHOR AND DATE
        timestrfmt = r'%A, %B %d %Y at %I:%M:%S %p'
        datetimestr = datetime.now().strftime(timestrfmt)
        if posteditedAt == createdat:
            authoranddatetext = f"{author} posted on {createdat}"
        else:
            timedelta = datetime.strptime(
                datetimestr, timestrfmt) - datetime.strptime(posteditedAt, timestrfmt)
            if timedelta.days > 0:
                timedelta = f"{timedelta.days} days"
            elif timedelta.seconds//3600 > 0:
                timedelta = f"{timedelta.seconds//3600} hours"
            elif timedelta.seconds//60 > 0:
                timedelta = f"{timedelta.seconds//60} minutes"
            elif timedelta.seconds < 60:
                timedelta = f"{timedelta.seconds} seconds"
            authoranddatetext = f"{author} posted on {createdat} (edited {timedelta} ago)"
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\fullnamepostedon.png", xpos=20, ypos=20,
            classname="fullnamepostedon", root=self.scrolledframe, isPlaced=True,
            text=authoranddatetext, fg=BLACK, size=22, xoffset=-2
        )
        # EMAIL OF AUTHOR
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\emailofauthor.png", xpos=20, ypos=60,
            classname="emailofauthor", root=self.scrolledframe, isPlaced=True,
            text=f"{email}", fg=BLACK, size=15, xoffset=0
        )
        # COMPONENTS OF A POST:
        # 1. POST TITLE -> a single text element label
        # 2. "Full Name posted on date" -> a single text element label
        # 3. The poster's email below it -> a single text element label
        # 4. The content of the post -> a text widget from tkinter, read only
        # 5. The replies are also text widgets, read only
        # 6. The reply button -> a button
        # 7. The favorite button -> a button
        # 8. Area to type a reply -> a text widget
        self.contenttext = Text(
            self.scrolledframe, width=1, height=1, bg=WHITE, fg=BLACK, font=("Arial", 20), wrap=WORD,
            name="contenttext", padx=20, pady=20, relief=FLAT, bd=0, highlightthickness=0,
        )
        self.contenttext.insert(END, content)
        self.contenttext.place(
            x=20, y=120, width=1060, height=120
        )
        self.contenttext.config(state=DISABLED)
        # buttons to delete and edit the post
        if self.userId == authorId:
            self.controller.buttonCreator(
                imagepath=r"Assets\DiscussionsView\edit.png", xpos=960, ypos=20,
                classname="editpost", root=self.scrolledframe, isPlaced=True,
                buttonFunction=lambda post=(
                    postId, None, self.modulecodevar.get(), "contenttext", True): self.editReplyorPost(*post)
            )
            self.controller.buttonCreator(
                imagepath=r"Assets\DiscussionsView\Trash.png", xpos=1020, ypos=20,
                classname="deletepost", root=self.scrolledframe, isPlaced=True,
                buttonFunction=lambda post=(
                    postId, None, self.modulecodevar.get(), True): self.deleteReplyorPost(*post)
            )
        # REPLIES under a post
        replycoordinates = (40, 280)
        authorCoordinates = (
            replycoordinates[0] + 20, replycoordinates[1] + 20)
        textCoordinates = (replycoordinates[0] + 20, replycoordinates[1] + 120)
        replycounter = 0
        participants = []
        # adding the author of the post to the participants set
        participants.append(author + " (AUTHOR)")
        for replies in repliesList:
            replyContent = replies[0]
            replyAuthor = replies[1]
            if replyAuthor not in participants and replyAuthor != author:
                participants.append(replyAuthor)
            repAuthorEmail = replies[2]
            repCreatedAt = replies[3]
            repEditedAt = replies[4]
            replyId = replies[5]
            repAuthorId = replies[6]
            authorCoordinates = (
                replycoordinates[0] + 20, replycoordinates[1] + 20)
            textCoordinates = (
                replycoordinates[0] + 20, replycoordinates[1] + 120)
            # reply bg
            self.controller.buttonCreator(
                imagepath=r"Assets\DiscussionsView\exampleofareply.png", xpos=replycoordinates[0], ypos=replycoordinates[1],
                classname=f"exampleofareply{replycounter}", root=self.scrolledframe, isPlaced=True,
                buttonFunction=lambda rep=replies: print(f"{rep} was clicked")
            )
            timestrfmt = r'%A, %B %d %Y at %I:%M:%S %p'
            datetimestr = datetime.now().strftime(timestrfmt)
            if repEditedAt == repCreatedAt:
                repAuthorDate = f"{replyAuthor} replied on {repCreatedAt}"
            else:
                timedelta = datetime.strptime(
                    datetimestr, timestrfmt) - datetime.strptime(repEditedAt, timestrfmt)
                if timedelta.days > 0:
                    timedelta = f"{timedelta.days} days"
                elif timedelta.seconds//3600 > 0:
                    timedelta = f"{timedelta.seconds//3600} hours"
                elif timedelta.seconds//60 > 0:
                    timedelta = f"{timedelta.seconds//60} minutes"
                elif timedelta.seconds < 60:
                    timedelta = f"{timedelta.seconds} seconds"
                repAuthorDate = f"{replyAuthor} replied on {repCreatedAt} (edited {timedelta} ago)"
            # reply author and date
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\fullnamepostedon.png", xpos=authorCoordinates[0], ypos=authorCoordinates[1],
                classname=f"replydetailsfullnamedateemail{replycounter}", root=self.scrolledframe, isPlaced=True,
                text=repAuthorDate, fg=BLACK, size=22, xoffset=-2
            )
            # reply email
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\emailofauthor.png", xpos=authorCoordinates[0], ypos=authorCoordinates[1]+40,
                classname=f"replyemail{replycounter}", root=self.scrolledframe, isPlaced=True,
                text=f"{repAuthorEmail}", fg=BLACK, size=15, xoffset=0
            )
            # reply content
            replytextname = f"replycontent{replycounter}"

            text = Text(
                self.scrolledframe, width=1, height=1, bg=WHITE, fg=BLACK, font=("Arial", 16), wrap=WORD,
                name=replytextname, padx=20, pady=20, relief=FLAT, bd=0, highlightthickness=0,
            )
            text.insert(END, replyContent)
            text.place(
                x=textCoordinates[0], y=textCoordinates[1], width=1020, height=120
            )
            # buttons to edit and delete a reply
            if repAuthorId == self.userId:
                # edit
                self.controller.buttonCreator(
                    imagepath=r"Assets\DiscussionsView\edit.png", xpos=authorCoordinates[0]+900, ypos=authorCoordinates[1],
                    classname=f"editreply{replycounter}", root=self.scrolledframe, isPlaced=True,
                    buttonFunction=lambda rep=(postId, replyId,
                                               self.modulecodevar.get(), replytextname
                                               ): self.editReplyorPost(*rep)
                )
                # delete
                self.controller.buttonCreator(
                    imagepath=r"Assets\DiscussionsView\Trash.png", xpos=authorCoordinates[0]+960, ypos=authorCoordinates[1],
                    classname=f"deletereply{replycounter}", root=self.scrolledframe, isPlaced=True,
                    buttonFunction=lambda rep=(
                        postId, replyId, self.modulecodevar.get()): self.deleteReplyorPost(*rep)
                )
            text.config(state=DISABLED)
            replycounter += 1
            replycoordinates = (replycoordinates[0], replycoordinates[1] + 280)

        partiCoords = (1300, 140)
        partiCounter = 1
        try:
            for i in range(1, len(participants)+10):
                self.controller.widgetsDict[f"{i}inpost"].grid_remove()
        except:
            pass
        for p in participants:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\viewparticipants.png", xpos=partiCoords[0], ypos=partiCoords[1],
                classname=f"{partiCounter}inpost", root=self.postviewframe,
                text=f"{partiCounter}. {p.upper()}", fg=BLACK, size=24, xoffset=-1,
                buttonFunction=lambda p=p: print(f"{p} was clicked")
            )
            partiCoords = (partiCoords[0], partiCoords[1] + 40)
            partiCounter += 1

        # CREATE/EDIT REPLY REGION
        self.replytextwidget = Text(
            self.postviewframe, width=1, height=1, bg=WHITE, fg=BLACK, font=("Arial", 16), wrap=WORD,
            name="replytextwidget", padx=20, pady=20, relief=FLAT, bd=0, highlightthickness=0,
        )
        self.replytextwidget.place(
            x=1300, y=460, width=560, height=300
        )
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
            classname="replyheader", root=self.postviewframe, isPlaced=True,
            text="Add a reply:", fg=BLACK, size=36,
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\cancelreplyedit.png", xpos=1300, ypos=780,
            classname="cancelreplyedit", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\cancelreply.png", xpos=1300, ypos=780,
            classname="cancelreply", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\editreply.png", xpos=1620, ypos=780,
            classname="editreply", root=self.postviewframe,
            buttonFunction=lambda: self.replyThreaded(
                postId, self.modulecodevar.get())
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\addreply.png", xpos=1620, ypos=780,
            classname="addreply", root=self.postviewframe,
            buttonFunction=lambda: self.replyThreaded(
                postId, self.modulecodevar.get())
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\canceldelete.png", xpos=1300, ypos=780,
            classname="canceldelete", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\confirmdelete.png", xpos=1620, ypos=780,
            classname="confirmdelete", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.labelCreator(
            imagepath=r"Assets\DiscussionsView\deletewarninglabel.png", xpos=1300, ypos=460,
            classname="deletewarninglabel", root=self.postviewframe,
        )
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replytotal.png", xpos=1380, ypos=580,
            classname="replytotal", root=self.postviewframe, font=INTERBOLD,
            text=f"This post has {len(repliesList)} replies.", fg="#d2564e", size=28,
        )
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\participantstotal.png", xpos=1380, ypos=660,
            classname="participantstotal", root=self.postviewframe, font=INTERBOLD,
            text=f"From {len(participants)} participants.", fg="#d2564e", size=28,
        )
        wDict = self.controller.widgetsDict
        self.replyWidgets = [
            wDict["cancelreply"],
            wDict["addreply"],
        ]
        self.replyDeleteWidgets = [
            wDict["canceldelete"],
            wDict["confirmdelete"],
            wDict["deletewarninglabel"]
        ]
        self.replyDeletePostOnly = [
            wDict["replytotal"],
            wDict["participantstotal"]
        ]
        self.replyEditWidgets = [
            wDict["cancelreplyedit"],
            wDict["editreply"]
        ]
        for widget in self.replyDeletePostOnly:
            widget.grid_remove()
        for widget in self.replyDeleteWidgets:
            widget.grid_remove()
        for widget in self.replyEditWidgets:
            widget.grid_remove()

    def clearReplyText(self):
        self.replytextwidget.delete('1.0', END)

    def replyThreaded(self, postId, moduleCode: str = "INT4004CEM"):
        t = threading.Thread(target=self.addReply, args=(postId, moduleCode))
        t.daemon = True
        t.start()

    def deleteReplyorPost(self, postId, replyId, moduleCode: str = "INT4004CEM", isPost: bool = False):
        wDict = self.controller.widgetsDict
        addreplybtn = wDict["addreply"]
        editreplybtn = wDict["editreply"]
        canceldeletebtn = wDict["canceldelete"]
        confirmdeletebtn = wDict["confirmdelete"]
        deletewarninglabel = wDict["deletewarninglabel"]
        [widget.grid_remove() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyEditWidgets]
        [widget.grid() for widget in self.replyDeleteWidgets]
        [widget.tk.call("raise", widget._w)
         for widget in self.replyDeleteWidgets]
        [widget.grid() if isPost else None for widget in self.replyDeletePostOnly]
        [widget.tk.call("raise", widget._w)
         if isPost else None for widget in self.replyDeletePostOnly]
        if isPost:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Deleting post: ", fg=BLACK, size=36,
            )
            confirmdeletebtn.config(
                command=lambda: self.callDeleteReply(
                    postId, replyId, moduleCode, isPost=True)
            )
        else:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Deleting reply: ", fg=BLACK, size=36,
            )
            confirmdeletebtn.config(
                command=lambda: self.callDeleteReply(
                    postId, replyId, moduleCode)
            )
        canceldeletebtn.config(
            command=lambda: [
                [widget.grid_remove() for widget in self.replyEditWidgets],
                [widget.grid_remove() for widget in self.replyDeleteWidgets],
                [widget.grid_remove() for widget in self.replyDeletePostOnly],
                [widget.grid() for widget in self.replyWidgets],
                self.replytextwidget.delete('1.0', END),
                self.controller.textElement(
                    imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                    classname="replyheader", root=self.postviewframe, isPlaced=True,
                    text="Add a reply:", fg=BLACK, size=36,
                )
            ]
        )

    def callDeleteReply(self, postId, replyId, moduleCode: str = "INT4004CEM", isPost: bool = False):
        t = threading.Thread(target=self.deleteReply, args=(
            postId, replyId, moduleCode, isPost))
        t.daemon = True
        t.start()

    def deleteReply(self, postId, replyId, moduleCode: str = "INT4004CEM", isPost: bool = False):
        if isPost:
            toasttitle = "Deleting Post"
            toastmessage = "Please wait while we delete your post..."
        else:
            toasttitle = "Deleting Reply"
            toastmessage = "Please wait while we delete your reply..."
        toast = ToastNotification(
            title=toasttitle,
            message=toastmessage,
            bootstyle=INFO,
        )
        toast.show_toast()
        prisma = self.prisma
        if isPost:
            post = prisma.modulepost.delete(
                where={
                    "id": postId
                }
            )
            newtoasttitle = "Post Deleted"
            newtoastmessage = "Your post has been deleted successfully!"
        else:
            reply = prisma.reply.delete(
                where={
                    "replyId": replyId
                }
            )
            newtoasttitle = "Reply Deleted"
            newtoastmessage = "Your reply has been deleted successfully!"
        toast.hide_toast()
        newtoast = ToastNotification(
            title=newtoasttitle,
            message=newtoastmessage,
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        [widget.grid() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyDeleteWidgets]
        [widget.grid_remove() for widget in self.replyEditWidgets]
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
            classname="replyheader", root=self.postviewframe, isPlaced=True,
            text="Add a reply:", fg=BLACK, size=36,
        )
        try:
            self.refreshReplies(postId, prisma, moduleCode)
            if isPost:
                postContentList = self.refreshPosts(prisma, moduleCode)
                self.loadDiscussionTopics(postContentList)
                self.unloadPostView()
                toast = ToastNotification(
                    title="The post was deleted",
                    message="Returning to the discussion topics...",
                    bootstyle=DANGER,
                    duration=1000,
                )
                toast.show_toast()
        except:
            postContentList = self.refreshPosts(prisma, moduleCode)
            self.loadDiscussionTopics(postContentList)
            self.unloadPostView()

    def editReplyorPost(self, postId, replyId, moduleCode: str = "INT4004CEM", replytextname: Text = None, isPost: bool = False):
        textwidget = self.controller.widgetsDict[f"{replytextname}"]
        editreplybtn = self.controller.widgetsDict["editreply"]
        cancelreplyeditbtn = self.controller.widgetsDict["cancelreplyedit"]
        # important lesson for today, tuple comprehensions do not exist in python, so you have to use list comprehensions
        [widget.grid_remove() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyDeleteWidgets]
        [widget.grid_remove() for widget in self.replyDeletePostOnly]
        [widget.grid() for widget in self.replyEditWidgets]
        text = textwidget.get("1.0", 'end-1c')

        self.replytextwidget.focus_set()
        self.replytextwidget.delete('1.0', END)
        self.replytextwidget.insert(END, text)

        if isPost:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Editing Post: ", fg=BLACK, size=36,
            )
            editreplybtn.config(
                command=lambda: self.callUpdateReply(
                    postId, replyId, moduleCode, replytextname, isPost=True)
            )
        else:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Editing Reply: ", fg=BLACK, size=36,
            )
            editreplybtn.config(
                command=lambda: self.callUpdateReply(
                    postId, replyId, moduleCode, replytextname)
            )
        cancelreplyeditbtn.config(
            command=lambda: [
                [widget.grid_remove() for widget in self.replyEditWidgets],
                [widget.grid_remove() for widget in self.replyDeleteWidgets],
                [widget.grid() for widget in self.replyWidgets],
                self.replytextwidget.delete('1.0', END),
                self.controller.textElement(
                    imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                    classname="replyheader", root=self.postviewframe, isPlaced=True,
                    text="Add a reply:", fg=BLACK, size=36,
                )
            ]
        )

    def callUpdateReply(self, postId, replyId, moduleCode: str = "INT4004CEM", replytextname: Text = None, isPost: bool = False):
        t = threading.Thread(target=self.updateReply, args=(
            postId, replyId, moduleCode, replytextname, isPost))
        t.daemon = True
        t.start()

    def updateReply(self, postId, replyId, moduleCode: str = "INT4004CEM", replytextname: Text = None, isPost: bool = False):
        if isPost:
            toasttitle = "Updating Post"
            toastmessage = "Please wait while we update your post..."
        else:
            toasttitle = "Updating Reply"
            toastmessage = "Please wait while we update your reply..."
        toast = ToastNotification(
            title=toasttitle,
            message=toastmessage,
            bootstyle=INFO,
        )
        newtext = self.replytextwidget.get("1.0", 'end-1c')
        toast.show_toast()
        prisma = self.prisma
        utc = timezone('UTC')
        kualalumpur = timezone('Asia/Kuala_Lumpur')
        time = kualalumpur.convert(datetime.now())
        newtime = utc.convert(time)
        if isPost:
            reply = prisma.modulepost.update(
                data={
                    "content": newtext,
                    "editedAt": newtime
                },
                where={
                    "id": postId
                }
            )
            newtoasttitle = "Post Updated"
            newtoastmsg = "Your post has been updated successfully!"
        else:
            reply = prisma.reply.update(
                data={
                    "content": newtext,
                    "editedAt": newtime
                },
                where={
                    "replyId": replyId
                }
            )
            newtoasttitle = "Reply Updated"
            newtoastmsg = "Your reply has been updated successfully!"
        toast.hide_toast()
        newtoast = ToastNotification(
            title=newtoasttitle,
            message=newtoastmsg,
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        [widget.grid() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyDeleteWidgets]
        [widget.grid_remove() for widget in self.replyEditWidgets]
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
            classname="replyheader", root=self.postviewframe, isPlaced=True,
            text="Add a reply:", fg=BLACK, size=36,
        )
        self.replytextwidget.delete('1.0', END)
        self.refreshReplies(postId, prisma, moduleCode)

    def addReply(self, postId, moduleCode: str = "INT4004CEM"):
        toast = ToastNotification(
            title="Adding Reply",
            message="Please wait while we add your reply...",
            bootstyle=INFO,
        )
        toast.show_toast()
        replytext = self.replytextwidget.get("1.0", 'end-1c')
        prisma = self.prisma
        reply = prisma.reply.create(
            data={
                "content": replytext,
                "modulePostId": postId,
                "authorId": self.userId,  # taken from postlogin
            }
        )
        toast.hide_toast()
        newtoast = ToastNotification(
            title="Reply Added",
            message="Your reply has been added successfully!",
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        self.refreshReplies(postId, prisma, moduleCode)

    def callLoadLatestPosts(self, moduleCode: str = "INT4004CEM"):
        prisma = self.prisma
        t = threading.Thread(target=self.refreshPosts,
                             args=(prisma, moduleCode))
        t.daemon = True
        t.start()

    def callLoadLatestReplies(self, postId, moduleCode: str = "INT4004CEM"):
        prisma = self.prisma
        t = threading.Thread(target=self.refreshReplies,
                             args=(postId, prisma, moduleCode))
        t.daemon = True
        t.start()

    def loadLatestPosts(self, prisma: Prisma = None, moduleCode: str = "INT4004CEM"):
        posts = prisma.modulepost.find_many(
            include={
                "author": True,
                "replies": {
                    "include": {
                        "author": True
                    }
                }
            },
            where={
                "module": {
                    "is": {
                        "moduleCode": moduleCode
                    }
                }
            }
        )
        user = prisma.userprofile.find_first(
            where={
                "id": self.userId
            },
            include={
                "favoritePosts": True
            }
        )
        favoritedPostIds = [p.id for p in user.favoritePosts]
        # from pendulum
        # prisma's datetime fields are saved automatically in UTC
        # converting to local timezone:
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        timestrfmt = r'%A, %B %d %Y at %I:%M:%S %p'
        postContentList = [
            (
                post.id, post.title, post.content, post.author.fullName, post.author.email,
                kualalumpur.convert(post.createdAt).strftime(
                    timestrfmt),  # '%A %d %B %Y %H:%M:%S'
                kualalumpur.convert(post.editedAt).strftime(
                    timestrfmt),
                [
                    [
                        reply.content, reply.author.fullName, reply.author.email,
                        kualalumpur.convert(reply.createdAt).strftime(
                            timestrfmt),  # '%A %d %B %Y %H:%M:%S'
                        kualalumpur.convert(reply.editedAt).strftime(
                            timestrfmt),
                        reply.replyId, reply.authorId,
                    ] for reply in post.replies
                ],
                post.authorId,
                favoritedPostIds
            ) for post in posts
        ]
        return postContentList

    def refreshPosts(self, prisma: Prisma = None, moduleCode: str = "INT4004CEM"):
        toast = ToastNotification(
            title="Just a moment...",
            message=f"Loading latest posts for {moduleCode}...",
            bootstyle=INFO,
        )
        toast.show_toast()
        postContentList = self.loadLatestPosts(prisma, moduleCode)
        heightofframe = len(postContentList) * 100
        if heightofframe < 500:
            rowspanofFrame = int(500/20)
        else:
            rowspanofFrame = int(heightofframe/20)
        self.postscrolledframe = ScrolledFrame(
            self, width=840, height=heightofframe, name="postsframescrollable", autohide=True,
        )
        gridGenerator(self.postscrolledframe, int(
            840/20), rowspanofFrame, WHITE)
        self.postscrolledframe.grid_propagate(False)
        self.postscrolledframe.place(x=100, y=320, width=840, height=500)
        self.loadDiscussionTopics(postContentList)
        toast.hide_toast()
        newtoast = ToastNotification(
            title="Done!",
            message=f"Latest posts loaded for {moduleCode}.",
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        return postContentList

    def refreshReplies(self, postId, prisma, moduleCode: str = "INT4004CEM"):
        toast = ToastNotification(
            title="Just a moment...",
            message=f"Fetching latest replies for Post {postId}",
            bootstyle=INFO,
        )
        toast.show_toast()
        postContentList = self.refreshPosts(prisma, moduleCode)
        # probably can be refactored into a binary search
        for tuple in postContentList:
            if tuple[0] == postId:
                self.loadPostView(tuple)
                break
        toast.hide_toast()
        newtoast = ToastNotification(
            title="Done!",
            message=f"Latest replies loaded for {postId}.",
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()


class FavoritesView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)


class AppointmentsView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1, bg=WHITE,
                        name="appointmentsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()
        self.creationframe = self.controller.widgetsDict["appointmentscreation"]
        self.viewFrame = self.controller.widgetsDict["appointmentsmanage"]
        self.createElements()
        xpos = int(1420/20)
        ypos = int(140/20)
        columnspan = int(460/20)
        rowspan = int(40/20)
        self.dateentry = DateEntry(
            self, width=1,
        )
        self.dateentry.grid(row=ypos, column=xpos,
                            columnspan=columnspan, rowspan=rowspan, sticky=NSEW)
        print(self.dateentry.entry.get())
        self.scrolledframe = ScrolledFrame(
            self, width=1, height=1, name="appointmentscrolledframe", autohide=True, padding=0
        )
        self.scrolledframe.grid(
            row=int(180/20), column=int(1420/20), columnspan=int(460/20), rowspan=int(680/20), sticky=NSEW
        )
        self.scrolledframe.grid_propagate(False)
        gridGenerator(self.scrolledframe, int(460/20), int(920/20), DARKBLUE)
        # self.controller.frameCreator(
        #     xpos=1420, ypos=180, framewidth=460, frameheight=680, root=self,
        #     classname="appcanvasframe",
        # )
        # self.appcanvasframe = self.controller.widgetsDict["appcanvasframe"]
        # self.controller.canvasCreator(
        #     xpos=0, ypos=0, width=460, height=960, root=self.appcanvasframe,
        #     classname="appdisplaycanvas",
        #     # xpos=0, ypos=0, framewidth=460, frameheight=960, root=self,
        #     # classname="appdisplayframe",
        # )
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)
        print(now.strftime('%A %d %B %Y %H:%M:%S %z'))
        hours = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
                 "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                 "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                 "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
                 ]

        initialypos = 0
        for i in range(24):
            self.controller.textElement(
                r"Assets\AppointmentsView\timehours.png", xpos=0,
                ypos=initialypos, root=self.scrolledframe, size=30, classname=f"hour{i}",
                text=hours[i], isPlaced=True
            )
            self.controller.textElement(
                r"Assets\AppointmentsView\eventdetails.png", xpos=100,
                ypos=initialypos, root=self.scrolledframe, size=30, classname=f"event{i}",
                text=f"Placeholder event {i}", buttonFunction=lambda i=i: print(f"event {i} clicked"), isPlaced=True,
            )
            initialypos += 40
        self.creationframe.grid_remove()
        self.viewFrame.grid_remove()
    # self.controller.frameCreator(
    #         xpos=120, ypos=580,
    #         framewidth=1160, frameheight=180,
    #         root=self, classname="appointmentsmenuframe", bg="#F6F5D7",
    #     )
    #     buttontoloadmenubutton = ttk.Button(
    #         self.controller.widgetsDict["appointmentsmenuframe"], text="Appointments", command=lambda: self.loadmenubuttons())
    #     buttontoloadmenubutton.place(x=0, y=0, width=200, height=60)
    #     self.controller.frameCreator(
    #         120, 580, 1160, 180, self, classname="hostfr", bg=WHITE, relief=FLAT)
    #     self.controller.widgetsDict["appointmentsmenuframe"].tk.call(
    #         "raise", self.controller.widgetsDict["appointmentsmenuframe"]._w)
    #     self.coursebuttonvar = StringVar()
    #     self.lecturerbuttonvar = StringVar()
    #     self.purposebuttonvar = StringVar()
    #     ttk.Style().configure("TMenubutton", font=("Helvetica", 16, "bold"),
    #                           background=NICEBLUE, foreground=BLACK, relief=FLAT)
    #     self.coursebuttonvar = StringVar()
    #     self.coursemenubutton, self.coursemenubtnmenu, _ = self.create_menubutton(
    #         parent=self.controller.widgetsDict["appointmentsmenuframe"],
    #         text="Courses",
    #         values=["Computer Architecture", "Mathematics for Computer Science",
    #                 "Object Oriented Programming"],
    #         variable=self.coursebuttonvar,
    #         xpos=40, ypos=80
    #     )
    #     self.lecturerbuttonvar = StringVar()
    #     self.lecturermenubutton, self.lecturermenubtnmenu, _ = self.create_menubutton(
    #         parent=self.controller.widgetsDict["appointmentsmenuframe"],
    #         text="Lecturers",
    #         values=["Dr. John Doe", "Dr. Jane Doe", "Dr. John Smith"],
    #         variable=self.lecturerbuttonvar,
    #         xpos=420, ypos=80
    #     )
    #     self.purposebuttonvar = StringVar()
    #     self.purposemenubutton, self.purposemenubtnmenu, _ = self.create_menubutton(
    #         parent=self.controller.widgetsDict["appointmentsmenuframe"],
    #         text="Purpose",
    #         values=["Consultation", "Discussion", "Other"],
    #         variable=self.purposebuttonvar,
    #         xpos=800, ypos=80
    #     )
    #     self.controller.widgetsDict["coursemenubutton"] = self.coursemenubutton
    #     self.controller.widgetsDict["lecturermenubutton"] = self.lecturermenubutton
    #     self.controller.widgetsDict["purposemenubutton"] = self.purposemenubutton

    # def create_menubutton(self, parent, text, values, variable, xpos=0, ypos=0, command=None):
    #     menubutton_var = StringVar()
    #     style = ttk.Style()
    #     style.configure("TMenubutton", font=("Helvetica", 16, "bold"),
    #                     background="#e9d0c3", foreground=BLACK, relief=FLAT)
    #     menubutton = ttk.Menubutton(
    #         parent, width=320, text=text, name=text.lower() + "menubutton")
    #     menubutton.place(x=xpos, y=ypos,
    #                      width=320, height=60)
    #     menubutton_menu = Menu(menubutton, tearoff=0)
    #     for value in values:
    #         menubutton_menu.add_radiobutton(label=value, variable=menubutton_var, value=value,
    #                                         command=lambda: self.loadmenubuttons(menubutton, menubutton_var))
    #     if command:
    #         menubutton.config(command=command)
    #     menubutton.config(menu=menubutton_menu)
    #     variable.set(menubutton_var.get())
    #     return menubutton, menubutton_menu, menubutton_var

    # def loadmenubuttons(self, menubutton, menubutton_var):
    #     # retrieve the course name from the coursemenubutton
    #     menubutton.config(text=menubutton_var.get())
    #     course = self.controller.widgetsDict["coursemenubutton"].cget("text")
    #     if course.startswith("Computer"):
    #         messagebox.showerror("Error", "Please select a course")
    #     else:
    #         # if the course is not empty, load the buttons
    #         print(course)

    # def prismaQueries(self):
    #     prisma = Prisma()
    #     prisma.connect()
    #     # getting the courses using the context from controller
    #     courses = prisma.module.find_many(

    #     )
    #     prisma.disconnect()

    def createFrames(self):
        self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="appointmentscreation",
        )
        self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="appointmentsmanage",
        )

    def createElements(self):
        self.staticImgLabels = [
            (r"Assets\AppointmentsView\appointmentsdashboard.png",
             0, 0, "AppointmentsBG", self),
            (r"Assets\AppointmentsView\TitleLabel.png",
             0, 0, "AppointmentsHeader", self),
            (r"Assets\AppointmentsView\appointmentcreationbg.png",
             0, 0, "appcreationbg", self.creationframe),
        ]
        self.staticBtns = [
            (r"Assets\AppointmentsView\Create Appointment.png", 80, 600, "createappointmentbtn", self,
             lambda: self.loadAppCreation()),
            (r"Assets\AppointmentsView\manageappointments.png", 780, 600, "manageappointmentsbtn", self,
             lambda: self.loadAppView()),
            (r"Assets\My Courses\exitbutton.png", 1840, 0, "appcreateexitbtn", self.creationframe,
             lambda: self.unloadAppCreation()),
            (r"Assets\My Courses\exitbutton.png", 1840, 0, "appviewexitbtn", self.viewFrame,
             lambda: self.unloadAppView()),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def postLogin(self, data: dict = None, prisma: Prisma = None):
        self.prisma = prisma
        self.userId = data["id"]
        self.data = data
        self.role = data["role"]
        appContentList = self.loadLatestAppointments(
            prisma=self.prisma, userId=self.userId)
        print(f"In appointments view, {self.userId} ")
        print(appContentList)

    def loadLatestAppointments(self, prisma: Prisma = None, userId: str = None):
        if self.role == "lecturer":
            appointments = prisma.appointment.find_many(
                include={
                    "lecturer": {
                        "include": {
                            "userProfile": True
                        }
                    },
                    "student": {
                        "include": {
                            "userProfile": True
                        }
                    }
                },
                where={
                    "lecturer": {
                        "is": {
                            "userId": userId
                        }
                    }
                }
            )
        elif self.role == "student":
            appointments = prisma.appointment.find_many(
                include={
                    "lecturer": {
                        "include": {
                            "userProfile": True
                        }
                    },
                    "student": {
                        "include": {
                            "userProfile": True
                        }
                    }
                },
                where={
                    "student": {
                        "is": {
                            "userId": userId
                        }
                    }
                }
            )

        kualalumpur = timezone("Asia/Kuala_Lumpur")
        humanreadable = r"%A, %B %d %Y at %I:%M:%S %p"
        humandate = r"%A, %B %d %Y"
        for app in appointments:
            appContentList = [
                app.id,
                kualalumpur.convert(app.startTime).strftime(humanreadable),
                kualalumpur.convert(app.endTime).strftime(humanreadable),
                kualalumpur.convert(app.startTime).strftime(humandate),
                kualalumpur.convert(app.endTime).strftime(humandate),
                app.location,
                app.student.userProfile.fullName,
                app.lecturer.userProfile.fullName,
                app.isCompleted,
                kualalumpur.convert(app.createdAt).strftime(
                    humanreadable),
                kualalumpur.convert(app.updatedAt).strftime(
                    humanreadable),
                app.studAccept, app.lectAccept
            ]
            try:
                appContentList.append(
                    app.studAcceptAt.strftime(humanreadable)
                )
                appContentList.append(
                    app.lectAcceptAt.strftime(humanreadable)
                )
            except:
                appContentList.append(
                    "Not accepted yet by student"
                )
                appContentList.append(
                    "Not accepted yet by lecturer"
                )
        # appContentList = [
        #     (
        #         app.id,
        #         kualalumpur.convert(app.startTime).strftime(humanreadable),
        #         kualalumpur.convert(app.endTime).strftime(humanreadable),
        #         kualalumpur.convert(app.startTime).strftime(humandate),
        #         kualalumpur.convert(app.endTime).strftime(humandate),
        #         app.location,
        #         app.student.userProfile.fullName,
        #         app.lecturer.userProfile.fullName,
        #         app.studAccept, app.lectAccept,
        #         app.isCompleted,
        #         kualalumpur.convert(app.createdAt).strftime(
        #             r"%A, %B %e %Y at %I:%M %p"),
        #         kualalumpur.convert(app.updatedAt).strftime(
        #             r"%A, %B %e %Y at %I:%M %p"),
        #     ) for app in appointments
        # ]
        return appContentList

    def loadAppCreation(self):
        self.creationframe.grid()
        self.creationframe.tkraise()

    def unloadAppCreation(self):
        self.creationframe.grid_remove()

    def loadAppView(self):
        self.viewFrame.grid()
        self.viewFrame.tkraise()

    def unloadAppView(self):
        self.viewFrame.grid_remove()
        # for app in appointments:
        #     print(app)


def runGui():
    window = Window()
    window.mainloop()


def runGuiThreaded():
    t = Thread(ThreadStart(runGui))
    t.ApartmentState = ApartmentState.STA
    t.Start()
    t.Daemon = True
    t.Join()


if __name__ == "__main__":
    # runGui()
    try:
        runGuiThreaded()
    except Exception as e:
        print("sorry")
