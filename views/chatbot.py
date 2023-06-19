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
        # A host is used to remove the currently loaded scrolled frame using grid_remove()

        self.controller.frameCreator(
            root=self, framewidth=1680, frameheight=680,
            classname="chatscrframehost", xpos=120, ypos=100, bg=NICEBLUE
        )
        self.scrolledframehost = self.controller.widgetsDict["chatscrframehost"]
        self.currentPairs = IntVar()
        self.currentPairs.set(1)  # for the first pair of inputs
        heightOfFrame = (self.currentPairs.get()) * 220
        if heightOfFrame < 640:
            heightOfFrame = 640
        self.mainScrolledFrame = ScrolledFrame(
            self.scrolledframehost, width=1, height=heightOfFrame, name="conversationframe",
            autohide=True, bootstyle=PRIMARY, padding=0
        )
        self.mainScrolledFrame.place(x=40, y=20, width=1600, height=640)
        # self.controller.labelCreator(
        #     imagepath=r"Assets\DiscussionsView\scrolledframebg.png", xpos=0, ypos=0,
        #     classname="chatbotfrbg", root=self.mainScrolledFrame, isPlaced=True
        # )       
        # self.botwelcome = self.scrolledTextCreator(
        #     xpos=340, ypos=0, width=1000, height=200, bootstyle=WARNING,
        #     root=self.mainScrolledFrame, classname=f"botwelcome", isPlaced=True,
        # )

        # self.botwelcome.text.insert("end", message)
        # self.userInfo.text.insert("end", userPromptInfo)
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


    def testFrontEnd(self, numofinputs: int):
        # REPLIES
        # starting coordinates
        self.currentPairs.set(1)
        # self.currentPairs.set(self.currentPairs.get() + pairsofinputs)
        # heightOfFrame = (self.currentPairs.get()) * 440 - (pairsofinputs * 100)
        heightOfFrame = (1 + numofinputs) * 220 + 20
        if heightOfFrame < 640:
            heightOfFrame = 640
        print(heightOfFrame)
        self.mainScrolledFrame.destroy()
        self.mainScrolledFrame = ScrolledFrame(
            self.scrolledframehost, width=1, height=heightOfFrame, name="conversationframe",
            autohide=True, bootstyle=PRIMARY, padding=0
        )
        self.userInfo = self.scrolledTextCreator(
            xpos=340, ypos=20, width=1000, height=200, bootstyle=SECONDARY,
            root=self.mainScrolledFrame, classname=f"userprompt", isPlaced=True,
        )
        self.mainScrolledFrame.place(x=40, y=20, width=1600, height=640)
        # self.botwelcome.text.insert("end", "Hello, I am a chatbot. I am here to help you with your queries. Please type your query in the box below.")
        # self.userInfo.text.insert("end", "Enter your preprompt, i.e: \"Be helpful\"")
        fr = self.mainScrolledFrame
        replyCoordinates = (340, 240)
        replyCounter = 0
        #first reply is from the bot
        replymsg = "Bot reply 1"
        for i in range(numofinputs):
            st = self.scrolledTextCreator(
                xpos=replyCoordinates[0], ypos=replyCoordinates[1], width=1000, height=200,
                root=fr, classname=f"exampleofchatbotreply{i}", isPlaced=True,
            )
            st.text.insert("end", f"Chatbot reply {i+1}")
            replyCoordinates = (replyCoordinates[0], replyCoordinates[1] + 220)
        # for i in range(0, pairsofinputs):
        #     st1 = self.scrolledTextCreator(
        #         xpos=340, ypos=yposBotReply, width=1000, height=200,
        #         root=fr, classname=f"exampleofchatbotreply{i}", isPlaced=True,
        #     )
        #     st2 = self.scrolledTextCreator(
        #         xpos=340, ypos=yposUserMsg, width=1000, height=200,
        #         root=fr, classname=f"exampleofuserreply{i}", isPlaced=True,
        #     )
        #     st1.text.insert("end", f"Chatbot reply {i+1}")
        #     st2.text.insert("end", f"User reply {i+1}")
        #     yposBotReply += 220
        #     yposUserMsg += 220
        #     self.controller.updateWidgetsDict(st1)
        #     self.controller.updateWidgetsDict(st2)
        # # for i in range(0, pairsofinputs):
        # #     st1 = self.scrolledTextCreator(
        # #         xpos=60, ypos=yposBotMsg, width=720, height=200,
        # #         root=fr, classname=f"exampleofchatbotreply{i}", isPlaced=True,
        # #     )
        # #     st2 = self.scrolledTextCreator(
        # #         xpos=900, ypos=yposUserMsg, width=720, height=200,
        # #         root=fr, classname=f"exampleofuserreply{i}", isPlaced=True,
        # #     )
        # #     st1.text.insert("end", f"Chatbot reply {i+1}")
        # #     st2.text.insert("end", f"User reply {i+1}")
        # #     yposBotMsg += 280
        # #     yposUserMsg += 280
        # #     self.controller.updateWidgetsDict(st1)
        # #     self.controller.updateWidgetsDict(st2)
        # # convoNum = input
        # # heightIndex = convoNum * 380 + 180 # 380 is total pixels of one chatbot reply and one user reply
        # # newHeight = int(heightIndex / 20)
        # # fr.grid(rowspan=newHeight, sticky=NSEW)
        # # gridGenerator(fr.container, int(1680/20), newHeight, "#56cc9d")
        # # inputentry = self.controller.widgetsDict["chatbotinputboxentry"]
        # # inputentry.delete(0, END)
        # # inputentry.insert(0, "")
        # # inputentry.tk.call("focus", inputentry._w)

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
            autohide=True, padding=0, 
        )
        internaltext = scrolledText.text
        internaltext.config(
            font=("Arial", 16), wrap=WORD
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
