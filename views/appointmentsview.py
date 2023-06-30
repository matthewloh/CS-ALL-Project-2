import re
import threading
from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
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
        self.lecAddTimeslotFrame = self.controller.frameCreator(
            xpos=0, ypos=120, framewidth=1920, frameheight=800,
            root=self.creationFrame, classname="lecaddtimeslotframe",
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
            (r"Assets\AppointmentsView\LecturerTimeslots\lecturertimeslotbg.png",
             0, 0, "lecaddtimeslotbg", self.lecAddTimeslotFrame),
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

    def postLogin(self, data: dict = None):
        self.prisma = self.controller.mainPrisma
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
        lecturer = prisma.lecturer.find_first(
            where={
                "userProfile": {
                    "is": {
                        "id": self.userId
                    }
                }
            },
            include={
                "apptSettings": True,
                "userProfile": True
            }
        )
        return lecturer

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
            self.lecturerList = self.loadForLecturer()
            self.loadAsLecturer(kualalumpur, humanreadable)
        elif self.role == "student":
            self.fullinfo = self.loadForStudent()
            self.loadAsStudent(kualalumpur, humanreadable)

    # loadaslecturer will be using self.lecAddTimeslotFrame
    # there will be a location ttkEntryCreator
    # a select day menubuttonCreator
    # similar to start and end time
    # will require the ID of the lecaptsettingfield
    # id, lecturerid, day, starttime, endtime, location
    def loadAsLecturer(self, kualalumpur, humanreadable):
        self.LECAPTDAYS = [
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        # creating a list of DateTime objects using list comprehension, returns string format in format of 10:00AM
        start_time = datetime.strptime("08:00AM", "%I:%M%p")
        end_time = datetime.strptime("06:00PM", "%I:%M%p")
        pos = {
            "aptstglocationent": {"x": 140, "y": 340, "width": 240, "height": 60},
            "aptstgdaymb": {"x": 140, "y": 420, "width": 240, "height": 60},
            "aptstgstarttimemb": {"x": 140, "y": 500, "width": 240, "height": 60},
            "aptstgendtimemb": {"x": 140, "y": 580, "width": 240, "height": 60},
        }

        ENAME = "aptstglocationent"
        self.aptstglocationEnt = self.controller.ttkEntryCreator(
            root=self.lecAddTimeslotFrame, xpos=pos[ENAME]["x"], ypos=pos[ENAME]["y"],
            width=pos[ENAME]["width"], height=pos[ENAME]["height"], classname=ENAME
        )
        time_slots = [start_time + timedelta(minutes=30*i) for i in range(21)]
        time_slots_str = [ts.strftime("%I:%M%p") for ts in time_slots]
        lists = {
            "aptstgdaymb": self.LECAPTDAYS,
            "aptstgstarttimemb": time_slots_str,
            "aptstgendtimemb": time_slots_str
        }
        # stringvars
        self.aptstgdaymbvar = StringVar()
        self.aptstgstarttimembvar = StringVar()
        self.aptstgendtimembvar = StringVar()

        vars = {
            "aptstgdaymb": self.aptstgdaymbvar,
            "aptstgstarttimemb": self.aptstgstarttimembvar,
            "aptstgendtimemb": self.aptstgendtimembvar
        }
        selectName = {
            "aptstgdaymb": "Select Day",
            "aptstgstarttimemb": "Select Start Time",
            "aptstgendtimemb": "Select End Time"
        }

        # self.aptstgdaymbvar.set("MONDAY")
        # self.aptstgstarttimembvar.set("08:00AM")
        # self.aptstgendtimembvar.set("06:00PM")
        for name, values in lists.items():
            self.controller.menubuttonCreator(
                root=self.lecAddTimeslotFrame, xpos=pos[name]["x"], ypos=pos[name]["y"],
                width=pos[name]["width"], height=pos[name][
                    "height"], classname=name, text=f"{selectName[name]}",
                listofvalues=values, variable=vars[name], font=(
                    "Helvetica", 16),
                command=lambda name=name: [
                    self.validateDateVars(name, vars[name].get()),
                ]
            )
        # set the default values
        self.aptstgdaymbvar.set(self.LECAPTDAYS[0])
        self.aptstgstarttimembvar.set(time_slots_str[0])
        self.aptstgendtimembvar.set(time_slots_str[-1])
        self.controller.widgetsDict["aptstgdaymb"].configure(
            text=self.aptstgdaymbvar.get())
        self.controller.widgetsDict["aptstgstarttimemb"].configure(
            text=self.aptstgstarttimembvar.get())
        self.controller.widgetsDict["aptstgendtimemb"].configure(
            text=self.aptstgendtimembvar.get())

        self.lecAptSettings = self.lecturerList.apptSettings
        fullTimeslots = []
        for i in self.lecturerList.apptSettings:
            stgId = i.id
            day = i.day
            location = i.location
            starttime = kualalumpur.convert(
                i.startTime).strftime(humanreadable)
            endtime = kualalumpur.convert(
                i.endTime).strftime(humanreadable)
            # 10:00AM - 11:00AM
            formattedTime = f"{day}, {starttime} - {endtime} at {location}"
            fullTimeslots.append(
                (stgId, formattedTime, day, starttime, endtime, location))

        # renderAsATextElement
        self.timeScrolledFrame = ScrolledFrame(
            self.lecAddTimeslotFrame, width=820, height=300, autohide=True, bootstyle="warning-rounded"
        )
        self.timeScrolledFrame.place(
            x=420, y=340, width=820, height=300
        )
        h = (len(fullTimeslots)) * 100 + 20
        if h < 300:
            h = 300
        self.timeScrolledFrame.config(height=h)
        coords = (20, 20)
        IMAGEPATH = r"Assets\AppointmentsView\LecturerTimeslots\timeslottextbg.png"
        for id, timeslot, day, starttime, endtime, location in fullTimeslots:
            t = self.controller.textElement(
                imagepath=IMAGEPATH, xpos=coords[0], ypos=coords[1],
                classname=f"{id}timeslottext", root=self.timeScrolledFrame,
                text=timeslot, font=URBANIST, size=30, isPlaced=True
            )
            edit = self.controller.buttonCreator(
                imagepath=r"Assets\AppointmentsView\LecturerTimeslots\editbtn.png",
                xpos=coords[0] + 660, ypos=coords[1] + 20,
                root=self.timeScrolledFrame, classname=f"{id}timesloteditbtn",
                buttonFunction=lambda id=(id, day, starttime, endtime, location): self.editTimeslot(
                    id[0], id[1], id[2], id[3], id[4]),
                isPlaced=True
            )
            delete = self.controller.buttonCreator(
                imagepath=r"Assets\AppointmentsView\LecturerTimeslots\deletebtn.png",
                xpos=coords[0] + 720, ypos=coords[1] + 20,
                root=self.timeScrolledFrame, classname=f"{id}timeslotdeletebtn",
                buttonFunction=lambda id=id: self.deleteTimeslot(id),
                isPlaced=True
            )
            coords = (coords[0], coords[1] + 100)

    def deleteTimeslot(self, id):
        print(id)
        askConfirmation = messagebox.askyesno(
            title="Delete Timeslot", message="Are you sure you want to delete this timeslot?")
        if not askConfirmation:
            return
        
        self.prisma.lecapptsetting.delete(
            where={
                "id": id
            }
        )
        t = threading.Thread(target=self.loadAllDetailsForCreation, args=())
        t.daemon = True
        t.start()
        
    def editTimeslot(self, id, day, starttime, endtime, location):
        parentWidget = self.controller.widgetsDict[f"{id}timesloteditbtn"]
        buttonsList = ["Edit Location:success",
                       "Edit Time:secondary", "Edit Day:info", "Cancel:danger"]
        print(id)
        askOption = MessageDialog(
            parent=parentWidget,
            title="Edit Timeslot",
            message="What do you want to do with the timeslot?",
            buttons=buttonsList,
        )
        askOption.show()
        if askOption.result == "Edit Location":
            invalid = True
            while invalid:
                newLocation = Querybox.get_string(
                    parent=parentWidget,
                    title="Edit Location",
                    prompt="Enter new location",
                    initialvalue=location
                )
                if newLocation == "" or newLocation is None:
                    invalid = True
                else:
                    invalid = False
            if newLocation != "" and newLocation is not None:
                stg = self.prisma.lecapptsetting.find_first(
                    where={
                        "id": id
                    }
                )
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "location": newLocation
                    }
                )
                t = threading.Thread(target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
        elif askOption.result == "Edit Time":
            invalid = True
            while invalid:
                newStartTime = Querybox.get_string(
                    parent=parentWidget,
                    title="Edit Start Time",
                    prompt="Enter new start time",
                    initialvalue=starttime
                )
                newEndTime = Querybox.get_string(
                    parent=parentWidget,
                    title="Edit End Time",
                    prompt="Enter new end time",
                    initialvalue=endtime
                )
                if newStartTime == "" or newStartTime is None or newEndTime == "" or newEndTime is None:
                    invalid = True
                else:
                    invalid = False
            if newStartTime != "" and newStartTime is not None and newEndTime != "" and newEndTime is not None:
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "startTime": newStartTime,
                        "endTime": newEndTime
                    }
                )
                t = threading.Thread(target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
        elif askOption.result == "Edit Day":
            invalid = True
            while invalid:
                newDay = Querybox.get_string(
                    parent=parentWidget,
                    title="Edit Day",
                    prompt="Enter new day",
                    initialvalue=day
                )
                if newDay == "" or newDay is None:
                    invalid = True
                else:
                    invalid = False
            if newDay != "" and newDay is not None:
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "day": newDay.upper().strip()
                    }
                )
                t = threading.Thread(target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
    def validateDateVars(self, name, value):
        if name == "aptstgdaymb":
            print(value)
        elif name == "aptstgstarttimemb":
            startTime = self.aptstgstarttimembvar.get()
            endTime = self.aptstgendtimembvar.get()
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
            # do not accept diff < 30 minutes
            try:
                errToast.hide_toast()
            except:
                pass
            errToast = ToastNotification(
                title="Error",
                message="Start time must be earlier than end time",
                duration=2000,
                bootstyle=DANGER
            )
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time must be at least 30 minutes earlier than end time\nResetting {startTime} to {newTime}"
                self.aptstgstarttimembvar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time cannot be later than end time\nResetting {startTime} to {newTime}"
                self.aptstgstarttimembvar.set(newTime)
                errToast.show_toast()
        elif name == "aptstgendtimemb":
            startTime = self.aptstgstarttimembvar.get()
            endTime = self.aptstgendtimembvar.get()
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
            # do not accept diff < 30 minutes
            try:
                errToast.hide_toast()
            except:
                pass
            errToast = ToastNotification(
                title="Error",
                message="Start time must be earlier than end time",
                duration=2000,
                bootstyle=DANGER
            )
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time must be at least 30 minutes later than start time\nResetting {endTime} to {newTime}"
                self.aptstgendtimembvar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time cannot be earlier than start time\nResetting {endTime} to {newTime}"
                self.aptstgendtimembvar.set(newTime)
                errToast.show_toast()
        else:
            print("error")

    def uploadApptSetting(self):
        prisma = self.prisma
        lecturer = prisma.lecturer.find_first(
            where={
                "userId": self.userId
            },
            include={
                "apptSettings": True
            }
        )
        startTime = self.aptstgstarttimembvar.get()
        endTime = self.aptstgendtimembvar.get()
        #Convert to UTC
        startObj = datetime.strptime(startTime, "%I:%M%p")
        endObj = datetime.strptime(endTime, "%I:%M%p")
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        utc = timezone("UTC")
        startObj = kualalumpur.convert(startObj)
        endObj = kualalumpur.convert(endObj)
        startObj = utc.convert(startObj)
        endObj = utc.convert(endObj)
        if lecturer is not None:
            prisma.lecapptsetting.create(
                data={
                    "day": self.aptstgdaymbvar.get().upper().strip(),
                    "location": self.aptstglocationEnt.get().strip(),
                    "startTime": startObj,
                    "endTime": endObj,
                    "lecturer": {
                        "connect": {
                            "id": lecturer.id
                        }
                    }
                }
            )
            t = threading.Thread(target=self.loadAllDetailsForCreation, args=())
            t.daemon = True
            t.start()
            
    def loadAsStudent(self, kualalumpur, humanreadable):
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
        self.locationString = StringVar()
        self.startTimeString = StringVar()
        self.endTimeString = StringVar()
        self.dayString = StringVar()
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
            command=lambda: [
                print(f"timeslot selected: {self.timeslot.get()}"),
                self.setVars(self.timeslot.get())]
        )

    def setVars(self, timeslotString):
        # self.timeslot.get returns the formattedTime
        # formattedTime = f"{day}, {starttime} - {endtime} at {location}"
        location = self.timeslot.get().split(" at ")[1]
        day = self.timeslot.get().split(
            " at ")[0].split(" - ")[0].split(",")[0]
        starttime = self.timeslot.get().split(
            " at ")[0].split(" - ")[0].split(",")[1].strip()
        endtime = self.timeslot.get().split(" at ")[0].split(" - ")[1]
        self.dayString.set(day)
        self.locationString.set(location)
        self.startTimeString.set(starttime)
        self.endTimeString.set(endtime)

    def validateDateInputs(self):
        # Constructing a valid DateTime Object to send into DB
        startDate = self.startDateSelector.entry.get()
        endDate = self.endDateSelector.entry.get()
        startTimeStr = self.startTime.get()
        endTimeStr = self.endTime.get()

        # construct regexes to match against
        # Date Pattern = 30/06/2023
        # Time = 10:00AM
        date_pattern = re.compile(r"([0-9]{2}/[0-9]{2}/[0-9]{4})")
        time_pattern = re.compile(r"([0-9]{2}:[0-9]{2}[AP]M)")
        # match against the regexes
        # check individual inputs
        toast = ToastNotification(
            title="Invalid Date/Time Input",
            message="Please enter a valid date and time input",
            duration=5000,
            bootstyle=DANGER
        )

        if not date_pattern.match(startDate):
            toast.message = "Please enter a valid start date"
            toast.show_toast()
            return
        elif not date_pattern.match(endDate):
            toast.message = "Please enter a valid end date"
            toast.show_toast()
            return
        elif not time_pattern.match(startTimeStr):
            toast.message = "Please enter a valid start time, the format is 10:00AM"
            toast.show_toast()
        elif not time_pattern.match(endTimeStr):
            toast.message = "Please enter a valid end time, the format is 10:00AM"
            toast.show_toast()
        else:
            pass
        if date_pattern.match(startDate) and date_pattern.match(endDate) and time_pattern.match(startTimeStr) and time_pattern.match(endTimeStr):
            # if all the inputs are valid, construct the datetime object
            # 30/06/2023 10:00AM
            startDateTime = datetime.strptime(
                f"{startDate} {startTimeStr}", "%d/%m/%Y %I:%M%p")
            endDateTime = datetime.strptime(
                f"{endDate} {endTimeStr}", "%d/%m/%Y %I:%M%p")
            # check if the startDateTime is before the endDateTime
            if startDateTime < endDateTime:
                # if it is, return True
                return True
            else:
                # if it isn't, return False
                return False

    def createAppointment(self):
        prisma = self.prisma
        lecturer = prisma.lecturer.find_first(
            where={
                "userProfile": {
                    "is": {
                        "fullName": self.lecturer.get()
                    }
                }
            }
        )
        student = prisma.student.find_first(
            where={
                "userProfile": {
                    "is": {
                        "id": self.userId
                    }
                }
            }
        )
        prisma.appointment.create(
            data={
                "title": self.appTitleEntry.get(),
                "description": self.apptDesc.get(),
                "startTime": self.startTime.get(),
                "endTime": self.endTime.get(),


            }
        )

    def loadAppDetailsFrame(self):
        buttonsList = [
            (r"Assets\My Courses\exituploadsview.png", 1300, 40, "exitapptcreation",
             self.apptCreateFrame, lambda: self.unloadAppCreationDetails()),
            (r"Assets\AppointmentsView\confirmbutton.png", 1680, 680, "confirmapptcreation",
             self.apptCreateFrame, lambda: print("confirm button pressed")),
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
        self.apptLocation.insert(0, self.locationString.get())
        self.startDateSelector = DateEntry(
            master=self.apptCreateFrame, dateformat="%d/%m/%Y"
        )
        self.startDateSelector.place(x=480, y=560, width=280, height=60)
        self.endDateSelector = DateEntry(
            master=self.apptCreateFrame,  dateformat="%d/%m/%Y"
        )
        self.endDateSelector.place(x=480, y=640, width=280, height=60)
        self.startTime = self.controller.ttkEntryCreator(
            xpos=780, ypos=560, width=420, height=60,
            root=self.apptCreateFrame, classname="starttimeentry"
        )
        self.endTime = self.controller.ttkEntryCreator(
            xpos=780, ypos=640, width=420, height=60,
            root=self.apptCreateFrame, classname="endtimeentry"
        )
        self.startTime.insert(0, self.startTimeString.get())
        self.endTime.insert(0, self.endTimeString.get())

    def loadAppCreation(self):
        self.apptCreateFrame.grid_remove()
        # self.loadAllDetailsForCreation()
        print(self.role)
        self.creationFrame.grid()
        self.creationFrame.tkraise()
        if self.role == "student":
            self.lecAddTimeslotFrame.grid_remove()
            btnsettings = [
                (r"Assets\AppointmentsView\continuecreationbtn.png", 520, 740, "continuecreation", self.creationFrame,
                 lambda: self.loadAppDetailsFrame()),
            ]
        elif self.role == "lecturer":
            self.lecAddTimeslotFrame.grid()
            self.lecAddTimeslotFrame.tkraise()
            btnsettings = [
                (r"Assets\AppointmentsView\LecturerTimeslots\CancelForLecturer.png", 860, 700,
                 "timeslotcancel", self.lecAddTimeslotFrame, lambda: [self.unloadAppCreation()]),
                (r"Assets\AppointmentsView\LecturerTimeslots\AddTimeslot.png", 120, 700,
                 "timeslotadd", self.lecAddTimeslotFrame, lambda: self.uploadApptSetting()),
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
