import threading
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from elementcreator import gridGenerator
from static import * 
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma import Prisma
from win32gui import GetWindowText, GetForegroundWindow

from views.discussionsview import DiscussionsView
from PIL import Image, ImageTk, ImageSequence
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime

class CourseView(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg="#F6F5D7", name="courseview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()
        self.canvas = self.controller.widgetsDict["coursescanvas"]

    def postLogin(self, data: dict, prisma: Prisma = None):
        # print("The data is", data)
        self.prisma = prisma
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

    def loadcoursebuttons(self, modulecodes: list = None):
        # print(f"The modulecodes list is {modulecodes}")
        c = self.controller
        coursecanvas = self.controller.widgetsDict["coursescanvas"]
        for widgetname, widget in coursecanvas.children.items():
            if widgetname not in modulecodes and widgetname.startswith("int"):
                widget.grid_forget()

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


    def createFrames(self):
        self.controller.frameCreator(root=self,
                                     xpos=0, ypos=0,
                                     framewidth=1920, frameheight=920, classname="singlecourseviewframe"
                                     )
        self.mainframe = self.controller.widgetsDict["singlecourseviewframe"]
        self.controller.frameCreator(
            xpos=0, ypos=120, framewidth=1920, frameheight=800,
            root=self.mainframe, classname="viewuploadsframe"
        )
        self.viewUploadsFrame = self.controller.widgetsDict["viewuploadsframe"]
        self.staticImgLabels = [
            (r"Assets\My Courses\CoursesBG.png", 0, 0, "courseviewbg", self),
            (r"Assets\My Courses\loadedcoursebg.png",
             0, 0, "loadedcoursebg", self.mainframe),
            (r"Assets\My Courses\moduleuploadsbg.png", 0,
             0, "moduleuploadsbg", self.viewUploadsFrame),
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

        self.defaulturl = r"https://newinti.edu.my/campuses/inti-international-college-penang/"
        self.urlbar = self.controller.entryCreator(
            xpos=820, ypos=120, width=980, height=40,
            root=self.viewUploadsFrame, classname=f"uploadssearchbar",
        )
        self.urlbar.delete(0, END)
        self.urlbar.insert(0, f"{self.defaulturl}")

    def exitMainFrame(self):
        self.mainframe.grid_remove()
        self.exitUploadsView()
        self.canvas.grid()

    def exitUploadsView(self):
        self.viewUploadsFrame.grid_remove()
        try:
            self.webview.destroy()
            del self.webview
            self.urlbar.delete(0, END)
            self.urlbar.insert(0, f"{self.defaulturl}")
            self.viewUploadsFrame.focus_set()
        except:
            pass

    def initializeWebView(self):
        col = int(820/20)
        row = int(180/20)
        w = int(1060/20)
        h = int(580/20)

        self.webview = WebView2(parent=self.viewUploadsFrame, width=1, height=1,
                                url=self.defaulturl)
        self.webview.grid(row=row, column=col, rowspan=h,
                          columnspan=w, sticky=NSEW)

    def loadModuleUploadsView(self, modulecode):
        self.viewUploadsFrame.grid()
        self.viewUploadsFrame.tkraise()
        self.urlbar.delete(0, END)
        self.urlbar.insert(0, f"{self.defaulturl}")
        self.initializeWebView()
        toast = ToastNotification(
            title="Focus automatically regained",
            message="The focus was automatically regained to the window, to stop this, please exit the window manually.",
            duration=1000,
            bootstyle=INFO
        )
        def regainFocus():
            if GetWindowText(GetForegroundWindow()) == "INTI Learning Platform" and self.controller.focus_get() == None:
                self.focus_force()
            self.webview.after(1000, regainFocus)
        self.currenturl = self.defaulturl
        def updateUrlbar():
            if self.webview.get_url() == None:
                self.urlbar.delete(0, END)
                self.urlbar.insert(0, f"{self.defaulturl}")
                self.currenturl = self.defaulturl
            elif self.webview.get_url() == self.currenturl:
                pass
            else:
                self.urlbar.delete(0, END)
                self.urlbar.insert(0, f"{self.webview.get_url()}")
                self.currenturl = self.webview.get_url()
            self.webview.after(1, updateUrlbar)

        updateUrlbar()
        regainFocus()
        t = threading.Thread(target=self.loadModuleUploads, args=(modulecode,))
        t.daemon = True
        t.start()

    def loadModuleUploads(self, modulecode):
        prisma = self.prisma
        uploads = prisma.moduleupload.find_many(
            where={
                "module": {
                    "is": {
                        "moduleCode": modulecode
                    }
                }
            },
            include={
                "uploader": {
                    "include": {
                        "userProfile": True
                    }
                }
            }
        )
        h = len(uploads) * 100 + 40
        if h <= 640:
            rspan = int(640/20)
        else:
            rspan = int(h/20)

        self.upframe = ScrolledFrame(
            self.viewUploadsFrame, width=760, height=h, autohide=True,
        )
        gridGenerator(self.upframe, int(760/20), rspan, WHITE)
        self.upframe.grid_propagate(False)
        self.upframe.place(x=40, y=120, width=760, height=640)
        startx = 20
        starty = 40
        kl = timezone("Asia/Kuala_Lumpur")
        for u in uploads:
            createdAt = kl.convert(u.createdAt)
            editedAt = kl.convert(u.editedAt)
            self.renderModuleUploads(
                u.uploadType, u.id, u.title, u.description, u.url, createdAt, editedAt,
                startx, starty, u.uploader.userProfile.fullName, u.uploader.userProfile.email
            )
            starty += 100

    def renderModuleUploads(self, filetype, id, title, description, url, createdat, editedat, x, y, uploadername, uploaderemail):
        btnImgDict = {
            "PDF": r"Assets\My Courses\pdfbtn.png",
            "VIDEO": r"Assets\My Courses\videobtn.png",
            "IMG": r"Assets\My Courses\imgbtn.png",
            "LINK": r"Assets\My Courses\linkbtn.png",
        }
        textBgDict = {
            "PDF": r"Assets\My Courses\pdftxtbg.png",
            "VIDEO": r"Assets\My Courses\videotxtbg.png",
            "IMG": r"Assets\My Courses\imgtxtbg.png",
            "LINK": r"Assets\My Courses\linktxtbg.png",
        }
        c = self.controller
        tiptext = f"""Click me to load {title}, a {filetype.title()} file.\nDescription: {description}\nUrl: {url},\nUploaded by: {uploadername} ({uploaderemail})"""
        b = c.buttonCreator(
            imagepath=btnImgDict[filetype], xpos=x, ypos=y,
            classname=f"{id}btn", root=self.upframe,
            isPlaced=True,
            buttonFunction=lambda: self.webview.load_url(url),
        )
        ToolTip(b, text=tiptext, bootstyle=(INFO, INVERSE))
        t1 = c.textElement(
            imagepath=textBgDict[filetype], xpos=x+20, ypos=y,
            classname=f"{id}title", root=self.upframe,
            text=title, fg=BLACK, size=20, isPlaced=True,
            font=INTERBOLD,
            buttonFunction=lambda: self.webview.load_url(url),
        )
        ToolTip(t1, text=tiptext, bootstyle=(INFO, INVERSE))
        fCreatedAt = createdat.strftime(r"%d/%m/%y - %I:%M %p")
        fEditedAt = editedat.strftime(r"%d/%m/%y - %I:%M %p")
        if fCreatedAt == fEditedAt:
            strTime = f"Created: {fCreatedAt}"
        else:
            strTime = f"Created: {fCreatedAt} | Edited: {fEditedAt}"
        t2 = c.textElement(
            imagepath=textBgDict[filetype], xpos=x+20, ypos=y+40,
            classname=f"{id}time", root=self.upframe,
            text=strTime, fg=BLACK, size=16, isPlaced=True,
            font=INTER,
            buttonFunction=lambda: self.webview.load_url(url),
        )
        ToolTip(t2, text=tiptext, bootstyle=(INFO, INVERSE))

    # FUNCTIONS THAT NAVIGATE OUT OF COURSEVIEW
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
