from ctypes import windll
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.validation import add_text_validation, add_regex_validation, validator, add_validation, add_option_validation
from elementcreator import gridGenerator
from nonstandardimports import *
from tkinter import *
from static import * 
from PIL import Image, ImageTk, ImageSequence, ImageDraw, ImageFont
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
class ElementCreator(ttk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgetsDict = {}
        self.imageDict = {}
        self.imagePathDict = {}
    def createImageReference(self, imagepath: str, classname: str):
        # stores a key value pair of "classname" : "imagepath"
        self.imagePathDict[classname] = imagepath
        # creates a Tkinter image object
        image = ImageTk.PhotoImage(Image.open(imagepath))
        # stores a key value pair of "classname" : "image" to prevent garbage collection
        self.imageDict[classname] = image
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
    
    def buttonCreator(self, imagepath, xpos, ypos, classname=None, buttonFunction=None, root=None, relief=SUNKEN, overrideRelief=FLAT, pady=None, hasImage=True, bg=WHITE, isPlaced=False):
        """
        This function takes in the image path, x and y coordinates and the classname, which is necessary because the garbage collector
        will destroy the dictionary if not referenced to something. Thus, we pass it with an identifier string variable called classname.\n\n
        For example, :\n
        self.buttonCreator(r"Assets\Student Button.png", 240, 320, classname="StudentButton")
        will first return a dictionary with the following format:\n
        {'StudentButton': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 12, 'image': <PIL.ImageTk.PhotoImage object at 0x00000246A6976710>}}
        Then, we pass the classname to the inner dictionary, which gives us a label or button with the image we want.
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
        return self.widgetsDict[classname]

    def labelCreator(self, imagepath, xpos, ypos, classname=None, root=None, overrideRelief=FLAT, isPlaced=False, bg=WHITE):
        """
        This function takes in the image path, x and y coordinates and the classname, which is necessary because the garbage collector
        will destroy the image if not referenced to something. Thus, we pass it with an identifier string variable called classname.\n\n
        For example, :\n
        self.buttonCreator(r"Assets\Student Button.png", 240, 320, classname="StudentButton")
        will first return a dictionary with the following format:\n
        {'StudentButton': {'columnspan': 30, 'rowspan': 30, 'row': 16, 'column': 12, 'image': <PIL.ImageTk.PhotoImage object at 0x00000246A6976710>}}
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
            autostyle=False, bg = bg
        )
        if isPlaced:
            label.place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
        else:
            label.grid(row=rowarg, column=columnarg,
                       rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        self.updateWidgetsDict(root=root)

    def frameCreator(self, xpos, ypos, framewidth, frameheight, root=None, classname=None, bg=LIGHTYELLOW, relief=FLAT, imgSettings=None):
        classname = classname.replace(" ", "").lower()
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)

        Frame(root, width=1, height=1, bg=bg, relief=relief, name=classname, autostyle=False,).grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
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
        return self.widgetsDict[classname]

    def entryCreator(self, xpos, ypos, width, height, root=None, classname=None, bg=WHITE, relief=FLAT, fg=BLACK, textvariable=None, pady=None, font=("Avenir Next Medium", 16)):
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        self.updateWidgetsDict(root=root)
        Entry(root, bg=bg, relief=SOLID, font=font, fg=fg, width=1, name=classname, autostyle=False, textvariable=textvariable).grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW, pady=pady)
        self.updateWidgetsDict(root=root)
        for widgetname, widget in root.children.items():
            if widgetname == classname.lower().replace(" ", ""):
                widget.grid_propagate(False)
        return self.widgetsDict[classname]

    def canvasCreator(self, xpos, ypos, width, height, root, classname=None, bgcolor=WHITE, imgSettings=None, relief=FLAT, isTransparent=False, transparentcolor=TRANSPARENTGREEN):
        classname = classname.lower().replace(" ", "")
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        if imgSettings:
            listofimages = list(enumerate(imgSettings))
        Canvas(root, bg=bgcolor, highlightcolor=bgcolor, relief=FLAT, width=1, height=1, name=classname, highlightthickness=0, autostyle=False
               ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
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
        return self.widgetsDict[classname]

    def menubuttonCreator(self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), text=None, variable=None, listofvalues=None, command=None):
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
        menustyle = ttk.Style().configure(
            style=themename, font=("Helvetica", 10),
            background="#F9F5EB", foreground=BLACK, bordercolor="#78c2ad",
            relief="raised"
        )
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
        

    def ttkEntryCreator(self, xpos=None, ypos=None, width=None, height=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Helvetica", 16), validation=False, passwordchar="*", captchavar = None):
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
        self.frameCreator(xpos, ypos, width, height, root,
                          classname=f"{classname}hostfr", bg=bgcolor, relief=FLAT)
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

        frameref = self.widgetsDict[f"{classname}hostfr"]
        themename = f"{str(root).split('.')[-1]}.TEntry"
        ttk.Style().configure(
            style=themename, font=font, background=NICEBLUE, foreground=BLACK,
        )
        entry = ttk.Entry(frameref, bootstyle=PRIMARY,
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

    def textElement(self, imagepath, xpos, ypos, classname=None, buttonFunction=None, root=None, relief=FLAT, fg=BLACK, bg=WHITE, font=SFPRO, text=None, size=40, isPlaced=False, yIndex=0, xoffset=0):
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
                Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                       relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                       ).place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
            else:
                Button(root, image=image, cursor="hand2", command=lambda: buttonFunction() if buttonFunction else print("No function assigned to button"),
                       relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                       ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)
        else:
            if isPlaced:
                Label(root, image=image, relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                      ).place(x=xpos, y=ypos, width=placedwidth, height=placedheight)
            else:
                Label(root, image=image, relief=relief, bg=bg, width=1, height=1, name=classname, autostyle=False
                      ).grid(row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW)

        self.updateWidgetsDict(root=root)
        self.widgetsDict[classname].grid_propagate(False)
        return self.widgetsDict[classname]

    def hex_to_rgb(self, hexstring):
        # Convert hexstring to integer
        hexint = int(hexstring[1:], 16)
        # Extract Red, Green, and Blue values from integer using bit shifting
        red = hexint >> 16
        green = (hexint >> 8) & 0xFF
        blue = hexint & 0xFF
        colorkey = win32api.RGB(red, green, blue)
        return colorkey

    def togglethewindowbar(self):
        self.deletethewindowbar() if self.state() == "normal" else self.showthewindowbar()

    def deletethewindowbar(self):
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("zoomed")

    def showthewindowbar(self):
        hwnd: int = get_handle(self)
        style: int = GetWindowLongPtrW(hwnd, GWL_STYLE)
        style |= WS_CAPTION | WS_THICKFRAME
        SetWindowLongPtrW(hwnd, GWL_STYLE, style)
        self.state("normal")

    def resize(self):
        # the ratio of 1080p to the current screen size TODO: add aspect ratio sensing
        currentdimensions = (self.winfo_width(), self.winfo_height())
        # print(f"Current dimensions: {currentdimensions}")
        # how many times larger is the screensize than the original 1920 x 1080
        ratio = (currentdimensions[0] / 1920,
                 currentdimensions[1] / 1080)
        # take the original imagepath and resize it to the current screen size, then store it in the imageDict
        # only resize when the currentdimensions changes
        # do not constantly loop over the imageDict resizing the images
        if currentdimensions != (1920, 1080):
            for key, imagepath in self.imagePathDict.items():
                orgimg = Image.open(imagepath)
                orgimgwidth, orgimgheight = orgimg.size
                print(
                    f"Original image dimensions: {orgimgwidth} x {orgimgheight}, {key}")
                newimgwidth, newimgheight = int(
                    orgimgwidth * ratio[0]), int(orgimgheight * ratio[1])
                print(
                    f"New image dimensions: {newimgwidth} x {newimgheight}, {key}")
                image = ImageTk.PhotoImage(Image.open(imagepath).resize(
                    (newimgwidth, newimgheight), Image.Resampling.LANCZOS))
                self.imageDict[key] = image
                try:
                    self.widgetsDict[key].configure(image=image)
                except KeyError:
                    pass
        else:
            pass

    def resizeEvent(self, event):
        self.eventId = None
        if not (str(event.widget).split(".")[-1].startswith("!label")):
            if len(str(event.widget).split(".")) < 3:
                if event.widget == self:
                    self.resizeDelay = 100
                    if self.eventId:
                        self.after_cancel(self.eventId)
                    if self.state() == "zoomed":
                        self.eventId = self.after(
                            self.resizeDelay, self.resize)
                    elif self.state() == "normal":
                        self.eventId = self.after(
                            self.resizeDelay, self.resize)