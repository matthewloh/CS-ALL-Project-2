from tkinter import *
from static import *
from PIL import Image, ImageTk
from dotenv import load_dotenv
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification


def gridGenerator(root, width, height, color, overriderelief: bool = False, relief: str = FLAT, name=None):
    for x in range(width):
        root.columnconfigure(x, weight=1, uniform="row")
        # Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
        #     row=0, column=x, sticky=NSEW)
    for y in range(height):
        root.rowconfigure(y, weight=1, uniform="row")
        Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
            row=y, column=0, sticky=NSEW)
    return root

# The grid layout of the application is 96 x 54 to give each base grid a 20x20 pixel size

# Calculating the grid position of the is done through checking the W and H values of the image and then dividing it by 20
# i.e W : 960 H : 1080
#         960/20 = 48 1080/20 = 54
# The grid position is then set to 48,54
# Subject to offsetting the grid position by -1 to account for the 0 index of the grid
# Then, the rowspan and columnspan is set to the height and width of the image divided by 20

class UserForms(Frame):
    def __init__(self, parent=None, controller=None, name=None):
        super().__init__(parent, width=1, height=1, bg=WHITE, name=name)
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
        xpos=1000, ypos=40, framewidth= 800, frameheight= 920,
        root=self.parent, classname=f"{self.name}", 
        )
        self.frameref = self.controller.widgetsDict[f"{self.name}"]
        self.imgLabels = [
            (r"Assets\Login Page with Captcha\Sign Up Form.png", 0, 0, f"{self.name}BG", self.frameref),
        ]
        passwordvar = StringVar(value="")
        confPassvar = StringVar(value="")
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, "fullname"),
            (40, 220, 720, 60, self.frameref, "email", "isEmail"), 
            (40, 320, 340, 60, self.frameref, f"{self.name}passent", "isPassword"),
            (40, 480, 340, 60, self.frameref, f"{self.name}confpassent", "isConfPass"),
            (420, 320, 340, 60, self.frameref, "contactnumber", "isContactNo"),
            (420, 500, 340, 40, self.frameref, "captcha"),
        ]
        # looping to get a variable for each entry
        self.entrylist = []
    def loadLecturerReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\LecturerForm.png", 0 , 600, f"{self.name}Lecturer", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        # implementing the joining of the two lists
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOCAT", "SOE", "CEPS", "SOBIZ", "Unlisted"],
            "tenure": ["Full Time", "Part Time", "Unlisted"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course2": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course3": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        }
        institution = StringVar(name=f"{self.name}institution")
        school = StringVar(name=f"{self.name}school")
        tenure = StringVar(name=f"{self.name}tenure")
        programme = StringVar(name=f"{self.name}programme")
        course1 = StringVar(name=f"{self.name}course1")
        course2 = StringVar(name=f"{self.name}course2")
        course3 = StringVar(name=f"{self.name}course3")
        vars = {
            "institution": institution,
            "school": school,
            "tenure": tenure,
            "programme": programme,
            "course1": course1,
            "course2": course2,
            "course3": course3
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
                root=self.frameref, classname=name.capitalize(), text=f"Select {name.capitalize()}", listofvalues=values,
                variable=vars[name], font=("Helvetica", 10), command=lambda name=name:[print(vars[name].get())]
            )
        # fullname, email, password, confirmpassword, contactnumber
        entries = {
            "fullname": self.controller.widgetsDict["fullname"],
            "email": self.controller.widgetsDict["email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict["contactnumber"],
            "captcha": self.controller.widgetsDict["captcha"]
        }
        def foo():
            mainwindowcorners = self.controller.winfo_geometry().split("+")
            xval = int(mainwindowcorners[1])
            yval = int(mainwindowcorners[2])
            print(xval, yval)
            self.controller.mainwindowcorners = (xval, yval, "se")
            return self.controller.mainwindowcorners

        def foo_bar():
            details = []
            for name, entry in entries.items():
                details.append(entry.get())
            detailstoast = ToastNotification(
            title="Submission details",
            message=f"Full Name: {details[0]}\nEmail: {details[1]}\nPassword: {details[2]}\nContact Number: {details[4]}\nInstitution: {vars['institution'].get()}\nSchool: {vars['school'].get()}\nTenure: {vars['tenure'].get()}\nProgramme: {vars['programme'].get()}\nCourse 1: {vars['course1'].get()}\nCourse 2: {vars['course2'].get()}\nCourse 3: {vars['course3'].get()}",
            duration=3000,
            position=foo()
            )
            detailstoast.show_toast()
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
        buttonFunction=lambda:[foo_bar()],
        pady=5)
        
        
    def loadStudentReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\StudentForm.png", 0 , 600, f"{self.name}Student", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        for i in self.userRegEntries:
            self.controller.ttkEntryCreator(**self.tupleToDict(i))
        self.studentRegEntries = [
            # (200, 660, 160, 40, self.frameref, "currentinstitution"),
            # (200, 740, 160, 40, self.frameref, "currentschool"),
            # (600, 660, 160, 40, self.frameref, "semester"),
            # (600, 740, 160, 40, self.frameref, "currentprogramme"),
            # (200, 820, 560, 40, self.frameref, "enrolledcourses"),
        ]
        #self.studentRegEntries extends self.userRegEntries        
        lists = {
            "institution": ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"],
            "school": ["SOCAT", "SOE", "CEPS", "SOBIZ", "Unlisted"],
            "session": ["APR2023", "AUG2023", "JAN2024", "APR2024", "AUG2025"],
            "programme": ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"],
            "course1": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course2": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"],
            "course3": ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        }

        institution = StringVar()
        school = StringVar()
        session = StringVar()
        programme = StringVar()
        course1 = StringVar()
        course2 = StringVar()
        course3 = StringVar()

        vars = {
            "institution": institution,
            "school": school,
            "session": session,
            "programme": programme,
            "course1": course1,
            "course2": course2,
            "course3": course3,
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
                listofvalues=values, variable=vars[name], font=("Helvetica", 10),
                command=lambda name=name: print(vars[name].get())
            )

        # TODO: add absolute positioning for the toast notification
        entries = {
            "fullname": self.controller.widgetsDict["fullname"],
            "email": self.controller.widgetsDict["email"],
            "password": self.controller.widgetsDict[f"{self.name}passent"],
            "confirmpassword": self.controller.widgetsDict[f"{self.name}confpassent"],
            "contactnumber": self.controller.widgetsDict["contactnumber"],
            "captcha": self.controller.widgetsDict["captcha"]
        }
        def foo():
            mainwindowcorners = self.controller.winfo_geometry().split("+")
            xval = int(mainwindowcorners[1])
            yval = int(mainwindowcorners[2])
            print(xval, yval)
            self.controller.mainwindowcorners = (xval, yval, "se")
            return self.controller.mainwindowcorners
        def foo_bar():
            details = []
            for name, entry in entries.items():
                details.append(entry.get())
            detailstoast = ToastNotification(
            title="Submission details",
            message=f"Full Name: {details[0]}\nEmail: {details[1]}\nPassword: {details[2]}\nConfirm Password: {details[3]}\nContact Number: {details[4]}\nInstitution: {institution.get()}\nSchool: {school.get()}\nSession: {session.get()}\nProgramme: {programme.get()}\nCourse 1: {course1.get()}\nCourse 2: {course2.get()}\nCourse 3: {course3.get()}",
            duration=3000,
            position=foo()
            )
            detailstoast.show_toast()
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref,
        buttonFunction=lambda:[foo_bar()],
        pady=5)
        # listofunis = ["INTI International University Nilai", "INTI International College Penang", "INTI International College Subang", "INTI College Sabah"]
        # listofschools = ["SOBIZ", "SOEAT", "CEPS", "DCS", "Unlisted"]
        # listoftenures = ["Full Time", "Part Time", "Unlisted"]
        # listofprogrammes = ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"]
        # listofcourses = ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        # institutionvar = StringVar()
        # schoolvar  = StringVar()
        # tenurevar = StringVar()
        # programmevar = StringVar()
        # coursevar1 = StringVar()
        # coursevar2 = StringVar()
        # coursevar3 = StringVar()
        # self.controller.menubuttonCreator(xpos=140, ypos=660, width=240, height=40, root=self.frameref,
        # classname="institution", text="Select Institution", listofvalues=listofunis,
        # variable=institutionvar, font=("Helvetica", 10), command=lambda:[print(institutionvar.get())])
        # self.controller.menubuttonCreator(xpos=140, ypos=740, width=240, height=40, root=self.frameref,
        # classname="school", text="Select School", listofvalues=listofschools,
        # variable=schoolvar, font=("Helvetica", 10), command=lambda:[print(schoolvar.get())])
        # self.controller.menubuttonCreator(xpos=520, ypos=660, width=240, height=40, root=self.frameref,
        # classname="tenure", text="Select Tenure", listofvalues=listoftenures,
        # variable=tenurevar, font=("Helvetica", 10), command=lambda:[print(tenurevar.get())])
        # self.controller.menubuttonCreator(xpos=520, ypos=740, width=240, height=40, root=self.frameref,
        # classname="programme", text="Select Programme", listofvalues=listofprogrammes,
        # variable=programmevar, font=("Helvetica", 10), command=lambda:[print(programmevar.get())])
        # self.controller.menubuttonCreator(xpos=20, ypos=840, width=240, height=40, root=self.frameref,
        # classname="course1", text="Select Course 1", listofvalues=listofcourses,
        # variable=coursevar1, font=("Helvetica", 10), command=lambda:[print(coursevar1.get())])
        # self.controller.menubuttonCreator(xpos=280, ypos=840, width=240, height=40, root=self.frameref,
        # classname="course2", text="Select Course 2", listofvalues=listofcourses,
        # variable=coursevar2, font=("Helvetica", 10), command=lambda:[print(coursevar2.get())])
        # self.controller.menubuttonCreator(xpos=540, ypos=840, width=240, height=40, root=self.frameref,
        # classname="course3", text="Select Course 3", listofvalues=listofcourses,
        # variable=coursevar3, font=("Helvetica", 10), command=lambda:[print(coursevar3.get())])


        # listofunis = ["INTI International College Penang", "INTI International University Nilai", "INTI International College Subang", "INTI College Sabah"]
        # listofschools = ["SOCAT", "SOE", "CEPS", "SOBIZ", "Unlisted"]
        # listofsessions = ["APR2023", "AUG2023", "JAN2024", "APR2024", "AUG2025"]
        # listofprogrammes = ["BCSCU", "BCTCU", "DCS", "DCIT", "Unlisted"]
        # listofcourses = ["Computer Architecture & Network", "Object-Oriented Programming", "Mathematics For Computer Science", "Computer Science Activity Led Learning 2", "None"]
        # institutionvar = StringVar()
        # schoolvar  = StringVar()
        # sessionvar = StringVar()
        # programmevar = StringVar()
        # coursevar1 = StringVar()
        # coursevar2 = StringVar()
        # coursevar3 = StringVar()
        # self.controller.menubuttonCreator(xpos=140, ypos=660, width=240, height=40, root=self.frameref,
        # classname="institution", text="Select Institution", listofvalues=listofunis,
        # variable=institutionvar, font=("Helvetica", 10), command=lambda:[print(institutionvar.get())])
        # self.controller.menubuttonCreator(xpos=140, ypos=740, width=240, height=40, root=self.frameref,
        # classname="school", text="Select School", listofvalues=listofschools,
        # variable=schoolvar, font=("Helvetica", 10), command=lambda:[print(schoolvar.get())])
        # self.controller.menubuttonCreator(xpos=520, ypos=660, width=240, height=40, root=self.frameref,
        # classname="session", text="Select Session", listofvalues=listofsessions,
        # variable=sessionvar, font=("Helvetica", 10), command=lambda:[print(sessionvar.get())])
        # self.controller.menubuttonCreator(xpos=520, ypos=740, width=240, height=40, root=self.frameref,
        # classname="programme", text="Select Programme", listofvalues=listofprogrammes,
        # variable=programmevar, font=("Helvetica", 10), command=lambda:[print(programmevar.get())])
        # self.controller.menubuttonCreator(xpos=20, ypos=840, width=240, height=40, root=self.frameref,
        # classname="course1", text="Select Course 1", listofvalues=listofcourses,
        # variable=coursevar1, font=("Helvetica", 10), command=lambda:[print(coursevar1.get())])
        # self.controller.menubuttonCreator(xpos=280, ypos=840, width=240, height=40, root=self.frameref,
        # classname="course2", text="Select Course 2", listofvalues=listofcourses,
        # variable=coursevar2, font=("Helvetica", 10), command=lambda:[print(coursevar2.get())])
        # self.controller.menubuttonCreator(xpos=540, ypos=840, width=240, height=40, root=self.frameref,
        # classname="course3", text="Select Course 3", listofvalues=listofcourses,
        # variable=coursevar3, font=("Helvetica", 10), command=lambda:[print(coursevar3.get())])

