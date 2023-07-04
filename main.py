from components.slidepanel import SlidePanel
from components.topbar import TopBar
from static import *
from ctypes import windll
import threading
from tkinter import *
# A drop in replacement for ttk that uses bootstrap styles
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from dotenv import load_dotenv
from prisma import Prisma
from basewindow import gridGenerator
import bcrypt
# TODO: please stop formatting my imports you're breaking my code
# this contains my pywin32 imports, PIL imports, pythonnet
from nonstandardimports import *
from views.discussionsview import DiscussionsView
from views.chatbot import Chatbot
from views.courseview import CourseView
from views.favoritesview import FavoritesView
from views.appointmentsview import AppointmentsView
from views.learninghub import LearningHub
from views.searchpage import SearchPage
from components.userforms import UserForms
from basewindow import ElementCreator
load_dotenv()


user32 = windll.user32


class Window(ElementCreator):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self, themename="minty", *args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}
        self.frames = {}
        self.canvasInDashboard = {}
        self.initializeWindow()
        self.initMainPrisma()
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

        self.buttonSettingsPSF = [
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
                 self.loadSignIn(),
                 #  self.show_frame(Dashboard),
                 #  self.show_canvas(DashboardCanvas),
                 #  self.get_page(Dashboard).loadSpecificAssets("student"),
             ])
        ]

        self.settingsUnpacker(self.labelSettingsParentFrame, "label")
        self.settingsUnpacker(self.buttonSettingsPSF, "button")

        self.openDevWindow()
        # self.bind("<Configure>", self.resizeEvent)

        for F in (Dashboard, ):
            frame = F(parent=self.parentFrame, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, columnspan=96, rowspan=54, sticky=NSEW)
            frame.grid_propagate(False)
            self.maincanvas = self.canvasCreator(0, 80, 1920, 920, root=frame, classname="maincanvas",
                                                 bgcolor=WHITE, isTransparent=True, transparentcolor=LIGHTYELLOW)
            self.updateWidgetsDict(frame)
            frame.grid_remove()
        self.canvasTuple = (DashboardCanvas, SearchPage, Chatbot,
                            LearningHub, CourseView, DiscussionsView,
                            FavoritesView, AppointmentsView)
        for CANVAS in self.canvasTuple:
            canvas = CANVAS(
                parent=self.maincanvas, controller=self)
            self.canvasInDashboard[CANVAS] = canvas
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
        self.widgetsDict["skipbutton"].grid_remove()  # Comment to bypass login

        self.bind("<F11>", lambda e: self.togglethewindowbar())
        self.test()

    def test(self):
        def foo():
            baz = self.mainPrisma.execute_raw(
                """
                    SELECT 1;
                    """
            )
        t = threading.Thread(target=foo)
        t.daemon = True
        t.start()
        self.after(1000, self.test)

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
        self.title("INTI Learning Platform")
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
        try:
            self.widgetsDict["completeregbutton"].grid_remove()
        except:
            pass
        self.widgetsDict["skipbutton"].grid_remove()
        self.widgetsDict["gofullscreenbtn"].grid_remove()
        self.widgetsDict["backbutton"].grid()
        if student:
            ref.configure(image=self.loadedImgs[0])
            self.studentform = UserForms(
                self.postSelectFrame, self, "studentreg")
            self.studentform.loadRegThread("student")
        elif teacher:
            ref.configure(image=self.loadedImgs[1])
            self.teacherform = UserForms(
                self.postSelectFrame, self, "teacherreg")
            self.teacherform.loadRegThread("teacher")
        self.postSelectFrame.grid()
        self.postSelectFrame.tkraise()

    def loadSignIn(self):
        ref = self.widgetsDict["postselectframebg"]
        ref.configure(image=self.loadedImgs[2])
        try:
            if self.studentform:
                self.widgetsDict["studentreg"].grid_remove()
                self.widgetsDict["completeregbutton"].grid_remove()
                if self.teacherform:
                    self.widgetsDict["teacherreg"].grid_remove()
                    self.widgetsDict["completeregbutton"].grid_remove()
                self.studentform.loadSignIn()
        except AttributeError:
            pass
        try:
            if self.teacherform:
                self.widgetsDict["teacherreg"].grid_remove()
                self.widgetsDict["completeregbutton"].grid_remove()
                if self.studentform:
                    self.widgetsDict["studentreg"].grid_remove()
                    self.widgetsDict["completeregbutton"].grid_remove()
                self.teacherform.loadSignIn()
        except AttributeError:
            pass

        def reloadForm():
            try:
                if self.studentform:
                    self.studentform.grid()
                    self.widgetsDict["completeregbutton"].grid()
                    self.widgetsDict["postselectframebg"].configure(
                        image=self.loadedImgs[0])
            except AttributeError:
                pass
            try:
                if self.teacherform:
                    self.teacherform.grid()
                    self.widgetsDict["completeregbutton"].grid()
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
            self.prisma = self.mainPrisma
            emailtext = self.widgetsDict["signinemail"].get()
            entrytext = self.widgetsDict["signinpassent"].get()
            if emailtext == "" or entrytext == "":
                toast.hide_toast()
                toast = ToastNotification(
                    title="Error",
                    message=f"Please fill in all fields",
                    duration=3000,
                )
                toast.show_toast()
                return
            user = self.prisma.userprofile.find_first(
                where={
                    "email": emailtext
                },
                include={
                    "student": True,
                    "lecturer": True,
                }
            )
            if user is None:
                toast.hide_toast()
                toast = ToastNotification(
                    title="Email not found",
                    message=f"User not found, are you sure you have an account/have you entered the correct email?",
                    duration=3000,
                )
                toast.show_toast()
                return
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
                    programme = module.programme.programmeCode
                data = {
                    "id": student.userProfile.id,
                    "fullName": student.userProfile.fullName,
                    "email": student.userProfile.email,
                    "modules": modulesOfStudent,
                    "lecturerinfo": lecturerinfo,
                    "programme": programme,
                    "role": "student",
                }
            elif isTeacher:
                lecturer, modules = self.setUserContext(
                    userId=user.id, role="lecturer", prisma=self.prisma)
                modulesOfLecturer = []
                studentinfo = []
                programme = modules[0].programme.programmeCode
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
                    "programme": programme,
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
            postLoginCanvases = [
                "courseview", "discussionsview", "appointmentsview", "favoritesview", "learninghub"]
            for canvas in postLoginCanvases:
                canvas = self.widgetsDict[canvas]
                canvas.postLogin(data)

        except Exception as e:
            print(e)

    def openDevWindow(self):
        self.createDevWindow()

        def parseObjectsFromFrame():
            for widgetname, widget in self.widgetsDict.items():
                # skip widgets that are children of labels in hostfr
                if widgetname.startswith("!la") and widget.winfo_parent().endswith("hostfr"):
                    continue
                # skip widgets related to teacherreg or studentreg
                parents = widget.winfo_parent().split(".")
                # if any(p.endswith("reg") for p in parents[-3:]):
                #     continue
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

    def createDevWindow(self):
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

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.grid()
        frame.tkraise()

    def show_canvas(self, cont):
        canvas = self.canvasInDashboard[cont]
        canvas.grid()
        canvas.tk.call("raise", canvas._w)
        canvas.focus_force()

    def get_page(self, classname):
        return self.frames[classname]

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
                            },
                            "programme": True,
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
                    "modules": {
                        "include": {
                            "programme": True,
                        }
                    }
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
                    "programme": True,
                }
            )
            return lecturer, modules


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
            (r"Assets\Dashboard\05MyCoursesChip.png", 440, 1020, "MyCoursesChip",
             self.framereference, lambda: self.controller.show_canvas(CourseView)),
            (r"Assets\Dashboard\04LearningHubChip.png", 580, 1020, "LearningHubChip",
             self.framereference, lambda: self.controller.show_canvas(LearningHub)),
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
        self.maincanvasref = self.controller.canvasCreator(0, 80, 1920, 920, root=self.framereference, classname="maincanvas",
                                                           bgcolor=LIGHTYELLOW, isTransparent=True, transparentcolor=LIGHTYELLOW)
        self.dashboardcanvasref = self.controller.canvasCreator(0, 0, 1920, 920, root=self.maincanvasref, classname="dashboardcanvas",
                                                                bgcolor=NICEBLUE, isTransparent=True, transparentcolor=LIGHTYELLOW)
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

    def postLogin(self, data: dict):
        role = data["role"]
        id = data["id"]
        fullName = data["fullName"]
        email = data["email"]
        modules = data["modules"]
        # modules = [(moduleCode, moduleTitle, moduleDesc), (moduleCode, moduleTitle, moduleDesc), (moduleCode, moduleTitle, moduleDesc)]
        cont = self.controller
        initialypos = 20
        h = len(modules) * 300 + 20
        if h < 920:
            h = 920
        self.dashboardScrolledFrame = ScrolledFrame(
            self.dashboardcanvasref, width=600, height=h, bootstyle="success-rounded", autohide=True,
        )
        self.dashboardScrolledFrame.place(x=740, y=0, width=600, height=920)

        Label(self.dashboardScrolledFrame, bg="#dee8e0", width=600, height=h, relief=FLAT, bd=0, autostyle=False).place(x=0, y=0, width=600, height=h)
        for m in modules:
            cont.labelCreator(
                imagepath=r"Assets\Dashboard\ModuleTile.png", xpos=0, ypos=initialypos+20,
                classname=f"{m[0]}tile", root=self.dashboardScrolledFrame, isPlaced=True
            )
            if m[1] == "Computer Science Activity Led Learning Project 2": # too long to display properly
                cont.textElement(
                    imagepath=r"Assets\Dashboard\coursetitlebg.png", xpos=20, ypos=initialypos,
                    classname=f"{m[0]}title", root=self.dashboardScrolledFrame, text="Computer Science\nActivity Led Learning Project 2", size=28,
                    buttonFunction=lambda e=m[0]: self.navigateToModuleView(e), isPlaced=True, yIndex=-1/2
                )
                
            else:
                cont.textElement(
                    imagepath=r"Assets\Dashboard\coursetitlebg.png", xpos=20, ypos=initialypos,
                    classname=f"{m[0]}title", root=self.dashboardScrolledFrame, text=m[1], size=28, 
                    buttonFunction=lambda e=m[0]: self.navigateToModuleView(e), isPlaced=True
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
    def navigateToModuleView(self, moduleCode):
        courseview = self.controller.widgetsDict["courseview"]
        courseview.loadCourses(f"{moduleCode.upper()}")
        courseview.viewUploadsFrame.grid_remove()
        courseview.uploadCreationFrame.grid_remove()
        self.controller.show_canvas(CourseView)
        

class DashboardCanvas(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1, bg=WHITE,
                        name="dashboardcanvas", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)


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
    runGuiThreaded()
