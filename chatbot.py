import openai
import tiktoken
from static import *
import ctypes
from tkinter import *
# A drop in replacement for ttk that uses bootstrap styles
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame, ScrolledText
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.validation import add_text_validation, add_regex_validation, validator, add_validation, add_option_validation
from dotenv import load_dotenv
from prisma import Prisma
from elementcreator import gridGenerator
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
import bcrypt
from datetime import datetime, timedelta, timezone
# TODO: please stop formatting my imports you're breaking my code
# this contains my pywin32 imports, PIL imports, pythonnet
from nonstandardimports import *
import pendulum
from pendulum import timezone
# from main import Window


class Chatbot(Canvas):
    def __init__(self, parent, controller
                #    : Window
                 ):
        Canvas.__init__(self, parent, width=1, height=1,
                        bg=WHITE, name="chatbot", autostyle=False)
        self.controller = controller
        self.parent = parent
        gridGenerator(self, 96, 46, WHITE)
        self.staticImgLabels = [
            (r"Assets\Chatbot\ChatbotBg.png", 0, 0, "ChatbotBgLabel", self),
        ]

        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        # self.webview2creator(xpos=60, ypos=140, framewidth=1800, frameheight=700,
        #                                 root=self, classname="chatbotwebview2", url="http://localhost:5555/")

        self.engine = "gpt-3.5-turbo"
        self.encoding = tiktoken.encoding_for_model(self.engine)
        self.max_tokens = 3096
        self.slice_index = 0
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        self.filename = self.timestamp
        self.search_window_attributes = {}
        self.search_window = None
        # inputbox
        # focus inputbox
        # welcome message of chatbot
        message = "Hello, I am a chatbot. I am here to help you with your queries. Please type your query in the box below."
        fr = self.scrolledFrameCreator(
            xpos=120, ypos=100, width=1680, height=680,
            root=self, classname="conversationframe",
        )
        self.controller.labelCreator(
            imagepath=r"Assets\Chatbot\internalbg.png", xpos=0, ypos=0,
            classname="internalbgofchatbot", root=fr,
        )
        ne = self.scrolledTextCreator(
            xpos=60, ypos=20, width=720, height=200,
            root=fr, classname="exampleofchatbotreply",
            bootstyle=SUCCESS, msg=message
        )
        two = self.scrolledTextCreator(
            xpos=900, ypos=240, width=720, height=200,
            root=fr, classname="exampleofuserreply",
            bootstyle=SECONDARY
        )
        ne.tk.call("raise", ne._w)
        two.tk.call("raise", two._w)
        # using a for loop to emulate a conversation between the user and the chatbot
        self.controller.ttkEntryCreator(
            xpos=540, ypos=800, width=840, height=80,
            root=self, classname="chatbotinputboxentry"
        )

    def api_call(engine, history):
        # https://platform.openai.com/docs/api-reference/models
        return openai.ChatCompletion.create(
            model=engine,

        )
    def scrolledFrameCreator(self, xpos=0, ypos=0, width=0, height=0, root=None, classname=None):
        classname = classname.replace(" ", "").lower()
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        scrolledFrame = ScrolledFrame(
            master=root, name=classname, bootstyle=SUCCESS,
            autohide=True,
        )
        scrolledFrame.grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
        )
        scrolledFrame.grid_propagate(False)
        inside = scrolledFrame.container
        # # inside.config(width=1, height=1)
        # inside.grid(rowspan=heightspan, columnspan=widthspan,
        #             sticky=NSEW)
        inside.grid_propagate(False)
        gridGenerator(scrolledFrame, widthspan, heightspan, NICEBLUE)
        gridGenerator(inside, widthspan, heightspan, "#ff9d9d")
        return scrolledFrame

    def scrolledTextCreator(self,
                            xpos=0, ypos=0, width=0, height=0,
                            root=None, classname=None, bootstyle=SUCCESS,
                            msg=None):
        classname = classname.replace(" ", "").lower()
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        scrolledText = ScrolledText(
            master=root, bootstyle=bootstyle, height=1, name=classname, width=1,
            autohide=True,
        )
        internaltext = scrolledText.text
        internaltext.config(
            font=("Arial", 16),
        )
        if msg:
            internaltext.insert(END, msg)
        # scrolledText.text.insert("end", msg)
        scrolledText.grid(
            row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
        )
        scrolledText.grid_propagate(False)
        return scrolledText

    def send_message(self):
        # inputcontent = f"{self.inputbox.get('1.0', 'end-1c').strip()}"
        # self.history.append({"role": "user", "message": inputcontent})
        # save file to db
        # update the chatbox
        # call GPT API
        # t = threading.Thread(target=self.call_gpt, args = (self.engine, self.history))
        pass

    def webview2creator(self, xpos=None, ypos=None, framewidth=None, frameheight=None, root=None, classname=None, bgcolor=WHITE, relief=FLAT, font=("Avenir Next", 16), url=None):
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        widthspan = int(framewidth / 20)
        heightspan = int(frameheight / 20)
        classname = classname.lower().replace(" ", "")
        navigationbar = Frame(root, width=1, height=1,
                              bg=bgcolor, relief=FLAT, name=f"{classname}navbar")
        gridGenerator(navigationbar, widthspan, 3, WHITE)
        navigationbar.grid(row=rowarg-3, column=columnarg,
                           rowspan=3, columnspan=widthspan, sticky=NSEW)
        frame = WebView2(parent=root, width=1, height=1,
                         url=url, name=classname, bg=bgcolor)
        frame.grid(row=rowarg, column=columnarg, rowspan=heightspan,
                   columnspan=widthspan, sticky=NSEW)
        # binding a callback button to go back in javascript

        def goBack():
            frame.evaluate_js("window.history.back();")
            defocus()
        # binding a callback button to go forward in javascript

        def goForward():
            print(frame.get_url())
            frame.evaluate_js("window.history.forward();")
            defocus()

        def getUrlandGo():
            try:
                url = self.controller.widgetsDict[f"{classname}urlentry"].get()
                frame.load_url(url)
            except:
                url = f"https://www.google.com/search?q={self.controller.widgetsDict[f'{classname}urlentry'].get()}"
                frame.load_url(url)
            defocus()
            ctypes.windll.user32.SetForegroundWindow(
                ctypes.windll.kernel32.GetConsoleWindow())

        def gotoGoogle():
            self.controller.widgetsDict[f"{classname}urlentry"].focus_set()
            frame.load_url("https://www.google.com/")
            defocus()
            ctypes.windll.user32.SetForegroundWindow(
                ctypes.windll.kernel32.GetConsoleWindow())

        def toggleFullscreen():
            frame.evaluate_js(
                "document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen();")
            defocus()
            self.controller.widgetsDict[f"{classname}urlentry"].focus_set()

        def defocus():
            # getting the current window using the window handle, then simulating a refocusing
            # frame.evaluate_js("document.activeElement.blur();")
            ctypes.windll.user32.SetForegroundWindow(
                ctypes.windll.kernel32.GetConsoleWindow())
            self.controller.widgetsDict[f"{classname}urlentry"].focus_set()
            self.controller.focus_set()

        self.controller.buttonCreator(r"Assets\Chatbot\Backbutton.png", 0, 0, classname=f"{classname}backbutton",
                                      buttonFunction=lambda: goBack(),
                                      root=navigationbar)
        self.controller.buttonCreator(r"Assets\Chatbot\Forwardbutton.png", 80, 0, classname=f"{classname}forwardbutton",
                                      buttonFunction=lambda: goForward(),
                                      root=navigationbar)
        self.controller.entryCreator(160, 0, 760, 60, navigationbar, classname=f"{classname}urlentry",
                                     bg=bgcolor)
        self.controller.widgetsDict[f"{classname}urlentry"].insert(0, url)
        self.controller.widgetsDict[f"{classname}urlentry"].bind(
            "<Return>", lambda event: getUrlandGo())
        self.controller.buttonCreator(r"Assets\Chatbot\EnterAndGoButton.png", 920, 0, classname=f"{classname}enterandgobutton",
                                      buttonFunction=lambda: getUrlandGo(),
                                      root=navigationbar)
        self.controller.buttonCreator(r"Assets\Chatbot\GoogleButton.png", 1060, 0, classname=f"{classname}googlebutton",
                                      buttonFunction=lambda: gotoGoogle(),
                                      root=navigationbar)
        self.controller.buttonCreator(r"Assets\Chatbot\Togglefullscreen.png", 1120, 0, classname=f"{classname}fullscreenbutton",
                                      buttonFunction=lambda: toggleFullscreen(),
                                      root=navigationbar)

        self.controller.updateWidgetsDict(root=root)
