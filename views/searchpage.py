import threading
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import uuid
import boto3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.tooltip import ToolTip
from components.animatedgif import AnimatedGif
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma import Prisma
from win32gui import GetWindowText, GetForegroundWindow
from views.courseview import CourseView
from views.discussionsview import DiscussionsView
from PIL import Image, ImageTk, ImageSequence
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime

from views.learninghub import LearningHub


class SearchPage(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="searchpage", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()

    def createFrames(self):
        self.loadSearchElements()
        self.helpdeskFrame = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="helpdeskframe",
        )
        self.loadHelpdeskElements()
        self.helpdeskFrame.grid_remove()

    def postLogin(self, data: dict):
        self.prisma = self.controller.mainPrisma
        self.userId = data["id"]
        self.role = data["role"]

    def loadSearchElements(self):
        self.staticImgs = [
            (r"Assets\SearchView\searchframe.png", 0, 0, "searchpagebg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")
        self.searchEntry = self.controller.ttkEntryCreator(
            xpos=100, ypos=220, width=420, height=60, root=self, classname="searchentry")
        self.searchEntry.insert(0, "Enter Keyword Here")
        self.searchEntry.bind(
            "<FocusIn>", lambda event: [
                self.searchEntry.delete(0, END)] if self.searchEntry.get() == "Enter Keyword Here" else None
        )
        self.searchEntry.bind("<FocusOut>", lambda event: [
            [self.searchEntry.delete(0, END),
             self.searchEntry.insert(0, "Enter Keyword Here")
             ] if self.searchEntry.get() == "" else None
        ])
        self.sortByVar = StringVar()
        self.sortByOptions = ["Relevance", "New", "Posts - Reply Count"]
        self.controller.menubuttonCreator(
            xpos=780, ypos=220, width=260, height=60,
            classname="sortbymenubtn", root=self,
            text="Relevance", listofvalues=self.sortByOptions,
            variable=self.sortByVar,
            command=lambda: self.sortByVar.set(self.sortByVar.get()),
        )
        self.sortByVar.set(self.sortByOptions[0])
        self.inPosts, self.inUploads, self.inHubContent = IntVar(), IntVar(), IntVar()
        self.inPosts.set(1)
        self.inUploads.set(1)
        self.inHubContent.set(1)
        self.searchInPosts = ttk.Checkbutton(
            master=self, bootstyle="success-outline-toolbutton",
            onvalue=1, offvalue=0, text="Discussion Posts",
            width=140, variable=self.inPosts,
            cursor="hand2"
        )
        self.searchInPosts.place(x=780, y=340, width=140, height=40)
        self.searchInUploads = ttk.Checkbutton(
            master=self, bootstyle="info-outline-toolbutton",
            onvalue=1, offvalue=0, text="Module Uploads",
            width=140, variable=self.inUploads,
            cursor="hand2"
        )
        self.searchInUploads.place(x=940, y=340, width=140, height=40)
        self.searchInHubContent = ttk.Checkbutton(
            master=self, bootstyle="secondary-outline-toolbutton",
            onvalue=1, offvalue=0, text="Hub Content",
            width=140, variable=self.inHubContent,
            cursor="hand2"
        )
        self.searchInHubContent.place(x=1100, y=340, width=140, height=40)
        self.staticBtns = [
            (r"Assets\SearchView\Search.png", 540, 220, "searchbtncreation", self,
             lambda: self.searchByQuery(self.searchEntry.get())),
            (r"Assets\SearchView\Click.png", 1460, 740, "loadhelpdeskbtn", self,
             lambda: [self.helpdeskFrame.grid(), self.helpdeskFrame.tkraise()]),
            (r"Assets\SearchView\MyTickets.png", 1520, 820, "loadhelpdesktickets", self,
             lambda: [self.helpdeskFrame.grid(), self.helpdeskFrame.tkraise()]),
        ]
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def searchByQuery(self, query: str):
        KL = timezone("Asia/Kuala_Lumpur")
        prisma = self.prisma
        if query == "" or query == "Enter Keyword Here":
            messagebox.showerror(
                title="Error", message="Please enter a keyword to search!"
            )
            return
        # print(self.inPosts.get(), self.inUploads.get(), self.inHubContent.get())
        modules = prisma.module.find_many(
            where={
                "OR": [
                    {
                        "lecturer": {
                            "is": {
                                "userId": self.userId
                            }
                        }
                    },
                    {
                        "moduleEnrollments": {
                            "some": {
                                "student": {
                                    "is": {
                                        "userId": self.userId
                                    }
                                }
                            }
                        }
                    }
                ],

            },
            include={
                "modulePosts": {
                    "include": {
                        "replies": True,
                        "author": True,
                    }
                } if self.inPosts.get() else False,
                "moduleHubContent": {
                    "include": {
                        "attempts": True,
                    }
                } if self.inHubContent.get() else False,
                "moduleUploads": True if self.inUploads.get() else False,
            }
        )
        finalList = []
        query = query.lower()  # convert query to lowercase
        for m in modules:
            if self.inPosts.get():
                for p in m.modulePosts:
                    # convert title and content to lowercase before searching
                    if query in p.title.lower() or query in p.content.lower():
                        finalList.append(
                            (m.moduleCode, p.id, p.title, p.author.fullName, "post"))
            if self.inHubContent.get():
                for h in m.moduleHubContent:
                    # convert title and description to lowercase before searching
                    if query in h.title.lower() or query in h.description.lower():
                        finalList.append(
                            (m.moduleCode, h.id, h.title, "hubcontent"))
            if self.inUploads.get():
                for u in m.moduleUploads:
                    # convert title and description to lowercase before searching
                    if query in u.title.lower() or query in u.description.lower():
                        finalList.append(
                            (m.moduleCode, u.id, u.title, u.objKey, u.uploadType, "upload"))
        if len(finalList) == 0:
            messagebox.showinfo(
                title="No Results Found", message="No results found for your search."
            )
            return
        self.loadSearchResults(finalList)

    def loadSearchResults(self, results: list):
        POSTPATH = r"Assets\SearchView\discpostsbutton.png"
        CONTENTPATH = r"Assets\SearchView\contentbutton.png"
        UPLOADPATH = r"Assets\SearchView\uploadsbutton.png"
        # Scrolled Frame
        self.scrolledframe = ScrolledFrame(
            master=self, width=1160, height=480, autohide=True, bootstyle="bg-round"
        )
        self.scrolledframe.place(x=100, y=400, width=1200, height=480)
        h = len(results) * 120 + 20
        if h < 480:
            h = 480
        self.scrolledframe.configure(height=h)
        initCoords = (20, 20)
        for result in results:
            typeOfResult = result[-1]
            if typeOfResult == "post":
                p = self.controller.textElement(
                    imagepath=POSTPATH, xpos=initCoords[0], ypos=initCoords[1],
                    classname=f"searchresult{result[0]}{typeOfResult}{result[1]}",
                    root=self.scrolledframe,
                    text=f"{result[0]} - {result[2]}\nA {typeOfResult.title()} by {result[3]}",
                    fg=WHITE, font=URBANIST, size=30, isPlaced=True,
                    xoffset=-2, yIndex=-0.4,
                    buttonFunction=lambda i=(
                        result[0], result[2]): self.navigateToModulePostView(i[0], i[1])
                )
            elif typeOfResult == "hubcontent":
                h = self.controller.textElement(
                    imagepath=CONTENTPATH, xpos=initCoords[0], ypos=initCoords[1],
                    classname=f"searchresult{result[0]}{typeOfResult}{result[1]}",
                    root=self.scrolledframe,
                    text=f"{result[0]} - {result[2]}\n{typeOfResult.title()}",
                    fg=WHITE, font=URBANIST, size=30, isPlaced=True,
                    xoffset=-2, yIndex=-0.4,
                    buttonFunction=lambda i=(
                        result[0], result[2]): self.navigateToModuleContentView(i[0], i[1])
                )
            elif typeOfResult == "upload":
                u = self.controller.textElement(
                    imagepath=UPLOADPATH, xpos=initCoords[0], ypos=initCoords[1],
                    classname=f"searchresult{result[0]}{typeOfResult}{result[1]}",
                    root=self.scrolledframe,
                    text=f"{result[0]} - {result[2]}\nHub Content",
                    fg=WHITE, font=URBANIST, size=30, isPlaced=True,
                    xoffset=-2, yIndex=-0.4,
                    buttonFunction=lambda i=(result[0], result[3], result[4]): self.navigateToModuleUploadView(
                        i[0], i[1], i[2])
                )
            initCoords = (initCoords[0], initCoords[1] + 120)

    def loadHelpdeskElements(self):
        # Entry
        self.nameEntry = self.controller.ttkEntryCreator(
            xpos=340, ypos=260, width=520, height=60, root=self.helpdeskFrame, classname="helpdeskframe")

        self.nameEntry.insert(0, "Enter Name Here")

        self.emailEntry = self.controller.ttkEntryCreator(
            xpos=1080, ypos=260, width=600, height=60, root=self.helpdeskFrame, classname="emailentry")

        self.emailEntry.insert(0, "Enter E-mail Here")

        # Scrolled Text
        self.scrolledtext = ScrolledText(
            master=self.helpdeskFrame, width=630, height=330, autohide=True)
        self.scrolledtext.place(x=222, y=402, width=630, height=330)
        self.textArea = self.scrolledtext.text
        self.textArea.configure(font=(INTERBOLD, 20))

        self.helpdeskLabels = [
            (r"Assets\SearchView\helpdeskframebg.png", 0,
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
            (r"Assets\SearchView\imagebutton.png", 1180, 340,
             "helpdeskimage", self.helpdeskFrame,
             lambda: print("UploadImage"))
        ]
        self.controller.settingsUnpacker(self.helpdeskButtons, "button")

    def navigateToModuleContentView(self, courseCode, contentTitle, hub: LearningHub = None):
        hub = self.controller.widgetsDict["learninghub"]
        hub.role = self.role
        hub.prisma = self.controller.mainPrisma
        hub.loadCourseHubContent(courseCode)
        hub.learninghubquizzesvar.set(contentTitle)
        self.controller.widgetsDict["learninghubquizzesmb"].config(
            text=contentTitle)
        hub.loadQuizHubContent(contentTitle)
        self.controller.show_canvas(LearningHub)

    def navigateToModulePostView(self, modulecode, moduletitle, discview: DiscussionsView = None):
        toast = ToastNotification(
            title=f"Loading Discussions for {modulecode}",
            message="Please wait while we load the discussions for this module",
            bootstyle="info"
        )
        toast.show_toast()
        discview = self.controller.widgetsDict["discussionsview"]
        discview.role = self.role
        discview.prisma = self.controller.mainPrisma
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

    def navigateToModuleUploadView(self, modulecode, objKey, filetype, courseview: CourseView = None):
        courseview = self.controller.widgetsDict["courseview"]
        courseview.role = self.role
        courseview.prisma = self.controller.mainPrisma
        courseview.loadCourses(f"{modulecode.upper()}")
        courseview.viewUploadsFrame.grid_remove()
        courseview.uploadCreationFrame.grid_remove()
        courseview.loadModuleUploadsView(modulecode.lower())
        courseview.loadAndOpenObject(objKey, filetype)
        self.controller.show_canvas(CourseView)
