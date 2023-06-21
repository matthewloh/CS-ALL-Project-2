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

from PIL import Image, ImageTk, ImageSequence
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime

class AppointmentsView(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1, bg=WHITE,
                        name="appointmentsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()
        self.creationframe = self.controller.widgetsDict["appointmentscreation"]
        self.viewFrame = self.controller.widgetsDict["appointmentsmanage"]
        self.createElements()
        self.dateentry = DateEntry(
            self, width=1, 
        )
        self.dateentry.place(x=1420, y=140, width=460, height=60)
        print(self.dateentry.entry.get())
        self.scrolledframe = ScrolledFrame(
            self, width=1, height=920, name="appointmentscrolledframe", autohide=True, padding=0
        )
        self.scrolledframe.place(
            x=1420, y=220, width=460, height=680
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
        self.creationframe.grid_remove()
        self.viewFrame.grid_remove()
    

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
            (r"Assets\AppointmentsView\appmanagebg.png",
                0, 0, "appmanagebg", self.viewFrame),
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
        if appointments == []:
            return None
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