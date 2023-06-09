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
from elementcreator import gridGenerator
from tkwebview2.tkwebview2 import WebView2, have_runtime, install_runtime
from datetime import datetime, timedelta, timezone
# TODO: please stop formatting my imports you're breaking my code
# this contains my pywin32 imports, PIL imports, pythonnet
from nonstandardimports import *
import pendulum
from pendulum import timezone
from basewindow import ElementCreator
# from main import Window


class Chatbot(Canvas):
    def __init__(self, parent, controller: ElementCreator):
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
        userPromptInfo = "Enter your preprompt, i.e: \"Be helpful\""

        self.botwelcome = self.scrolledTextCreator(
            xpos=180, ypos=120, width=720, height=200,
            root=self, classname=f"botwelcome",
        )
        self.userInfo = self.scrolledTextCreator(
            xpos=1020, ypos=260, width=720, height=200,
            root=self, classname=f"userprompt",
        )

        # expand the mainscrolledframe
        self.botwelcome.text.insert("end", message)
        self.userInfo.text.insert("end", userPromptInfo)
        self.controller.ttkEntryCreator(
            xpos=540, ypos=800, width=840, height=80,
            root=self, classname="chatbotinputboxentry"
        )
        inputentry = self.controller.widgetsDict["chatbotinputboxentry"]
        self.staticBtns = [
            (r"Assets\Chatbot\sendmessage.png", 1420, 800, "sendChatBtn",
             self, lambda: self.testFrontEnd(int(inputentry.get()))),
        ]
        self.controller.settingsUnpacker(self.staticBtns, "button")
        self.currentPairs = IntVar()
        self.currentPairs.set(1)  # for the first pair of inputs

    def testFrontEnd(self, pairsofinputs: int):
        # REPLIES
        yposBotMsg = 20
        yposUserMsg = 160
        # a pair of responses 1 from chatbot and 1 from user
        # chatbot on left, user on right
        # the total combined height of the text of the chatbot and user is 340 pixels
        self.currentPairs.set(1)
        self.currentPairs.set(self.currentPairs.get() + pairsofinputs)
        heightOfFrame = (self.currentPairs.get()) * 340
        rowspanFrame = int(heightOfFrame / 21)
        self.mainScrolledFrame = ScrolledFrame(
            self, width=1, height=1, name="conversationframe",
            autohide=True,
        )
        self.mainScrolledFrame.grid_propagate(False)
        # https://platform.openai.com/docs/guides/gpt/chat-completions-api
        # c, r, cs, rs = int(120/20), int(100/20), int(1680/20), int(680/20)
        # self.mainScrolledFrame.grid(
        #     row=r, column=c, rowspan=rs, columnspan=cs, sticky="nsew"
        # )
        self.mainScrolledFrame.place(x=120, y=100, width=1680, height=680)
        self.botwelcome.grid_remove()
        self.userInfo.grid_remove()
        print(self.mainScrolledFrame.winfo_width(), "<- width")
        print(heightOfFrame, "<- heightOfFrame")
        print(rowspanFrame, "<- rowspanFrame")
        print(self.mainScrolledFrame.winfo_height(), "<- height")
        print(self.currentPairs.get())
        gridGenerator(self.mainScrolledFrame, int(
            1680/20), rowspanFrame, WHITE)
        fr = self.mainScrolledFrame
        for i in range(0, pairsofinputs):
            st1 = self.scrolledTextCreator(
                xpos=60, ypos=yposBotMsg, width=720, height=200,
                root=fr, classname=f"exampleofchatbotreply{i}", isPlaced=True,
            )
            st2 = self.scrolledTextCreator(
                xpos=900, ypos=yposUserMsg, width=720, height=200,
                root=fr, classname=f"exampleofuserreply{i}", isPlaced=True,
            )
            st1.text.insert("end", f"Chatbot reply {i+1}")
            st2.text.insert("end", f"User reply {i+1}")
            yposBotMsg += 280
            yposUserMsg += 280
            self.controller.updateWidgetsDict(st1)
            self.controller.updateWidgetsDict(st2)
        # convoNum = input
        # heightIndex = convoNum * 380 + 180 # 380 is total pixels of one chatbot reply and one user reply
        # newHeight = int(heightIndex / 20)
        # fr.grid(rowspan=newHeight, sticky=NSEW)
        # gridGenerator(fr.container, int(1680/20), newHeight, "#56cc9d")
        # inputentry = self.controller.widgetsDict["chatbotinputboxentry"]
        # inputentry.delete(0, END)
        # inputentry.insert(0, "")
        # inputentry.tk.call("focus", inputentry._w)

    def api_call(user_response):
        # https://platform.openai.com/docs/api-reference/models
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_response},
            ],
            stream=True,
            max_tokens=512,
        )
        print(completion)
        bot_response = completion.choices[0].message.content
        print(bot_response)
        return bot_response

    def scrolledTextCreator(self,
                            xpos=0, ypos=0, width=0, height=0,
                            root=None, classname=None, bootstyle=SUCCESS,
                            msg=None, isPlaced=False):
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
        if isPlaced:
            scrolledText.place(x=xpos, y=ypos, width=width, height=height)
        else:
            scrolledText.grid(
                row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
            )
            scrolledText.grid_propagate(False)
        return scrolledText

    def scrolledFrameCreator(self, xpos=0, ypos=0, width=0, height=0, root=None, classname=None, isPlaced=False):
        classname = classname.replace(" ", "").lower()
        widthspan = int(width / 20)
        heightspan = int(height / 20)
        columnarg = int(xpos / 20)
        rowarg = int(ypos / 20)
        scrolledFrame = ScrolledFrame(
            master=root, name=classname, bootstyle=SUCCESS,
            autohide=True,
        )
        if isPlaced:
            scrolledFrame.place(x=xpos, y=ypos, width=width, height=height)
        else:
            scrolledFrame.grid(
                row=rowarg, column=columnarg, rowspan=heightspan, columnspan=widthspan, sticky=NSEW
            )
        scrolledFrame.grid_propagate(False)
        inside = scrolledFrame.container
        # # inside.config(width=1, height=1)
        inside.grid(rowspan=heightspan, columnspan=widthspan,
                    sticky=NSEW)
        inside.grid_propagate(False)
        gridGenerator(scrolledFrame, widthspan, heightspan, NICEBLUE)
        gridGenerator(inside, widthspan, heightspan, "#56cc9d")
        return scrolledFrame

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
