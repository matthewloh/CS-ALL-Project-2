from ctypes import windll
import threading
from tkinter import FLAT, NSEW, Frame, Label
from prisma import Prisma
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.validation import add_regex_validation, validator, add_validation
from nonstandardimports import *
from tkinter import *
from static import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
# https://stackoverflow.com/a/68621773
# This bit of code allows us to remove the window bar present in tkinter
# More information on the ctypes library can be found here:
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
# https://learn.microsoft.com/en-us/windows/win32/winmsg/window-styles
GetWindowLongPtrW = windll.user32.GetWindowLongPtrW
SetWindowLongPtrW = windll.user32.SetWindowLongPtrW


def get_handle(root) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)


user32 = windll.user32
eventId = None


def gridGenerator(root: Frame, width, height, color, overriderelief: bool = False, relief: str = FLAT, name=None):
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


class ElementCreator(ttk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}

    def startPrisma(self):
        try:
            self.mainPrisma = Prisma()
            self.mainPrisma.connect()
            print("Successfully connected to Prisma client.")
        except Exception as e:
            print(e)

    def initMainPrisma(self):
        t = threading.Thread(target=self.startPrisma)
        t.daemon = True
        t.start()

    def createImageReference(self, imagepath: str, classname: str):
        # stores a key value pair of "classname" : "imagepath"
        self.imagePathDict[classname] = imagepath
        # creates a Tkinter image object
        image = ImageTk.PhotoImage(Image.open(imagepath))
        # stores a key value pair of "classname" : "image" to prevent garbage collection
        self.imageDict[classname] = image
        return image

    def settingsUnpacker(self, listoftuples, typeoftuple):
        """
        format for labels: (imagepath, x, y, classname, root)\n
        format for buttons: (imagepath, x, y, classname, root, buttonFunction)\n
        tupletodict creates a dict mapping to the creator functions.
        TODO: enable styling within here
        """
        for i in listoftuples:
            if typeoftuple == "button":
                self.buttonCreator(**self.tupleToDict(i))
            elif typeoftuple == "label":
                self.labelCreator(**self.tupleToDict(i))

    def tupleToDict(self, tup):  # TODO: make this multipurpose
        if len(tup) == 5:
            return dict(zip(("imagepath", "xpos", "ypos", "classname", "root"), tup))
        if len(tup) == 6:
            return dict(zip(("imagepath", "xpos", "ypos", "classname", "root", "buttonFunction"), tup))

    def buttonCreator(self, imagepath=None, xpos=None, ypos=None, classname=None, buttonFunction=None, root=None, relief=SUNKEN, overrideRelief=FLAT, bg=WHITE, isPlaced=False) -> Button:
        """
        Args:
            imagepath (str): path to the image
            xpos (int): x position of the button
            ypos (int): y position of the button
            classname (str): name of the button.
            buttonFunction (function): function to be called when the button is clicked.
            root (Frame): the root frame to place the button in.
            isPlaced (bool): whether or not the button is placed.

        Returns:
             Button: the button object placed in the root container

        Usage:
            self.controller.buttonCreator(
                imagepath=r"\imagepath.png", xpos=0, ypos=0, 
                classname="classname", root=validtkinterparent (Frame, Canvas, ttk.ScrolledFrame),
                buttonFunction=lambda: function()
            )
        """
        classname = classname.replace(" ", "").lower()
        self.createImageReference(imagepath, classname)
        image = self.imageDict[classname]
        widthspan = int(image.width()/20)
        # just the vertical length of the image divided by 20 to get rowspan
        heightspan = int(image.height()/20)
        # the W value of the image divided by 20 to get the column position
        columnarg = int(xpos/20)
        rowarg = int(ypos/20)
        if isPlaced:
            placedwidth = int(image.width())
            placedheight = int(image.height())
        button = Button(
            root, image=image, command=lambda: buttonFunction(
            ) if buttonFunction else print(f"This is the {classname} button"),
            relief=relief if not overrideRelief else overrideRelief, bg=bg, width=1, height=1,
            cursor="hand2", state=NORMAL,
            name=classname, autostyle=False
        )
        if isPlaced:
            button.place(x=xpos, y=ypos, width=placedwidth,
                         height=placedheight)
        else:
            button.grid(row=rowarg, column=columnarg,
                        rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)
        return button

    def labelCreator(self, imagepath, xpos, ypos, classname=None, root=None, overrideRelief=FLAT, isPlaced=False, bg=WHITE) -> Label:
        """
        Args:
            imagepath (str): path to the image
            xpos (int): x position of the label
            ypos (int): y position of the label
            classname (str): name of the label.
            root (Frame): the root frame to place the label in.
            isPlaced (bool): whether or not the label is placed.

        Returns:
             Label: the label object placed in the root container

        Usage:
            self.controller.labelCreator(
                imagepath=r"\imagepath.png", xpos=0, ypos=0, 
                classname="classname", root=validtkinterparent (Frame, Canvas, ttk.ScrolledFrame),
            )
        """
        classname = classname.replace(" ", "").lower()
        self.createImageReference(imagepath, classname)
        image = self.imageDict[classname]
        widthspan = int(image.width()/20)
        # just the vertical length of the image divided by 20 to get rowspan
        heightspan = int(image.height()/20)
        # the W value of the image divided by 20 to get the column position
        columnarg = int(xpos/20)
        rowarg = int(ypos/20)
        placedwidth = int(image.width())
        placedheight = int(image.height())
        label = Label(
            root, image=image, relief=FLAT, width=1, height=1,
            state=NORMAL, name=classname,
            autostyle=False, bg=bg
        )
        if isPlaced:
            label.place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
        else:
            label.grid(row=rowarg, column=columnarg,
                       rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)
        return label

    def frameCreator(self, xpos, ypos, framewidth, frameheight, root=None, classname=None, bg=LIGHTYELLOW, relief=FLAT, imgSettings=None, isPlaced=False) -> Frame:
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)

        frame = Frame(root, width=1, height=1, bg=bg,
                      relief=relief, name=classname, autostyle=False,)
        if isPlaced:
            frame.place(x=xpos, y=ypos, width=framewidth, height=frameheight)
        else:
            frame.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                       columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)
        if imgSettings:
            listofimages = list(enumerate(imgSettings))
        # imgBg is a list of tuples containing (imagepath, x, y, name)
        # example = [("Assets\Dashboard\Top Bar.png", 0, 0, "stringwhatever"),] -> 0 ('Assets\\Dashboard\\Top Bar.png', 0, 0, 'stringwhatever')
        for widgetname, widget in root.children.items():
            if widgetname == classname:
                gridGenerator(widget, widthspan, heightspan, WHITE)
                widget.grid_propagate(False)
                if imgSettings:
                    for i, j in listofimages:
                        # print(j[1] / 20, j[2] / 20)
                        self.buttonCreator(
                            j[0],
                            j[1] - xpos,
                            j[2] - ypos,
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4])
        return frame

    def entryCreator(self, xpos, ypos, width, height, root=None, classname=None, bg=WHITE, relief=FLAT, fg=BLACK, textvariable=None, pady=None, font=("Avenir Next Medium", 16)) -> Entry:
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        self.updateWidgetsDict(root=root)
        entry = Entry(root, bg=bg, relief=SOLID, font=font, fg=fg, width=1,
                      name=classname, autostyle=False, textvariable=textvariable)
        entry.grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW, pady=pady)
        self.updateWidgetsDict(root=root)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                widget.grid_propagate(False)
        return entry

    def canvasCreator(self, xpos, ypos, width, height, root, classname=None, bgcolor=WHITE, imgSettings=None, relief=FLAT, isTransparent=False, transparentcolor=TRANSPARENTGREEN) -> Canvas:
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        if imgSettings:
            listofimages = list(enumerate(imgSettings))
        canvas = Canvas(root, bg=bgcolor, highlightcolor=bgcolor, relief=FLAT,
                        width=1, height=1, name=classname, highlightthickness=0, autostyle=False)
        canvas.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                    columnspan=widthspan, sticky=NSEW)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                gridGenerator(widget, widthspan, heightspan, bgcolor)
                widget.grid_propagate(False)
                if isTransparent:
                    hwnd = widget.winfo_id()  # TRANSPARENTGREEN IS the default colorkey
                    transparentcolor = self.hex_to_rgb(transparentcolor)
                    wnd_exstyle = win32gui.GetWindowLong(
                        hwnd, win32con.GWL_EXSTYLE)
                    new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
                    win32gui.SetWindowLong(
                        hwnd, win32con.GWL_EXSTYLE, new_exstyle)
                    win32gui.SetLayeredWindowAttributes(
                        hwnd, transparentcolor, 255, win32con.LWA_COLORKEY)
                if imgSettings:
                    for i, j in listofimages:
                        self.buttonCreator(
                            j[0],
                            j[1],
                            j[2],
                            classname=j[3],
                            root=widget,
                            buttonFunction=j[4]
                        )
        self.updateWidgetsDict(root=root)
        return canvas

    def menubuttonCreator(self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), text=None, variable=None, listofvalues=None, command=None) -> ttk.Menubutton:
        """
        Takes in arguments xpos, ypos, width, height, from Figma, creates a frame,\n
        and places a menubutton inside of it. The menubutton is then returned into the global dict of widgets.\n
        Requires a var like StringVar() to be initialized and passed in.\n
        Feed in a list of values and command functions to be used in the menubutton.\n
        Styling handled by passing in a formatted classname and font to config a style.
        """
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        classname = classname.lower().replace(" ", "")
        themename = f"{str(root).split('.')[-1]}.TMenubutton"
        # print(themename, classname)
        menustyle = ttk.Style()
        menustyle.configure(
            style=themename, font=("Helvetica", 10),
            background="#F9F5EB", foreground=BLACK,
            bordercolor="#78c2ad",
            relief="raised",
        )
        if themename == "apptcreateframe.TMenubutton":
            menustyle.configure(style=themename, background=LIGHTPURPLE,
                                foreground=BLACK, bordercolor=LIGHTPURPLE,
                                font=("Urbanist Medium", 20))
            menustyle.map(themename, foreground=[('active', BLACK), ("disabled", BLACK)],
                          background=[('active', "#ffe3bd"), ("disabled", "#ffe3bd")])
        self.frameCreator(xpos, ypos, width, height, root,
                          classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT)
        frameref = self.widgetsDict[f"{classname}hostfr"]
        menubutton = ttk.Menubutton(
            frameref, text=text.title(),
            style=themename,
            name=classname,
            # bootstyle=(DANGER)
        )
        menubutton.grid(row=0, column=0, rowspan=heightspan,
                        columnspan=widthspan, sticky=NSEW)
        menubtnmenu = Menu(
            menubutton, tearoff=0, name=f"{classname}menu",
            bg=LIGHTPURPLE, relief=FLAT, font=("Helvetica", 12),
        )
        for x in listofvalues:
            menubtnmenu.add_radiobutton(label=x, variable=variable, value=x,
                                        command=lambda: [command(), menubutton.config(text=variable.get())])
        menubutton["menu"] = menubtnmenu
        self.widgetsDict[menubutton["menu"]] = menubtnmenu
        self.widgetsDict[classname] = menubutton
        self.updateWidgetsDict(root=root)

        return menubutton

    def ttkEntryCreator(self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), fg=BLACK, validation=False, passwordchar="*", captchavar=None, isPlaced=False) -> ttk.Entry:
        """
        Takes in arguments xpos, ypos, width, height, from Figma, creates a frame,\n
        and places a ttk.Entry inside of it. The ttk.Entry is then returned into the global dict of widgets.\n
        Requires a var like StringVar() to be initialized and passed in.\n
        Styling handled by passing in a formatted classname and font to config a style.
        """
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        # entrystyle = ttk.Style()
        # entrystyle.configure(f"{classname}.TEntry", font=font, background=bgcolor, foreground=WHITE)
        frame = self.frameCreator(xpos, ypos, width, height, root,
                                  classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT, isPlaced=isPlaced)

        @validator
        def validateCaptcha(event):
            """
            Validates the captcha entry.
            """
            parentname = str(root).split(".")[-1]
            if self.widgetsDict[f"{parentname}captcha"].get() == captchavar.get():
                return True
            else:
                return False

        @validator
        def validatePassword(event):
            """
            Validates the password and confirms password entries.
            """
            parentname = str(root).split(".")[-1]
            if self.widgetsDict[f"{parentname}passent"].get() == "":
                return False
            if self.widgetsDict[f"{parentname}passent"].get() == self.widgetsDict[f"{parentname}confpassent"].get():
                return True
            else:
                return False

        themename = f"{str(root).split('.')[-1]}.TEntry"
        ttk.Style().configure(
            style=themename, font=font, background=NICEBLUE, foreground=BLACK,
        )
        entry = ttk.Entry(frame, bootstyle=PRIMARY, foreground=fg,
                          name=classname, font=font, background=bgcolor)
        entry.grid(row=0, column=0, rowspan=heightspan,
                   columnspan=widthspan, sticky=NSEW)

        if validation == "isPassword":
            entry.config(show=passwordchar)
            add_regex_validation(
                widget=entry, pattern="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$")
        elif validation == "isConfPass":
            entry.config(show=passwordchar)
            add_validation(widget=entry, func=validatePassword)
        elif validation == "isEmail":
            add_regex_validation(
                widget=entry, pattern="^[a-zA-Z0-9._%+-]+@(?:student\.newinti\.edu\.my|newinti\.edu\.my)$")
        elif validation == "isContactNo":
            add_regex_validation(
                widget=entry, pattern="^(\+?6?01)[02-46-9]-*[0-9]{7}$|^(\+?6?01)[1]-*[0-9]{8}$")
        elif validation == "isCaptcha":
            add_validation(widget=entry, func=validateCaptcha)
        else:
            # just not blank
            add_regex_validation(widget=entry, pattern="^.*\S.*$")
            pass

        self.widgetsDict[classname] = entry
        self.updateWidgetsDict(root=root)
        return entry

    def textElement(self, imagepath, xpos, ypos, classname=None, buttonFunction=None, root=None, relief=FLAT, fg=BLACK, bg=WHITE, font=SFPRO, text=None, size=40, isPlaced=False, yIndex=0, xoffset=0) -> Label | Button:
        classname = classname.replace(" ", "").lower()
        # ~~~ ADD TEXT TO IMAGE FUNCTIONS ~~~
        h = fg.lstrip("#")
        textcolor = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        im = Image.open(imagepath)
        font = ImageFont.truetype(font, size)
        draw = ImageDraw.Draw(im)
        # print(im.size) # Returns (width, height) tuple
        xcoord, ycoord = im.size
        # push the text to the right by xoffset pixels
        xcoord = im.size[0]/20 + xoffset*20
        y_offset = size * yIndex  # Vertical offset based on font size and index
        ycoord = ycoord/2 - (font.getbbox(text)[3]/2) + y_offset
        draw.text((xcoord, ycoord), text, font=font, fill=textcolor)
        self.imageDict[f"{classname}"] = ImageTk.PhotoImage(im)
        image = self.imageDict[f"{classname}"]
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        widthspan = int(image.width()/20)
        heightspan = int(image.height()/20)
        columnarg = int(xpos/20)
        rowarg = int(ypos/20)
        placedwidth = int(widthspan*20)
        placedheight = int(heightspan*20)

        if buttonFunction:
            if isPlaced:
                element = Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                                 relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False)
                element.place(x=xpos, y=ypos, width=placedwidth,
                              height=placedheight)
            else:
                element = Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                                 relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False)
                element.grid(row=rowarg, column=columnarg,
                             rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        else:
            if isPlaced:
                element = Label(root, image=image, relief=relief, bg=bg,
                                width=1, height=1, name=classname, autostyle=False)
                element.place(x=xpos, y=ypos, width=placedwidth,
                              height=placedheight)
            else:
                element = Label(root, image=image, relief=relief, bg=bg,
                                width=1, height=1, name=classname, autostyle=False)
                element.grid(row=rowarg, column=columnarg,
                             rowspan=heightspan, columnspan=widthspan, sticky=NSEW)

        self.updateWidgetsDict(root=root)
        element.grid_propagate(False)
        return element

    def hex_to_rgb(self, hexstring) -> tuple:
        # Convert hexstring to integer
        hexint = int(hexstring[1:], 16)
        # Extract Red, Green, and Blue values from integer using bit shifting
        red = hexint >> 16
        green = (hexint >> 8) & 0xFF
        blue = hexint & 0xFF
        colorkey = win32api.RGB(red, green, blue)
        return colorkey

    def togglethewindowbar(self) -> None:
        self.deletethewindowbar() if self.state() == "normal" else self.showthewindowbar()

    def deletethewindowbar(self) -> None:
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("zoomed")

    def showthewindowbar(self) -> None:
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style |= WS_CAPTION | WS_THICKFRAME
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("normal")
