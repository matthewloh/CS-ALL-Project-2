from static import *
import ctypes
from ctypes import windll
import threading
from tkinter import *
# A drop in replacement for ttk that uses bootstrap styles
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.validation import add_text_validation, add_regex_validation, validator, add_validation, add_option_validation
from dotenv import load_dotenv
from prisma import Prisma
from elementcreator import gridGenerator
import bcrypt
from datetime import datetime, timedelta, timezone
# TODO: please stop formatting my imports you're breaking my code
# this contains my pywin32 imports, PIL imports, pythonnet
from nonstandardimports import *
from pendulum import timezone
from views.discussionsview import DiscussionsView
from views.chatbot import Chatbot
from views.courseview import CourseView
from views.appointmentsview import AppointmentsView
from components.animatedstarbtn import AnimatedStarBtn
from components.animatedgif import AnimatedGif
from basewindow import ElementCreator
from win32gui import GetWindowText, GetForegroundWindow
load_dotenv()


from PIL import Image, ImageTk, ImageSequence

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
                # self.show_frame(Dashboard),
                # self.show_canvas(DashboardCanvas),
                # self.get_page(Dashboard).loadSpecificAssets("student"),
             ])
        ]

        self.settingsUnpacker(self.labelSettingsParentFrame, "label")
        self.settingsUnpacker(self.buttonSettingsPSF, "button")

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
        self.widgetsDict["skipbutton"].grid_remove()  # Comment to bypass login

        self.bind("<F11>", lambda e: self.togglethewindowbar())

    def updateWidgetsDict(self, root: Frame):
        widgettypes = (Label, Button, Frame, Canvas, Entry, Text, ScrolledFrame, ScrolledText)
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
            if isinstance(widget, (Label, Button, Frame, Canvas, Entry, Text, ScrolledFrame, ScrolledText)) and not widgetname.startswith("!la"):
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
        self.widgetsDict["gofullscreenbtn"].grid_remove()
        self.widgetsDict["backbutton"].grid()
        self.widgetsDict["skipbutton"].grid()
        if student:
            ref.configure(image=self.loadedImgs[0])
            self.studentform = UserForms(
                self.postSelectFrame, self, "studentreg")
            self.studentform.loadStudentReg()
        elif teacher:
            ref.configure(image=self.loadedImgs[1])
            self.teacherform = UserForms(
                self.postSelectFrame, self, "teacherreg")
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
            self.prisma = self.mainPrisma
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

    def openDevWindow(self):
        self.createDevWindow()

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

    def validation(self):
        
        return True
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
    def dbGetLists(self, role):
        prisma = self.controller.mainPrisma
        institution = prisma.institution.find_first(
            where={
                "institutionCode": "IICP"
            }
        )
        schools = prisma.school.find_many(
            where={
                "institution": {
                    "is": {
                        "institutionCode": institution.institutionCode
                    }
                }
            }
        )
        lists = {}
        return lists
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
        prisma = self.controller.mainPrisma
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

class FavoritesView(Canvas):
    def __init__(self, parent, controller: Window):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="favoritesview", autostyle=False)
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
    try:
        runGuiThreaded()
    except Exception as e:
        print("sorry")
