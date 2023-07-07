import os
import threading
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import simpledialog
import uuid
import boto3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from components.animatedgif import AnimatedGif
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma import Prisma
from win32gui import GetWindowText, GetForegroundWindow

from views.discussionsview import DiscussionsView
from views.appointmentsview import AppointmentsView
from PIL import Image, ImageTk, ImageSequence
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime

from views.learninghub import LearningHub


class CourseView(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg="#F6F5D7", name="courseview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()

    def postLogin(self, data: dict):
        # print("The data is", data)
        self.prisma = self.controller.mainPrisma
        modules = data["modules"]
        self.userId = data["id"]
        self.role = data["role"]
        modulecodes = []
        if self.role == "student":
            lecturerinfo = data["lecturerinfo"]
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
            # lecturer specific functions here like show student info
            # and upload course files and upload schedule
            self.loadcoursebuttons(modulecodes)

    def loadcoursebuttons(self, modulecodes: list = None):
        c = self.controller
        for widgetname, widget in self.canvas.children.items():
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
        self.mainframe = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="singlecourseviewframe"
        )
        self.viewUploadsFrame = self.controller.frameCreator(
            xpos=0, ypos=120, framewidth=1920, frameheight=800,
            root=self.mainframe, classname="viewuploadsframe"
        )
        self.uploadCreationFrame = self.controller.frameCreator(
            xpos=0, ypos=120, framewidth=1920, frameheight=800,
            root=self.mainframe, classname="uploadcreationframe"
        )
        self.staticImgLabels = [
            (r"Assets\My Courses\CoursesBG.png",
             0, 0, "courseviewbg", self),
            (r"Assets\My Courses\loadedcoursebg.png",
             0, 0, "loadedcoursebg", self.mainframe),
            (r"Assets\My Courses\moduleuploadsbg.png",
             0, 0, "moduleuploadsbg", self.viewUploadsFrame),
            (r"Assets\My Courses\uploaditemframebg.png",
             0, 0, "uploadcreationbg", self.uploadCreationFrame),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.canvas = self.controller.canvasCreator(
            xpos=0, ypos=100, width=1920, height=820,
            root=self, classname="coursescanvas",
            bgcolor="#F6F5D7", isTransparent=True, transparentcolor="#efefef"
        )
        self.viewUploadsFrame.grid_remove()
        self.uploadCreationFrame.grid_remove()

    def loadCourses(self, coursecode: str):
        self.canvas.grid_remove()
        self.mainframe.grid()
        self.mainframe.tkraise()
        self.BUCKET_NAME = f"{coursecode.lower()}bucket"
        buttonsList = [
            (r"Assets\My Courses\exitbutton.png", 1820, 20,
             "exitbutton", self.mainframe,
             lambda:[self.exitMainFrame(), self.focus_force()]
             ),
            (r"Assets\My Courses\exituploadsview.png", 1780, 20,
             "exituploadsview", self.viewUploadsFrame,
             lambda:[self.exitUploadsView(), self.focus_force()]),
        ]
        self.controller.settingsUnpacker(buttonsList, "button")
        coursecode = coursecode.lower()
        staticBtns = ["checkschedule", "gotolearninghub",
                      "viewcoursefiles", "exitbutton"]
        self.viewUploadsFrame.grid_remove()
        for widgetname, widget in self.mainframe.children.items():
            if isinstance(widget, Label) and not widgetname.startswith("!la"):
                if not widgetname.startswith(f"{coursecode}") and not widgetname.startswith("loadedcoursebg"):
                    widget.grid_remove()
                if widgetname.startswith(f"{coursecode}"):
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
            (f"{modulecode}_lecemail", lectureremail, 25, -1,
             220, 300, r"Assets\My Courses\whitebgtextfield.png"),
            (f"{modulecode}_lecphone", lecturerphone, 25, -1,
             220, 360, r"Assets\My Courses\whitebgtextfield.png")
        ]

        for classname, text, size, xoffset, xpos, ypos, imagepath in positions:
            self.controller.textElement(
                imagepath=imagepath, xpos=xpos, ypos=ypos,
                classname=classname, root=self.mainframe,
                text=text, size=size, xoffset=xoffset,
            )

        buttons = [
            (f"{modulecode}checkschedule", r"Assets\My Courses\checklecschedule.png", 1060, 280,
             lambda m=(modulecode, moduletitle, lecturername): self.loadAppointmentsView(m[0], m[1], m[2])),
            (f"{modulecode}_gotolearninghub", r"Assets\My Courses\gotolearninghub.png", 1340, 280,
             lambda m=(modulecode): self.loadLearningHubView(m)),
            (f"{modulecode}_viewcoursefiles", r"Assets\My Courses\loadcoursefiles.png", 1620, 280,
             lambda m=(modulecode): self.loadModuleUploadsView(m)),
            (f"{modulecode}_discussions", r"Assets\My Courses\go_to_discussions.png", 700, 780,
             lambda: self.loadDiscussionsView(modulecode, moduletitle)),
        ]
        try:
            self.controller.widgetsDict["uploaditembtn"].grid_remove()
        except:
            pass
        for classname, imagepath, xpos, ypos, buttonFunction in buttons:
            self.controller.buttonCreator(imagepath=imagepath, xpos=xpos, ypos=ypos,
                                          classname=classname, root=self.mainframe, buttonFunction=buttonFunction)
        buttonsList = [
            (r"Assets\My Courses\go_to_discussions.png", 700, 780,
             f"{modulecode}_discussions", self.mainframe,
             lambda:[self.loadDiscussionsView(modulecode, moduletitle), self.focus_force()]),
        ]
        self.controller.settingsUnpacker(buttonsList, "button")

        self.defaulturl = r"https://newinti.edu.my/campuses/inti-international-college-penang/"
        self.urlbar = self.controller.ttkEntryCreator(
            xpos=820, ypos=120, width=980, height=40,
            root=self.viewUploadsFrame, classname=f"uploadssearchbar",
        )
        self.urlbar.delete(0, END)
        self.urlbar.insert(0, f"{self.defaulturl}")

    def exitMainFrame(self):
        self.mainframe.grid_remove()
        self.exitUploadsView()
        self.exitUploadCreation()
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

    def exitUploadCreation(self):
        self.uploadCreationFrame.grid_remove()
        self.uploadCreationFrame.focus_set()

    def initializeWebView(self):
        col = int(820/20)
        row = int(180/20)
        w = int(1060/20)
        h = int(580/20)

        self.webview = WebView2(parent=self.viewUploadsFrame, width=1, height=1,
                                url=self.defaulturl)
        self.webview.grid(row=row, column=col, rowspan=h,
                          columnspan=w, sticky=NSEW)

    def loadUploadPage(self, modulecode):
        self.uploadCreationFrame.grid()
        self.uploadCreationFrame.tkraise()

        self.uploadTitleEntry = self.controller.ttkEntryCreator(
            xpos=1120, ypos=120, width=680, height=60,
            root=self.uploadCreationFrame, classname=f"uploadtitle",
        )
        self.uploadDescEntry = self.controller.ttkEntryCreator(
            xpos=1120, ypos=200, width=680, height=60,
            root=self.uploadCreationFrame, classname=f"uploaddesc",
        )
        self.uploadTitleEntry.delete(0, END)
        self.uploadDescEntry.delete(0, END)
        buttonSettings = [
            (r"Assets\My Courses\CreateUploads\UploadDocument.png", 940, 280,
             "uploaddocument", self.uploadCreationFrame,
             lambda: self.sendUploadRequest(modulecode, "pdf")),
            (r"Assets\My Courses\CreateUploads\UploadImage.png", 1160, 280,
             "uploadimage", self.uploadCreationFrame,
             lambda: self.sendUploadRequest(modulecode, "image")),
            (r"Assets\My Courses\CreateUploads\UploadVideo.png", 1380, 280,
             "uploadvideo", self.uploadCreationFrame,
             lambda: self.sendUploadRequest(modulecode, "video")),
            (r"Assets\My Courses\CreateUploads\UploadURL.png", 1600, 280,
             "uploadurl", self.uploadCreationFrame,
             lambda: self.sendUploadRequest(modulecode, "url")),
            (r"Assets\My Courses\exituploadsview.png", 1780, 20,
             "exituploadcreation", self.uploadCreationFrame,
             lambda:self.exitUploadCreationAndReload(modulecode)),
        ]

        self.controller.settingsUnpacker(buttonSettings, "button")
        print(f"Loading upload page for {modulecode}")
        self.modifyUploadFrame = ScrolledFrame(
            self.uploadCreationFrame, width=760, height=640, autohide=True,
            bootstyle="danger-rounded"
        )
        self.modifyUploadFrame.place(x=80, y=120, width=760, height=640)
        t = threading.Thread(target=self.frontEndModuleUploads, args=(
            modulecode, self.modifyUploadFrame, True))
        t.daemon = True
        t.start()

    def editModuleUploads(self, id, title, description, objKey, modulecode, filetype):
        print(id, title, description, objKey)
        self.uploadTitleEntry.delete(0, END)
        self.uploadDescEntry.delete(0, END)
        self.uploadTitleEntry.insert(0, title)
        self.uploadDescEntry.insert(0, description)
        parentWidget = self.controller.widgetsDict[f"{id}editbtn"]
        if filetype == "LINK":
            buttonsList = ["Edit Title:success",
                           "Edit Description:info", "Edit URL:warning", "Cancel"]
        else:
            buttonsList = ["Edit Title:success",
                           "Edit Description:info", "Cancel"]
        askOption = MessageDialog(
            parent=parentWidget,
            message=f"What do you want to do with the {filetype} upload {title}?",
            title=f"Select an option for the {filetype} upload {title}",
            buttons=buttonsList,
        )

        askOption.show()
        if askOption.result == "Edit Title":
            newTitle = Querybox.get_string(
                parent=parentWidget,
                prompt=f"Enter the new title for the {filetype} upload {title}",
                initialvalue=title,
            )
            if newTitle is not None:
                self.prisma.moduleupload.update(
                    where={
                        "id": id
                    },
                    data={
                        "title": newTitle
                    }
                )
                t = threading.Thread(target=self.frontEndModuleUploads, args=(
                    modulecode, self.modifyUploadFrame, True))
                t.daemon = True
                t.start()
        elif askOption.result == "Edit Description":
            newDesc = Querybox.get_string(
                parent=parentWidget,
                prompt=f"Enter the new description for the {filetype} upload {title}",
                initialvalue=description,
            )
            if newDesc is not None:
                self.prisma.moduleupload.update(
                    where={
                        "id": id
                    },
                    data={
                        "description": newDesc
                    }
                )
                t = threading.Thread(target=self.frontEndModuleUploads, args=(
                    modulecode, self.modifyUploadFrame, True))
                t.daemon = True
                t.start()
        elif askOption.result == "Edit URL":
            newURL = Querybox.get_string(
                parent=parentWidget,
                prompt=f"Enter the new URL for the {filetype} upload {title}",
                initialvalue=objKey,
            )
            if newURL is not None:
                self.prisma.moduleupload.update(
                    where={
                        "id": id
                    },
                    data={
                        "objKey": newURL
                    }
                )
                t = threading.Thread(target=self.frontEndModuleUploads, args=(
                    modulecode, self.modifyUploadFrame, True))
                t.daemon = True
                t.start()

    def deleteModuleUploads(self, id, title, description, objKey, modulecode, filetype):
        print(id, title, description, objKey)
        self.uploadTitleEntry.delete(0, END)
        self.uploadDescEntry.delete(0, END)
        self.uploadTitleEntry.insert(0, title)
        self.uploadDescEntry.insert(0, description)
        s3 = boto3.client('s3')
        BUCKET_NAME = self.BUCKET_NAME
        # get all items in the bucket
        askConfirmation = messagebox.askyesno(
            title=f"Delete the upload {title}?",
            message=f"Are you sure you want to delete the {filetype} upload with the title {title}?",
        )
        if not askConfirmation:
            return
        if filetype != "LINK":
            resp = s3.list_objects_v2(Bucket=BUCKET_NAME)
            for obj in resp['Contents']:
                if obj['Key'] == objKey:
                    s3.delete_object(Bucket=BUCKET_NAME, Key=objKey)
        prisma = self.prisma
        prisma.moduleupload.delete(
            where={
                "id": id
            }
        )
        loadedurl = self.webview.get_url()
        if loadedurl == f"https://csprojectbucket.s3.amazonaws.com/{objKey}":
            self.webview.load_url(self.defaulturl)
        toast = ToastNotification(
            title="Upload Deleted",
            message="The upload has been deleted successfully",
            duration=5000,
            bootstyle="success"
        )
        toast.show_toast()
        t = threading.Thread(target=self.frontEndModuleUploads, args=(
            modulecode, self.modifyUploadFrame, True))
        t.daemon = True
        t.start()

    def exitUploadCreationAndReload(self, modulecode):
        self.exitUploadCreation(),
        self.focus_force()
        t = threading.Thread(target=self.frontEndModuleUploads,
                             args=(modulecode, self.upframe))
        t.daemon = True
        t.start()

    def saveObjectKey(self, modulecode, objKey, fileType):
        prisma = self.prisma
        uploadType = {
            "pdf": "PDF",
            "image": "IMG",
            "video": "VIDEO",
            "url": "LINK"
        }
        module = prisma.module.find_first(
            where={
                "moduleCode": modulecode
            }
        )
        lecturer = prisma.lecturer.find_first(
            where={
                "userProfile": {
                    "is": {
                        "id": self.userId
                    }
                }
            }
        )
        upload = prisma.moduleupload.create(
            data={
                "title": self.uploadTitleEntry.get(),
                "description": self.uploadDescEntry.get(),
                "objKey": objKey,
                "uploadType": uploadType[fileType],
                "moduleId": module.id,
                "uploaderId": lecturer.id
            }
        )
        self.successToast.show_toast()
        t = threading.Thread(target=self.frontEndModuleUploads, args=(
            modulecode, self.modifyUploadFrame, True))
        t.daemon = True
        t.start()
        self.uploadTitleEntry.delete(0, END)
        self.uploadDescEntry.delete(0, END)

    def sendUploadRequest(self, modulecode, fileType):
        BUCKET_NAME = self.BUCKET_NAME
        self.successToast = ToastNotification(
            title="Upload successful",
            message="Your upload has been successfully uploaded",
            duration=5000,
            bootstyle=SUCCESS
        )
        if self.uploadTitleEntry.get() == "" or self.uploadDescEntry.get() == "":
            toast = ToastNotification(
                title="Missing fields",
                message=f"Please fill in all fields",
                duration=3000,
                bootstyle=DANGER
            )
            toast.show_toast()
            return
        if fileType == "url":
            entry = self.controller.entryCreator(
                xpos=1120, ypos=360, width=680, height=60,
                root=self.uploadCreationFrame, classname="uploadurlentry",
            )
            entry.focus_set()
            entry.bind("<Return>", lambda event: self.saveObjectKey(
                modulecode, entry.get(), fileType))
            toast = ToastNotification(
                title="Upload URL",
                message=f"Enter the URL for the {fileType} you want to upload and press enter.",
                duration=5000,
                bootstyle=INFO
            )
            toast.show_toast()
            return
        filetypes = {
            "pdf": ("Document Files", "*.pdf *.docx *.doc *.pptx *.ppt *.xlsx *.xls *.txt *.csv *rtf"),
            "image": ("Image Files", "*.jpg *.png *.jpeg *.gif *webp"),
            "video": ("Video Files", "*.mp4 *.mov *webm"),
        }
        filename = filedialog.askopenfilename(
            title=f"Upload {fileType} for {modulecode}",
            filetypes=[filetypes[fileType]]
        )
        if filename == "":
            return
        fileExt = filename.split(".")[-1].lower()
        if fileExt not in filetypes[fileType][1]:
            toast = ToastNotification(
                title="Invalid file type",
                message=f"Please upload a {filetypes[fileType][0]}",
                duration=3000,
                bootstyle=DANGER
            )
            toast.show_toast()
            return
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
        if fileExt in ["jpg", "jpeg", "png", "gif", "webp"]:
            if fileExt in ["jpg", "jpeg"]:
                fileExt = "jpeg"
            contentType = "image/" + fileExt
        elif fileExt in ["mp4", "webm", "mov"]:
            contentType = "video/" + fileExt
        elif fileExt in ["doc", "docx"]:
            if fileExt == "doc":
                contentType = "application/msword"
            else:
                contentType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif fileExt in ["pdf"]:
            contentType = "application/pdf"
        elif fileExt in ["ppt", "pptx"]:
            if fileExt == "ppt":
                contentType = "application/vnd.ms-powerpoint"
            else:
                contentType = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif fileExt in ["xls", "xlsx"]:
            if fileExt == "xls":
                contentType = "application/vnd.ms-excel"
            else:
                contentType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif fileExt in ["txt", "csv", "rtf"]:
            if fileExt == "txt":
                contentType = "text/plain"
            elif fileExt == "csv":
                contentType = "text/csv"
            else:
                contentType = "application/rtf"
        else:
            toast = ToastNotification(
                title="Invalid file type",
                message=f"Please upload a {filetypes[fileType][0]}",
                duration=3000,
                bootstyle=DANGER
            )
            toast.show_toast()
            return
        savedfilename = os.path.basename(filename)
        savedfilename = savedfilename.replace(" ", "_").split(".")[0]
        askConfirmation = messagebox.askyesno(
            title="Confirm Upload",
            message=f"Are you sure you want to upload {savedfilename}.{fileExt}?"
        )
        if not askConfirmation:
            return
        askRename = messagebox.askyesno(
            title="Rename file?",
            message=f"Do you want to rename {savedfilename}.{fileExt}? The file will remain a .{fileExt} file"
        )
        if askRename:
            newfilename = simpledialog.askstring(
                title="Rename file",
                prompt="Enter new file name",
            )
            if newfilename is not None and newfilename != "":
                newfilename = newfilename.replace(" ", "_").strip()
                savedfilename = f"{newfilename}"
        s3 = boto3.client('s3')
        # check for duplicate file names in the bucket
        listofobjects = s3.list_objects_v2(
            Bucket=BUCKET_NAME, Prefix=f"{savedfilename}.{fileExt}")
        numOfDuplicates = listofobjects.get("KeyCount", 0)
        if listofobjects.get("KeyCount", 0) > 0:
            if numOfDuplicates == 1:
                numofSameFiles = s3.list_objects_v2(
                    Bucket=BUCKET_NAME, Prefix=f"{savedfilename}").get("KeyCount", 0)
                numOfDuplicates = numofSameFiles
            askDuplicate = messagebox.askyesno(
                title="Duplicate file name",
                message=f"{savedfilename}.{fileExt} already exists in the bucket. Do you want to overwrite it? Otherwise, the file will be saved as {savedfilename}({numOfDuplicates}).{fileExt}"
            )
            if askDuplicate == False:
                savedfilename = f"{savedfilename}({numOfDuplicates})"
            else:
                # ONLY OVERWRITE when the key is the same, thus not needing to create a new moduleupload
                savedfilename = f"{savedfilename}.{fileExt}"
                with open(filename, "rb") as f:
                    s3.upload_fileobj(
                        f, BUCKET_NAME, savedfilename,
                        ExtraArgs={'ACL': 'public-read',
                                   'ContentType': contentType}
                    )
                    self.successToast.message = f"Successfully updated {savedfilename}"
                    self.successToast.show_toast()
                    t = threading.Thread(target=self.frontEndModuleUploads, args=(
                        modulecode, self.modifyUploadFrame, True))
                    t.daemon = True
                    t.start()
                return
        savedfilename = f"{savedfilename}.{fileExt}"
        with open(filename, "rb") as f:
            # rename file to prevent duplicates
            s3.upload_fileobj(
                f, BUCKET_NAME, savedfilename,
                ExtraArgs={'ACL': 'public-read',
                           'ContentType': contentType}
            )
        self.saveObjectKey(modulecode, savedfilename, fileType)

    def loadModuleUploadsView(self, modulecode):
        self.viewUploadsFrame.grid()
        self.viewUploadsFrame.tkraise()
        self.urlbar.delete(0, END)
        self.urlbar.insert(0, f"{self.defaulturl}")
        _ = [
            (r"Assets\My Courses\uploaditembtn.png", 420, 20,
             "uploaditembtn", self.viewUploadsFrame,
             lambda:[self.loadUploadPage(modulecode)])
        ]
        if self.role == "lecturer":
            self.controller.settingsUnpacker(_, "button")
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
                toast.show_toast()
            self.webview.after(10000, regainFocus)
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
        self.upframe = ScrolledFrame(
            self.viewUploadsFrame, width=760, height=640, autohide=True,
            bootstyle="warning-rounded"
        )
        self.upframe.place(x=40, y=120, width=760, height=640)
        t = threading.Thread(target=self.frontEndModuleUploads,
                             args=(modulecode, self.upframe))
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
        return uploads

    def frontEndModuleUploads(self, modulecode, rootFrame: ScrolledFrame, withModifyBtns=False):
        uploads = self.loadModuleUploads(modulecode)
        h = len(uploads) * 100 + 40
        if h <= 640:
            h = 640
        rootFrame.config(height=h)
        # White BG
        Label(rootFrame, bg="white", width=760, height=h,
              relief=FLAT, bd=0).place(x=0, y=0, width=760, height=h)
        startx = 20
        starty = 40
        kl = timezone("Asia/Kuala_Lumpur")
        for u in uploads:
            createdAt = kl.convert(u.createdAt)
            editedAt = kl.convert(u.editedAt)
            self.renderModuleUploads(
                rootFrame,
                u.uploadType, u.id, u.title, u.description, u.objKey,
                createdAt, editedAt,
                startx, starty,
                u.uploader.userProfile.fullName, u.uploader.userProfile.email,
                withModifyBtns, modulecode
            )
            starty += 100

    def renderModuleUploads(self,
                            rootFrame: ScrolledFrame,
                            filetype, id, title, description, objKey,
                            createdat, editedat, x, y,
                            uploadername, uploaderemail,
                            withModifyBtns=False, modulecode=None
                            ):
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
        tiptext = f"""Click me to load {title}, a {filetype.title()} file.\nDescription: {description}\nName: {objKey},\nUploaded by: {uploadername} ({uploaderemail})"""
        b = c.buttonCreator(
            imagepath=btnImgDict[filetype], xpos=x, ypos=y,
            classname=f"{id}btn", root=rootFrame,
            buttonFunction=lambda: self.loadAndOpenObject(
                objKey, fileType=filetype),
            isPlaced=True,
        )
        titleandfile = f"{title} | {objKey}"
        ToolTip(b, text=tiptext, bootstyle=(INFO, INVERSE))
        t1 = c.textElement(
            imagepath=textBgDict[filetype], xpos=x+20, ypos=y,
            classname=f"{id}title", root=rootFrame,
            text=titleandfile, fg=BLACK, size=20, font=INTERBOLD,
            buttonFunction=lambda: self.loadAndOpenObject(
                objKey, fileType=filetype),
            isPlaced=True, xoffset=-1,
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
            classname=f"{id}time", root=rootFrame,
            text=strTime, fg=BLACK, size=16, font=INTER,
            buttonFunction=lambda: self.loadAndOpenObject(
                objKey, fileType=filetype),
            isPlaced=True, xoffset=-1,
        )
        ToolTip(t2, text=tiptext, bootstyle=(INFO, INVERSE))

        if withModifyBtns:
            c.buttonCreator(
                imagepath=r"Assets\DiscussionsView\edit.png", xpos=x+500, ypos=y+20,
                classname=f"{id}editbtn", root=rootFrame,
                buttonFunction=lambda: self.editModuleUploads(
                    id, title, description, objKey, modulecode, filetype),
                isPlaced=True,
            )
            c.buttonCreator(
                imagepath=r"Assets\DiscussionsView\Trash.png", xpos=x+560, ypos=y+20,
                classname=f"{id}deletebtn", root=rootFrame,
                buttonFunction=lambda: self.deleteModuleUploads(
                    id, title, description, objKey, modulecode, filetype),
                isPlaced=True,
            )

    def loadAndOpenObject(self, objKey, fileType):
        BUCKET_NAME = self.BUCKET_NAME
        if fileType == "LINK":
            self.webview.load_url(objKey)
            return
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{objKey}"
        self.webview.load_url(url)

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

    def loadAppointmentsView(self, modulecode, moduletitle, lecturerName):
        WD = self.controller.widgetsDict
        appView = WD["appointmentsview"]
        appView.creationFrame.grid_remove()
        appView.viewFrame.grid_remove()
        appView.loadAllDetailsForCreation()
        appView.loadAppCreation()
        self.controller.show_canvas(AppointmentsView)
        if self.role == "student":
            appView.module.set(f"{modulecode} - {moduletitle}")
            appView.lecturer.set(lecturerName)
            appView.loadLecturerMenuBtns(appView.module.get())
            appView.loadTimeslotMenuBtns(appView.module.get(), lecturerName)
            WD["modules"].configure(text=f"{modulecode} - {moduletitle}")
            WD["lecturersaptmenu"].configure(text=lecturerName)

    def loadLearningHubView(self, modulecode):
        WD = self.controller.widgetsDict
        learningHub = WD["learninghub"]
        learningHub.loadCourseHubContent(modulecode)
        self.controller.show_canvas(LearningHub)
