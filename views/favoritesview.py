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

class FavoritesView(Canvas):
    def __init__(self, parent, controller: ElementCreator):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=ORANGE, name="favoritesview", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, ORANGE)
        self.staticImgs = [
            (r"Assets\FavoritesView\FavoritesView.png", 0, 0, "favviewbg", self),]
        self.controller.settingsUnpacker(self.staticImgs, "label")


        

    def postLogin(self, data: dict):
        self.prisma = self.controller.mainPrisma
        self.userId = data["id"]
        prisma = self.prisma
        self.loadFavoritePosts()
        self.renderFavoritePosts()
        # This returns a student

                

        # Calculates the number of post, if heightofFrame needs to exceed 580:

    
    def loadFavoritePosts(self):
        prisma = self.prisma
         # This returns a student
        self.scrolledframe = ScrolledFrame(
            master=self, width=1680, height=580, autohide=True, bootstyle="bg-round"
        )
        self.scrolledframe.place(x=120, y=260, width=1680, height=580)
        user = prisma.userprofile.find_first(
            where={
                "id": self.userId
            },
            include={
                "favoritePosts": {
                    "include": {
                        "author": True,
                        "module": True
                    }
                }
            }
        )
        favPosts = user.favoritePosts
        self.favPostList = []
        kualalumpur = timezone("Asia/Kuala_Lumpur")
        timestrfmt = r"%A, %B %d %Y at %I:%M:%S %p"
        for favPost in favPosts:
            postModule = favPost.module
            postAuthor = favPost.author
            createdAt = kualalumpur.convert(favPost.createdAt).strftime(timestrfmt)
            postInfo = (
                favPost.id, favPost.title, 
                postAuthor.fullName,
                createdAt,
                postModule.moduleCode, postModule.moduleTitle,
            )
            self.favPostList.append(postInfo)
        return self.favPostList
    
    def renderFavoritePosts(self):
        heightofFrame = len(self.favPostList) * 140
        if heightofFrame < 580:
            heightofFrame = 580
    
        self.scrolledframe.config(height=heightofFrame)

        IMAGEPATH = r"Assets\FavoritesView\Button.png"
        initCoords = (20, 20)
        for post in self.favPostList:
            id, title, author, createdAt, moduleCode, moduleTitle = post
            fmttext = f"{title}\n{moduleCode} - {moduleTitle}"
            tipText = f"Created on {createdAt} by {author} in {moduleCode} - {moduleTitle}"
            t = self.controller.textElement(
                imagepath=IMAGEPATH, xpos=initCoords[0], ypos=initCoords[1], 
                classname=f"favpost{id}", root=self.scrolledframe,
                text=fmttext, fg="#5975D7", font=INTERBOLD, size=32,
                isPlaced=True, xoffset=-2, yIndex=-1/2
            )
            ToolTip(t, text=tipText, bootstyle=(INFO,INVERSE))
            AnimatedStarBtn(
                parent=self.scrolledframe, controller=self.controller,
                xpos=initCoords[0]+1540, ypos=initCoords[1]+20,
                frameheight=60, framewidth=60,
                classname=f"favpost{id}star",
                prisma=self.controller.mainPrisma, userId=self.userId,
                resizeWidth=60, resizeHeight=60,
                isPlaced=True, isFavorited=True,
                postId=id, postTitle=title,
                isFromFavView=True
            )
            initCoords = (initCoords[0], initCoords[1]+140)
    
    def refreshFavoritesView(self):
        self.loadFavoritePosts()
        self.renderFavoritePosts()