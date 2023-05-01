from tkinter import *
from elementcreator import gridGenerator
from static import *
# TODO: Make this modular
class DashboardCanvas(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="dashboardcanvas", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
                
class SearchPage(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="searchpage", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Search Page", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")

class Chatbot(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="chatbot", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\Chatbot\ChatbotBg.png", 0, 0, "ChatbotBgLabel", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.webview2creator(xpos=60, ypos=160, framewidth=1200, frameheight=740, root=self, classname="chatbotwebview2", url="http://localhost:5555/")

class LearningHub(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="learninghub", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        namelabel = Label(self, text="Learning Hub", font=("Avenir Next", 20), bg=WHITE)
        namelabel.grid(row=0, column=0, columnspan=96, rowspan=5, sticky="nsew")
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\LearningHub\LearningHubBG.png", 0, 0, "LearningHubBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")



class CourseView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg="#F6F5D7", name="courseview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\My Courses\CoursesBG.png", 0, 0, "CoursesBG", self),
        ]
        self.controller.canvasCreator(80, 100, 1760, 720, root=self, classname="coursescanvas", bgcolor="#F6F5D7",
            isTransparent=True, transparentcolor="#efefef")
        canvas = self.controller.widgetsDict["coursescanvas"]
        self.buttonImgLabels = [
                (r"Assets\My Courses\CompArch.png", 0, 0, "cancourse", canvas,lambda: self.grid_remove()),
                (r"Assets\My Courses\MathForCS.png", 0, 300, "csmathcourse", canvas,lambda: self.grid_remove()),
                (r"Assets\My Courses\ObjectOP.png", 920, 0, "oopcourse", canvas ,lambda: self.grid_remove()),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.buttonImgLabels, "button")
        self.controller.widgetsDict["coursescanvas"].tk.call("raise", self.controller.widgetsDict["coursescanvas"]._w)

            # if widgetname.endswith("course"):
                # buttonstoconfig.append(widget)
        # for widget in buttonstoconfig:
            # widget.bind("<Enter>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=RAISED))
            # widget.bind("<Leave>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=FLAT))
        # self.controller.widgetsDict[f"{widget}"].bind("<Enter>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=RAISED))
        # self.controller.widgetsDict[f"{widget}"].bind("<Leave>", lambda event: self.controller.widgetsDict[f"{widget}"].config(relief=FLAT))

class DiscussionsView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="discussionsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\DiscussionsView\DiscussionsViewBG.png", 0, 0, "DiscussionsBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")

class FavoritesView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)

class AppointmentsView(Canvas):
    def __init__(self, parent, controller):
        Canvas.__init__(self, parent, width=1, height=1, bg= WHITE, name="appointmentsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\AppointmentsView\BGForAppointments1920x780+0+200.png", 0, 120, "AppointmentsBG", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")