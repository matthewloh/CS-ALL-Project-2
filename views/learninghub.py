import json
import threading
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import uuid
import boto3
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.dialogs import Messagebox, MessageDialog, Querybox
from ttkbootstrap.tooltip import ToolTip
from components.animatedgif import AnimatedGif
from basewindow import gridGenerator
from static import *
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma.errors import UniqueViolationError
from prisma import Json
from win32gui import GetWindowText, GetForegroundWindow

from views.discussionsview import DiscussionsView
from PIL import Image, ImageTk, ImageSequence
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime


class LearningHub(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="learninghub", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()

    def createFrames(self):
        self.mainframe = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="mainlearninghubframe"
        )
        self.rulesFrame = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="rulesframe"
        )
        self.playingFrame = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="playingframe"
        )
        self.createContentFrame = self.controller.frameCreator(
            xpos=0, ypos=0, framewidth=1920, frameheight=920,
            root=self, classname="createcontentframe"
        )
        self.editSectionFrame = self.controller.frameCreator(
            xpos=60, ypos=280, framewidth=1800, frameheight=600,
            root=self.createContentFrame, classname="editsectionframe"
        )
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\LearningHub\LearningHubBG.png", 0, 0, "LearningHubBG", self),
            (r"Assets\LearningHub\mainframebg.png", 0,
             0, "learninghubmainbg", self.mainframe),
            (r"Assets\LearningHub\RulesFrame\RulesFrameBg.png",
             0, 0, "rulesframemainbg", self.rulesFrame),
            (r"Assets\LearningHub\ContentCreationBg\CreateContentFrameBg.png",
             0, 0, "createcontentframemainbg", self.createContentFrame),
            (r"Assets\LearningHub\ContentCreationBg\EditingContentFrame.png",
             0, 0, "editsectionframemainbg", self.editSectionFrame),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.canvas = self.controller.canvasCreator(
            xpos=0, ypos=0, width=1920, height=920,
            root=self, classname="learninghubcanvas",
            bgcolor="#A799F5", isTransparent=True, transparentcolor="#A799F5"
        )
        self.mainframe.grid_remove()

    def postLogin(self, data: dict):
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
                modulecodes.append(modulecode.lower())
            self.loadCourseButtons(modulecodes)
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
            for i in range(len(studentinfo)):
                studentname = studentinfo[i][0]
                studentemail = studentinfo[i][1]
                studentphone = studentinfo[i][2]
            # lecturer specific functions here like show student info
            # and upload course files and upload schedule
            self.loadCourseButtons(modulecodes)

    def loadCourseButtons(self, modulecodes: list = None):
        c = self.controller

        for widgetname, widget in self.canvas.children.items():
            if widgetname not in modulecodes and widgetname.startswith("int"):
                widget.grid_forget()
        try:
            self.controller.widgetsDict["createquizbutton"].grid_remove()
        except:
            pass
        btnDict = {
            "int4004cem": (r"Assets\LearningHub\ComputerArchitecture.png", 160, 220,
                           "int4004cemhub", self.canvas, lambda: self.loadCourseHubContent("int4004cem")),
            "int4068cem": (r"Assets\LearningHub\MathematicsCS.png", 160, 220,
                           "int4068cemhub", self.canvas, lambda: self.loadCourseHubContent("int4068cem")),
            "int4003cem": (r"Assets\LearningHub\ObjectOrientedProgramming.png", 160, 220,
                           "int4003cemhub", self.canvas, lambda: self.loadCourseHubContent("int4003cem")),
            "int4009cem": (r"Assets\LearningHub\CSALL2.png", 160, 220,
                           "int4009cemhub", self.canvas, lambda: self.loadCourseHubContent("int4009cem")),
        }
        BGFORBUTTON = r"Assets\LearningHub\BackgroundForAButton.png"
        btnCount = 0
        yCount = 0
        for code in modulecodes:
            yCount += 1 if btnCount == 2 else 0
            btnCount = btnCount if btnCount < 2 else 0
            btn = btnDict[code]
            c.labelCreator(
                imagepath=BGFORBUTTON,
                xpos=btn[1] + (btnCount * 1200) - 40,
                ypos=btn[2] + (yCount * 360) - 40,
                root=btn[4], classname=btn[3] + "bg",
            )
            c.buttonCreator(
                imagepath=btn[0],
                xpos=btn[1] + (btnCount * 1200),
                ypos=btn[2] + (yCount * 360),
                root=btn[4], classname=btn[3], buttonFunction=btn[5],
            )
            btnCount += 1

    def fillLists(self, coursecode: str):
        prisma = self.prisma
        self.moduleGames = {}   # <--- contentType == "GAME"
        self.moduleActivities = {}  # <--- contentType == "ACTIVITY"
        # <--- contentType == "MULTIPLE_CHOICE" or contentType == "FILL_IN_THE_BLANK"
        self.moduleQuizzes = {}

        allContent = prisma.module.find_first(
            where={
                "moduleCode": coursecode.upper()
            },
            include={
                "moduleHubContent": {
                    "include": {
                        "author": {
                            "include": {
                                "userProfile": True
                            }
                        }
                    }
                }
            }
        )
        for c in allContent.moduleHubContent:
            KL = timezone('Asia/Kuala_Lumpur')
            typeOfContent = c.contentType
            title = c.title
            description = c.description
            creationTime = KL.convert(c.createdAt).strftime('%d %B %Y %I:%M%p')
            author = c.author.userProfile.fullName
            dictObject = c.contentInfo
            questions = dictObject["questions"]
            numOfQuestions = dictObject["numOfQuestions"]
            if typeOfContent == "GAME":
                dictOfDetails = {
                    "detailsOfContent": (title, description, creationTime, author),
                    "numOfQuestions": numOfQuestions,
                    "questions": questions,
                }
                self.moduleGames[f"{title}"] = dictOfDetails
            elif typeOfContent == "ACTIVITY":
                dictOfDetails = {
                    "detailsOfContent": (title, description, creationTime, author),
                    "numOfQuestions": numOfQuestions,
                    "questions": questions,
                }
                self.moduleActivities[f"{title}"] = dictOfDetails
            elif typeOfContent == "MULTIPLE_CHOICE" or typeOfContent == "FILL_IN_THE_BLANK":
                dictOfDetails = {
                    "typeOfContent": typeOfContent,  # "MULTIPLE_CHOICE" or "FILL_IN_THE_BLANK
                    "detailsOfContent": (title, description, creationTime, author),
                    "numOfQuestions": numOfQuestions,
                    "questions": questions,
                }
                self.moduleQuizzes[f"{title}"] = dictOfDetails

    def exitModuleContentView(self):
        self.mainframe.grid_remove()
        self.canvas.grid()
        self.canvas.tk.call("raise", self.canvas._w)

    def loadMultipleChoiceQuestionCreation(self, coursecode: str):
        self.editSectionFrame.grid()
        self.editSectionFrame.tkraise()
        prisma = self.prisma
        try:
            widgets = []
            for widgetname, widget in self.mcqScrolledFrame.children.items():
                widgets.append(widget)
            [widget.destroy() for widget in widgets]
        except:
            pass
        try:
            widgets = []
            for widgetname, widget in self.allQuestionsScrolledFrame.children.items():
                widgets.append(widget)
            [widget.destroy() for widget in widgets]
        except:
            pass
        try:
            self.allQuestionsScrolledFrame.place_forget()
            self.hostframe.grid_remove()
        except:
            pass
        allModuleContent = prisma.modulehubcontent.find_many(
            where={
                "AND": [
                    {
                        "module": {
                            "is": {
                                "moduleCode": coursecode.upper()
                            }
                        },
                        "contentType": "MULTIPLE_CHOICE"
                    }
                ]
            },
            include={
                "attempts": True
            }
        )
        h = len(allModuleContent) * 200 + 20
        if h < 400:
            h = 400
        self.mcqScrolledFrame = ScrolledFrame(
            self.editSectionFrame, width=880, height=h, autohide=True, bootstyle="rounded"
        )
        self.mcqScrolledFrame.place(x=20, y=180, width=880, height=400)
        startx, starty = 20, 20
        for c in allModuleContent:
            rootFrame = self.mcqScrolledFrame,
            title = c.title
            desc = c.description if c.description else "No description"
            numOfQuestions = c.contentInfo["numOfQuestions"]
            questions = c.contentInfo["questions"]
            numOfAttempts = len(c.attempts)
            self.renderQuizWidget(
                c.id,
                self.mcqScrolledFrame, title, desc, numOfQuestions, questions, numOfAttempts,
                startx, starty
            )
            starty += 200

    def renderQuizWidget(self,
                         id: int,
                         rootFrame: ScrolledFrame,
                         title: str, desc: str, numOfQuestions: int, questions: dict,
                         numOfAttempts: int,
                         startx: int = 20, starty: int = 20):
        # Quiz Title Entry and Insert
        self.controller.labelCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\Quiz Widget.png",
            xpos=startx, ypos=starty, root=rootFrame, classname=f"{id}quizwidgetbg", isPlaced=True
        )
        singleQuizTitle = self.controller.ttkEntryCreator(
            xpos=startx+20, ypos=starty+40, width=380, height=40,
            root=rootFrame, classname=f"{id}quiztitleentry", isPlaced=True
        )
        singleQuizTitle.insert(0, title)
        # Quiz Description Entry and Insert
        quizDesc = self.controller.ttkEntryCreator(
            xpos=startx+20, ypos=starty+120, width=380, height=40,
            root=rootFrame, classname=f"{id}quizdescentry", isPlaced=True
        )
        quizDesc.insert(0, desc)
        # Num Of Questions Text Element
        self.controller.textElement(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\NumTextBg.png",
            xpos=startx+640, ypos=starty+40, root=rootFrame, classname=f"{id}numofquestionstext",
            font=INTERBOLD, size=32, text=f"{numOfQuestions}", isPlaced=True, fg=WHITE
        )
        # Add A Question Button
        self.controller.buttonCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IncreaseQuestionNum.png",
            xpos=startx+700, ypos=starty+40, root=rootFrame, classname=f"{id}addquestionbutton",
            buttonFunction=lambda: self.addQuestionToQuiz(id, numOfQuestions, questions), isPlaced=True
        )
        # Num Of Attempts Text Element
        self.controller.textElement(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\NumTextBg.png",
            xpos=startx+640, ypos=starty+120, root=rootFrame, classname=f"{id}numofattemptstext",
            font=INTERBOLD, size=32, text=f"{numOfAttempts}", isPlaced=True, fg=WHITE
        )

        # ID-based functions
        # Edit Button
        self.controller.buttonCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\Edit60x60.png",
            xpos=startx+760, ypos=starty+20, root=rootFrame, classname=f"{id}editbutton",
            buttonFunction=lambda: self.loadEditQuizContent(id, numOfQuestions, questions), isPlaced=True
        )
        # Delete Button
        self.controller.buttonCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\Delete60x60.png",
            xpos=startx+760, ypos=starty+100, root=rootFrame, classname=f"{id}deletebutton",
            buttonFunction=lambda: self.deleteQuizContent(id), isPlaced=True
        )

    def addQuiz(self, modulecode: str):
        btnLocation = self.controller.widgetsDict["addquizbutton"]
        if self.quizTitle.get() in [content.title for content in self.prisma.modulehubcontent.find_many()]:
            Messagebox.show_error(
                title="Error", message="Quiz title already exists", parent=self.quizTitle)
            return
        if self.quizTitle.get() == "":
            Messagebox.show_error(
                title="Error", message="Quiz title cannot be empty", parent=self.quizTitle)
            return
        if self.quizDesc.get() == "":
            Messagebox.show_error(
                title="Error", message="Quiz description cannot be empty", parent=self.quizDesc)
            return
        numOfQuestions = Querybox.get_integer(
            title="Number of Questions",
            prompt="Enter the number of questions for this quiz (1-20)",
            parent=btnLocation,
            minvalue=1,
            maxvalue=20
        )
        # generic template for questions
        """ 
            # list comprehension to get 
            {
                "question": "Please enter your question here",
                "options": ["Enter Option 1", "Enter Option 2", "Enter Option 3", "Enter Option 4"],
                "correctAnswer": 0 # by default, correct answer is the first option
            }
            questions = [ { "question": f"Please enter your question here {i}", "options": [f"Enter Option {i}" for i in range(1, 5)] } for i in range(1, numOfQuestions+1) ]
            {
                "numOfQuestions": numOfQuestions,
                "questions": questions
            }
        """
        title = self.quizTitle.get()
        questions = [
            {
                "question": f"Please enter question {i} for quiz {title}.",
                "options": [f"Enter Option {i}" for i in range(1, 5)],
                "correctAnswer": 0
            } for i in range(1, numOfQuestions+1)]
        finalDict = {
            "numOfQuestions": numOfQuestions,
            "questions": questions
        }
        c = self.prisma.modulehubcontent.create(
            data={
                "title": self.quizTitle.get(),
                "description": self.quizDesc.get(),
                "contentType": "MULTIPLE_CHOICE",
                "contentInfo": Json(finalDict),
                "author": {
                    "connect": {
                        "id": self.prisma.lecturer.find_first(
                            where={
                                "userId": self.userId
                            }
                        ).id
                    }
                },
                "module": {
                    "connect": {
                        "moduleCode": modulecode.upper()
                    }
                }
            }
        )
        overallIndex = 0
        id = c.id
        self.loadMultipleChoiceQuestionCreation(modulecode.lower())
        numOfQuestions = c.contentInfo["numOfQuestions"]
        questions = c.contentInfo["questions"]
        options = c.contentInfo["questions"][overallIndex]["options"]
        correctAnswer = c.contentInfo["questions"][overallIndex]["correctAnswer"]
        self.loadEditQuizContent(id, numOfQuestions, questions)
        self.loadViewOptionsContent(
            id, overallIndex, options, correctAnswer)
        self.loadMenuButtons(self.currentCourseCode)

    def addQuestionToQuiz(self, id: int, numOfQuestions: int, questions: dict):
        overallIndex = numOfQuestions
        questions.append(
            {
                "question": f"Please enter question {overallIndex+1} for quiz {self.quizTitle.get()}.",
                "options": [f"Enter Option {i}" for i in range(1, 5)],
                "correctAnswer": 0
            }
        )
        newDict = {
            "numOfQuestions": numOfQuestions+1,
            "questions": questions
        }
        self.prisma.modulehubcontent.update(
            where={
                "id": id
            },
            data={
                "contentInfo": Json(newDict)
            }
        )
        self.loadMultipleChoiceQuestionCreation(self.currentCourseCode)
        self.loadMenuButtons(self.currentCourseCode)
        self.loadEditQuizContent(id, numOfQuestions+1, questions)

    def loadEditQuizContent(self, id: int, numOfQuestions: int, questions: dict):
        try:
            widgets = []
            for widgetname, widget in self.allQuestionsScrolledFrame.children.items():
                widgets.append(widget)
            [widget.destroy() for widget in widgets]
        except Exception as e:
            pass
        h = numOfQuestions * 220 + 20
        if h < 560:
            h = 560
        self.allQuestionsScrolledFrame = ScrolledFrame(
            self.editSectionFrame, width=840, height=h, autohide=True, bootstyle="rounded"
        )
        self.allQuestionsScrolledFrame.place(
            x=940, y=20, width=840, height=560)
        startx, starty = 20, 20
        count = 0
        self.currentWorkingDict = questions
        for q in self.currentWorkingDict:
            overallIndex = count
            # options is a list
            options = q["options"]
            # correctAnswer is an index of the options list
            correctAnswer = q["correctAnswer"]
            # question is a string
            question = q["question"]
            # finalAnswer is accessed using q["options"][q["correctAnswer"]]
            finalAnswer = options[correctAnswer]
            self.renderIndividualQuestion(
                id, overallIndex, options, correctAnswer, question, finalAnswer, startx, starty
            )
            count += 1
            starty += 220

    def renderIndividualQuestion(self,
                                 id: int,
                                 overallIndex: int,
                                 options: list, correctAnswer: int, question: str, finalAnswer: str,
                                 startx: int = 20, starty: int = 20):
        # Individual Question Widget
        self.controller.labelCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\OneQuestionWidget.png",
            xpos=startx, ypos=starty, root=self.allQuestionsScrolledFrame, classname=f"{overallIndex}questionwidgetbg",
            isPlaced=True
        )
        # Question Number Text Element
        self.controller.textElement(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\QuestionNumberTxtBg.png",
            xpos=startx, ypos=starty, root=self.allQuestionsScrolledFrame, classname=f"{overallIndex}questionnumbertext",
            font=INTERBOLD, size=32, text=f"{overallIndex+1}.", isPlaced=True, fg=WHITE
        )
        # Question Entry
        qEntry = self.controller.ttkEntryCreator(
            xpos=startx+60, ypos=starty+20, width=640, height=80,
            root=self.allQuestionsScrolledFrame, classname=f"{overallIndex}questionentry",
            isPlaced=True
        )
        qEntry.insert(0, question)
        # Correct Answer Entry
        cAnswerEntry = self.controller.ttkEntryCreator(
            xpos=startx+60, ypos=starty+120, width=640, height=60,
            root=self.allQuestionsScrolledFrame, classname=f"{overallIndex}correctanswerentry",
            isPlaced=True
        )
        cAnswerEntry.insert(0, finalAnswer)
        # Overall Index-based functions
        # View Options Button
        self.controller.buttonCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\ViewOptions.png",
            xpos=startx+720, ypos=starty+20, root=self.allQuestionsScrolledFrame, classname=f"{overallIndex}viewoptionsbutton",
            buttonFunction=lambda: self.loadViewOptionsContent(id, overallIndex, options, correctAnswer), isPlaced=True
        )
        # Delete Question Button
        self.controller.buttonCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\DeleteQuestion.png",
            xpos=startx+720, ypos=starty+120, root=self.allQuestionsScrolledFrame, classname=f"{overallIndex}deletequestionbutton",
            buttonFunction=lambda: self.deleteQuestion(id, overallIndex), isPlaced=True
        )

    # TODO: Add backend query to update the modulehubcontent
    # Where the id is of the modulehubcontent is the same as the id of the quiz
    # Then update the contentInfo under this field
    # Then update the quiz content

    def loadViewOptionsContent(self, id: int, overallIndex: int, options: list, correctAnswer: int):
        # questions = self.currentWorkingDict
        # ask if the user wants to edit the question or view the options
        parentWidget = self.controller.widgetsDict[f"{overallIndex}viewoptionsbutton"]
        editOrViewOptions = ["Edit Question:success",
                             "Edit Answers:info", "Cancel:danger"]
        askOption = MessageDialog(
            title="Edit or View Options",
            message="Do you want to edit the question or edit the answers?",
            buttons=editOrViewOptions,
            parent=parentWidget
        )
        self.hostframe = self.controller.frameCreator(
            xpos=940, ypos=20, framewidth=840, frameheight=560,
            root=self.editSectionFrame, classname="overallquestionframe",
        )
        _labels = [
            (r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\IndividualBg.png",
             0, 0, "overallquestionbg", self.hostframe)
        ]
        for _label in _labels:
            self.controller.labelCreator(
                imagepath=_label[0], xpos=_label[1], ypos=_label[2], root=_label[4], classname=_label[3],
            )
        self.mainTextHost = ScrolledText(
            master=self.hostframe, width=800, height=300, autohide=True, bootstyle="rounded"
        )
        self.mainTextHost.place(x=20, y=20, width=800, height=300)
        self.mainText = self.mainTextHost.text
        self.mainText.configure(
            font=("Inter Bold", 24), fg=BLACK, wrap=WORD, spacing1=10, spacing2=10, spacing3=10
        )
        q = self.currentWorkingDict[overallIndex]["question"]
        self.mainText.insert(
            END, f"{overallIndex+1}. {q}")

        _buttons = [
            (r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\exitindividual.png",
             800, 0, "exitindividual", self.hostframe, lambda: [self.hostframe.grid_remove()]),
            (r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\EditQuestion.png",
             740, 240, "editquestion", self.hostframe, lambda: self.editQuestion(id, overallIndex)),
        ]

        for _button in _buttons:
            self.controller.buttonCreator(
                imagepath=_button[0], xpos=_button[1], ypos=_button[2], root=_button[4], classname=_button[3],
                buttonFunction=_button[5]
            )
        # 4 entries
        # index 0 -> 1
        # index 2 -> 3
        startx, starty = 40, 360
        for i in range(4):
            x = i % 2  # 0 , 1 , 0 , 1
            yIndex = i // 2  # 0 , 0 , 1 , 1
            finalX = startx + (x*420)
            finalY = starty + (yIndex*100)
            entry = self.controller.ttkEntryCreator(
                xpos=finalX, ypos=finalY,
                width=300, height=40,
                root=self.hostframe, classname=f"option{i}entry",
            )
            entry.insert(0, options[i])
            if i == correctAnswer:
                self.correctAnsLabel = self.controller.labelCreator(
                    imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\correctanswerlabel.png",
                    xpos=finalX+320, ypos=finalY-20, root=self.hostframe, classname=f"correctanswerentrylabel",
                )
            # The edit button to ask to change this option to the correct answer
            self.controller.buttonCreator(
                imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\editanoption.png",
                xpos=finalX+320, ypos=finalY+20, root=self.hostframe, classname=f"editoption{i}button",
                buttonFunction=lambda i=(id, overallIndex, i, options[i]): self.editOption(
                    i[0], i[1], i[2], i[3])
            )
        # askOption.show()
        if askOption.result == "Edit Question":
            self.hostframe.place(x=0, y=0, width=840, height=560)
            askNewQuestion = Querybox.get_string(
                title="Edit Question",
                prompt="Enter the new question",
                initialvalue=self.currentWorkingDict[overallIndex]["question"],
                parent=parentWidget
            )
            askNewQuestion.show()
            if askNewQuestion is not None and askNewQuestion != "":
                self.currentWorkingDict[overallIndex]["question"] = askNewQuestion
                self.controller.widgetsDict[f"{overallIndex}questionentry"].delete(
                    0, END)
                self.controller.widgetsDict[f"{overallIndex}questionentry"].insert(
                    0, askNewQuestion)

    def editQuestion(self, id: int, overallIndex: int):
        parentWidget = self.mainTextHost
        askNewQuestion = Querybox.get_string(
            title="Edit Question",
            prompt="Enter the new question",
            initialvalue=self.currentWorkingDict[overallIndex]["question"],
            parent=parentWidget
        )
        if askNewQuestion is not None and askNewQuestion != "":
            self.currentWorkingDict[overallIndex]["question"] = askNewQuestion
            self.mainText.delete("1.0", END)
            self.mainText.insert(END, f"{overallIndex+1}. {askNewQuestion}")
            newDict = {
                "numOfQuestions": len(self.currentWorkingDict),
                "questions": self.currentWorkingDict
            }
            c = self.prisma.modulehubcontent.update(
                where={
                    "id": id
                },
                data={
                    "contentInfo": Json(newDict)
                }
            )
            numOfQuestions = c.contentInfo["numOfQuestions"]
            questions = c.contentInfo["questions"]
            options = c.contentInfo["questions"][overallIndex]["options"]
            correctAnswer = c.contentInfo["questions"][overallIndex]["correctAnswer"]
            self.loadEditQuizContent(id, numOfQuestions, questions)
            self.loadViewOptionsContent(
                id, overallIndex, options, correctAnswer)
            self.loadMenuButtons(self.currentCourseCode)

    def deleteQuestion(self, id: int, overallIndex: int):
        parentWidget = self.controller.widgetsDict[f"{overallIndex}deletequestionbutton"]
        askConfirm = Messagebox.yesno(
            title="Delete Quiz Question?",
            message="Are you sure you want to delete this question?",
            parent=parentWidget
        )
        if askConfirm == "Yes":
            if len(self.currentWorkingDict) == 1:
                deleteQuestion = messagebox.askyesno(
                    title="Delete Quiz Question?",
                    message="This is the last question in the quiz. Are you sure you want to delete this quiz content?",
                )
                if deleteQuestion:
                    self.prisma.modulehubcontent.delete(where={
                        "id": id
                    })
                    self.loadMultipleChoiceQuestionCreation(
                        self.currentCourseCode)
                    self.loadMenuButtons(self.currentCourseCode)
                    self.allQuestionsScrolledFrame.place_forget()
                    return
                else:
                    return
            self.currentWorkingDict.pop(overallIndex)
            newDict = {
                "numOfQuestions": len(self.currentWorkingDict),
                "questions": self.currentWorkingDict
            }
            c = self.prisma.modulehubcontent.update(
                where={
                    "id": id
                },
                data={
                    "contentInfo": Json(newDict)
                }
            )
            numOfQuestions = c.contentInfo["numOfQuestions"]
            questions = c.contentInfo["questions"]
            self.loadMultipleChoiceQuestionCreation(self.currentCourseCode)
            self.loadEditQuizContent(id, numOfQuestions, questions)
            self.loadMenuButtons(self.currentCourseCode)

    def editOption(self, id: int,  overallIndex: int, optionIndex: int, option: str):
        # ask if the user wants to edit the option's content or change this option to the correct answer
        parentWidget = self.controller.widgetsDict[f"editoption{optionIndex}button"]
        editOrViewOptions = ["Edit Option:success",
                             "Change to Correct Answer:info", "Cancel:danger"]
        askOption = MessageDialog(
            title="Edit or View Options",
            message="Do you want to edit the option's content or change this option to the correct answer?",
            buttons=editOrViewOptions,
            parent=parentWidget
        )
        # print("Current question: ", self.currentWorkingDict[overallIndex])
        # print("Current option index: ", optionIndex)
        # print("Current option: ",
        #       self.currentWorkingDict[overallIndex]["options"][optionIndex])
        # print("Current correct answer index: ",
        #       self.currentWorkingDict[overallIndex]["correctAnswer"])
        # print("Current correct answer: ", self.currentWorkingDict[overallIndex]
        #       ["options"][self.currentWorkingDict[overallIndex]["correctAnswer"]])
        askOption.show()
        if askOption.result == "Edit Option":
            askNewOption = Querybox.get_string(
                title="Edit Option",
                prompt="Enter the new option",
                initialvalue=option,
                parent=parentWidget
            )
            if askNewOption is not None and askNewOption != "":
                self.currentWorkingDict[overallIndex]["options"][optionIndex] = askNewOption
                self.controller.widgetsDict[f"option{optionIndex}entry"].delete(
                    0, END)
                self.controller.widgetsDict[f"option{optionIndex}entry"].insert(
                    0, askNewOption)
                newDict = {
                    "numOfQuestions": len(self.currentWorkingDict),
                    "questions": self.currentWorkingDict
                }
                c = self.prisma.modulehubcontent.update(
                    where={
                        "id": id
                    },
                    data={
                        "contentInfo": Json(newDict)
                    }
                )
                numOfQuestions = c.contentInfo["numOfQuestions"]
                questions = c.contentInfo["questions"]
                options = c.contentInfo["questions"][overallIndex]["options"]
                correctAnswer = c.contentInfo["questions"][overallIndex]["correctAnswer"]
                self.loadEditQuizContent(id, numOfQuestions, questions)
                self.loadViewOptionsContent(
                    id, overallIndex, options, correctAnswer)
                self.loadMenuButtons(self.currentCourseCode)
        elif askOption.result == "Change to Correct Answer":
            if self.currentWorkingDict[overallIndex]["correctAnswer"] == optionIndex:
                Messagebox.show_error(
                    title="Error", message="This option is already the correct answer",
                    parent=parentWidget
                )
                return
            self.currentWorkingDict[overallIndex]["correctAnswer"] = optionIndex
            newDict = {
                "numOfQuestions": len(self.currentWorkingDict),
                "questions": self.currentWorkingDict
            }
            c = self.prisma.modulehubcontent.update(
                where={
                    "id": id
                },
                data={
                    "contentInfo": Json(newDict)
                }
            )
            numOfQuestions = c.contentInfo["numOfQuestions"]
            questions = c.contentInfo["questions"]
            options = c.contentInfo["questions"][overallIndex]["options"]
            correctAnswer = c.contentInfo["questions"][overallIndex]["correctAnswer"]
            self.loadEditQuizContent(id, numOfQuestions, questions)
            self.loadViewOptionsContent(
                id, overallIndex, options, correctAnswer)
            self.correctAnsLabel = self.controller.labelCreator(
                imagepath=r"Assets\LearningHub\ContentCreationBg\QuizWidget\IndividualQuestionWidget\correctanswerlabel.png",
                xpos=360+(optionIndex % 2)*420, ypos=340+(optionIndex//2)*100,
                root=self.hostframe, classname=f"correctanswerentrylabel",
            )
            self.loadMenuButtons(self.currentCourseCode)

    def deleteQuizContent(self, id: int):
        parentWidget = self.controller.widgetsDict[f"{id}deletebutton"]
        askConfirm = Messagebox.yesno(
            title="Delete Quiz Content?",
            message="Are you sure you want to delete this quiz content?",
            parent=parentWidget
        )
        if askConfirm == "Yes":
            self.prisma.modulehubcontent.delete(where={
                "id": id
            })
            self.loadMultipleChoiceQuestionCreation(self.currentCourseCode)
            self.loadMenuButtons(self.currentCourseCode)
        else:
            return

    def loadCreateQuizContent(self, coursecode: str):
        self.createContentFrame.grid()
        self.createContentFrame.tkraise()
        btns = [
            (r"Assets\LearningHub\ContentCreationBg\Multiple Choice Question Creation.png",
             980, 120, "multiplechoicequestioncreation", self.createContentFrame,
             lambda: self.loadMultipleChoiceQuestionCreation(coursecode)),
            (r"Assets\My Courses\exitbutton.png", 1800, 20,
             "exitcreationofcontent", self.createContentFrame,
             lambda: [self.createContentFrame.grid_remove(), self.editSectionFrame.grid_remove()])
        ]
        self.controller.settingsUnpacker(btns, "button")
        self.quizTitle = self.controller.ttkEntryCreator(
            xpos=320, ypos=20, width=480, height=60,
            root=self.editSectionFrame, classname="quiztitleentry"
        )
        self.quizDesc = self.controller.ttkEntryCreator(
            xpos=320, ypos=100, width=480, height=60,
            root=self.editSectionFrame, classname="quizdescentry"
        )
        self.addQuizBtn = self.controller.buttonCreator(
            imagepath=r"Assets\LearningHub\ContentCreationBg\AddQuiz.png",
            xpos=840, ypos=60, root=self.editSectionFrame, classname="addquizbutton",
            buttonFunction=lambda: self.addQuiz(coursecode)
        )

    def loadCourseHubContent(self, coursecode: str):
        self.canvas.grid_remove()
        self.mainframe.grid()
        self.mainframe.tkraise()
        self.currentCourseCode = coursecode
        _ = [
            (r"Assets\LearningHub\ContentCreationBg\CreateQuizBtn.png", 1440, 60,
             "createquizbutton", self.mainframe, lambda: self.loadCreateQuizContent(coursecode)),
        ]
        if self.role == "lecturer":
            self.controller.settingsUnpacker(_, "button")
            self.editSectionFrame.grid_remove()

        staticButtons = [
            (r"Assets\LearningHub\HomePage.png", 160, 580,
             "learninghubhome", self.mainframe,
             lambda: self.exitModuleContentView()),
            (r"Assets\LearningHub\INT4004CEM\FillInBlanksGame.png", 160, 220,
             "learninghubgamesbutton", self.mainframe,
             lambda:self.loadGameHubContent(self.learninghubgamesvar.get())),
            (r"Assets\LearningHub\INT4004CEM\ActivityHardwareOfTheDay.png", 1360, 220,
             "learninghubactivitiesbutton", self.mainframe,
             lambda:self.loadActivityHubContent(self.learninghubactivitiesvar.get())),
            (r"Assets\LearningHub\INT4004CEM\MultipleChoiceQuizNumSystem.png", 1360, 580,
             "learninghubquizzesbutton", self.mainframe,
             lambda:self.loadQuizHubContent(self.learninghubquizzesvar.get())),
        ]
        self.controller.settingsUnpacker(staticButtons, "button")

        self.loadMenuButtons(coursecode)

    def loadMenuButtons(self, coursecode):
        self.fillLists(coursecode)
        pos = {
            "learninghubgamesmb": {"x": 180, "y": 380, "width": 360, "height": 60},
            "learninghubactivitiesmb": {"x": 1380, "y": 380, "width": 360, "height": 60},
            "learninghubquizzesmb": {"x": 1380, "y": 740, "width": 360, "height": 60},
        }
        self.listOfGames = list(self.moduleGames.keys())
        self.listOfActivities = list(self.moduleActivities.keys())
        self.listOfQuizzes = list(self.moduleQuizzes.keys())

        lists = {
            "learninghubgamesmb": self.listOfGames,
            "learninghubactivitiesmb": self.listOfActivities,
            "learninghubquizzesmb": self.listOfQuizzes,
        }

        # Vars
        self.learninghubgamesvar = StringVar()
        self.learninghubactivitiesvar = StringVar()
        self.learninghubquizzesvar = StringVar()

        vars = {
            "learninghubgamesmb": self.learninghubgamesvar,
            "learninghubactivitiesmb": self.learninghubactivitiesvar,
            "learninghubquizzesmb": self.learninghubquizzesvar,
        }
        selectNames = {
            "learninghubgamesmb": "a game :",
            "learninghubactivitiesmb": "an activity :",
            "learninghubquizzesmb": "a quiz :",
        }
        for name, values in lists.items():
            self.controller.menubuttonCreator(
                root=self.mainframe, xpos=pos[name]["x"], ypos=pos[name]["y"],
                width=pos[name]["width"], height=pos[name]["height"],
                classname=name, text=f"Select {selectNames[name]}",
                listofvalues=values, variable=vars[name],
                command=lambda name=name: [
                    print(vars[name].get()),
                ]
            )

    def loadGameHubContent(self, titleKey):
        if titleKey == "":
            return
        self.rulesFrame.grid()
        self.rulesFrame.tkraise()
        IMGPATH = r"Assets\LearningHub\PlayingFrame\ActivityPlayingBG.png"
        # self.playingFrameBg = self.controller.labelCreator(
        #     imagepath=IMGPATH, xpos=0, ypos=0,
        #     classname="playingframebg", root=self.playingFrame,
        # )
        # self.playingFrame.grid()
        # self.playingFrame.tkraise()
        title = self.moduleGames[titleKey]["detailsOfContent"][0]
        description = self.moduleGames[titleKey]["detailsOfContent"][1]
        creationTime = self.moduleGames[titleKey]["detailsOfContent"][2]
        author = self.moduleGames[titleKey]["detailsOfContent"][3]
        numOfQuestions = self.moduleGames[titleKey]["numOfQuestions"]
        questions = self.moduleGames[titleKey]["questions"]
        for q in questions:
            print(q["question"])
            print(q["options"])
            print(q["correctAnswer"])
            print(
                f"The correct answer is {q['options'][q['correctAnswer']]}")

    def loadActivityHubContent(self, titleKey):
        if titleKey == "":
            return
        # IMGPATH = r"Assets\LearningHub\PlayingFrame\ActivityPlayingBG.png"
        # self.playingFrameBg = self.controller.labelCreator(
        #     imagepath=IMGPATH, xpos=0, ypos=0,
        #     classname="playingframebg", root=self.playingFrame,
        # )
        # self.playingFrame.grid()
        # self.playingFrame.tkraise()
        print(titleKey)
        print(self.moduleActivities[titleKey])

    def loadQuizHubContent(self, titleKey):
        if titleKey == "":
            return
        typeOfQuiz = self.moduleQuizzes[titleKey]["typeOfContent"]
        IMGPATH = r"Assets\LearningHub\RulesFrame\FillInBlanksRules.png" if typeOfQuiz == "FILL_IN_THE_BLANK" else r"Assets\LearningHub\RulesFrame\QuizRules.png"
        self.rulesFrameBg = self.controller.labelCreator(
            imagepath=IMGPATH, xpos=220, ypos=160,
            classname="rulesframebg", root=self.rulesFrame,
        )
        buttonsForRules = [
            (r"Assets\LearningHub\RulesFrame\returnbutton.png", 360, 680,
             "returnbtnrulesframe", self.rulesFrame,
             lambda: self.rulesFrame.grid_remove()),
            (r"Assets\LearningHub\RulesFrame\startbutton.png", 1220, 680,
             "startbtnrulesframe", self.rulesFrame,
             lambda: self.loadQuizPlayingFrameContent(titleKey)),
        ]
        self.controller.settingsUnpacker(buttonsForRules, "button")
        self.rulesFrame.grid()
        self.rulesFrame.tkraise()

    def loadGamePlayingFrameContent(self, titleKey):
        pass

    def loadActivityPlayingFrameContent(self, titleKey):
        pass

    def loadQuizPlayingFrameContent(self, titleKey):
        typeOfQuiz = self.moduleQuizzes[titleKey]["typeOfContent"]
        if typeOfQuiz == "FILL_IN_THE_BLANK":
            self.loadFillInTheBlankQuizPlayingFrameContent(titleKey)
        else:
            self.loadMultipleChoiceQuizPlayingFrameContent(titleKey)

    def loadFillInTheBlankQuizPlayingFrameContent(self, titleKey):
        IMGPATH = r"Assets\LearningHub\PlayingFrame\FillInTheBlanksPlayingBG.png"
        self.playingFrameBg = self.controller.labelCreator(
            imagepath=IMGPATH, xpos=0, ypos=0,
            classname="playingframebg", root=self.playingFrame,
        )
        self.playingFrame.grid()
        self.playingFrame.tkraise()
        playingFrameBtns = [
            (r"Assets\LearningHub\PlayingFrame\playingframereturnbutton.png", 240, 60,
             "returnbtnplayingframe", self.playingFrame,
             lambda: self.playingFrame.grid_remove()),
            (r"Assets\LearningHub\PlayingFrame\playingframesubmitbutton.png", 1340, 60,
             "submitbtnplayingframe", self.playingFrame,
             lambda: self.loadFITBResultsFrameContent(titleKey)),
        ]
        self.controller.settingsUnpacker(playingFrameBtns, "button")
        title = self.moduleQuizzes[titleKey]["detailsOfContent"][0]
        description = self.moduleQuizzes[titleKey]["detailsOfContent"][1]
        descText = self.controller.textElement(
            imagepath=r"Assets\LearningHub\PlayingFrame\FITBDescription.png", xpos=300, ypos=180,
            root=self.playingFrame, classname="descText", text=description,
            font=INTERBOLD, size=30, xoffset=-3
        )
        creationTime = self.moduleQuizzes[titleKey]["detailsOfContent"][2]
        author = self.moduleQuizzes[titleKey]["detailsOfContent"][3]
        numOfQuestions = self.moduleQuizzes[titleKey]["numOfQuestions"]
        questions = self.moduleQuizzes[titleKey]["questions"]
        # for q in questions:
        #     print(q["question"])
        #     print(q["options"])
        #     print(q["correctAnswer"])
        #     print(
        #         f"The correct answer is {q['options'][q['correctAnswer']]}")

    def loadMultipleChoiceQuizPlayingFrameContent(self, titleKey):
        self.titleKey = titleKey
        IMGPATH = r"Assets\LearningHub\PlayingFrame\QuizPlayingBg.png"
        self.playingFrameBg = self.controller.labelCreator(
            imagepath=IMGPATH, xpos=0, ypos=0,
            classname="playingframebg", root=self.playingFrame,
        )
        self.playingFrame.grid()
        self.playingFrame.tkraise()
        playingFrameBtns = [
            (r"Assets\LearningHub\PlayingFrame\playingframereturnbutton.png", 240, 60,
             "returnbtnplayingframe", self.playingFrame,
             lambda: self.playingFrame.grid_remove()),
            (r"Assets\LearningHub\PlayingFrame\playingframesubmitbutton.png", 1340, 60,
             "submitbtnplayingframe", self.playingFrame,
             lambda: self.loadQuizResultsFrameContent()),
        ]
        self.controller.settingsUnpacker(playingFrameBtns, "button")
        title = self.moduleQuizzes[titleKey]["detailsOfContent"][0]
        description = self.moduleQuizzes[titleKey]["detailsOfContent"][1]
        descText = self.controller.textElement(
            imagepath=r"Assets\LearningHub\PlayingFrame\FITBDescription.png", xpos=300, ypos=180,
            root=self.playingFrame, classname="descText", text=description,
            font=INTERBOLD, size=30, xoffset=-3
        )
        creationTime = self.moduleQuizzes[titleKey]["detailsOfContent"][2]
        author = self.moduleQuizzes[titleKey]["detailsOfContent"][3]
        numOfQuestions = self.moduleQuizzes[titleKey]["numOfQuestions"]
        self.questionTextWidget = ScrolledText(
            master=self.playingFrame, width=1, height=1, bootstyle="info-rounded", autohide=True
        )
        self.questionTextWidget.place(x=260, y=260, width=1400, height=320)
        self.questionSpace = self.questionTextWidget.text
        self.questionSpace.config(
            font=("Inter Bold", 30), fg=BLACK, wrap=WORD, spacing1=10, spacing2=10, spacing3=10
        )
        self.questions = self.moduleQuizzes[titleKey]["questions"]
        self.currentQuestion = IntVar()
        self.correctScore = IntVar()
        self.attemptScore = IntVar()
        self.maxScore = IntVar()
        self.maxScore.set(int(numOfQuestions))
        self.ans1Var = StringVar()
        self.ans2Var = StringVar()
        self.ans3Var = StringVar()
        self.ans4Var = StringVar()
        self.vars = {
            "ans1": self.ans1Var,
            "ans2": self.ans2Var,
            "ans3": self.ans3Var,
            "ans4": self.ans4Var,
        }
        self.MCQAssets = {
            # Ans options are text elements with buttonFunction
            "ans1": (r"Assets\LearningHub\PlayingFrame\MCQAns1BG.png", 260, 600,
                     "ans1bg", self.playingFrame),
            "ans2": (r"Assets\LearningHub\PlayingFrame\MCQAns2BG.png", 980, 600,
                     "ans2bg", self.playingFrame),
            "ans3": (r"Assets\LearningHub\PlayingFrame\MCQAns3BG.png", 260, 720,
                     "ans3bg", self.playingFrame),
            "ans4": (r"Assets\LearningHub\PlayingFrame\MCQAns4BG.png", 980, 720,
                     "ans4bg", self.playingFrame),
            "questiontracker": (r"Assets\LearningHub\PlayingFrame\MCQQuestionTracker.png", 1720, 160,
                                "mcqquestiontracker", self.playingFrame),
            "currentscoretracker": (r"Assets\LearningHub\PlayingFrame\MCQScoreTrackerAndTotalText.png", 1740, 380,
                                    "mcqscoretracker", self.playingFrame),
            "totalscoreamount": (r"Assets\LearningHub\PlayingFrame\MCQScoreTrackerAndTotalText.png", 1840, 480,
                                 "maxnumofquestions", self.playingFrame),
        }
        # initialize all the options
        self.questionSpace.insert(
            END, f"{self.currentQuestion.get()+1}. {self.questions[0]['question']}"
        )
        # initialize the question tracker, only has the current question num
        self.controller.textElement(
            imagepath=self.MCQAssets["questiontracker"][0], xpos=self.MCQAssets[
                "questiontracker"][1], ypos=self.MCQAssets["questiontracker"][2],
            root=self.playingFrame, classname=self.MCQAssets["questiontracker"][
                3], text=f"{self.currentQuestion.get()+1} / {self.maxScore.get()}",
            font=INTERBOLD, size=48,
        )
        # initialize the score tracker
        self.controller.textElement(
            imagepath=self.MCQAssets["currentscoretracker"][0], xpos=self.MCQAssets[
                "currentscoretracker"][1], ypos=self.MCQAssets["currentscoretracker"][2],
            root=self.playingFrame, classname=self.MCQAssets[
                "currentscoretracker"][3], text=f"{self.correctScore.get()}",
            font=INTERBOLD, size=30, xoffset=1/2
        )
        # initialize the total score, just a static text
        self.controller.textElement(
            imagepath=self.MCQAssets["totalscoreamount"][0], xpos=self.MCQAssets[
                "totalscoreamount"][1], ypos=self.MCQAssets["totalscoreamount"][2],
            root=self.playingFrame, classname=self.MCQAssets[
                "totalscoreamount"][3], text=f"{self.maxScore.get()}",
            font=INTERBOLD, size=30, xoffset=1/2
        )
        # initialize the answer options
        for i in range(1, 5):
            self.controller.textElement(
                imagepath=self.MCQAssets[f"ans{i}"][0], xpos=self.MCQAssets[
                    f"ans{i}"][1], ypos=self.MCQAssets[f"ans{i}"][2],
                root=self.playingFrame, classname=self.MCQAssets[
                    f"ans{i}"][3], text=self.questions[0]["options"][i-1],
                font=INTERBOLD, size=30,
                buttonFunction=lambda num=i: self.MCQAnswerButtonFunction(
                    num)
            )

    def MCQAnswerButtonFunction(self, num):
        self.currentQuestion.set(self.currentQuestion.get()+1)
        self.attemptScore.set(self.attemptScore.get()+1)
        if num == self.questions[self.currentQuestion.get()-1]["correctAnswer"]+1:
            # increment correctScores if the answer is correct
            self.correctScore.set(self.correctScore.get()+1)
        if self.currentQuestion.get() == len(self.questions):
            self.loadQuizResultsFrameContent()
        else:
            self.questionSpace.delete("1.0", END)
            self.questionSpace.insert(
                END, f"{self.currentQuestion.get()+1}. {self.questions[self.currentQuestion.get()]['question']}"
            )
            for i in range(1, 5):
                self.controller.textElement(
                    imagepath=self.MCQAssets[f"ans{i}"][0], xpos=self.MCQAssets[
                        f"ans{i}"][1], ypos=self.MCQAssets[f"ans{i}"][2],
                    root=self.playingFrame, classname=self.MCQAssets[
                        f"ans{i}"][3], text=self.questions[self.currentQuestion.get()]["options"][i-1],
                    font=INTERBOLD, size=30,
                    buttonFunction=lambda num=i: self.MCQAnswerButtonFunction(
                        num)
                )
            self.controller.textElement(
                imagepath=self.MCQAssets["questiontracker"][0], xpos=self.MCQAssets[
                    "questiontracker"][1], ypos=self.MCQAssets["questiontracker"][2],
                root=self.playingFrame, classname=self.MCQAssets["questiontracker"][
                    3], text=f"{self.currentQuestion.get()+1} / {self.maxScore.get()}",
                font=INTERBOLD, size=48, xoffset=1/2
            )
            self.controller.textElement(
                imagepath=self.MCQAssets["currentscoretracker"][0], xpos=self.MCQAssets[
                    "currentscoretracker"][1], ypos=self.MCQAssets["currentscoretracker"][2],
                root=self.playingFrame, classname=self.MCQAssets[
                    "currentscoretracker"][3], text=f"{self.correctScore.get()}",
                font=INTERBOLD, size=30, xoffset=1/2
            )

    def loadQuizResultsFrameContent(self):
        correctScore = self.correctScore.get()
        maxScore = self.maxScore.get()
        parentWidget = self.controller.widgetsDict["submitbtnplayingframe"]
        Messagebox.show_info(
            title="Quiz Completed", message=f"You have completed the quiz with a score of {correctScore}/{maxScore}!",
            parent=parentWidget
        )
        options = ["Submit to the leaderboard:success",
                   "Return to the main menu:danger"]
        askOption = MessageDialog(
            parent=parentWidget,
            title="Quiz Completed",
            message=f"You have completed the quiz with a score of {correctScore}/{maxScore}!\nWould you like to submit your score to the leaderboard?",
            buttons=options,
        )
        askOption.show()
        if askOption.result == "Submit to the leaderboard":
            content = self.prisma.modulehubcontent.find_first(
                where={
                    "title": self.titleKey
                }
            )
            # if user has already attempted the quiz, update the score
            attempt = self.prisma.hubcontentattempt.find_first(
                where={
                    "AND": [
                        {
                            "userId": self.userId
                        },
                        {
                            "contentId": content.id
                        }
                    ]
                },
            )
            if attempt is not None:
                askOverWrite = MessageDialog(
                    parent=parentWidget,
                    title="We found an existing attempt",
                    message=f"We found an existing attempt for this quiz, would you like to overwrite it? Your previous score was {attempt.contentScore}/{maxScore}",
                    buttons=["Yes:success", "No:danger"]
                )
                askOverWrite.show()
                if askOverWrite.result == "Yes":
                    self.prisma.hubcontentattempt.update(
                        where={
                            "id": attempt.id
                        },
                        data={
                            "contentScore": correctScore
                        }
                    )
                else:
                    return
            else:
                self.prisma.hubcontentattempt.create(
                    data={
                        "contentId": content.id,
                        "contentScore": correctScore,
                        "userId": self.userId
                    }
                )
        elif askOption.result == "Return to the main menu":
            self.playingFrame.grid_remove()
            self.rulesFrame.grid_remove()
        elif askOption.result is None:
            return
