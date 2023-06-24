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
from components.animatedstarbtn import AnimatedStarBtn
from PIL import Image, ImageTk, ImageSequence

class DiscussionsView(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1, bg=WHITE,
                        name="discussionsview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.createFrames()

        self.createElements()


        self.posttitleent = self.controller.ttkEntryCreator(
            xpos=900, ypos=160, width=920, height=40, root=self.creationframe, classname="posttitleent"
        )
        textxpos, textypos, textcolumnspan, textrowspan = int(
            900/20), int(340/20), int(920/20), int(360/20)
        self.postcontenttext = Text(
            master=self.creationframe, width=1, height=1, font=("Helvetica", 18), wrap="word", name="postcontenttext"
        )
        self.postcontenttext.grid(
            column=textxpos, row=textypos, columnspan=textcolumnspan, rowspan=textrowspan, sticky=NSEW
        )

        self.creationframe.grid_remove()
        self.postviewframe.grid_remove()

    def createElements(self):
        self.staticImgLabels = [
            (r"Assets\DiscussionsView\DiscussionsViewBG.png",
             0, 0, "DiscussionsBG", self),
            (r"Assets\DiscussionsView\postcreationbg.png",
             0, 0, "postcreationbg", self.creationframe),
            (r"Assets\DiscussionsView\postviewbg.png",
             0, 0, "postviewbg", self.postviewframe),
        ]
        self.staticBtns = [
            (r"Assets\DiscussionsView\creatediscussion.png", 80, 120, "creatediscussionbtn", self,
             lambda: self.loadPostCreation()),
            (r"Assets\DiscussionsView\refreshbutton.png", 860, 220, "refreshbtn", self,
             lambda: 
             self.callLoadLatestPosts(self.modulecodevar.get())
             ),
            (r"Assets\DiscussionsView\cancelbuttondisc.png", 40, 760, "cancelbtncreation", self.creationframe,
             lambda: self.unloadPostCreation()),
            (r"Assets\DiscussionsView\createpostbuttondisc.png", 480, 760, "postbtncreation", self.creationframe,
             lambda: self.threadStart()),
            (r"Assets\My Courses\exitbutton.png", 1840, 0, "cancelbtnview", self.postviewframe,
             lambda: self.unloadPostView()),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.controller.settingsUnpacker(self.staticBtns, "button")

    def createFrames(self):
        self.creationframe = self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="postcreation",
        )
        self.postviewframe = self.controller.frameCreator(
            root=self, xpos=0, ypos=0, framewidth=1920, frameheight=920,
            classname="postview",
        )
    # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#text-anchors

    def loadPostCreation(self):
        self.creationframe.grid()
        self.creationframe.tkraise()
        self.posttitleent.delete(0, END)
        self.postcontenttext.delete("1.0", END)
        self.posttitleent.focus_set()
        self.posttitleent.bind(
            "<Return>", lambda event: self.postcontenttext.focus_set()
        )

    def postLogin(self, data: dict = None, prisma: Prisma = None):
        self.prisma = prisma
        self.userId = data["id"]
        self.programme = data["programme"]
        self.role = data["role"]
        self.frameref = self.controller.frameCreator(
            xpos=560, ypos=120, framewidth=400, frameheight=80, root=self,
            classname="modulecodeframe", bg=WHITE
        )
        self.menubutton = ttk.Menubutton(
            self.frameref, text="INT4004CEM", name="modulecodemenubtn", style="info.TMenubutton"
        )
        self.menubutton.grid(column=0, row=0,
                             columnspan=int(400/20), rowspan=int(80/20), sticky=NSEW)
        self.menubuttonmenu = Menu(
            self.menubutton, tearoff=0, font=("Helvetica", 12))
        self.modulecodevar = StringVar()
        if self.role == "lecturer":
            modules = prisma.module.find_many(
                where={
                    "lecturer": {
                        "is": {
                            "userId": {
                                "equals": self.userId
                            }
                        }
                    }    
                }
            )
        elif self.role == "student":
            modules = prisma.module.find_many(
                where={
                    "programme": {
                        "is": {
                            "programmeCode": {
                                "equals": self.programme
                            }
                        }
                    }
                }
            )
        listofvalues = []
        self.valueDict = {}
        for module in modules:
            self.valueDict[f"{module.moduleCode}"] = f"{module.moduleCode} - {module.moduleTitle}"
            listofvalues.append(module.moduleCode)
        for value in listofvalues:
            _text = self.valueDict[f"{value}"]
            self.menubuttonmenu.add_radiobutton(
                label=_text,
                variable=self.modulecodevar,
                value=value,
                command=lambda: [
                    self.menubutton.config(
                        text=self.valueDict[self.modulecodevar.get()]),
                    self.callLoadLatestPosts(self.modulecodevar.get()),
                ]
            )
        self.modulecodevar.set(listofvalues[0])
        self.menubutton["menu"] = self.menubuttonmenu
        self.menubutton.config(text=self.valueDict[self.modulecodevar.get()])

        postContentList = self.loadLatestPosts(self.modulecodevar.get())
        heightofframe = len(postContentList) * 100
        # minimum height of frame is 500 for 5 posts
        if heightofframe < 500:
            heightofframe = 500
            
        self.postscrolledframe = ScrolledFrame(
            self, width=840, height=heightofframe, name="postsframescrollable", autohide=True,
            bootstyle="rounded"
        )

        self.postscrolledframe.place(x=100, y=320, width=840, height=500)
        self.loadDiscussionTopics(postContentList)
        print("In discussionview, userid is: ", self.userId)

    def threadStart(self):
        t = threading.Thread(target=self.createPost)
        self.gif = AnimatedGif(
            parent=self.creationframe, controller=self.controller,
            xpos=280, ypos=400, bg="#344557",
            framewidth=320, frameheight=320, classname="creatingpostspinner",
            imagepath=r"Assets\200x200spinner.gif", imagexpos=60, imageypos=60)
        t.daemon = True
        t.start()

    def createPost(self):
        # ~~~~ BACKEND FUNCTIONALITY ~~~~
        prisma = self.prisma
        title = self.posttitleent.get()
        content = self.postcontenttext.get("1.0", 'end-1c')
        findmodule = prisma.module.find_first(
            where={
                "moduleCode": self.modulecodevar.get()
            }
        )
        module = prisma.modulepost.create(
            data={
                "authorId": self.userId,
                "moduleId": findmodule.id,
                "title": title,
                "content": content,
            }
        )
        self.gif.grid_forget()
        postContentList = self.loadLatestPosts(
            moduleCode=self.modulecodevar.get())
        heightofframe = len(postContentList) * 100
        # minimum height of frame is 500 for 5 posts
        if heightofframe < 500:
            heightofframe = 500
        self.postscrolledframe = ScrolledFrame(
            self, width=840, height=heightofframe, name="postsframescrollable", autohide=True,
        )
        self.postscrolledframe.grid_propagate(False)
        self.postscrolledframe.place(x=100, y=320, width=840, height=500)
        self.loadDiscussionTopics(postContentList)
        self.unloadPostCreation()

    def unloadPostCreation(self):
        self.creationframe.grid_remove()

    def loadDiscussionTopics(self, postidtitles: list = []):
        # ~~~~ BACKEND FUNCTIONALITY ~~~~
        # size of frame needed is postidtitles * 100, 80 for the post and 20 for the gap below
        heightframe = len(postidtitles) * 100
        self.postscrolledframe.configure(height=heightframe)
        initialcoordinates = (0, 0)
        for tupleofcontent in postidtitles:
            postId = tupleofcontent[0]
            discussiontitle = tupleofcontent[1]
            # content = tupleofcontent[2]
            # author = tupleofcontent[3]
            # email = tupleofcontent[4]
            # createdat = tupleofcontent[5]
            # posteditedAt = tupleofcontent[6]
            # repliesList = tupleofcontent[7]
            # authorId = tupleofcontent[8]
            favoritedPostIds = tupleofcontent[9]
            imagepath = r"Assets\DiscussionsView\discussionstitlecomponentbg.png"
            xpos = initialcoordinates[0]
            ypos = initialcoordinates[1]
            cont = self.controller
            cont.textElement(
                imagepath=imagepath, xpos=xpos, ypos=ypos,
                classname=f"post{postId}title",
                buttonFunction=lambda num=tupleofcontent: self.loadPostView(
                    num),
                root=self.postscrolledframe, text=discussiontitle, fg=BLACK, size=28, xoffset=-1, isPlaced=True,
            )
            if postId in favoritedPostIds:
                AnimatedStarBtn(
                    parent=self.postscrolledframe, xpos=initialcoordinates[0] + 760,
                    ypos=initialcoordinates[1] + 20, frameheight=40, framewidth=40,
                    classname=f"post{postId}favoritestar", imagexpos=0, imageypos=0,
                    isPlaced=True, prisma=self.prisma, postId=postId, userId=self.userId,
                    isFavorited=True, postTitle=discussiontitle,
                    resizeWidth=40, resizeHeight=40
                )
            else:
                AnimatedStarBtn(
                    parent=self.postscrolledframe,
                    xpos=initialcoordinates[0] + 760,
                    ypos=initialcoordinates[1] + 20,
                    framewidth=40, frameheight=40, classname=f"post{postId}favoritestar",
                    imagexpos=0, imageypos=0, isPlaced=True,
                    prisma=self.prisma, postId=postId, userId=self.userId,
                    postTitle=discussiontitle,
                    resizeWidth=40, resizeHeight=40
                )
            initialcoordinates = (
                initialcoordinates[0], initialcoordinates[1] + 100)

    def unloadPostView(self):
        self.postviewframe.grid_remove()

    def loadPostView(self, tupleofcontent: tuple = ()):
        self.postviewframe.grid()
        self.postviewframe.tkraise()
        postId = tupleofcontent[0]
        discussiontitle = tupleofcontent[1]
        content = tupleofcontent[2]
        author = tupleofcontent[3]
        email = tupleofcontent[4]
        createdat = tupleofcontent[5]
        posteditedAt = tupleofcontent[6]
        repliesList = tupleofcontent[7]
        authorId = tupleofcontent[8]

        # A host is used to remove the currently loaded scrolled frame using grid_remove()
        self.scrolledframehost = self.controller.frameCreator(
            root=self.postviewframe, framewidth=1100, frameheight=660,
            classname="scrolledframehostframe", xpos=100, ypos=180, bg=NICEBLUE
        )
        totalheight = (1 + len(repliesList)) * 280
        if totalheight < 660:
            totalheight = 660
        self.scrolledframe = ScrolledFrame(
            self.scrolledframehost, width=1, height=totalheight, name="postviewcontent", autohide=True, padding=0, bootstyle=WARNING
        )
        self.scrolledframe.place(
            x=0, y=0, width=1100, height=660
        )
        # TITLE OF THE POST
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\titleofthepost.png", xpos=60, ypos=40,
            classname="titleofthepost", root=self.postviewframe, isPlaced=True,
            text=f"{discussiontitle}", fg=BLACK, size=34, xoffset=-2
        )
        # MODULE CODE
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\modulecode.png", xpos=100, ypos=120,
            classname="modulecode", root=self.postviewframe, isPlaced=True,
            text=f"SOC / BCSCU / {self.modulecodevar.get()}", fg=BLACK, size=36, xoffset=-1
        )
        # REFRESH BUTTON
        self.controller.buttonCreator(
            # imagepath, xpos, ypos, classname, root, isPlaced, buttonFunction
            imagepath=r"Assets\DiscussionsView\refreshbutton.png", xpos=1160, ypos=20,
            classname="repliesrefreshbtn", root=self.postviewframe, isPlaced=True,
            buttonFunction=lambda: self.callLoadLatestReplies(
                postId, moduleCode=self.modulecodevar.get())
        )
        # PURPLE BG
        # Normal size is 1100 x 660
        self.scrolledframebg = self.controller.labelCreator(
            imagepath=r"Assets\DiscussionsView\scrolledframebg.png", xpos=0, ypos=0,
            classname="scrolledframebg", root=self.scrolledframe, isPlaced=True
        )            
        image = self.controller.imagePathDict["scrolledframebg"]
        image = Image.open(image)
        if totalheight > 660:
            image = image.resize((1100, totalheight),
                                 Image.Resampling.LANCZOS)
            self.controller.imageDict["scrolledframebg"] = ImageTk.PhotoImage(
                image)
            newimage = self.controller.imageDict["scrolledframebg"]
            self.scrolledframebg.configure(
                image=newimage, bg="#acbcff")
            self.scrolledframebg.place(
                x=0, y=0, width=1100, height=totalheight
            )
        else:
            image = image.resize((1100, totalheight),
                                 Image.Resampling.LANCZOS)
            self.controller.imageDict["scrolledframebg"] = ImageTk.PhotoImage(
                image)
            newimage = self.controller.imageDict["scrolledframebg"]
            self.scrolledframebg.configure(
                image=newimage, bg="#acbcff")
            self.scrolledframebg.place(
                x=0, y=0, width=1100, height=660
            )
        # POST BG
        self.controller.labelCreator(
            imagepath=r"Assets\DiscussionsView\exampleofapost.png", xpos=0, ypos=0,
            classname="exampleofapost", root=self.scrolledframe, isPlaced=True,
            # buttonFunction=lambda: print(f"{tupleofcontent} was clicked")
        )
        # AUTHOR AND DATE
        timestrfmt = r'%A, %B %d %Y at %I:%M:%S %p'
        datetimestr = datetime.now().strftime(timestrfmt)
        if posteditedAt == createdat:
            authoranddatetext = f"{author} posted on {createdat}"
        else:
            timedelta = datetime.strptime(
                datetimestr, timestrfmt) - datetime.strptime(posteditedAt, timestrfmt)
            if timedelta.days > 0:
                timedelta = f"{timedelta.days} days"
            elif timedelta.seconds//3600 > 0:
                timedelta = f"{timedelta.seconds//3600} hours"
            elif timedelta.seconds//60 > 0:
                timedelta = f"{timedelta.seconds//60} minutes"
            elif timedelta.seconds < 60:
                timedelta = f"{timedelta.seconds} seconds"
            authoranddatetext = f"{author} posted on {createdat} (edited {timedelta} ago)"
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\fullnamepostedon.png", xpos=20, ypos=20,
            classname="fullnamepostedon", root=self.scrolledframe, isPlaced=True,
            text=authoranddatetext, fg=BLACK, size=22, xoffset=-2
        )
        # EMAIL OF AUTHOR
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\emailofauthor.png", xpos=20, ypos=60,
            classname="emailofauthor", root=self.scrolledframe, isPlaced=True,
            text=f"{email}", fg=BLACK, size=15, xoffset=0
        )
        # COMPONENTS OF A POST:
        # 1. POST TITLE -> a single text element label
        # 2. "Full Name posted on date" -> a single text element label
        # 3. The poster's email below it -> a single text element label
        # 4. The content of the post -> a text widget from tkinter, read only
        # 5. The replies are also text widgets, read only
        # 6. The reply button -> a button
        # 7. The favorite button -> a button
        # 8. Area to type a reply -> a text widget
        self.scrolledtext = ScrolledText(
            master=self.scrolledframe, width=1, height=1, name = "contenttext",
            bootstyle=INFO, autohide=True,
        )
        self.contenttext = self.scrolledtext.text
        self.contenttext.config(
            font=("Inter", 16), wrap=WORD, 
            fg=BLACK, 
        )

        self.contenttext.insert(END, content)
        self.scrolledtext.place(
            x=20, y=120, width=1060, height=120
        )
        self.contenttext.config(state=DISABLED)
        self.controller.widgetsDict["contenttext"] = self.contenttext
        # buttons to delete and edit the post
        if self.userId == authorId:
            self.controller.buttonCreator(
                imagepath=r"Assets\DiscussionsView\edit.png", xpos=960, ypos=20,
                classname="editpost", root=self.scrolledframe, isPlaced=True,
                buttonFunction=lambda post=(
                    postId, None, self.modulecodevar.get(), "contenttext", True): self.editReplyorPost(*post)
            )
            self.controller.buttonCreator(
                imagepath=r"Assets\DiscussionsView\Trash.png", xpos=1020, ypos=20,
                classname="deletepost", root=self.scrolledframe, isPlaced=True,
                buttonFunction=lambda post=(
                    postId, None, self.modulecodevar.get(), True): self.deleteReplyorPost(*post)
            )
        # REPLIES under a post
        replycoordinates = (40, 280)
        authorCoordinates = (
            replycoordinates[0] + 20, replycoordinates[1] + 20)
        textCoordinates = (replycoordinates[0] + 20, replycoordinates[1] + 120)
        replycounter = 0
        participants = []
        # adding the author of the post to the participants set
        participants.append(author + " (AUTHOR)")
        for replies in repliesList:
            replyContent = replies[0]
            replyAuthor = replies[1]
            if replyAuthor not in participants and replyAuthor != author:
                participants.append(replyAuthor)
            repAuthorEmail = replies[2]
            repCreatedAt = replies[3]
            repEditedAt = replies[4]
            replyId = replies[5]
            repAuthorId = replies[6]
            authorCoordinates = (
                replycoordinates[0] + 20, replycoordinates[1] + 20)
            textCoordinates = (
                replycoordinates[0] + 20, replycoordinates[1] + 120)
            # reply bg
            self.controller.buttonCreator(
                imagepath=r"Assets\DiscussionsView\exampleofareply.png", xpos=replycoordinates[0], ypos=replycoordinates[1],
                classname=f"exampleofareply{replycounter}", root=self.scrolledframe, isPlaced=True,
                buttonFunction=lambda rep=replies: print(f"{rep} was clicked")
            )
            timestrfmt = r'%A, %B %d %Y at %I:%M:%S %p'
            datetimestr = datetime.now().strftime(timestrfmt)
            if repEditedAt == repCreatedAt:
                repAuthorDate = f"{replyAuthor} replied on {repCreatedAt}"
            else:
                timedelta = datetime.strptime(
                    datetimestr, timestrfmt) - datetime.strptime(repEditedAt, timestrfmt)
                if timedelta.days > 0:
                    timedelta = f"{timedelta.days} days"
                elif timedelta.seconds//3600 > 0:
                    timedelta = f"{timedelta.seconds//3600} hours"
                elif timedelta.seconds//60 > 0:
                    timedelta = f"{timedelta.seconds//60} minutes"
                elif timedelta.seconds < 60:
                    timedelta = f"{timedelta.seconds} seconds"
                repAuthorDate = f"{replyAuthor} replied on {repCreatedAt} (edited {timedelta} ago)"
            # reply author and date
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\fullnamepostedon.png", xpos=authorCoordinates[0], ypos=authorCoordinates[1],
                classname=f"replydetailsfullnamedateemail{replycounter}", root=self.scrolledframe, isPlaced=True,
                text=repAuthorDate, fg=BLACK, size=22, xoffset=-2
            )
            # reply email
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\emailofauthor.png", xpos=authorCoordinates[0], ypos=authorCoordinates[1]+40,
                classname=f"replyemail{replycounter}", root=self.scrolledframe, isPlaced=True,
                text=f"{repAuthorEmail}", fg=BLACK, size=15, xoffset=0
            )
            # reply content
            scrolledtextname = f"scrolledtext{replycounter}"
            replytextname = f"replycontent{replycounter}"
            scrolledtext = ScrolledText(
                master=self.scrolledframe, width=1, height=1, name=scrolledtextname,
                bootstyle=SECONDARY, autohide=True,
            )
            contenttext = scrolledtext.text
            contenttext.config(
                font=("Inter", 14), wrap=WORD, 
                fg=BLACK, 
            )
            contenttext.insert(END, replyContent)

            contenttext.config(state=DISABLED)

            scrolledtext.place(
                x=textCoordinates[0], y=textCoordinates[1], width=1020, height=120
            )
            self.controller.widgetsDict[replytextname] = contenttext
            # buttons to edit and delete a reply
            if repAuthorId == self.userId:
                # edit
                self.controller.buttonCreator(
                    imagepath=r"Assets\DiscussionsView\edit.png", xpos=authorCoordinates[0]+900, ypos=authorCoordinates[1],
                    classname=f"editreply{replycounter}", root=self.scrolledframe, isPlaced=True,
                    buttonFunction=lambda rep=(postId, replyId,
                                               self.modulecodevar.get(), replytextname
                                               ): self.editReplyorPost(*rep)
                )
                # delete
                self.controller.buttonCreator(
                    imagepath=r"Assets\DiscussionsView\Trash.png", xpos=authorCoordinates[0]+960, ypos=authorCoordinates[1],
                    classname=f"deletereply{replycounter}", root=self.scrolledframe, isPlaced=True,
                    buttonFunction=lambda rep=(
                        postId, replyId, self.modulecodevar.get()): self.deleteReplyorPost(*rep)
                )
            replycounter += 1
            replycoordinates = (replycoordinates[0], replycoordinates[1] + 280)

        partiCoords = (1300, 140)
        partiCounter = 1
        try:
            for i in range(1, len(participants)+10):
                self.controller.widgetsDict[f"{i}inpost"].grid_remove()
        except:
            pass
        for p in participants:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\viewparticipants.png", xpos=partiCoords[0], ypos=partiCoords[1],
                classname=f"{partiCounter}inpost", root=self.postviewframe,
                text=f"{partiCounter}. {p.upper()}", fg=BLACK, size=24, xoffset=-1,
                buttonFunction=lambda p=p: print(f"{p} was clicked")
            )
            partiCoords = (partiCoords[0], partiCoords[1] + 40)
            partiCounter += 1

        # CREATE/EDIT REPLY REGION
        self.replytextwidget = Text(
            self.postviewframe, width=1, height=1, bg=WHITE, fg=BLACK, font=("Arial", 16), wrap=WORD,
            name="replytextwidget", padx=20, pady=20, relief=FLAT, bd=0, highlightthickness=0,
        )
        self.replytextwidget.place(
            x=1300, y=460, width=560, height=300
        )
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
            classname="replyheader", root=self.postviewframe, isPlaced=True,
            text="Add a reply:", fg=BLACK, size=36,
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\cancelreplyedit.png", xpos=1300, ypos=780,
            classname="cancelreplyedit", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\cancelreply.png", xpos=1300, ypos=780,
            classname="cancelreply", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\editreply.png", xpos=1620, ypos=780,
            classname="editreply", root=self.postviewframe,
            buttonFunction=lambda: self.replyThreaded(
                postId, self.modulecodevar.get())
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\addreply.png", xpos=1620, ypos=780,
            classname="addreply", root=self.postviewframe,
            buttonFunction=lambda: self.replyThreaded(
                postId, self.modulecodevar.get())
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\canceldelete.png", xpos=1300, ypos=780,
            classname="canceldelete", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.buttonCreator(
            imagepath=r"Assets\DiscussionsView\confirmdelete.png", xpos=1620, ypos=780,
            classname="confirmdelete", root=self.postviewframe,
            buttonFunction=lambda: self.replytextwidget.delete('1.0', END)
        )
        self.controller.labelCreator(
            imagepath=r"Assets\DiscussionsView\deletewarninglabel.png", xpos=1300, ypos=460,
            classname="deletewarninglabel", root=self.postviewframe,
        )
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replytotal.png", xpos=1380, ypos=580,
            classname="replytotal", root=self.postviewframe, font=INTERBOLD,
            text=f"This post has {len(repliesList)} replies.", fg="#d2564e", size=28,
        )
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\participantstotal.png", xpos=1380, ypos=660,
            classname="participantstotal", root=self.postviewframe, font=INTERBOLD,
            text=f"From {len(participants)} participants.", fg="#d2564e", size=28,
        )
        wDict = self.controller.widgetsDict
        self.replyWidgets = [
            wDict["cancelreply"],
            wDict["addreply"],
        ]
        self.replyDeleteWidgets = [
            wDict["canceldelete"],
            wDict["confirmdelete"],
            wDict["deletewarninglabel"]
        ]
        self.replyDeletePostOnly = [
            wDict["replytotal"],
            wDict["participantstotal"]
        ]
        self.replyEditWidgets = [
            wDict["cancelreplyedit"],
            wDict["editreply"]
        ]
        for widget in self.replyDeletePostOnly:
            widget.grid_remove()
        for widget in self.replyDeleteWidgets:
            widget.grid_remove()
        for widget in self.replyEditWidgets:
            widget.grid_remove()

    def clearReplyText(self):
        self.replytextwidget.delete('1.0', END)

    def replyThreaded(self, postId, moduleCode: str = "INT4004CEM"):
        t = threading.Thread(target=self.addReply, args=(postId, moduleCode))
        t.daemon = True
        t.start()

    def deleteReplyorPost(self, postId, replyId, moduleCode: str = "INT4004CEM", isPost: bool = False):
        wDict = self.controller.widgetsDict
        addreplybtn = wDict["addreply"]
        editreplybtn = wDict["editreply"]
        canceldeletebtn = wDict["canceldelete"]
        confirmdeletebtn = wDict["confirmdelete"]
        deletewarninglabel = wDict["deletewarninglabel"]
        [widget.grid_remove() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyEditWidgets]
        [widget.grid() for widget in self.replyDeleteWidgets]
        [widget.tk.call("raise", widget._w)
         for widget in self.replyDeleteWidgets]
        [widget.grid() if isPost else None for widget in self.replyDeletePostOnly]
        [widget.tk.call("raise", widget._w)
         if isPost else None for widget in self.replyDeletePostOnly]
        if isPost:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Deleting post: ", fg=BLACK, size=36,
            )
            confirmdeletebtn.config(
                command=lambda: self.callDeleteReply(
                    postId, replyId, moduleCode, isPost=True)
            )
        else:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Deleting reply: ", fg=BLACK, size=36,
            )
            confirmdeletebtn.config(
                command=lambda: self.callDeleteReply(
                    postId, replyId, moduleCode)
            )
        canceldeletebtn.config(
            command=lambda: [
                [widget.grid_remove() for widget in self.replyEditWidgets],
                [widget.grid_remove() for widget in self.replyDeleteWidgets],
                [widget.grid_remove() for widget in self.replyDeletePostOnly],
                [widget.grid() for widget in self.replyWidgets],
                self.replytextwidget.delete('1.0', END),
                self.controller.textElement(
                    imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                    classname="replyheader", root=self.postviewframe, isPlaced=True,
                    text="Add a reply:", fg=BLACK, size=36,
                )
            ]
        )

    def callDeleteReply(self, postId, replyId, moduleCode: str = "INT4004CEM", isPost: bool = False):
        t = threading.Thread(target=self.deleteReply, args=(
            postId, replyId, moduleCode, isPost))
        t.daemon = True
        t.start()

    def deleteReply(self, postId, replyId, moduleCode: str = "INT4004CEM", isPost: bool = False):
        prisma = self.prisma
        if isPost:
            toasttitle = "Deleting Post"
            toastmessage = "Please wait while we delete your post..."
        else:
            toasttitle = "Deleting Reply"
            toastmessage = "Please wait while we delete your reply..."
        toast = ToastNotification(
            title=toasttitle,
            message=toastmessage,
            bootstyle=INFO,
        )
        toast.show_toast()
        if isPost:
            post = prisma.modulepost.delete(
                where={
                    "id": postId
                }
            )
            newtoasttitle = "Post Deleted"
            newtoastmessage = "Your post has been deleted successfully!"
        else:
            reply = prisma.reply.delete(
                where={
                    "replyId": replyId
                }
            )
            newtoasttitle = "Reply Deleted"
            newtoastmessage = "Your reply has been deleted successfully!"
        toast.hide_toast()
        newtoast = ToastNotification(
            title=newtoasttitle,
            message=newtoastmessage,
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        [widget.grid() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyDeleteWidgets]
        [widget.grid_remove() for widget in self.replyEditWidgets]
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
            classname="replyheader", root=self.postviewframe, isPlaced=True,
            text="Add a reply:", fg=BLACK, size=36,
        )
        try:
            self.refreshReplies(postId, moduleCode)
            if isPost:
                postContentList = self.refreshPosts(moduleCode)
                self.loadDiscussionTopics(postContentList)
                self.unloadPostView()
                toast = ToastNotification(
                    title="The post was deleted",
                    message="Returning to the discussion topics...",
                    bootstyle=DANGER,
                    duration=1000,
                )
                toast.show_toast()
        except:
            postContentList = self.refreshPosts(moduleCode)
            self.loadDiscussionTopics(postContentList)
            self.unloadPostView()

    def editReplyorPost(self, postId, replyId, moduleCode: str = "INT4004CEM", replytextname: Text = None, isPost: bool = False):
        textwidget = self.controller.widgetsDict[f"{replytextname}"]
        editreplybtn = self.controller.widgetsDict["editreply"]
        cancelreplyeditbtn = self.controller.widgetsDict["cancelreplyedit"]
        # important lesson for today, tuple comprehensions do not exist in python, so you have to use list comprehensions
        [widget.grid_remove() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyDeleteWidgets]
        [widget.grid_remove() for widget in self.replyDeletePostOnly]
        [widget.grid() for widget in self.replyEditWidgets]
        text = textwidget.get("1.0", 'end-1c')

        self.replytextwidget.focus_set()
        self.replytextwidget.delete('1.0', END)
        self.replytextwidget.insert(END, text)

        if isPost:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Editing Post: ", fg=BLACK, size=36,
            )
            editreplybtn.config(
                command=lambda: self.callUpdateReply(
                    postId, replyId, moduleCode, replytextname, isPost=True)
            )
        else:
            self.controller.textElement(
                imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                classname="replyheader", root=self.postviewframe, isPlaced=True,
                text="Editing Reply: ", fg=BLACK, size=36,
            )
            editreplybtn.config(
                command=lambda: self.callUpdateReply(
                    postId, replyId, moduleCode, replytextname)
            )
        cancelreplyeditbtn.config(
            command=lambda: [
                [widget.grid_remove() for widget in self.replyEditWidgets],
                [widget.grid_remove() for widget in self.replyDeleteWidgets],
                [widget.grid() for widget in self.replyWidgets],
                self.replytextwidget.delete('1.0', END),
                self.controller.textElement(
                    imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
                    classname="replyheader", root=self.postviewframe, isPlaced=True,
                    text="Add a reply:", fg=BLACK, size=36,
                )
            ]
        )

    def callUpdateReply(self, postId, replyId, moduleCode: str = "INT4004CEM", replytextname: Text = None, isPost: bool = False):
        t = threading.Thread(target=self.updateReply, args=(
            postId, replyId, moduleCode, replytextname, isPost))
        t.daemon = True
        t.start()

    def updateReply(self, postId, replyId, moduleCode: str = "INT4004CEM", replytextname: Text = None, isPost: bool = False):
        prisma = self.prisma
        if isPost:
            toasttitle = "Updating Post"
            toastmessage = "Please wait while we update your post..."
        else:
            toasttitle = "Updating Reply"
            toastmessage = "Please wait while we update your reply..."
        toast = ToastNotification(
            title=toasttitle,
            message=toastmessage,
            bootstyle=INFO,
        )
        newtext = self.replytextwidget.get("1.0", 'end-1c')
        toast.show_toast()
        utc = timezone('UTC')
        kualalumpur = timezone('Asia/Kuala_Lumpur')
        time = kualalumpur.convert(datetime.now())
        newtime = utc.convert(time)
        if isPost:
            reply = prisma.modulepost.update(
                data={
                    "content": newtext,
                    "editedAt": newtime
                },
                where={
                    "id": postId
                }
            )
            newtoasttitle = "Post Updated"
            newtoastmsg = "Your post has been updated successfully!"
        else:
            reply = prisma.reply.update(
                data={
                    "content": newtext,
                    "editedAt": newtime
                },
                where={
                    "replyId": replyId
                }
            )
            newtoasttitle = "Reply Updated"
            newtoastmsg = "Your reply has been updated successfully!"
        toast.hide_toast()
        newtoast = ToastNotification(
            title=newtoasttitle,
            message=newtoastmsg,
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        [widget.grid() for widget in self.replyWidgets]
        [widget.grid_remove() for widget in self.replyDeleteWidgets]
        [widget.grid_remove() for widget in self.replyEditWidgets]
        self.controller.textElement(
            imagepath=r"Assets\DiscussionsView\replyheader.png", xpos=1320, ypos=400,
            classname="replyheader", root=self.postviewframe, isPlaced=True,
            text="Add a reply:", fg=BLACK, size=36,
        )
        self.replytextwidget.delete('1.0', END)
        self.refreshReplies(postId, moduleCode)

    def addReply(self, postId, moduleCode: str = "INT4004CEM"):
        prisma = self.prisma
        toast = ToastNotification(
            title="Adding Reply",
            message="Please wait while we add your reply...",
            bootstyle=INFO,
        )
        toast.show_toast()
        replytext = self.replytextwidget.get("1.0", 'end-1c')
        reply = prisma.reply.create(
            data={
                "content": replytext,
                "modulePostId": postId,
                "authorId": self.userId,  # taken from postlogin
            }
        )
        toast.hide_toast()
        newtoast = ToastNotification(
            title="Reply Added",
            message="Your reply has been added successfully!",
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        self.refreshReplies(postId, moduleCode)

    def callLoadLatestPosts(self, moduleCode: str = "INT4004CEM"):
        t = threading.Thread(target=self.refreshPosts,
                             args=(moduleCode,))
        t.daemon = True
        t.start()

    def callLoadLatestReplies(self, postId, moduleCode: str = "INT4004CEM"):
        t = threading.Thread(target=self.refreshReplies,
                             args=(postId, moduleCode))
        t.daemon = True
        t.start()

    def loadLatestPosts(self, moduleCode: str = "INT4004CEM"):
        prisma = self.prisma
        posts = prisma.modulepost.find_many(
            include={
                "author": True,
                "replies": {
                    "include": {
                        "author": True
                    }
                }
            },
            where={
                "module": {
                    "is": {
                        "moduleCode": moduleCode
                    }
                }
            }
        )
        user = prisma.userprofile.find_first(
            where={
                "id": self.userId
            },
            include={
                "favoritePosts": True
            }
        )
        favoritedPostIds = [p.id for p in user.favoritePosts]
        # from pendulum
        # prisma's datetime fields are saved automatically in UTC
        # converting to local timezone:
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        timestrfmt = r'%A, %B %d %Y at %I:%M:%S %p'
        postContentList = [
            (
                post.id, post.title, post.content, post.author.fullName, post.author.email,
                kualalumpur.convert(post.createdAt).strftime(
                    timestrfmt),  # '%A %d %B %Y %H:%M:%S'
                kualalumpur.convert(post.editedAt).strftime(
                    timestrfmt),
                [
                    [
                        reply.content, reply.author.fullName, reply.author.email,
                        kualalumpur.convert(reply.createdAt).strftime(
                            timestrfmt),  # '%A %d %B %Y %H:%M:%S'
                        kualalumpur.convert(reply.editedAt).strftime(
                            timestrfmt),
                        reply.replyId, reply.authorId,
                    ] for reply in post.replies
                ],
                post.authorId,
                favoritedPostIds
            ) for post in posts
        ]
        return postContentList

    def refreshPosts(self, moduleCode: str = "INT4004CEM"):
        toast = ToastNotification(
            title="Just a moment...",
            message=f"Loading latest posts for {moduleCode}...",
            bootstyle=INFO,
        )
        toast.show_toast()
        postContentList = self.loadLatestPosts(moduleCode)
        heightofframe = len(postContentList) * 100
        if heightofframe < 500:
            rowspanofFrame = int(500/20)
        else:
            rowspanofFrame = int(heightofframe/20)
        self.postscrolledframe = ScrolledFrame(
            self, width=840, height=heightofframe, name="postsframescrollable", autohide=True,
        )
        self.postscrolledframe.grid_propagate(False)
        self.postscrolledframe.place(x=100, y=320, width=840, height=500)
        self.loadDiscussionTopics(postContentList)
        toast.hide_toast()
        newtoast = ToastNotification(
            title="Done!",
            message=f"Latest posts loaded for {moduleCode}.",
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
        return postContentList

    def refreshReplies(self, postId, moduleCode: str = "INT4004CEM"):
        toast = ToastNotification(
            title="Just a moment...",
            message=f"Fetching latest replies for Post {postId}",
            bootstyle=INFO,
        )
        toast.show_toast()
        postContentList = self.refreshPosts(moduleCode)
        # probably can be refactored into a binary search
        for tuple in postContentList:
            if tuple[0] == postId:
                self.loadPostView(tuple)
                break
        toast.hide_toast()
        newtoast = ToastNotification(
            title="Done!",
            message=f"Latest replies loaded for {postId}.",
            bootstyle=SUCCESS,
            duration=500,
        )
        newtoast.show_toast()
