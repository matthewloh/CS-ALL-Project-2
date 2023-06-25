import random
import re
import string
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
from components.animatedgif import AnimatedGif
from captcha.image import ImageCaptcha
from components.animatedgif import AnimatedGif
from components.animatedstarbtn import AnimatedStarBtn
from PIL import Image, ImageTk, ImageSequence
import bcrypt


class UserForms(Frame):
    def __init__(self, parent=None, controller: ElementCreator = None, name=None):
        super().__init__(parent, width=1, height=1, bg="#344557", name=name)
        self.controller = controller
        self.parent = parent
        self.name = name
        self.prisma = self.controller.mainPrisma

    def tupleToDict(self, tup):
        if len(tup) == 6:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname"], tup))
        elif len(tup) == 7:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname", "validation"], tup))
        elif len(tup) == 8:
            return dict(zip(["xpos", "ypos", "width", "height", "root", "classname", "validation", "captchavar"], tup))

    def loadAllDetailsForRegistration(self):
        prisma = self.prisma
        institutions = prisma.institution.find_many(
            include={
                "school": {
                    "include": {
                        "programme": {
                            "include": {
                                "modules": True
                            }
                        }
                    }
                }
            }
        )
        return institutions

    def userReg(self):
        self.frameref = self.controller.frameCreator(
            xpos=1000, ypos=40, framewidth=800, frameheight=920,
            root=self.parent, classname=f"{self.name}",
        )
        self.imgLabels = [
            (r"Assets\Login Page with Captcha\Sign Up Form.png",
             0, 0, f"{self.name}BG", self.frameref),
        ]
        self.captchavar = StringVar()
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, f"{self.name}fullname"),
            (40, 220, 720, 60, self.frameref, f"{self.name}email", "isEmail"),
            (40, 320, 340, 60, self.frameref,
             f"{self.name}passent", "isPassword"),
            (40, 480, 340, 60, self.frameref,
             f"{self.name}confpassent", "isConfPass"),
            (420, 320, 340, 60, self.frameref,
             f"{self.name}contactnumber", "isContactNo"),
            (420, 500, 340, 40, self.frameref, f"{self.name}captcha", "isCaptcha", self.captchavar),
        ]

    def loadRegThread(self, role):
        t = threading.Thread(target=self.loadReg, args=(role,))
        t.daemon = True
        t.start()
        
    def loadReg(self, role):
        toast = ToastNotification(
            title="Please be patient",
            message="We are loading the Registration Form for you",
            bootstyle=INFO,
        )
        toast.show_toast()
        self.userReg()
        lectBgPath = (r"Assets\Login Page with Captcha\LecturerForm.png"
                      , 0, 600, f"{self.name}Lecturer", self.frameref)
        studBgPath = (r"Assets\Login Page with Captcha\StudentForm.png",
                    0, 600, f"{self.name}Student", self.frameref)
        if role == "teacher":
            self.imgLabels.append(lectBgPath)
        elif role == "student":
            self.imgLabels.append(studBgPath)
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        self.generateCaptchaChallenge()
        # Create a structure to split institutions and their schools
        # an Institution has many Schools
        # A school has many Programmes
        # A programme has many modules
        # I.E IICP -> SOC -> BCSCU -> INT4004CEM
        self.instDict = {}
        self.fullInfo = self.loadAllDetailsForRegistration()
        toast.hide_toast()
        successtoast = ToastNotification(
            title="Success!",
            message="You can now register.",
            bootstyle=SUCCESS,
            duration=1000,
        )
        successtoast.show_toast()
        for inst in self.fullInfo:
            schoolsDict = {}
            if inst.school == []:
                self.instDict[f"{inst.institutionCode}"] = {
                    "schools": schoolsDict,
                }
                continue
            for school in inst.school:
                progDict = {}
                if school.programme == []:
                    schoolsDict[f"{school.schoolCode}"] = {
                        "programmes": progDict,
                    }
                    continue
                for programme in school.programme:
                    modList = []
                    if programme.modules == []:
                        progDict[f"{programme.programmeCode}"] = {
                            "modules": modList,
                        }
                        continue
                    for module in programme.modules:
                        modList.append(module.moduleTitle)
                    progDict[f"{programme.programmeCode}"] = {
                        "modules": modList,
                    }
                schoolsDict[f"{school.schoolCode}"] = {
                    "programmes": progDict,
                }
            self.instDict[f"{inst.institutionCode}"] = {
                "schools": schoolsDict,
            }
        institutionlist = list(self.instDict.keys())
        lists = {
            "institution": institutionlist,
        }
        self.institution = StringVar()
        self.school = StringVar()
        self.tenure = StringVar()
        self.programme = StringVar()
        self.course1 = StringVar()
        self.course2 = StringVar()
        self.course3 = StringVar()
        self.course4 = StringVar()
        if role == "teacher":
            self.tenure = StringVar()
        elif role == "student":
            self.session = StringVar()
        vars = {
            "institution": self.institution,
            "tenure": self.tenure,
        } if role == "teacher" else {
            "institution": self.institution,
            "session": self.session,
        }
        positions = {
            "institution": {"x": 160, "y": 660, "width": 240, "height": 40},
            "tenure": {"x": 520, "y": 660, "width": 240, "height": 40},
        } if role == "teacher" else {
            "institution": {"x": 160, "y": 660, "width": 240, "height": 40},
            "session": {"x": 520, "y": 660, "width": 240, "height": 40},
        }

        for name, values in lists.items():
            self.controller.menubuttonCreator(
                xpos=positions[name]["x"], ypos=positions[name]["y"], width=positions[name]["width"], height=positions[name]["height"],
                root=self.frameref, classname=name, text=f"Select {name}", listofvalues=values,
                variable=vars[name], font=("Helvetica", 10),
                command=lambda name=name: [
                    self.loadSchoolMenubuttons(vars[name].get())]
            )
        # tenure menu button
        if role == "teacher":
            tenurelist = ["FULLTIME", "PARTTIME"]
            positionKey = positions["tenure"]
            classname = "tenure"
            varKey = vars["tenure"]
        elif role == "student":
            sessionlist = ["APR2023", "AUG2023", "JAN2024"]
            positionKey = positions["session"]
            classname = "session"
            varKey = vars["session"]

        self.controller.menubuttonCreator(
            xpos=positionKey["x"], ypos=positionKey["y"], width=positionKey["width"], height=positionKey["height"],
            root=self.frameref, classname=classname, text=f"Select {classname.title()}", listofvalues=tenurelist if role == "teacher" else sessionlist,
            variable=varKey, font=("Helvetica", 10),
            command=lambda: [print(f"{vars[f'{classname}'].get()}")]
        )
        entries = {
            "fullname": self.controller.widgetsDict[f"{self.name}fullname"],
            "email": self.controller.widgetsDict[f"{self.name}email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict[f"{self.name}contactnumber"],
            "captcha": self.controller.widgetsDict[f"{self.name}captcha"]
        }
        def checkCaptchaCorrect():
            if self.validate_captcha(entries["captcha"].get()):
                toast = ToastNotification(
                    title="Captcha Correct",
                    message="Captcha is correct",
                    duration=3000,
                    bootstyle="success"
                )
                toast.show_toast()
            else:
                pass
                
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
                                      buttonFunction=lambda: [
                                          checkCaptchaCorrect()],
                                      pady=5)
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\regeneratecaptcha.png", 680, 420, 
                classname="regeneratecaptcha", root=self.frameref,
                buttonFunction=lambda: self.generateCaptchaChallenge())
        if role == "teacher":
            self.controller.buttonCreator(
                r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
                classname=f"{self.name}completeregbutton", buttonFunction=lambda: self.send_data(
                    data={
                        "fullName": entries["fullname"].get(),
                        "email": entries["email"].get(),
                        "password": self.encryptPassword(entries["password"].get()),
                        "confirmPassword": self.encryptPassword(entries["confirmpassword"].get()),
                        "contactNo": entries["contactnumber"].get(),
                        "currentCourses": [self.course1.get(), self.course2.get(), self.course3.get(), self.course4.get()],
                        "institution": self.institution.get(),
                        "school":  self.school.get(),
                        "tenure": self.tenure.get(),
                        "programme": self.programme.get(),
                        "role": "LECTURER"
                    }
                ),
                root=self.parent
            )
        elif role == "student":
            self.controller.buttonCreator(
                r"Assets\Login Page with Captcha\CompleteRegSignIn.png", 1240, 980,
                classname=f"{self.name}completeregbutton", buttonFunction=lambda: self.send_data(
                    data={
                        "fullName": entries["fullname"].get(),
                        "email": entries["email"].get(),
                        "password": self.encryptPassword(entries["password"].get()),
                        "confirmPassword": self.encryptPassword(entries["confirmpassword"].get()),
                        "contactNo": entries["contactnumber"].get(),
                        "currentCourses": [self.course1.get(), self.course2.get(), self.course3.get(), self.course4.get()],
                        "institution": self.institution.get(),
                        "school":  self.school.get(),
                        "session": self.session.get(),
                        "programme": self.programme.get(),
                        "role": "STUDENT"
                    }
                ),
                root=self.parent
            )
        self.completeregbutton = self.controller.widgetsDict[f"{self.name}completeregbutton"]

    def generateCaptchaChallenge(self):
        # fonts=[r"Fonts\AvenirNext-Regular.ttf", r"Fonts\SF-Pro.ttf"]
        image = ImageCaptcha(width=260, height=80, )
        # random alphanumeric string of length 6
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        data = image.generate(captcha_text)
        image.write(captcha_text, r"Assets\Login Page with Captcha\captcha.png")
        self.captchavar.set(captcha_text)
        self.controller.labelCreator(
            imagepath=r"Assets\Login Page with Captcha\captcha.png",
            xpos=420, ypos=420, classname="imagecaptchachallenge",
            root=self.frameref
        )

    def loadSchoolMenubuttons(self, instCode):
        # remove all widgets and refresh options
        for widgetname, widget in self.frameref.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["schoolhostfr", "programmehostfr",
                                  "course1hostfr", "course2hostfr", "course3hostfr", "course4hostfr"]:
                    widget.grid_remove()
        # reset variables
        for var in [self.school, self.programme, self.course1, self.course2, self.course3, self.course4]:
            var.set("")
        positions = {
            "school": {"x": 160, "y": 740, "width": 240, "height": 40},
        }
        schoollist = list(self.instDict[f"{instCode}"]["schools"].keys())
        if schoollist == []:
            schoollist = ["No Schools Found"]
            self.school.set("")
        self.controller.menubuttonCreator(
            xpos=positions["school"]["x"], ypos=positions["school"]["y"], width=positions[
                "school"]["width"], height=positions["school"]["height"],
            root=self.frameref, classname="school", text=f"Select School", listofvalues=schoollist,
            variable=self.school, font=("Helvetica", 10),
            command=lambda: [self.loadProgrammeMButtons(
                instCode, self.school.get())]
        )

    def loadProgrammeMButtons(self, instCode, schoolCode):
        # remove all widgets and refresh options
        if schoolCode == "No Schools Found":
            return
        for widgetname, widget in self.frameref.children.items():
            if not widgetname.startswith("!la"):
                if widgetname in ["programmehostfr",
                                  "course1hostfr", "course2hostfr", "course3hostfr", "course4hostfr"]:
                    widget.grid_remove()
        # reset variables
        for var in [self.programme, self.course1, self.course2, self.course3, self.course4]:
            var.set("")
        positions = {
            "programme": {"x": 520, "y": 740, "width": 240, "height": 40},
        }
        programmeslist = list(
            self.instDict[f"{instCode}"]["schools"][f"{schoolCode}"]["programmes"])
        self.controller.menubuttonCreator(
            xpos=positions["programme"]["x"], ypos=positions["programme"]["y"], width=positions[
                "programme"]["width"], height=positions["programme"]["height"],
            root=self.frameref, classname="programme", text=f"Select Programme", listofvalues=programmeslist,
            variable=self.programme, font=("Helvetica", 10),
            command=lambda: [self.loadModulesMButtons(
                instCode, schoolCode, self.programme.get())]
        )

    def loadModulesMButtons(self, instCode, schoolCode, progCode):
        vars = {
            "course1": self.course1,
            "course2": self.course2,
            "course3": self.course3,
            "course4": self.course4,
        }
        positions = {
            "course1": {"x": 160, "y": 800, "width": 280, "height": 40},
            "course2": {"x": 160, "y": 860, "width": 280, "height": 40},
            "course3": {"x": 480, "y": 800, "width": 280, "height": 40},
            "course4": {"x": 480, "y": 860, "width": 280, "height": 40},
        }
        moduleslist = list(self.instDict[f"{instCode}"]["schools"]
                           [f"{schoolCode}"]["programmes"][f"{progCode}"]["modules"])
        enumeratedModList = list(enumerate(moduleslist.copy(), 1))
        for i, module in enumeratedModList:
            self.controller.menubuttonCreator(
                xpos=positions[f"course{i}"]["x"], ypos=positions[f"course{i}"]["y"], width=positions[
                    f"course{i}"]["width"], height=positions[f"course{i}"]["height"],
                root=self.frameref, classname=f"course{i}", text=f"Select Module {i}", listofvalues=moduleslist,
                variable=vars[f"course{i}"], font=("Helvetica", 10),
                command=lambda c=f"course{i}": [
                    self.checkDuplicateModules(c, vars[c].get(), moduleslist)]
            )

    def checkDuplicateModules(self, courseNum, course, originalModules):
        vars = {
            "course1": self.course1,
            "course2": self.course2,
            "course3": self.course3,
            "course4": self.course4,
        }
        positions = {
            "course1": {"x": 160, "y": 800, "width": 280, "height": 40},
            "course2": {"x": 160, "y": 860, "width": 280, "height": 40},
            "course3": {"x": 480, "y": 800, "width": 280, "height": 40},
            "course4": {"x": 480, "y": 860, "width": 280, "height": 40},
        }
        modules = originalModules.copy()
        checkedcourseNum = courseNum
        checkedcourse = course
        selectedCourses = [self.course1.get(), self.course2.get(
        ), self.course3.get(), self.course4.get()]
        # print("The selected courses are,", selectedCourses)
        # Check for duplicates
        if selectedCourses.count(checkedcourse) > 1:
            # Will be overriding the one before the current one
            for i, x in enumerate(selectedCourses, 1):
                if x == checkedcourse and i != int(checkedcourseNum[-1]):
                    # print("Removing", (i, x))
                    vars[f"course{i}"].set("")
                    self.controller.menubuttonCreator(
                        xpos=positions[f"course{i}"]["x"], ypos=positions[f"course{i}"]["y"], width=positions[
                            f"course{i}"]["width"], height=positions[f"course{i}"]["height"],
                        root=self.frameref, classname=f"course{i}", text=f"Select Module {i}", listofvalues=modules,
                        variable=vars[f"course{i}"], font=("Helvetica", 10),
                        command=lambda c=f"course{i}": [
                            self.checkDuplicateModules(c, vars[c].get(), modules)]
                    )
    
    def encryptPassword(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def validatePassword(self, password: str, encrypted: str) -> str:
        return bcrypt.checkpw(password.encode("utf-8"), encrypted.encode("utf-8"))

    def prismaFormSubmit(self,  data: dict):
        # LECTURER OR STUDENT
        prisma = self.controller.mainPrisma
        emailCheck = prisma.userprofile.find_first(
            where={
                "email": data["email"]
            }
        )
        if emailCheck:
            toast = ToastNotification(
                title="Error",
                message="Email already exists, please use another email address",
                bootstyle="danger",
                duration=5000,
            )
            toast.show_toast()
            self.gif.grid_forget()
            return 
        try:
            if data["role"] == "STUDENT":
                school = prisma.school.find_first(
                    where={
                        "schoolCode": data["school"]
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
                    duration=3000,
                    bootstyle=SUCCESS
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
                toast = ToastNotification(
                    title="Success",
                    message=f"Welcome, {lecturer.userProfile.fullName}!",
                    duration=3000,
                    bootstyle=SUCCESS
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
            return
        self.controller.loadSignIn()
    
    def validate_captcha(self, captcha: str):
        captchaToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        if captcha != self.captchavar.get():
            captchaToast.message = "Captcha is incorrect."
            captchaToast.show_toast()
            return False
        return True
    
    def validate_password(self, password: str, confirmpassword: str):
        pwToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        symbols = "!@#$%^&*()_+"
        if password != confirmpassword:
            pwToast.message = "Passwords do not match."
            pwToast.show_toast()
            return False
        elif not any(char.isdigit() for char in password):
            msg = "Password should have at least one numeral."
        elif not any(char.isupper() for char in password):
            msg = "Password should have at least one uppercase letter."
        elif not any(char.islower() for char in password):
            msg = "Password should have at least one lowercase letter."
        elif not any(char in symbols for char in password):
            msg = "Password should have at least one of the symbols !@#$%^&*()_+"
        elif len(password) < 8:
            msg = "Password should be at least 8 characters."
        else:
            return True
        pwToast.message = msg
        pwToast.show_toast()
        return False
   
    def validate_email(self, email: str, role:str):
        emailToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        if role.startswith("student"):
            regex = re.compile(r"^[a-zA-Z0-9_.+-]+@student.newinti.edu.my$")
            addressedAs = "student"
        elif role.startswith("teacher"):
            regex = re.compile(r"^[a-zA-Z0-9_.+-]+@newinti.edu.my$")
            addressedAs = "lecturer"
        if re.match(regex, email):
            return True
        else:
            emailToast.message = f"Please enter a valid {addressedAs} email."
            emailToast.show_toast()
            return False
        
    def validate_contactNo(self, contactNo: str):
        contactToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        phoneregex = re.compile(r"^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$")
        if re.match(phoneregex, contactNo):
            return True
        else:
            contactToast.message = "Please enter a valid contact number."
            contactToast.show_toast()
            return False
    
    def validateData(self, data: dict):
        fullname = data["fullName"]
        email = data["email"]
        contactNo = data["contactNo"]
        password = self.controller.widgetsDict[f"{self.name}passent"].get()
        confirmpassword = self.controller.widgetsDict[f"{self.name}confpassent"].get()
        captcha = self.controller.widgetsDict[f"{self.name}captcha"].get()
        entries = [fullname, email, contactNo, password, confirmpassword]
        mainToast = ToastNotification(
            title="Error",
            message="",
            duration=3000,
            bootstyle=DANGER
        )
        for info in entries:
            if info == "":
                toast = ToastNotification(
                    title="Error",
                    message=f"Please fill in the fields.",
                    duration=3000,
                    bootstyle=DANGER
                )
                toast.show_toast()
                return False 
        if any(char in string.punctuation for char in fullname):
            errMsg = "Your name cannot contain any special characters."
            mainToast.message = errMsg
            mainToast.show_toast()
            return False
        if not self.validate_email(email, self.name):
            return False
        if not self.validate_password(password, confirmpassword):
            return False
        if not self.validate_contactNo(contactNo):
            return False
        if captcha != self.captchavar.get():
            mainToast.message = "Please enter the correct captcha."
            mainToast.show_toast()
            return False
        for var in [self.course1, self.course2, self.course3, self.course4]:
            blankCourses = 0
            if var.get() == "":
                blankCourses += 1
        if blankCourses >= 3:
            toast = ToastNotification(
                title="Error",
                message=f"Please select at least 1 course.",
                duration=3000
            )
            toast.show_toast()
            return False
        return True

    def send_data(self, data: dict):
        if self.validateData(data) == False:
            return
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
