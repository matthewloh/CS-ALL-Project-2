from tkinter import *
from static import *
from PIL import Image, ImageTk
from dotenv import load_dotenv
import ttkbootstrap as ttk
from ttkbootstrap.toast import ToastNotification


def gridGenerator(root:Frame, width, height, color, overriderelief: bool = False, relief: str = FLAT, name=None):
    for x in range(width):
        root.columnconfigure(x, weight=1, uniform="row")
        if height > width:
            Label(root, width=1, bg=color, relief=relief if overriderelief else FLAT, name=name, autostyle=False).grid(
                row=0, column=x, sticky=NSEW)
    for y in range(height):
        root.rowconfigure(y, weight=1, uniform="row")
        if width >= height:
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

