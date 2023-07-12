import calendar
import re
import threading
from tkinter import *
from tkinter import messagebox
import ttkbootstrap as ttk
from prisma.models import Appointment
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.dialogs.dialogs import DatePickerDialog
from ttkbootstrap.tooltip import ToolTip
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from datetime import datetime, timedelta
import datetime as dt
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
        self.creationFrame.grid_remove()
        self.viewFrame.grid_remove()
        self.KL = timezone("Asia/Kuala_Lumpur")
        self.UTC = timezone("UTC")

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
            (r"Assets\AppointmentsView\refreshviewappointments.png", 520, 60,
             "refreshviewappointmentsbtn", self.viewFrame, lambda: self.loadFullDetails()),
            (r"Assets\AppointmentsView\DateTimeDialog.png", 1800, 160, "datepickerdialogbtn", self,
             lambda: self.selectingDate())
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")

        self.scrolledframe = ScrolledFrame(
            self, width=460, height=660, name="appointmentscrolledframe", autohide=True,
            bootstyle="dark-rounded"
        )
        self.scrolledframe.place(
            x=1420, y=260, width=460, height=620
        )
        self.mainDateEntry = self.controller.ttkEntryCreator(
            root=self, xpos=1420, ypos=180, width=360, height=40, classname="maindateentry",
            font=("Inter", 16), fg=BLACK,
        )
        self.mainDateEntry.insert(0, datetime.now().strftime('%A, %d %B %Y'))
        self.mainDateEntry.configure(state=READONLY)

    def selectingDate(self, btn: Button, entry: Entry):
        # the pairs of variables
        textvar1 = self.startDateString
        dialog = DatePickerDialog(
            parent=btn, title="Select Date", firstweekday=0,
        )
        entry.configure(state=NORMAL)
        entry.delete(0, END)
        date = dialog.date_selected.strftime('%A, %d %B %Y')
        entry.insert(0, date)
        entry.configure(state=READONLY)
        dayOfTextVar1 = datetime.strptime(
            textvar1.get(), '%A, %d %B %Y').strftime('%A')
        toast = ToastNotification(
            title="Invalid Date Selected",
            message=f"The timeslot you have selected falls before the current time. Please select a date which is after the current time.",
            duration=5000,
            bootstyle=DANGER
        )
        starttime = self.timeslot.get().split(
            " at ")[0].split(" - ")[0].split(",")[1].strip()
        target_datetime = datetime.combine(datetime.strptime(textvar1.get(
        ), '%A, %d %B %Y').date(), dt.datetime.strptime(starttime, "%I:%M%p").time())
        if target_datetime <= datetime.now():
            # check if the dayOfTextVar1 is before the current time
            textvar1.set(self.formatString)
            toast.message = f"The timeslot you have selected falls before the current time. Please select a date which is after the current time."
            toast.show_toast()
        elif self.dayString.get() == dayOfTextVar1.upper():
            # check if the dayOfTextVar1 is the same as the dayString
            # check if the target date is today, but the meeting time has already passed
            target_date = datetime.strptime(
                textvar1.get(), '%A, %d %B %Y').date()
            today = datetime.now().date()
            starttime = self.timeslot.get().split(
                " at ")[0].split(" - ")[0].split(",")[1].strip()
            if target_date == today and dt.datetime.strptime(starttime, "%I:%M%p").time() < dt.datetime.now().time():
                target_date = today + dt.timedelta(days=7)
                toast.message = f"The time for the timeslot you have selected has already passed. The date has been changed to {target_date.strftime('%A, %d %B %Y')}."
                toast.show_toast()
                textvar1.set(target_date.strftime('%A, %d %B %Y'))
        # if the dayOfTextVar1 is before the current time, then revert the textvar1 to the original date
        else:
            # revert textvar1 to the original date
            ToastNotification(
                title="Invalid Date",
                message=f"The day of the date you have selected, {dayOfTextVar1.upper()} is invalid. Please select a date which is on a {self.dayString.get()}.",
                duration=5000,
                bootstyle=DANGER
            ).show_toast()
            textvar1.set(self.formatString)

    def postLogin(self, data: dict = None):
        self.prisma = self.controller.mainPrisma
        self.userId = data["id"]
        self.role = data["role"]
        self.loadAllDetailsForCreation()

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
                "userProfile": True,
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

    def refreshAppCreationStudent(self):
        self.loadAllDetailsForCreation()

    def loadAllDetailsForCreation(self):
        # MODULE -> LECTURER -> TIMESLOT
        for widgetname, widget in self.creationFrame.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["moduleshostfr", "lecturersaptmenuhostfr", "timeslotmenuhostfr"]:
                    widget.grid_remove()
        self.moduleDict = {}
        if self.role == "lecturer":
            self.lecturerList = self.loadForLecturer()
            self.loadAsLecturer()
        elif self.role == "student":
            self.fullinfo = self.loadForStudent()
            self.loadAsStudent()

    # loadaslecturer will be using self.lecAddTimeslotFrame
    # there will be a location ttkEntryCreator
    # a select day menubuttonCreator
    # similar to start and end time
    # will require the ID of the lecaptsettingfield
    # id, lecturerid, day, starttime, endtime, location
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ START OF TIMESLOT CREATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def loadAsLecturer(self):
        KL = timezone("Asia/Kuala_Lumpur")
        humanreadable = r"%I:%M%p"
        self.LECAPTDAYS = [
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"
        ]
        start_time = datetime.strptime("08:00AM", "%I:%M%p")
        end_time = datetime.strptime("06:00PM", "%I:%M%p")
        time_slots = [start_time + timedelta(minutes=30*i) for i in range(21)]
        time_slots_str = [ts.strftime("%I:%M%p") for ts in time_slots]

        pos = {
            "aptstglocationent": {"x": 140, "y": 340, "width": 240, "height": 60},
            "aptstgdaymb": {"x": 140, "y": 420, "width": 240, "height": 60},
            "aptstgstarttimemb": {"x": 140, "y": 500, "width": 240, "height": 60},
            "aptstgendtimemb": {"x": 140, "y": 580, "width": 240, "height": 60},
        }

        lists = {
            "aptstgdaymb": self.LECAPTDAYS,
            "aptstgstarttimemb": time_slots_str,
            "aptstgendtimemb": time_slots_str
        }

        ENAME = "aptstglocationent"
        self.aptstglocationEnt = self.controller.ttkEntryCreator(
            root=self.lecAddTimeslotFrame, xpos=pos[ENAME]["x"], ypos=pos[ENAME]["y"],
            width=pos[ENAME]["width"], height=pos[ENAME]["height"], classname=ENAME,
            font=("Urbanist", 20), fg=BLACK,
        )

        self.aptstgdaymbvar = StringVar()
        self.aptstgstarttimembvar = StringVar()
        self.aptstgendtimembvar = StringVar()

        vars = {
            "aptstgdaymb": self.aptstgdaymbvar,
            "aptstgstarttimemb": self.aptstgstarttimembvar,
            "aptstgendtimemb": self.aptstgendtimembvar
        }

        for name, values in lists.items():
            self.controller.menubuttonCreator(
                root=self.lecAddTimeslotFrame, xpos=pos[name]["x"], ypos=pos[name]["y"],
                width=pos[name]["width"], height=pos[name]["height"],
                classname=name,
                listofvalues=values, variable=vars[name],
                font=("Urbanist", 20), text="",
                command=lambda name=name: [
                    self.validateDateVars(name, vars[name].get()),
                ]
            )

        # set the default values
        self.aptstgdaymbvar.set(self.LECAPTDAYS[0])
        self.aptstgstarttimembvar.set(time_slots_str[0])
        self.aptstgendtimembvar.set(time_slots_str[-1])

        WD = self.controller.widgetsDict
        WD["aptstgdaymb"].configure(
            text=self.aptstgdaymbvar.get())
        WD["aptstgstarttimemb"].configure(
            text=self.aptstgstarttimembvar.get())
        WD["aptstgendtimemb"].configure(
            text=self.aptstgendtimembvar.get())

        fullTimeslots = []

        for i in self.lecturerList.apptSettings:
            stgId = i.id
            day = i.day
            location = i.location
            starttime = KL.convert(i.startTime).strftime(humanreadable)
            endtime = KL.convert(i.endTime).strftime(humanreadable)
            formattedTime = f"{day}, {starttime} - {endtime} at {location}"
            fullTimeslots.append(
                (stgId, formattedTime, day, starttime, endtime, location)
            )

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
        KL = timezone("Asia/Kuala_Lumpur")
        UTC = timezone("UTC")
        humanreadable = "%I:%M%p"
        # Regex patterns for Location, Time, and Day Inputs for Dialog Validation
        # Location pattern allows only alphanumeric characters, spaces and no more.
        locationPattern = r"^[a-zA-Z0-9 ]+$"
        # Time pattern allows only 12-hour time format with AM/PM
        # I.E: 12:00PM, do not allow 12:00 PM or 12:00 pm or 12:00 Pm or 12:00 pM or 12:00pm
        timePattern = r"^(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)$"
        # compile the regex patterns
        locationRegex = re.compile(locationPattern)
        timeRegex = re.compile(timePattern)

        buttonsList = ["Edit Location:success",
                       "Edit Time:secondary", "Edit Day:info", "Cancel:danger"]
        timeOptions = ["Edit Start Time:primary",
                       "Edit End Time:secondary", "Cancel:danger"]
        dayOptions = ["MONDAY:primary", "TUESDAY:secondary", "WEDNESDAY:success",
                      "THURSDAY:info", "FRIDAY:warning", "Cancel:danger"]

        askOption = MessageDialog(
            parent=parentWidget,
            title="Edit Timeslot",
            message="What do you want to do with the timeslot?",
            buttons=buttonsList,
        )
        askOption.show()
        if askOption.result == "Edit Location":
            while True:
                newLocation = Querybox.get_string(
                    parent=parentWidget,
                    title="Edit Location",
                    prompt="Enter new location",
                    initialvalue=location
                )
                if not locationRegex.match(newLocation):
                    Messagebox.show_error(
                        parent=parentWidget,
                        title="Error",
                        message="Please enter a valid input for location, it must be alphanumeric and spaces only",
                    )
                    continue
                elif newLocation == location:
                    Messagebox.show_error(
                        parent=parentWidget,
                        title="Error",
                        message=f"Please enter a location different from the current one, {location}",
                    )
                    continue
                else:
                    break
            if newLocation is not None:
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "location": newLocation
                    }
                )
                t = threading.Thread(
                    target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
            else:
                return
        elif askOption.result == "Edit Time":
            askTimeEdit = MessageDialog(
                parent=parentWidget,
                title="Options to Edit Time",
                message="What do you want to edit?",
                buttons=timeOptions,
            )
            askTimeEdit.show()
            if askTimeEdit.result == "Edit Start Time":
                while True:  # Infinitely loop until user cancels or enters a valid input
                    newStartTime = Querybox.get_string(
                        parent=parentWidget,
                        title="Edit Start Time",
                        prompt=f"Enter new start time, originally {starttime} - {endtime}",
                        initialvalue=starttime
                    )
                    # check if newStartTime is None, if so, return
                    if newStartTime is None:
                        return
                    # check newStartTime string matches regex pattern
                    if not timeRegex.match(newStartTime):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter a start time, following the format HH:MMAM/PM",
                        )
                        continue
                    # check if newStartTime is the same as the original start time
                    if newStartTime == starttime:
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter a different start time or cancel",
                        )
                        continue
                    # check if newStartTime is before 8:00AM
                    elif datetime.strptime(newStartTime, humanreadable) < datetime.strptime("8:00AM", humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter a start time that is not before 8:00AM",
                        )
                        continue
                    # check if newStartTime is after the original end time
                    elif datetime.strptime(newStartTime, humanreadable) >= datetime.strptime(endtime, humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter a start time that is before the end time, {newStartTime} is not before {endtime}",
                        )
                        continue
                    else:  # Valid input, break out of the loop
                        break
                if newStartTime is not None:
                    startObj = datetime.strptime(newStartTime, humanreadable)
                    startObj = UTC.convert(KL.convert(startObj))
                    self.prisma.lecapptsetting.update(
                        where={
                            "id": id
                        },
                        data={
                            "startTime": startObj
                        }
                    )
                    t = threading.Thread(
                        target=self.loadAllDetailsForCreation, args=())
                    t.daemon = True
                    t.start()
            elif askTimeEdit.result == "Edit End Time":
                while True:
                    newEndTime = Querybox.get_string(
                        parent=parentWidget,
                        title="Edit End Time",
                        prompt=f"Enter new end time, originally {starttime} - {endtime}",
                        initialvalue=endtime
                    )
                    # check newEndTime string matches regex pattern
                    if not timeRegex.match(newEndTime):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter an end time, following the format HH:MMAM/PM",
                        )
                        continue
                    # check if newEndTime is the same as the original end time
                    if newEndTime == endtime:
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message="Please enter a different end time or cancel",
                        )
                        continue
                    # check if newEndTime is after 6:00PM
                    elif datetime.strptime(newEndTime, humanreadable) > datetime.strptime("06:00PM", humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter an end time that is not after 6:00PM",
                        )
                        continue
                    # check if newEndTime is before the original start time
                    elif datetime.strptime(newEndTime, humanreadable) <= datetime.strptime(starttime, humanreadable):
                        Messagebox.show_error(
                            parent=parentWidget,
                            title="Error",
                            message=f"Please enter an end time that is after the start time, {newEndTime} is not after {starttime}",
                        )
                        continue
                    elif newEndTime is None:
                        return
                    else:
                        break
                if newEndTime is not None:
                    endObj = datetime.strptime(newEndTime, humanreadable)
                    endObj = UTC.convert(KL.convert(endObj))
                    self.prisma.lecapptsetting.update(
                        where={
                            "id": id
                        },
                        data={
                            "endTime": endObj
                        }
                    )
                    t = threading.Thread(
                        target=self.loadAllDetailsForCreation, args=())
                    t.daemon = True
                    t.start()
            else:
                return
        elif askOption.result == "Edit Day":
            askDay = MessageDialog(
                parent=parentWidget,
                title=f"Changing the day from {day}",
                message="Select a New Day",
                buttons=dayOptions
            )
            askDay.show()
            newDay = askDay.result
            if newDay is not None:
                self.prisma.lecapptsetting.update(
                    where={
                        "id": id
                    },
                    data={
                        "day": newDay.upper().strip()
                    }
                )
                t = threading.Thread(
                    target=self.loadAllDetailsForCreation, args=())
                t.daemon = True
                t.start()
            else:
                return

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
            # do not accept diff < 30 minutes
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
        elif name == "appstarttimemb":
            startTime = self.appStartTimeVar.get()
            endTime = self.appEndTimeVar.get()
            print(f"The lecturer selected is {self.lecturer.get()}")
            print(f"The location string is {self.locationString.get()}")
            print(f"The timeslot selected is {self.timeslot.get()}")
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
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
            # do not accept diff < 30 minutes
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time must be at least 30 minutes earlier than end time\nResetting {startTime} to {newTime}"
                self.appStartTimeVar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(endTime, "%I:%M%p") -
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"Start time cannot be later than end time\nResetting {startTime} to {newTime}"
                self.appStartTimeVar.set(newTime)
                errToast.show_toast()
        elif name == "appendtimemb":
            startTime = self.appStartTimeVar.get()
            endTime = self.appEndTimeVar.get()
            print(f"The lecturer selected is {self.lecturer.get()}")
            print(f"The location string is {self.locationString.get()}")
            print(f"The timeslot selected is {self.timeslot.get()}")
            start = datetime.strptime(startTime, "%I:%M%p")
            end = datetime.strptime(endTime, "%I:%M%p")
            diff = timedelta(hours=end.hour, minutes=end.minute) - \
                timedelta(hours=start.hour, minutes=start.minute)
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
            # do not accept diff < 30 minutes
            if diff < timedelta(minutes=30):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time must be at least 30 minutes later than start time\nResetting {endTime} to {newTime}"
                self.appEndTimeVar.set(newTime)
                errToast.show_toast()
            # if diff is negative
            elif diff < timedelta(hours=0):
                # reset startTime to 30 minutes earlier
                newTime = (datetime.strptime(startTime, "%I:%M%p") +
                           timedelta(minutes=30)).strftime("%I:%M%p")
                errToast.message = f"End time cannot be earlier than start time\nResetting {endTime} to {newTime}"
                self.appEndTimeVar.set(newTime)
                errToast.show_toast()
        else:
            print("error")

    def uploadApptSetting(self):
        prisma = self.prisma
        KL = timezone("Asia/Kuala_Lumpur")
        UTC = timezone("UTC")
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
        # Convert to UTC
        startObj = datetime.strptime(startTime, "%I:%M%p")
        endObj = datetime.strptime(endTime, "%I:%M%p")
        startObj = UTC.convert(KL.convert(startObj))
        endObj = UTC.convert(KL.convert(endObj))
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
            t = threading.Thread(
                target=self.loadAllDetailsForCreation, args=())
            t.daemon = True
            t.start()
        else:
            return

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ END OF TIMESLOT CREATION ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~ START OF STUDENT APPOINTMENT CREATION ~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadAsStudent(self):
        self.KL = timezone("Asia/Kuala_Lumpur")
        humanreadable = r"%I:%M%p"
        self.studentRefreshBtn = self.controller.buttonCreator(
            imagepath=r"Assets\AppointmentsView\refreshforstudents.png",
            xpos=560, ypos=540, root=self.creationFrame, classname="studentRefreshBtn",
            buttonFunction=lambda: self.refreshAppCreationStudent()
        )
        for me in self.fullinfo:
            lecturerDict = {}
            if me.module.lecturer == None:
                lecturerDict = {
                    "No lecturer": []
                }
                self.moduleDict[f"{me.module.moduleCode} - {me.module.moduleTitle}"] = lecturerDict
                continue
            lecturer = me.module.lecturer.userProfile.fullName
            apptStgTimes = []
            if me.module.lecturer.apptSettings == []:
                lecturerDict = {
                    f"{lecturer}": ["No timeslots provided"]
                }
                self.moduleDict[f"{me.module.moduleCode} - {me.module.moduleTitle}"] = lecturerDict
                continue
            for apptStg in me.module.lecturer.apptSettings:
                day = apptStg.day
                location = apptStg.location
                starttime = self.KL.convert(
                    apptStg.startTime).strftime(humanreadable)
                endtime = self.KL.convert(
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
        lecturerList = list(self.moduleDict[modCode].keys())
        l = self.controller.menubuttonCreator(
            xpos=positions["lecturer"]["x"], ypos=positions["lecturer"]["y"], width=positions[
                "lecturer"]["width"], height=positions["lecturer"]["height"],
            root=self.creationFrame, classname="lecturersaptmenu", text="Select Lecturer", listofvalues=lecturerList,
            variable=self.lecturer, font=("Helvetica", 12),
            command=lambda: self.loadTimeslotMenuBtns(
                modCode, self.lecturer.get())
        )
        if lecturerList == ["No lecturer"]:
            self.lecturer.set("")
            l.configure(text="No lecturer", state="disabled")

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
        if timeslotlist == ["No timeslots provided"]:
            timeslotlist = ["No available timeslots"]
            textForBtn = "No available timeslots"
            self.timeslot.set("")
        else:
            textForBtn = "Select Timeslot"
        t = self.controller.menubuttonCreator(
            xpos=positions["timeslot"]["x"], ypos=positions["timeslot"]["y"], width=positions[
                "timeslot"]["width"], height=positions["timeslot"]["height"],
            root=self.creationFrame, classname="timeslotmenu", text=textForBtn, listofvalues=timeslotlist,
            variable=self.timeslot, font=("Helvetica", 12),
            command=lambda: [
                self.setVars()]
        )
        if timeslotlist == ["No available timeslots"]:
            self.timeslot.set("")
            t.configure(state="disabled")
            return

    def setVars(self):
        # self.timeslot.get returns the formattedTime
        # formattedTime = f"{day}, {starttime} - {endtime} at {location}"
        location = self.timeslot.get().split(" at ")[1]
        day = self.timeslot.get().split(
            " at ")[0].split(" - ")[0].split(",")[0]
        starttime = self.timeslot.get().split(
            " at ")[0].split(" - ")[0].split(",")[1].strip()
        endtime = self.timeslot.get().split(" at ")[0].split(" - ")[1]
        self.dayString.set(day)
        self.controller.textElement(
            imagepath=r"Assets\AppointmentsView\daytextbg.png", xpos=340, ypos=720,
            root=self.apptCreateFrame, classname="daytextbg",
            font=URBANIST, size=32, text=day.upper(), yIndex=-1/8,
        )
        today = dt.date.today()
        current_weekday = today.weekday()
        target_weekday = list(calendar.day_name).index(day.capitalize())
        days_ahead = (target_weekday - current_weekday) % 7
        target_date = today + dt.timedelta(days=days_ahead)
        if target_date == today and dt.datetime.strptime(starttime, "%I:%M%p").time() < dt.datetime.now().time():
            target_date = today + dt.timedelta(days=7)
        self.formatString = target_date.strftime("%A, %d %B %Y")
        self.startDateString = StringVar()
        self.startDateEntry = self.controller.ttkEntryCreator(
            xpos=140, ypos=620, width=380, height=80,
            root=self.apptCreateFrame, classname="startdateentry",
            font=("Inter", 20),
        )
        self.startDateString.set(self.formatString)
        self.startDateEntry.insert(0, self.formatString)
        self.startDateEntry.configure(textvariable=self.startDateString)
        self.startDateEntry.config(state=READONLY)
        self.locationString.set(location)
        self.startTimeString.set(starttime)
        self.endTimeString.set(endtime)

    def createAppointment(self):
        prisma = self.prisma
        KL = timezone("Asia/Kuala_Lumpur")
        UTC = timezone("UTC")
        if self.appTitleEntry.get() == "" or self.apptDesc.get("1.0", END) == "":
            Messagebox.show_error(
                title="Blank Fields",
                message="Please fill in all the fields",
                parent=self.appTitleEntry,
            )
            return
        originalFmt = r"%A, %d %B %Y"
        finalDate = self.startDateString.get()
        finalDate = datetime.strptime(finalDate, originalFmt)
        finalStartTime = self.appStartTimeVar.get()
        finalEndTime = self.appEndTimeVar.get()
        timeFmt = r"%I:%M%p"
        finalStartTime = datetime.strptime(finalStartTime, timeFmt)
        finalEndTime = datetime.strptime(finalEndTime, timeFmt)
        savedDateAndStartTime = UTC.convert(
            KL.convert(
                datetime.combine(finalDate, finalStartTime.time())
            )
        )
        savedDateAndEndTime = UTC.convert(
            KL.convert(
                datetime.combine(finalDate, finalEndTime.time())
            )
        )
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
                "description": self.apptDesc.get("1.0", "end-1c"),
                "location": self.locationString.get(),
                "startTime": savedDateAndStartTime,
                "endTime": savedDateAndEndTime,
                "lectAccept": True,
                "studAccept": True,
                "lecturerId": lecturer.id,
                "studentId": student.id,
                "studAcceptAt": self.UTC.convert(self.KL.convert(datetime.now())),
                "lectAcceptAt": self.UTC.convert(self.KL.convert(datetime.now())),
            },
        )
        options = ["Create Another Appointment:success",
                   "Return to Main Menu:info"]
        ask = MessageDialog(
            title="Appointment Created",
            parent=self.controller.widgetsDict["confirmapptcreation"],
            message="Appointment has been created successfully, what would you like to do now?",
            buttons=options,
        )
        ask.show()
        if ask.result == "Create Another Appointment":
            self.unloadAppCreationDetails()
        elif ask.result == "Return to Main Menu":
            self.unloadAppCreationDetails()
            self.unloadAppCreation()

    def loadAppDetailsFrame(self):
        WD = self.controller.widgetsDict
        buttonsList = [
            (r"Assets\My Courses\exituploadsview.png", 1140, 40, "exitapptcreation",
             self.apptCreateFrame, lambda: self.unloadAppCreationDetails()),
            (r"Assets\AppointmentsView\cancelbutton.png", 1360, 680, "cancelapptcreation",
             self.apptCreateFrame, lambda: self.unloadAppCreationDetails()),
            (r"Assets\AppointmentsView\confirmbutton.png", 1600, 680, "confirmapptcreation",
             self.apptCreateFrame, lambda: self.createAppointment()),
            (r"Assets\AppointmentsView\StartDateSelector.png", 520, 620, "startdateselectorbtn",
             self.apptCreateFrame, lambda: self.selectingDate(
                 btn=WD["startdateselectorbtn"], entry=WD["startdateentry"]
             )
             ),
        ]

        self.controller.settingsUnpacker(buttonsList, "button")
        self.apptCreateFrame.grid()
        self.apptCreateFrame.tkraise()
        self.appTitleEntry = self.controller.ttkEntryCreator(
            xpos=480, ypos=160, width=720, height=60,
            root=self.apptCreateFrame, classname="apptcreatetitle"
        )
        self.apptDescText = ScrolledText(
            master=self.apptCreateFrame, width=1, height=1, bootstyle="info-rounded", autohide=True
        )
        self.apptDescText.place(x=480, y=240, width=720, height=120)
        self.apptDesc = self.apptDescText.text
        self.apptDesc.config(font=("Inter", 20), wrap=WORD, fg=BLACK)
        self.apptLocation = self.controller.ttkEntryCreator(
            xpos=480, ypos=480, width=720, height=60,
            root=self.apptCreateFrame, classname="apptlocation"
        )
        self.apptLocation.insert(0, self.locationString.get())
        self.apptLocation.config(textvariable=self.locationString)
        self.apptLocation.config(state="readonly")
        start_time = datetime.strptime("08:00AM", "%I:%M%p")
        time_slots = [start_time + timedelta(minutes=30*i) for i in range(21)]
        time_slots_str = [ts.strftime("%I:%M%p") for ts in time_slots]
        pos = {
            "appstarttimemb": {"x": 940, "y": 560, "width": 260, "height": 60},
            "appendtimemb": {"x": 940, "y": 640, "width": 260, "height": 60},
        }
        lists = {
            "appstarttimemb": time_slots_str,
            "appendtimemb": time_slots_str
        }
        self.appStartTimeVar = StringVar()
        self.appEndTimeVar = StringVar()
        vars = {
            "appstarttimemb": self.appStartTimeVar,
            "appendtimemb": self.appEndTimeVar
        }
        for name, values in lists.items():
            self.controller.menubuttonCreator(
                root=self.apptCreateFrame, xpos=pos[name]["x"], ypos=pos[name]["y"],
                width=pos[name]["width"], height=pos[name]["height"],
                classname=name,
                listofvalues=values, variable=vars[name],
                font=("SF Pro", 20), text="",
                command=lambda name=name: [
                    self.validateDateVars(name, vars[name].get()),
                ]
            )

        # test = self.controller.menubuttonCreator()
        # set the default values for the menu button vars
        self.appStartTimeVar.set(self.startTimeString.get())
        self.appEndTimeVar.set(self.endTimeString.get())
        WD["appstarttimemb"].config(text=self.startTimeString.get())
        WD["appendtimemb"].config(text=self.endTimeString.get())
        WD["appendtimemb"].config(state=DISABLED)
        WD["appstarttimemb"].config(state=DISABLED)

    def navigateAppDetailsFrame(self):
        warnToast = ToastNotification(
            title="Empty Fields",
            message="Please fill in all the fields before continuing",
            bootstyle=DANGER,
            duration=3000,
        )
        if self.module.get() == "":
            warnToast.message = "Please select a module before continuing"
            warnToast.show_toast()
            return
        elif self.lecturer.get() == "":
            warnToast.message = "Please select a lecturer before continuing"
            warnToast.show_toast()
            return
        elif self.timeslot.get() == "":
            warnToast.message = "Please select a timeslot before continuing"
            warnToast.show_toast()
            return
        self.loadAppDetailsFrame()

    def loadAppCreation(self):
        self.apptCreateFrame.grid_remove()
        # self.loadAllDetailsForCreation()
        self.creationFrame.grid()
        self.creationFrame.tkraise()
        if self.role == "student":
            self.lecAddTimeslotFrame.grid_remove()
            btnsettings = [
                (r"Assets\AppointmentsView\continuecreationbtn.png", 520, 740, "continuecreation", self.creationFrame,
                 lambda: self.navigateAppDetailsFrame()),
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

    def loadLatestAppointmentsLecturer(self):
        prisma = self.prisma
        appointments = prisma.appointment.find_many(
            where={
                "lecturer": {
                    "is": {
                        "userId": self.userId
                    }
                }
            },
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
            }
        )
        if appointments == []:
            return None
        return appointments

    def loadLatestAppointmentsStudent(self):
        prisma = self.prisma
        appointments = prisma.appointment.find_many(
            where={
                "student": {
                    "is": {
                        "userId": self.userId
                    }
                }
            },
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
            }
        )
        if appointments == []:
            return None
        return appointments

    def loadAppView(self):
        WD = self.controller.widgetsDict
        self.viewFrame.grid()
        self.viewFrame.tkraise()
        self.loadFullDetails()

    def loadFullDetails(self):
        WD = self.controller.widgetsDict
        try:
            staticList = ["viewappname",
                          "viewappemail",
                          "viewappcontact",
                          "viewapplocation",
                          "viewappstartdate",
                          "viewappstarttime",
                          "viewappenddate",
                          "viewappendtime",
                          "viewappstudstatus",
                          "viewapplectstatus",
                          "refreshstatus"]
            for i in staticList:
                WD[i].grid_remove()
        except:
            pass
        self.appContentList = self.loadLatestAppointmentsStudent(
        ) if self.role == "student" else self.loadLatestAppointmentsLecturer()
        if self.appContentList == None:
            self.appContentList = []
        h = 760 if len(self.appContentList) * 200 + \
            20 < 760 else len(self.appContentList) * 200 + 20
        self.viewScrolledFrame = ScrolledFrame(
            self.viewFrame, width=520, height=h, autohide=True, bootstyle="bg-rounded"
        )
        self.viewScrolledFrame.place(
            x=60, y=120, width=520, height=760
        )
        startx, starty = 20, 20
        for i in self.appContentList:
            # convert timestamp to human readable
            self.KL.convert(i.startTime).strftime(
                r"%A, %B %d %Y at %I:%M:%S %p")
            self.KL.convert(i.endTime).strftime(r"%A, %B %d %Y at %I:%M:%S %p")
            # Appointment Card Widget
            self.loadAppointmentCard(i, startx, starty)
            starty += 200

    def loadAppointmentCard(self, app: Appointment, startx, starty):
        humanreadable = r"%A, %B %d %Y at %I:%M:%S %p"
        humandate = r"%A, %B %d %Y"
        self.controller.labelCreator(
            imagepath=r"Assets\AppointmentsView\ManageApp\AppointmentCard.png",
            xpos=startx, ypos=starty, root=self.viewScrolledFrame,
            classname=f"{app.id}appcardbg", isPlaced=True
        )
        # title
        self.controller.textElement(
            imagepath=r"Assets\AppointmentsView\ManageApp\AppTitleTextBg.png",
            xpos=startx+20, ypos=starty+20, root=self.viewScrolledFrame,
            classname=f"{app.id}apptitlebg",
            font=SFPRO, size=32, fg="#000000",
            text=f"{app.title}", isPlaced=True
        )
        # description
        textHost = ScrolledText(
            master=self.viewScrolledFrame, autohide=True, bootstyle="success-rounded"
        )
        mainText = textHost.text
        mainText.configure(
            font=("Helvetica", 18), fg=BLACK, wrap=WORD
        )
        mainText.insert(END, f"{app.description}")
        mainText.configure(state=DISABLED)
        textHost.place(
            x=startx+20, y=starty+80, width=360, height=80
        )
        # view button
        self.controller.buttonCreator(
            imagepath=r"Assets\AppointmentsView\ManageApp\viewapp.png",
            xpos=startx+400, ypos=starty+20, root=self.viewScrolledFrame,
            classname=f"{app.id}viewappbtn",
            buttonFunction=lambda: self.viewAppointment(app),
            isPlaced=True
        )
        # delete button
        self.controller.buttonCreator(
            imagepath=r"Assets\AppointmentsView\ManageApp\deleteapp.png",
            xpos=startx+400, ypos=starty+100, root=self.viewScrolledFrame,
            classname=f"{app.id}deleteappbtn",
            buttonFunction=lambda: self.deleteAppointment(app),
            isPlaced=True
        )

    def refreshApptStatus(self, app: Appointment):
        self.loadFullDetails()
        prisma = self.prisma
        newapp = prisma.appointment.find_first(
            where={
                "id": app.id
            },
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
            }
        )
        self.viewAppointment(newapp)

    def viewAppointment(self, app: Appointment):
        VBG = r"Assets\AppointmentsView\ManageApp\AppWithTextBg.png"
        ACCEPT = r"Assets\AppointmentsView\ManageApp\Accept.png"
        NOTACCEPT = r"Assets\AppointmentsView\ManageApp\NotAccept.png"
        LOCATIONDETAILS = r"Assets\AppointmentsView\ManageApp\LocationDetailsBg.png"
        DATEDETAILS = r"Assets\AppointmentsView\ManageApp\DateDetailsText.png"
        TIMEDETAILS = r"Assets\AppointmentsView\ManageApp\TimeDetailsBg.png"
        REFRESHSTATUS = r"Assets\AppointmentsView\refreshappointwithstatus.png"
        UNDERWAY = r"Assets\AppointmentsView\ManageApp\appointmentunderway.png"
        COMPLETE = r"Assets\AppointmentsView\ManageApp\completeappt.png"
        INCOMPLETE = r"Assets\AppointmentsView\ManageApp\incompleteappt.png"
        self.refreshAppStatusBtn = self.controller.buttonCreator(
            imagepath=REFRESHSTATUS, xpos=1080, ypos=60,
            root=self.viewFrame, classname=f"refreshstatus",
            buttonFunction=lambda app=app: self.refreshApptStatus(app),
        )
        humanreadable = r"%A, %B %d %Y at %I:%M:%S %p"
        if self.role == "student":
            texts = [
                f"{app.lecturer.userProfile.fullName}",
                f"{app.lecturer.userProfile.email}",
                f"{app.lecturer.userProfile.contactNo}",
            ]
            try:
                texts.append(app.studAcceptAt.strftime(humanreadable))
            except:
                texts.append("Not accepted yet by student")
            try:
                texts.append(
                    app.lectAcceptAt.strftime(humanreadable))
            except:
                texts.append("Not accepted yet by lecturer")
        elif self.role == "lecturer":
            texts = [
                f"{app.student.userProfile.fullName}",
                f"{app.student.userProfile.email}",
                f"{app.student.userProfile.contactNo}",
            ]
            try:
                texts.append(
                    app.studAcceptAt.strftime(humanreadable))
            except:
                texts.append("Not accepted yet by student")
            try:
                texts.append(
                    app.lectAcceptAt.strftime(humanreadable))
            except:
                texts.append("Not accepted yet by lecturer")
        self.controller.textElement(
            imagepath=VBG, xpos=680, ypos=160,
            root=self.viewFrame, classname="viewappname",
            text=f"{texts[0]}", font=SFPRO, size=32, fg=BLACK,
        )
        self.controller.textElement(
            imagepath=VBG, xpos=680, ypos=340,
            root=self.viewFrame, classname="viewappemail",
            text=f"{texts[1]}", font=SFPRO, size=24, fg=BLACK,
        )
        self.controller.textElement(
            imagepath=VBG, xpos=680, ypos=500,
            root=self.viewFrame, classname="viewappcontact",
            text=f"{texts[2]}", font=SFPRO, size=32, fg=BLACK,
        )
        # Status Checks
        # If student has accepted
        studAccept = app.studAccept
        lectAccept = app.lectAccept
        if self.role == "student":
            self.controller.buttonCreator(
                imagepath=ACCEPT if studAccept else NOTACCEPT,
                xpos=740, ypos=700,
                root=self.viewFrame, classname="viewappstudstatus",
                buttonFunction=lambda: self.showAcceptedAgo(
                    app, isStudent=True)
            )
            self.controller.buttonCreator(
                imagepath=ACCEPT if lectAccept else NOTACCEPT,
                xpos=980, ypos=700,
                root=self.viewFrame, classname="viewapplectstatus",
                buttonFunction=lambda: self.showAcceptedAgo(
                    app, isLecturer=True)
            )
        elif self.role == "lecturer":
            self.controller.buttonCreator(
                imagepath=ACCEPT if lectAccept else NOTACCEPT,
                xpos=740, ypos=700,
                root=self.viewFrame, classname="viewappstudstatus",
                buttonFunction=lambda: self.showAcceptedAgo(
                    app, isLecturer=True)
            )
            self.controller.buttonCreator(
                imagepath=ACCEPT if studAccept else NOTACCEPT,
                xpos=980, ypos=700,
                root=self.viewFrame, classname="viewapplectstatus",
                buttonFunction=lambda: self.showAcceptedAgo(
                    app, isStudent=True)
            )
        self.controller.textElement(
            imagepath=LOCATIONDETAILS, xpos=1520, ypos=120,
            root=self.viewFrame, classname="viewapplocation",
            text=f"{app.location}", font=SFPRO, size=40, fg=BLACK,
        )
        # Start Date and Time
        humandate = "%a, %d %b %Y"
        humantime = "%I:%M:%S %p"
        startTime = self.KL.convert(app.startTime)
        endTime = self.KL.convert(app.endTime)
        self.controller.textElement(
            imagepath=DATEDETAILS, xpos=1360, ypos=240,
            root=self.viewFrame, classname="viewappstartdate",
            text=f"{startTime.strftime(humandate)}", font=SFPRO, size=24, fg=BLACK,
        )
        self.controller.textElement(
            imagepath=TIMEDETAILS, xpos=1680, ypos=240,
            root=self.viewFrame, classname="viewappstarttime",
            text=f"{startTime.strftime(humantime)}", font=SFPRO, size=24, fg=BLACK,
        )
        # End Date and Time
        self.controller.textElement(
            imagepath=DATEDETAILS, xpos=1360, ypos=320,
            root=self.viewFrame, classname="viewappenddate",
            text=f"{endTime.strftime(humandate)}", font=SFPRO, size=24, fg=BLACK,
        )
        self.controller.textElement(
            imagepath=TIMEDETAILS, xpos=1680, ypos=320,
            root=self.viewFrame, classname="viewappendtime",
            text=f"{endTime.strftime(humantime)}", font=SFPRO, size=24, fg=BLACK,
        )

        # Completion Status
        if app.isCompleted:
            self.controller.buttonCreator(
                imagepath=COMPLETE, xpos=1240, ypos=400,
                root=self.viewFrame, classname="viewappcomplete",
                buttonFunction=lambda: self.showCompletedAgo(app)
            ) if self.role == "lecturer" else self.controller.labelCreator(
                imagepath=COMPLETE, xpos=1240, ypos=400,
                root=self.viewFrame, classname="viewappcomplete",
            )
        else:
            self.controller.buttonCreator(
                imagepath=INCOMPLETE, xpos=1240, ypos=400,
                root=self.viewFrame, classname="viewappcomplete",
                buttonFunction=lambda: self.showCompletedAgo(app)
            ) if self.role == "lecturer" else self.controller.labelCreator(
                imagepath=INCOMPLETE, xpos=1240, ypos=400,
                root=self.viewFrame, classname="viewappcomplete",
            )

    def showCompletedAgo(self, app: Appointment):
        prisma = self.prisma
        parent = self.controller.widgetsDict["viewappcomplete"]
        completedAgo = app.completedAt
        if completedAgo:
            completedAgo = self.KL.convert(completedAgo)
            # ask if want to uncomplete
            ask = MessageDialog(
                title="Completed At",
                parent=parent,
                message=f"This was completed at {completedAgo.strftime('%A, %B %d %Y at %I:%M:%S %p')}\nWould you like to uncomplete this appointment?",
                buttons=["Yes:success", "No:danger"]
            )
            ask.show()
            if ask.result == "Yes":
                newapp = prisma.appointment.update(
                    where={
                        "id": app.id
                    },
                    data={
                        "isCompleted": False,
                        "completedAt": None
                    },
                    include={
                        "student": {
                            "include": {
                                "userProfile": True
                            }
                        },
                        "lecturer": {
                            "include": {
                                "userProfile": True
                            }
                        }
                    }
                )
                self.refreshApptStatus(newapp)
            else:
                return
        else:
            # ask if want to accept
            ask = MessageDialog(
                title="Complete Appointment",
                parent=parent,
                message=f"Would you like to complete this appointment?",
                buttons=["Yes:success", "No:danger"]
            )
            ask.show()
            if ask.result == "Yes":
                newapp = prisma.appointment.update(
                    where={
                        "id": app.id
                    },
                    data={
                        "isCompleted": True,
                        "completedAt": self.UTC.convert(self.KL.convert(datetime.now()))
                    },
                    include={
                        "student": {
                            "include": {
                                "userProfile": True
                            }
                        },
                        "lecturer": {
                            "include": {
                                "userProfile": True
                            }
                        }
                    }
                )
                self.refreshApptStatus(newapp)
            else:
                return

    def showAcceptedAgo(self, app: Appointment, isStudent: bool = False, isLecturer: bool = False):
        prisma = self.prisma
        if isStudent and self.role == "student":
            parent = self.controller.widgetsDict["viewappstudstatus"]
            try:
                acceptedAgo = app.studAcceptAt
                acceptedAgo = self.KL.convert(acceptedAgo)
                # ask if want to unaccept
                ask = MessageDialog(
                    title="Accepted At",
                    parent=parent,
                    message=f"This was accepted at {acceptedAgo.strftime('%A, %B %d %Y at %I:%M:%S %p')}\nWould you like to unaccept this appointment?",
                    buttons=["Yes:success", "No:danger"]
                )
                ask.show()
                if ask.result == "Yes":
                    newapp = prisma.appointment.update(
                        where={
                            "id": app.id
                        },
                        data={
                            "studAccept": False,
                            "studAcceptAt": None,
                        },
                        include={
                            "student": {
                                "include": {
                                    "userProfile": True
                                }
                            },
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            }
                        }
                    )
                    self.refreshApptStatus(newapp)
                else:
                    return
            except:
                ask = MessageDialog(
                    title="Not Accepted Yet",
                    parent=parent,
                    message="This appointment has not been accepted yet by you, would you like to accept it?",
                    buttons=["Yes:success", "No:danger"]
                )
                ask.show()
                if ask.result == "Yes":
                    newapp = prisma.appointment.update(
                        where={
                            "id": app.id
                        },
                        data={
                            "studAccept": True,
                            "studAcceptAt": self.UTC.convert(self.KL.convert(datetime.now()))
                        },
                        include={
                            "student": {
                                "include": {
                                    "userProfile": True
                                }
                            },
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            }
                        }
                    )
                    self.refreshApptStatus(newapp)
                else:
                    return
        elif isLecturer and self.role == "student":
            try:
                acceptedAgo = app.lectAcceptAt
                acceptedAgo = self.KL.convert(acceptedAgo)
                messagebox.showinfo(
                    title="Accepted At", message=f"{acceptedAgo.strftime('%A, %B %d %Y at %I:%M:%S %p')}"
                )
            except:
                pass
        elif isLecturer and self.role == "lecturer":
            parent = self.controller.widgetsDict["viewappstudstatus"]
            try:
                acceptedAgo = app.lectAcceptAt
                acceptedAgo = self.KL.convert(acceptedAgo)
                # ask if want to unaccept
                ask = MessageDialog(
                    title="Accepted At",
                    parent=parent,
                    message=f"This was accepted at {acceptedAgo.strftime('%A, %B %d %Y at %I:%M:%S %p')}\nWould you like to unaccept this appointment?",
                    buttons=["Yes:success", "No:danger"]
                )
                ask.show()
                if ask.result == "Yes":
                    newapp = prisma.appointment.update(
                        where={
                            "id": app.id
                        },
                        data={
                            "lectAccept": False,
                            "lectAcceptAt": None,
                        },
                        include={
                            "student": {
                                "include": {
                                    "userProfile": True
                                }
                            },
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            }
                        }
                    )
                    self.refreshApptStatus(newapp)
                else:
                    return
            except:
                ask = MessageDialog(
                    title="Not Accepted Yet",
                    parent=parent,
                    message="This appointment has not been accepted yet by you, would you like to accept it?",
                    buttons=["Yes:success", "No:danger"]
                )
                ask.show()
                if ask.result == "Yes":
                    newapp = prisma.appointment.update(
                        where={
                            "id": app.id
                        },
                        data={
                            "lectAccept": True,
                            "lectAcceptAt": self.UTC.convert(self.KL.convert(datetime.now()))
                        },
                        include={
                            "student": {
                                "include": {
                                    "userProfile": True
                                }
                            },
                            "lecturer": {
                                "include": {
                                    "userProfile": True
                                }
                            }
                        }
                    )
                    self.refreshApptStatus(newapp)
                else:
                    return
        elif isStudent and self.role == "lecturer":
            try:
                acceptedAgo = app.studAcceptAt
                acceptedAgo = self.KL.convert(acceptedAgo)
                messagebox.showinfo(
                    title="Accepted At", message=f"{acceptedAgo.strftime('%A, %B %d %Y at %I:%M:%S %p')}"
                )
            except:
                pass

    def unloadAppView(self):
        self.viewFrame.grid_remove()
        # for app in appointments:
        #     print(app)
