import base64
import io
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
from prisma import Base64
from prisma.models import HelpdeskTicket
from win32gui import GetWindowText, GetForegroundWindow
from views.courseview import CourseView
from views.discussionsview import DiscussionsView
from PIL import Image, ImageTk, ImageSequence, ImageOps
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
        self.helpdeskViewFrame = self.controller.frameCreator(
            xpos=40, ypos=120, framewidth=1840, frameheight=780,
            root=self.helpdeskFrame, classname="helpdeskviewticketframe",
        )
        self.adminFrame = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="helpdeskadminframe",
        )
        self.loadHelpdeskElements()
        self.loadHelpdeskViewTicketElements()
        self.helpdeskViewFrame.grid_remove()
        self.helpdeskFrame.grid_remove()
        self.adminFrame.grid_remove()

    def postLogin(self, data: dict):
        try:
            self.adminFrame.grid_remove()
        except:
            pass
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
            "<Return>", lambda event: self.searchByQuery(
                self.searchEntry.get())
        )
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
             lambda: self.navigateToHelpdesk()),
            (r"Assets\SearchView\MyTickets.png", 1520, 820, "loadhelpdesktickets", self,
             lambda: self.navigateToHelpdeskView()),
        ]
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def navigateToHelpdesk(self):
        try:
            self.loadAdminManageBtn.grid_remove()
        except:
            pass
        self.helpdeskFrame.grid()
        self.helpdeskFrame.tkraise()
        if self.role == "lecturer":
            user = self.prisma.userprofile.find_first(
                where={
                    "id": self.userId
                }
            )
            if user.isAdmin:
                self.loadAdminManageBtn = self.controller.buttonCreator(
                    imagepath=r"Assets\SearchView\Helpdesk\managetickets.png",
                    xpos=1560, ypos=20,
                    classname="helpdeskmanagetickets", root=self.helpdeskFrame,
                    buttonFunction=lambda: self.loadAdminView()
                )

    def loadAdminView(self):
        self.adminFrame.grid()
        self.adminFrame.tkraise()

    def navigateToHelpdeskView(self):
        self.navigateToHelpdesk()
        self.helpdeskViewFrame.grid()
        self.helpdeskViewFrame.tkraise()
        self.loadTickets()

    def loadTickets(self):
        prisma = self.prisma
        TICKETBG = r"Assets\SearchView\Helpdesk\tickettextbg.png"
        tickets = prisma.helpdeskticket.find_many(
            where={
                "authorId": self.userId
            },
            include={
                "replies": {
                    "include": {
                        "author": True
                    }
                },
                "author": True
            }
        )
        self.viewTicketScrFrame = ScrolledFrame(
            master=self.helpdeskViewFrame, width=880, height=620, bootstyle="bg-round", autohide=True
        )
        self.viewTicketScrFrame.place(x=20, y=120, width=880, height=620)
        h = len(tickets) * 120 + 20
        if h < 620:
            h = 620
        self.viewTicketScrFrame.config(height=h)
        initCoords = (20, 20)
        for ticket in tickets:
            t = self.controller.textElement(
                imagepath=TICKETBG, xpos=initCoords[0], ypos=initCoords[1],
                classname=f"ticket{ticket.id}", root=self.viewTicketScrFrame,
                text=f"{ticket.title}\n{ticket.status}",
                fg=BLACK, size=30, isPlaced=True, font=INTERBOLD,
                xoffset=-2, yIndex=-0.3,
                buttonFunction=lambda i=(ticket): self.loadTicket(i)
            )
            initCoords = (initCoords[0], initCoords[1] + 120)

    def loadTicket(self, ticket: HelpdeskTicket):
        try:
            self.exitViewReplies()
        except:
            pass
        img = self.decodingBase64data(ticket.image)
        img.thumbnail((800, 580))
        self.placeholderImg = self.controller.buttonCreator(
            imagepath=r"Assets\SearchView\Helpdesk\blanklabelforview.png",
            xpos=980, ypos=140, root=self.helpdeskViewFrame, classname="imgplaceholder",
            buttonFunction=lambda: self.loadRepliesForTicket(ticket)
        )
        self.controller.imageDict["imgplaceholder"] = ImageTk.PhotoImage(
            img)
        newImage = self.controller.imageDict["imgplaceholder"]
        self.placeholderImg.config(image=newImage, width=800, height=580)
        # x = 1020, y = 220, calculate the new x and y
        self.placeholderImg.place(x=980+(800-img.width)/2,
                                  y=140+(580-img.height)/2,
                                  width=img.width, height=img.height)

        self.placeholderImg.bind("<Enter>", self.showImageSize)
        self.placeholderImg.bind("<Leave>", self.hideImageSize)

    def decodingBase64data(self, b64):
        decoded = Base64.decode(b64)
        dataBytesIO = io.BytesIO(decoded)
        im = Image.open(dataBytesIO)
        return im

    def loadRepliesForTicket(self, ticket: HelpdeskTicket):
        try:
            self.repliesScrolledFrame.place_forget()
        except:
            pass
        self.repliesScrolledFrame = ScrolledFrame(
            master=self.helpdeskViewFrame, width=840, height=620, bootstyle="info-round", autohide=True
        )
        self.repliesScrolledFrame.place(x=960, y=120, width=840, height=620)
        h = len(ticket.replies) * 140 + 20
        if h < 620:
            h = 620
        self.controller.buttonCreator(
            imagepath=r"Assets\SearchView\Helpdesk\exitviewreplies.png",
            xpos=1760, ypos=120, root=self.helpdeskViewFrame, classname="exitviewreplies",
            isPlaced=True,
            buttonFunction=lambda: self.exitViewReplies()
        )
        self.addReplyBtn = self.controller.buttonCreator(
            imagepath=r"Assets\SearchView\Helpdesk\addreplybtn.png",
            xpos=960, ypos=120, root=self.helpdeskViewFrame, classname="addreplybtntoticket",
            isPlaced=True,
            buttonFunction=lambda: self.addReplyToTicket(ticket)
        )
        self.repliesScrolledFrame.config(height=h)
        initCoords = (40, 80)
        for reply in ticket.replies:
            if reply.authorId == self.userId:
                repText = f"You - {reply.content}"
            else:
                repText = f"{reply.author.fullName} - {reply.content}"
            r = self.controller.textElement(
                imagepath=r"Assets\SearchView\Helpdesk\replybg.png",
                xpos=initCoords[0], ypos=initCoords[1],
                classname=f"reply{reply.id}", root=self.repliesScrolledFrame,
                text=repText,
                fg=WHITE, size=30, isPlaced=True, font=INTERBOLD,
                yIndex=-0.2,
            )
            initCoords = (initCoords[0], initCoords[1] + 140)

    def addReplyToTicket(self, ticket: HelpdeskTicket):
        prisma = self.prisma
        replyContent = Querybox.get_string(
            title="Add Reply", prompt="Enter your reply here",
            parent=self.addReplyBtn,
        )
        if replyContent == "" or replyContent is None:
            return
        prisma.ticketreply.create(
            data={
                "authorId": self.userId,
                "content": replyContent,
                "ticketId": ticket.id
            }
        )
        newTicket = prisma.helpdeskticket.find_first(
            where={
                "id": ticket.id
            },
            include={
                "author": True,
                "replies": {
                    "include": {
                        "author": True
                    }
                }
            }
        )
        self.loadRepliesForTicket(newTicket)

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
                            (m.moduleCode, p.id, p.title, p.author.fullName, m.moduleTitle, "post"))
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
                        result[0], result[4]): self.navigateToModulePostView(modulecode=i[0], moduletitle=i[1])
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

    def loadHelpdeskViewTicketElements(self):
        self.helpdeskViewLabels = [
            (r"Assets\SearchView\Helpdesk\viewticketbg.png", 0, 0,
             "helpdeskviewbg", self.helpdeskViewFrame),
        ]
        self.controller.settingsUnpacker(self.helpdeskViewLabels, "label")
        self.helpdeskViewButtons = [
            (r"Assets\SearchView\Helpdesk\exithelpdeskview.png", 1760, 0,
             "helpdeskviewexit", self.helpdeskViewFrame,
             lambda: self.exitHelpdeskView()),
        ]
        self.controller.settingsUnpacker(self.helpdeskViewButtons, "button")

    def exitHelpdeskView(self):
        try:
            self.repliesScrolledFrame.place_forget()
        except:
            pass
        try:
            self.placeholderImg.place_forget()
        except:
            pass
        try:
            self.exitViewReplies()
        except:
            pass
        self.helpdeskViewFrame.grid_remove()

    def exitViewReplies(self):
        self.repliesScrolledFrame.place_forget(),
        self.controller.widgetsDict["exitviewreplies"].place_forget(),
        self.controller.widgetsDict["addreplybtntoticket"].place_forget()

    def loadHelpdeskElements(self):
        self.helpdeskLabels = [
            (r"Assets\SearchView\Helpdesk\helpdeskbg.png", 0, 0,
             "helpdeskbg", self.helpdeskFrame),
            (r"Assets\SearchView\Helpdesk\adminframebg.png", 0, 0,
             "helpdeskadminframebg", self.adminFrame),
        ]
        self.controller.settingsUnpacker(self.helpdeskLabels, "label")
        self.helpdeskButtons = [
            (r"Assets\SearchView\helpdeskreturnbtn.png", 60, 840,
             "helpdeskreturnbtn", self.helpdeskFrame,
             lambda: self.helpdeskFrame.grid_remove()),
            (r"Assets\SearchView\Helpdesk\submitticket.png", 1640, 840,
             "helpdesksubmit", self.helpdeskFrame,
             lambda: self.submitHelpdeskTicket()),
            (r"Assets\SearchView\Helpdesk\uploadimagebtn.png", 1420, 120,
             "helpdeskupload", self.helpdeskFrame,
             lambda: self.uploadImage()),
            (r"Assets\SearchView\Helpdesk\gotomytickets.png", 700, 40,
             "helpdeskviewtickets", self.helpdeskFrame,
             lambda: self.navigateToHelpdeskView()),
            (r"Assets\SearchView\Helpdesk\exitadminframe.png", 1800, 120,
             "helpdeskexitadminframe", self.adminFrame,
             lambda: self.adminFrame.grid_remove()),
        ]
        self.controller.settingsUnpacker(self.helpdeskButtons, "button")
        self.titleEntry = self.controller.ttkEntryCreator(
            xpos=60, ypos=280, width=880, height=60, root=self.helpdeskFrame, classname="helpdeskframe"
        )
        self.scrolledtext = ScrolledText(
            master=self.helpdeskFrame, width=880, height=400, autohide=True, bootstyle="bg-rounded"
        )
        self.scrolledtext.text.config(
            font=(INTERBOLD, 20), bg=WHITE, fg=BLACK, insertbackground=BLACK, highlightthickness=0
        )
        self.scrolledtext.place(x=60, y=420, width=880, height=400)
        self.textArea = self.scrolledtext.text
        self.textArea.configure(font=(INTERBOLD, 20))

    def uploadImage(self):
        self.imagePath = filedialog.askopenfilename(
            initialdir="Assets", title="Select file", filetypes=(
                ("Image Files", "*.jpg *.png *.jpeg *.webp"),
            )
            # ("Image Files", "*.jpg *.png *.jpeg *.gif *webp")
        )
        if self.imagePath == "":
            return
        # ask if want to maintain aspect ratio or crop to fit
        img = Image.open(self.imagePath)
        # getting the dimensions of the image
        ask = MessageDialog(
            parent=self.controller.widgetsDict["helpdeskupload"],
            title="Select an option",
            message="Submit using Pad to maintain a 4:3 aspect ratio with white border\nSubmit using Thumbnail in original aspect ratio with no padding\nSelect fit for completely filling 800x600\nYou may hover over the image to see the size submitted.",
            buttons=["Pad:success", "Thumbnail:secondary",
                     "Fit:info", "Cancel"],
        )
        ask.show()
        if ask.result == "Pad":
            self.imageLabel = self.controller.labelCreator(
                imagepath=self.imagePath, xpos=1020, ypos=220,
                classname="helpdeskimage", root=self.helpdeskFrame,
                isPlaced=True
            )
            image = self.controller.imagePathDict["helpdeskimage"]
            image = Image.open(image)
            image = ImageOps.pad(image, (800, 600))
            self.controller.imageDict["helpdeskimage"] = ImageTk.PhotoImage(
                image)
            newImage = self.controller.imageDict["helpdeskimage"]
            self.imageLabel.config(image=newImage, width=800, height=600)
            # x = 1020, y = 220, calculate the new x and y
            self.imageLabel.place(x=1020+(800-image.width)/2,
                                  y=220+(600-image.height)/2,
                                  width=image.width, height=image.height)
        elif ask.result == "Thumbnail":
            self.imageLabel = self.controller.labelCreator(
                imagepath=self.imagePath, xpos=1020, ypos=220,
                classname="helpdeskimage", root=self.helpdeskFrame,
                isPlaced=True
            )
            image = self.controller.imagePathDict["helpdeskimage"]
            image = Image.open(image)
            image.thumbnail((800, 600))
            self.controller.imageDict["helpdeskimage"] = ImageTk.PhotoImage(
                image)
            newImage = self.controller.imageDict["helpdeskimage"]
            self.imageLabel.config(image=newImage, width=800, height=600)
            # x = 1020, y = 220, calculate the new x and y
            self.imageLabel.place(x=1020+(800-image.width)/2,
                                  y=220+(600-image.height)/2,
                                  width=image.width, height=image.height)
        elif ask.result == "Fit":
            self.imageLabel = self.controller.labelCreator(
                imagepath=self.imagePath, xpos=1020, ypos=220,
                classname="helpdeskimage", root=self.helpdeskFrame,
                isPlaced=True
            )
            image = self.controller.imagePathDict["helpdeskimage"]
            image = Image.open(image)
            image = ImageOps.fit(image, (800, 600))
            self.controller.imageDict["helpdeskimage"] = ImageTk.PhotoImage(
                image)
            newImage = self.controller.imageDict["helpdeskimage"]
            self.imageLabel.config(image=newImage, width=800, height=600)
            # x = 1020, y = 220, calculate the new x and y
            self.imageLabel.place(x=1020+(800-image.width)/2,
                                  y=220+(600-image.height)/2,
                                  width=image.width, height=image.height)
        self.finalImage = image
        self.imageLabel.bind("<Enter>", self.showImageSize)
        self.imageLabel.bind("<Leave>", self.hideImageSize)
        self.cropOptions = [
            (r"Assets\SearchView\Helpdesk\pad.png", 1020, 180,
             "padoption", self.helpdeskFrame, lambda: self.cropImage("pad")),
            (r"Assets\SearchView\Helpdesk\thumbnail.png", 1140, 180,
             "thumbnailoption", self.helpdeskFrame, lambda: self.cropImage("thumbnail")),
            (r"Assets\SearchView\Helpdesk\fit.png", 1260, 180,
             "fitoption", self.helpdeskFrame, lambda: self.cropImage("fit")),
            (r"Assets\SearchView\Helpdesk\canceluploadimg.png", 1720, 180,
             "canceluploadimg", self.helpdeskFrame, lambda: self.cancelImageUpload())
        ]
        self.controller.settingsUnpacker(self.cropOptions, "button")

    def cropImage(self, option):
        if option == "pad":
            image = self.controller.imagePathDict["helpdeskimage"]
            image = Image.open(image)
            image = ImageOps.pad(image, (800, 600))
            self.controller.imageDict["helpdeskimage"] = ImageTk.PhotoImage(
                image)
            newImage = self.controller.imageDict["helpdeskimage"]
            self.imageLabel.config(image=newImage, width=800, height=600)
            # x = 1020, y = 220, calculate the new x and y
            self.imageLabel.place(x=1020+(800-image.width)/2,
                                  y=220+(600-image.height)/2,
                                  width=image.width, height=image.height)
        elif option == "thumbnail":
            image = self.controller.imagePathDict["helpdeskimage"]
            image = Image.open(image)
            image.thumbnail((800, 600))
            self.controller.imageDict["helpdeskimage"] = ImageTk.PhotoImage(
                image)
            newImage = self.controller.imageDict["helpdeskimage"]
            self.imageLabel.config(image=newImage, width=800, height=600)
            # x = 1020, y = 220, calculate the new x and y
            self.imageLabel.place(x=1020+(800-image.width)/2,
                                  y=220+(600-image.height)/2,
                                  width=image.width, height=image.height)
        elif option == "fit":
            image = self.controller.imagePathDict["helpdeskimage"]
            image = Image.open(image)
            image = ImageOps.fit(image, (800, 600))
            self.controller.imageDict["helpdeskimage"] = ImageTk.PhotoImage(
                image)
            newImage = self.controller.imageDict["helpdeskimage"]
            self.imageLabel.config(image=newImage, width=800, height=600)
            # x = 1020, y = 220, calculate the new x and y
            self.imageLabel.place(x=1020+(800-image.width)/2,
                                  y=220+(600-image.height)/2,
                                  width=image.width, height=image.height)
        self.finalImage = image
        self.imageLabel.bind("<Enter>", self.showImageSize)
        self.imageLabel.bind("<Leave>", self.hideImageSize)

    def cancelImageUpload(self):
        self.imageLabel.place_forget()
        for btnname in ["padoption", "thumbnailoption", "fitoption", "canceluploadimg"]:
            self.controller.widgetsDict[btnname].grid_remove()

    def getBase64data(self):
        byteIMGIO = io.BytesIO()
        format = self.imagePath.split(".")[-1]
        self.finalImage.save(byteIMGIO, f"{format.upper()}")
        byteIMGIO.seek(0)
        byteIMG = byteIMGIO.read()
        b64 = Base64.encode(byteIMG)
        return b64

    def submitHelpdeskTicket(self):
        if self.titleEntry.get() == "":
            messagebox.showerror("Error", "Please enter a title")
            return
        prisma = self.prisma
        prisma.helpdeskticket.create(
            data={
                "authorId": self.userId,
                "title": self.titleEntry.get(),
                "content": self.scrolledtext.text.get("1.0", "end-1c"),
                "image": self.getBase64data(),
            }
        )
        self.cancelImageUpload()

    def showImageSize(self, event):
        try:
            self.imageLabel.config(relief="solid")
        except:
            pass
        try:
            self.placeholderImg.config(relief="solid")
        except:
            pass

    def hideImageSize(self, event):
        try:
            self.imageLabel.config(relief="flat")
        except:
            pass
        try:
            self.placeholderImg.config(relief="flat")
        except:
            pass

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
