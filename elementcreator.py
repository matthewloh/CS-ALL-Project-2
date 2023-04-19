from tkinter import *
from static import *
from PIL import Image, ImageTk
from dotenv import load_dotenv
import ttkbootstrap as ttk


def gridGenerator(root, width, height, color, overriderelief: bool = False, relief: str = FLAT, name=None):
    for x in range(width):
        root.columnconfigure(x, weight=1, uniform="row")
        Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
            row=0, column=x, sticky=NSEW)
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

    def userReg(self):
        self.controller.frameCreator(
        xpos=1000, ypos=40, framewidth= 800, frameheight= 920,
        root=self.parent, classname=f"{self.name}", 
        )
        self.frameref = self.controller.widgetsDict[f"{self.name}"]
        self.imgLabels = [
            (r"Assets\Login Page with Captcha\Sign Up Form.png", 0, 0, f"{self.name}BG", self.frameref),
        ]
        self.controller.settingsUnpacker(self.imgLabels, "label")
        #fullname, email, password, contact number, 
        #self, xpos,ypos,width, height,
        #root=None, classname=None, bg=WHITE, relief=FLAT,
        # fg=BLACK, textvariable=None, pady=None,):
        self.userRegEntries = [
            (40, 120, 720, 60, self.frameref, "fullname"),
            (40, 220, 720, 60, self.frameref, "emailname"),
            (40, 320, 340, 60, self.frameref, "password"),
            (40, 480, 340, 60, self.frameref, "confirmpassword"),
            (420, 320, 340, 60, self.frameref, "contactnumber"),
            (420, 500, 340, 40, self.frameref, "captcha"),

        ]
        for i in self.userRegEntries:
            self.controller.entryCreator(*i)
        
        
    def loadLecturerReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\LecturerForm.png", 0 , 600, f"{self.name}Lecturer", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        self.lecturerRegEntries = [
            (200, 660, 160, 40, self.frameref, "currentinstitution"),
            (200, 740, 160, 40, self.frameref, "currentschool"),
            (600, 660, 160, 40, self.frameref, "tenure"),
            (600, 740, 160, 40, self.frameref, "currentprogramme"),
            (200, 820, 560, 40, self.frameref, "coursetaught"),
        ]
        #self.lecturerRegEntries extends self.userRegEntries
        # implementing the joining of the two lists
        self.lecturerRegEntries = self.userRegEntries + self.lecturerRegEntries
        for i in self.lecturerRegEntries:
            self.controller.entryCreator(*i)

        frametoholdmenubutton = Frame(self.frameref, bg=WHITE, width=1, height=1)
        frametoholdmenubutton.grid(row=33, column=7, rowspan=2, columnspan=12, sticky=NSEW)
        frametoholdmenubutton.grid_propagate(False)
        gridGenerator(frametoholdmenubutton, 1, 1, WHITE)
        institutionmenustyle = ttk.Style()
        institutionmenustyle.configure("custom.TMenubutton", background=WHITE, foreground=BLACK, font=("Helvetica", 10))
        #institutionmenu = ttk.Menubutton(frametoholdmenubutton, text="Select Institution", style="custom.TMenubutton")
        institutionmenu = ttk.Menubutton(frametoholdmenubutton, text="Select Institution", style="custom.TMenubutton", name="institution")
        institutionmenu.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=NSEW)
        institutionmenu.grid_propagate(False)
        institutionmenu.option_add('*Menu.font', 'Helvetica 12')
        institutionmenu.menu = Menu(institutionmenu, tearoff=0)
        institute_var = StringVar()
        for x in ["INTI International University Nilai", "INTI International College Penang", "INTI International College Subang", "INTI College Sabah"]:
            institutionmenu.menu.add_radiobutton(label=x, variable=institute_var, command=lambda: institutionmenu.config(text=institute_var.get()))
        institutionmenu["menu"] = institutionmenu.menu
        self.controller.widgetsDict["institutionmenu"] = institutionmenu
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref, buttonFunction=lambda:print("hello"), pady=5)
        
        
    def loadStudentReg(self):
        self.userReg()
        self.imgLabels.append((r"Assets\Login Page with Captcha\StudentForm.png", 0 , 600, f"{self.name}Student", self.frameref))
        self.controller.settingsUnpacker(self.imgLabels, "label")
        self.studentRegEntries = [
            (200, 660, 160, 40, self.frameref, "currentinstitution"),
            (200, 740, 160, 40, self.frameref, "currentschool"),
            (600, 660, 160, 40, self.frameref, "semester"),
            (600, 740, 160, 40, self.frameref, "currentprogramme"),
            (200, 820, 560, 40, self.frameref, "enrolledcourses"),
        ]
        #self.studentRegEntries extends self.userRegEntries
        # implementing the joining of the two lists
        self.studentRegEntries = self.userRegEntries + self.studentRegEntries
        for i in self.studentRegEntries:
            self.controller.entryCreator(*i)
        self.controller.buttonCreator(r"Assets\Login Page with Captcha\ValidateInfoButton.png", 600, 560, classname="validateinfobtn", root=self.frameref, buttonFunction=lambda:print("hello"), pady=5)

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

