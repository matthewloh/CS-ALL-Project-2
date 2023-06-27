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

        self.createElements()
        self.dateentry = DateEntry(
            self, width=1,
        )
        self.dateentry.place(x=1420, y=140, width=460, height=60)
        print(self.dateentry.entry.get())
        self.scrolledframe = ScrolledFrame(
            self, width=460, height=920, name="appointmentscrolledframe", autohide=True,
        )
        self.scrolledframe.place(
            x=1420, y=220, width=460, height=680
        )
        gridGenerator(self.scrolledframe, int(460/20), int(920/20), DARKBLUE)

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
        self.creationFrame.grid_remove()
        self.viewFrame.grid_remove()

    def createFrames(self):
        self.creationFrame = self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="appointmentscreation",
        )
        self.viewFrame = self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="appointmentsmanage",
        )
        self.apptCreateFrame = self.controller.frameCreator(
            xpos=0, ypos=120, framewidth=1920, frameheight=800,
            root=self.creationFrame, classname="apptcreateframe",
        )

    def createElements(self):
        self.staticImgLabels = [
            (r"Assets\AppointmentsView\appointmentsdashboard.png",
             0, 0, "AppointmentsBG", self),
            (r"Assets\AppointmentsView\TitleLabel.png",
             0, 0, "AppointmentsHeader", self),
            (r"Assets\AppointmentsView\appointmentcreationbg.png",
             0, 0, "appcreationbg", self.creationFrame),
            (r"Assets\AppointmentsView\appmanagebg.png",
             0, 0, "appmanagebg", self.viewFrame),
            (r"Assets\AppointmentsView\apptcreationframebg.png",
             0, 0, "apptcreationframebg", self.apptCreateFrame),
        ]
        self.staticBtns = [
            (r"Assets\AppointmentsView\Create Appointment.png", 60, 600, "createappointmentbtn", self,
             lambda: self.loadAppCreation()),
            (r"Assets\AppointmentsView\manageappointments.png", 720, 600, "manageappointmentsbtn", self,
             lambda: self.loadAppView()),
            (r"Assets\My Courses\exitbutton.png", 1820, 20, "appcreateexitbtn", self.creationFrame,
             lambda: self.unloadAppCreation()),
            (r"Assets\My Courses\exitbutton.png", 1820, 20, "appviewexitbtn", self.viewFrame,
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
        self.loadAllDetailsForCreation()

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
        return appContentList

    def loadForLecturer(self):
        prisma = self.prisma
        # save for later
        pass

    def loadForStudent(self):
        prisma = self.prisma
        modules = prisma.moduleenrollment.find_many(
            where={
                "student": {
                    "is": {
                        "userId": self.userId
                    }
                }
            },
            include={
                "module": {
                    "include": {
                        "lecturer": {
                            "include": {
                                "userProfile": True,
                                "apptSettings": True
                            }
                        }
                    }
                }
            }
        )
        return modules

    def loadLecturerMenuBtns(self, modCode):
        for widgetname, widget in self.creationFrame.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["lecturersaptmenuhostfr", "timeslotmenuhostfr"]:
                    widget.grid_remove()
        # reset variables
        for var in [self.lecturer, self.timeslot]:
            var.set("")
        positions = {
            "lecturer": {"x": 540, "y": 620, "width": 320, "height": 60},
        }
        # self.moduleDict[modCode] returns
        timeslotlist = list(self.moduleDict[modCode].keys())
        self.controller.menubuttonCreator(
            xpos=positions["lecturer"]["x"], ypos=positions["lecturer"]["y"], width=positions[
                "lecturer"]["width"], height=positions["lecturer"]["height"],
            root=self.creationFrame, classname="lecturersaptmenu", text="Select Lecturer", listofvalues=timeslotlist,
            variable=self.lecturer, font=("Helvetica", 12),
            command=lambda: self.loadTimeslotMenuBtns(
                modCode, self.lecturer.get())
        )

    def loadTimeslotMenuBtns(self, modCode, lecturer):
        for widgetname, widget in self.creationFrame.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["timeslotmenuhostfr"]:
                    widget.grid_remove()
        # reset variables
        for var in [self.timeslot]:
            var.set("")
        positions = {
            "timeslot": {"x": 920, "y": 620, "width": 320, "height": 60},
        }
        timeslotlist = self.moduleDict[modCode][lecturer]
        self.controller.menubuttonCreator(
            xpos=positions["timeslot"]["x"], ypos=positions["timeslot"]["y"], width=positions[
                "timeslot"]["width"], height=positions["timeslot"]["height"],
            root=self.creationFrame, classname="timeslotmenu", text="Select Timeslot", listofvalues=timeslotlist,
            variable=self.timeslot, font=("Helvetica", 12),
            command=lambda: print(f"timeslot selected: {self.timeslot.get()}")
        )

    def loadAllDetailsForCreation(self):
        # MODULE -> LECTURER -> TIMESLOT
        for widgetname, widget in self.creationFrame.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["moduleshostfr", "lecturersaptmenuhostfr", "timeslotmenuhostfr"]:
                    widget.grid_remove()
        self.moduleDict = {}
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        # 10:00AM strfmt
        humanreadable = r"%I:%M%p"
        if self.role == "lecturer":
            self.fullinfo = self.loadForLecturer()
        elif self.role == "student":
            self.fullinfo = self.loadForStudent()
        for me in self.fullinfo:
            lecturerDict = {}
            lecturer = me.module.lecturer.userProfile.fullName
            apptStgTimes = []
            for apptStg in me.module.lecturer.apptSettings:
                day = apptStg.day
                location = apptStg.location
                starttime = kualalumpur.convert(
                    apptStg.startTime).strftime(humanreadable)
                endtime = kualalumpur.convert(
                    apptStg.endTime).strftime(humanreadable)
                # 10:00AM - 11:00AM
                formattedTime = f"{day}, {starttime} - {endtime} at {location}"
                apptStgTimes.append(formattedTime)
                lecturerDict[f"{lecturer}"] = apptStgTimes
            self.moduleDict[f"{me.module.moduleCode} - {me.module.moduleTitle}"] = lecturerDict
        modulelist = list(self.moduleDict.keys())
        lists = {
            "modules": modulelist,
        }
        self.module = StringVar()
        self.lecturer = StringVar()
        self.timeslot = StringVar()
        for var in [self.module, self.lecturer, self.timeslot]:
            var.set("")
        vars = {
            "modules": self.module,
            "lecturers": self.lecturer,
            "timeslots": self.timeslot,
        }
        positions = {
            "modules": {"x": 160, "y": 620, "width": 320, "height": 60},
        }
        for name, values in lists.items():
            self.controller.menubuttonCreator(
                xpos=positions[name]["x"], ypos=positions[name]["y"], width=positions[name]["width"], height=positions[name]["height"],
                root=self.creationFrame, classname=name, text=f"Select {name}", listofvalues=values,
                variable=vars[name], font=("Helvetica", 12),
                command=lambda name=name: [
                    self.loadLecturerMenuBtns(vars[name].get())
                ]
            )

    def loadAllAppointments(self):
        prisma = self.prisma

        
    def loadAppDetailsFrame(self):
        buttonsList = [
            (r"Assets\My Courses\exituploadsview.png", 1300, 40, "exitapptcreation",
             self.apptCreateFrame, lambda: self.unloadAppCreationDetails()),
        ]
        self.controller.settingsUnpacker(buttonsList, "button")
        self.apptCreateFrame.grid()
        self.apptCreateFrame.tkraise()
        self.appTitleEntry = self.controller.ttkEntryCreator(
            xpos=480, ypos=160, width=720, height=60,
            root=self.apptCreateFrame, classname="apptcreatetitle"
        )
        self.apptDesc = self.controller.ttkEntryCreator(
            xpos=480, ypos=240, width=720, height=120,
            root=self.apptCreateFrame, classname="apptdescription"
        )
        self.apptLocation = self.controller.ttkEntryCreator(
            xpos=480, ypos=480, width=720, height=60,
            root=self.apptCreateFrame, classname="apptlocation"
        )
        self.apptLocation.insert(0, self.timeslot.get())
        self.startDateSelector = DateEntry(
            master=self.apptCreateFrame, dateformat= "%d/%m/%Y"
        )
        self.startDateSelector.place(x=480, y=560, width=280, height=60)
        self.endDateSelector = DateEntry(
            master=self.apptCreateFrame,  dateformat= "%d/%m/%Y"
        )
        self.endDateSelector.place(x=480, y=640, width=280, height=60)
        self.startTime = self.controller.ttkEntryCreator(
            xpos = 780, ypos = 560, width=420, height=60,
            root=self.apptCreateFrame, classname="starttimeentry"
        )
        self.endTime = self.controller.ttkEntryCreator(
            xpos = 780, ypos = 640, width=420, height=60,
            root=self.apptCreateFrame, classname="endtimeentry"
        )
        self.startTime.insert(0, self.timeslot.get())
        self.endTime.insert(0, self.timeslot.get())

        
    
    
    def loadAppCreation(self):
        self.apptCreateFrame.grid_remove()
        self.creationFrame.grid()
        self.creationFrame.tkraise()
        # self.loadAllDetailsForCreation()
        btnsettings = [
            (r"Assets\AppointmentsView\continuecreationbtn.png", 520, 740, "continuecreation", self.creationFrame,
             lambda: self.loadAppDetailsFrame()),
        ]
        self.controller.settingsUnpacker(btnsettings, "button")
    # loads the confirmation screen.

    def unloadAppCreation(self):
        self.creationFrame.grid_remove()
    def unloadAppCreationDetails(self):
        self.apptCreateFrame.grid_remove()

    def loadAppView(self):
        self.viewFrame.grid()
        self.viewFrame.tkraise()
        self.viewScrolledFrame = ScrolledFrame(
            self.viewFrame, width=520, height=740, autohide=True,
        )
        self.viewScrolledFrame.place(
            x=60, y=120, width=520, height=740
        )

    def unloadAppView(self):
        self.viewFrame.grid_remove()
        # for app in appointments:
        #     print(app)
