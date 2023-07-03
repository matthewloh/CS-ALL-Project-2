import json
import threading
from tkinter import *
from tkinter import filedialog
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
from prisma import Prisma
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
        self.staticImgLabels = [
            # (r"Assets\AppointmentsView\TitleLabel.png", 0, 0, "AppointmentsHeader", self),
            (r"Assets\LearningHub\LearningHubBG.png", 0, 0, "LearningHubBG", self),
            (r"Assets\LearningHub\mainframebg.png", 0,
             0, "learninghubmainbg", self.mainframe),
            (r"Assets\LearningHub\RulesFrame\RulesFrameBg.png",
             0, 0, "rulesframemainbg", self.rulesFrame),
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

        btnDict = {
            "int4004cem": (r"Assets\LearningHub\ComputerArchitecture.png", 160, 220,
                           "int4004cemhub", self.canvas, lambda: self.loadCourseHubContent("int4004cem")),
            "int4068cem": (r"Assets\LearningHub\MathematicsCS.png", 160, 220,
                           "int4068cemhub", self.canvas, lambda: print('hehe')),
            "int4003cem": (r"Assets\LearningHub\ObjectOrientedProgramming.png", 160, 220,
                           "int4003cemhub", self.canvas, lambda: print('hehe')),
            "int4009cem": (r"Assets\LearningHub\CSALL2.png", 160, 220,
                           "int4009cemhub", self.canvas, lambda: print('hehe')),
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
                isPlaced=True,
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
            # for q in questions:
            #     print(q["question"])
            #     print(q["options"])
            #     print(q["correctAnswer"])
            #     print(
            #         f"The correct answer is {q['options'][q['correctAnswer']]}")
            if typeOfContent == "GAME":
                dictOfDetails = {
                    # details is (title, description, creationTime, author)
                    "detailsOfContent": (title, description, creationTime, author),
                    "numOfQuestions": numOfQuestions,
                    "questions": questions,
                }
                self.moduleGames[f"{title}"] = dictOfDetails
            elif typeOfContent == "ACTIVITY":
                dictOfDetails = {
                    # details is (title, description, creationTime, author)
                    "detailsOfContent": (title, description, creationTime, author),
                    "numOfQuestions": numOfQuestions,
                    "questions": questions,
                }
                self.moduleActivities[f"{title}"] = dictOfDetails
            elif typeOfContent == "MULTIPLE_CHOICE" or typeOfContent == "FILL_IN_THE_BLANK":
                dictOfDetails = {
                    # details is (title, description, creationTime, author)
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

    def loadCourseHubContent(self, coursecode: str):
        self.canvas.grid_remove()
        self.mainframe.grid()
        self.mainframe.tkraise()
        self.fillLists(coursecode)
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
