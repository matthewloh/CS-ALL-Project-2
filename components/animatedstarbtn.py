from itertools import cycle
from pathlib import Path
import threading
from tkinter import *
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from basewindow import gridGenerator
from static import * 
from basewindow import ElementCreator
from datetime import datetime, timedelta
from pendulum import timezone
from prisma import Prisma
from PIL import Image, ImageTk, ImageSequence

class AnimatedStarBtn(Frame):
    def __init__(self,
                 parent=None, controller: ElementCreator = None,
                 xpos=0, ypos=0, framewidth=0, frameheight=0, isPlaced=False,
                 classname=None, imagexpos=0, imageypos=0, resizeWidth=0, resizeHeight=0, 
                 bg=WHITE,
                 prisma: Prisma = None, postId=None, userId=None,
                 isFavorited=False, postTitle=None,
                 isFromFavView=False):
        super().__init__(parent, width=1, bg=bg, autostyle=False, name=classname)
        self.controller = controller
        self.grid_propagate(False)
        self.postId = postId
        self.userId = userId
        self.prisma = prisma
        self.isFavorited = isFavorited
        self.isFromFavView = isFromFavView
        self.postTitle = postTitle
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        self.configure(bg=bg)
        gridGenerator(self, widthspan, heightspan, bg)
        if isPlaced:
            self.place(x=xpos, y=ypos, width=framewidth, height=frameheight)
        else:
            self.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                      columnspan=widthspan, sticky=NSEW)

        file_path = Path(__file__).parent.parent / \
            r"Assets\DiscussionsView\stargifs.gif"
        if self.isFavorited:
            with Image.open(file_path) as im:
                sequence = ImageSequence.Iterator(im)
                reversedsequence = [frame.copy() for frame in sequence]
                reversedsequence.reverse()
                # resize each frame
                reversedsequence = [frame.resize((resizeWidth, resizeHeight)) for frame in reversedsequence]
                self.images = [ImageTk.PhotoImage(
                    sequence_frame) for sequence_frame in reversedsequence]
                self.image_cycle = cycle(self.images)
                self.framerate = im.info['duration']
        else:
            with Image.open(file_path) as im:
                # sequence
                sequence = ImageSequence.Iterator(im)
                # resize each frame
                sequence = [frame.resize((resizeWidth, resizeHeight)) for frame in sequence]
                self.images = [ImageTk.PhotoImage(
                    sequence_frame) for sequence_frame in sequence]
                self.image_cycle = cycle(self.images)
                # length of each frame
                self.framerate = im.info['duration']

        self.frame_index = 0
        self.end_index = len(self.images) - 1
        imagetogetdetails = ImageTk.PhotoImage(Image.open(file_path))
        self.imgwidth = resizeWidth if resizeWidth != 0 else imagetogetdetails.width()
        self.imgheight = resizeHeight if resizeHeight != 0 else imagetogetdetails.height()
        imgrow = int(imageypos / 20)
        imgcolumn = int(imagexpos / 20)
        imgrowspan = int(self.imgheight / 20)
        imgcolumnspan = int(self.imgwidth / 20)

        self.img_container = Button(self, image=next(self.image_cycle), width=1, bg="#344557", cursor="hand2",
                                    command=lambda: self.trigger_animation())

        if isPlaced:
            self.img_container.place(
                x=0, y=0, width=self.imgwidth, height=self.imgheight
            )
        else:
            self.img_container.grid(
                column=imgcolumn, row=imgrow, columnspan=imgcolumnspan, rowspan=imgrowspan, sticky=NSEW)
        self.animation_length = len(self.images)

        self.animation_status = StringVar(value="start")
        self.animation_status.trace('w', self.animate)

        # self.after(self.framerate, self.next_frame)
        if self.isFavorited:
            self.tooltip = ToolTip(
                self.img_container, f"Click to unfavorite {self.postTitle}", bootstyle=(DANGER, INVERSE))
        else:
            self.tooltip = ToolTip(
                self.img_container, f"Click to favorite {self.postTitle}", bootstyle=(INFO, INVERSE))

    def next_frame(self):
        self.img_container.configure(image=next(self.image_cycle))
        self.after(self.framerate, self.next_frame)

    def trigger_animation(self):
        if self.animation_status.get() == "start":
            self.frame_index = 0
            self.animation_status.set("forward")
            if self.isFavorited:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUnfavoritePost(userId=self.userId, postId=self.postId)
            else:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUpdateUser(userId=self.userId, postId=self.postId)
        if self.animation_status.get() == "end":
            self.frame_index = self.animation_length
            self.animation_status.set("backward")
            if self.isFavorited:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUpdateUser(userId=self.userId, postId=self.postId)
            else:
                self.tooltip.hide_tip()
                self.tooltip = ToolTip(
                    self.img_container, f"Please wait as the server handles your request.", bootstyle=(INFO, INVERSE))
                self.tooltip.show_tip()
                self.callUnfavoritePost(userId=self.userId, postId=self.postId)

    def callUpdateUser(self, userId=None, postId=None):
        prisma = self.prisma

        def updateuser():
            toast = ToastNotification(
                title="Please be patient...",
                message="We are updating your favorite posts",
                bootstyle=(INFO)
            )
            toast.show_toast()
            userprofile = prisma.userprofile.update(
                where={
                    "id": userId
                },
                data={
                    "favoritePosts": {
                        "connect": {
                            "id": postId
                        }
                    }
                },
                include={
                    "favoritePosts": True
                }
            )
            toast.hide_toast()
            newtoast = ToastNotification(
                title="Success",
                message="Post added to your favorites",
                bootstyle=(SUCCESS),
                duration=500,
            )
            newtoast.show_toast()
            self.tooltip.hide_tip()
            self.tooltip = ToolTip(
                self.img_container, f"Click to unfavorite post {self.postTitle}", bootstyle=(DANGER, INVERSE))
            self.tooltip.show_tip()
            self.refreshFavoritesView()
            if self.isFromFavView:
                self.refreshPostsFromFavoritesView()
        t = threading.Thread(target=updateuser)
        t.daemon = True
        t.start()

    def callUnfavoritePost(self, userId=None, postId=None):
        prisma = self.prisma

        def updateuser():
            toast = ToastNotification(
                title="Please be patient...",
                message="We are updating your favorite posts",
                bootstyle=(INFO)
            )
            userprofile = prisma.userprofile.update(
                where={
                    "id": userId
                },
                data={
                    "favoritePosts": {
                        "disconnect": {
                            "id": postId
                        }
                    }
                },
                include={
                    "favoritePosts": True
                }
            )
            toast.hide_toast()
            newtoast = ToastNotification(
                title="Success",
                message="Post removed from your favorites",
                bootstyle=(SUCCESS),
                duration=500,
            )
            newtoast.show_toast()
            self.tooltip.hide_tip()
            self.tooltip = ToolTip(
                self.img_container, f"Click to favorite {self.postTitle}", bootstyle=(INFO, INVERSE))
            self.tooltip.show_tip()
            self.refreshFavoritesView()
            if self.isFromFavView:
                self.refreshPostsFromFavoritesView()

        t = threading.Thread(target=updateuser)
        t.daemon = True
        t.start()

    def animate(self, *args):
        if self.animation_status.get() == "forward":
            self.frame_index += 1
            self.img_container.configure(
                image=self.images[self.frame_index - 1])

            if self.frame_index < self.animation_length:
                self.after(20, self.animate)
            else:
                self.animation_status.set("end")
        if self.animation_status.get() == "backward":
            self.frame_index -= 1
            self.img_container.configure(image=self.images[self.frame_index])
            if self.frame_index > 0:
                self.after(20, self.animate)
            else:
                self.animation_status.set("start")
                

    def refreshFavoritesView(self):
        self.favoritesView = self.controller.widgetsDict["favoritesview"]
        self.favoritesView.refreshFavoritesView()
    
    def refreshPostsFromFavoritesView(self):
        self.discussionsView = self.controller.widgetsDict["discussionsview"]
        var = self.discussionsView.modulecodevar
        self.discussionsView.callLoadLatestPosts(var.get())