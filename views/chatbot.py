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
from basewindow import gridGenerator
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
        self.trackingNumber = IntVar()
        self.trackingNumber.set(0)
        self.createFrames()
        self.createElements()
        self.engine = "gpt-3.5-turbo"
        self.encoding = tiktoken.encoding_for_model(self.engine)
        self.max_tokens = 3096
        self.messages = [
            {'role': 'system', 'content': "You are a helpful assistant."},
            # {'role': 'user', 'content': "What's 1+1? Answer in one word."},
            # {'role': "assistant", "content": "Two."},
            # {'role': "user", "content": "Excellent, I think you're ready to take over the world now."},
        ]
        self.mainentry = self.controller.ttkEntryCreator(
            xpos=540, ypos=800, width=840, height=80,
            root=self, classname="chatbotinputboxentry"
        )
        self.mainentry.bind(
            "<Return>", lambda event: self.renderChat(self.messages)
        )
        self.mainentry = self.controller.widgetsDict["chatbotinputboxentry"]

    def createFrames(self):
        self.controller.frameCreator(
            root=self, framewidth=1680, frameheight=680,
            classname="chatscrframehost", xpos=120, ypos=100, bg=NICEBLUE
        )
        self.scrolledframehost = self.controller.widgetsDict["chatscrframehost"]

    def createElements(self):
        self.staticImgLabels = [
            (r"Assets\Chatbot\ChatbotBg.png", 0, 0, "ChatbotBgLabel", self),
        ]
        self.controller.settingsUnpacker(self.staticImgLabels, "label")
        self.staticBtns = [
            (r"Assets\Chatbot\sendmessage.png", 1420, 800, "sendChatBtn",
             self, lambda: self.renderChat(self.messages)),
            (r"Assets\Chatbot\resetchatbtn.png", 880, 0, "resetChatBtn",
             self, lambda: self.resetChat()),
        ]
        self.controller.settingsUnpacker(self.staticBtns, "button")
        self.scrolledframehost.tkraise()
        heightOfFrame = (self.trackingNumber.get()) * 220
        if heightOfFrame < 640:
            heightOfFrame = 640
        self.mainScrolledFrame = ScrolledFrame(
            self.scrolledframehost, width=1600, height=heightOfFrame, name="conversationframe",
            autohide=True, bootstyle="primary-round", padding=0
        )
        self.mainScrolledFrame.place(x=40, y=20, width=1600, height=640)

        self.scrollingVar = IntVar()
        self.scrollingVar.set(0)
        self.scrollingToggle = ttk.Checkbutton(
            master=self, variable=self.scrollingVar, onvalue=1, offvalue=0,
            command=lambda: self.toggleScrollingDown(), width=300, compound="text",
            bootstyle="danger-round-toggle", text="Click to toggle forced scrolling down"
        )
        self.scrollingToggle.place(x=1520, y=20, width=300, height=40)

    def resetChat(self):
        self.messages.clear()
        self.messages = [
            {'role': 'system', 'content': "You are a helpful assistant."},
        ]
        self.scrolledframehost.tkraise()
        self.mainScrolledFrame = ScrolledFrame(
            self.scrolledframehost, width=1600, height=640, name="conversationframe",
            autohide=True, bootstyle="primary-round", padding=0
        )
        self.mainScrolledFrame.place(x=40, y=20, width=1600, height=640)

    """
    example conversation:
    messages = [
        {'role': 'system', 'content': "You are a helpful assistant."},
        {'role': 'user', 'content': "What's 1+1? Answer in one word."},
        {'role': "assistant", "content": "Two."},
        {'role': "user", "content": "Excellent, I think you're ready to take over the world now."},
    ]
    # Example of an OpenAI ChatCompletion request with stream=False
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        stream=False # this is the default, but we set it explicitly here
    )
    return
    helper functions to write:
    def update_chat(messageslist, role, content):
        messageslist.append({'role': role, 'content': content})
        return messageslist
    
    def get_chatgpt_response(messages):
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
        )
        return response['choices'][0]['message']['content']

    initializing a predefined list of messages:
    # preprompt is accessed using messages[-1]
    messages = [
        {'role': 'system', 'content': "You are a helpful assistant."},
    ]
        
    the flow of the chat should be: 
    user_input = self.mainentry.get()
    messages = update_chat(messages, 'user', user_input)
    gpt_response = get_chatgpt_response(messages)
    messages = update_chat(messages, 'assistant', gpt_response)
    self.mainentry.delete(0, END)

    send this messages to a renderChat function that takes in the list of dictionaries and renders them
    according to the role of the message
    """

    def api_CallStream(self, engine, history):
        response = openai.ChatCompletion.create(
            model=engine,
            messages=history,
            stream=True
        )
        return response['choices'][0]['message']['content']

    def renderChatStream(self, messages: list):
        initCoords = (340, 20)
        messages.append({'role': 'user', 'content': self.mainentry.get()})
        streamedResponse = self.api_CallStream(self.engine, messages)
        # Create variables to collect the stream of chunks
        collected_chunks = []
        collected_messages = []
        # Iterate over the stream of events
        for chunk in streamedResponse:
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk['choices'][0]['delta']  # extract the message
            collected_messages.append(chunk_message)  # save the message

    def api_Call(self, engine, history):
        response = openai.ChatCompletion.create(
            model=engine,
            messages=history,
        )
        # print(response)
        return response['choices'][0]['message']['content']

    def renderChat(self, messages: list):
        # messages = [
        #     {'role': 'system', 'content': "You are a helpful assistant."},
        # ]
        # messages is a list of dictionaries initialized in __init__
        # it's an attribute for the entire class
        # passing in self.messages as the argument for this function
        messages.append({'role': 'user', 'content': self.mainentry.get()})
        # print(f"Messages before API call: {messages}")
        self.mainentry.delete(0, END)
        heightOfFrame = (len(messages) - 1) * 220 + 20
        if heightOfFrame < 640:
            heightOfFrame = 640
        self.mainScrolledFrame.config(height=heightOfFrame)
        fr = self.mainScrolledFrame
        initCoords = (340, 20)
        # iterate over previous list of dictionaries
        for msgDict in messages:
            role = msgDict['role']
            content = msgDict['content']
            if role != "system":
                if role == "user":
                    st = self.scrolledTextCreator(
                        xpos=initCoords[0], ypos=initCoords[1], width=1000, height=200,
                        root=fr, classname=f"message", isPlaced=True, bootstyle=INFO
                    )
                    st.text.config(fg=BLACK, font=("SF Pro Medium", 16))
                elif role == "assistant":
                    st = self.scrolledTextCreator(
                        xpos=initCoords[0], ypos=initCoords[1], width=1000, height=200,
                        root=fr, classname=f"message",
                        isPlaced=True, bootstyle=SECONDARY
                    )
                    st.text.config(fg=BLACK, font=("SF Pro Medium", 16))
                st.text.insert(END, content)
                st.text.config(state=DISABLED)
                initCoords = (initCoords[0], initCoords[1] + 220)
                print(f"Coordinates after iteration: {initCoords}")
        gpt_response = self.api_Call(self.engine, messages)
        messages.append({'role': 'assistant', 'content': gpt_response})
        heightOfFrame = (len(messages) - 1) * 220 + 20
        if heightOfFrame < 640:
            heightOfFrame = 640
        self.mainScrolledFrame.config(height=heightOfFrame)
        # print(f"Messages after API call: {messages}")
        # get the last message, which is the gpt_response
        lastMessageDict = messages[-1]
        # print(f"Last message dict: {lastMessageDict}")
        lastMessageRole = lastMessageDict['role']
        lastMessageContent = lastMessageDict['content']
        if lastMessageRole == "assistant":
            st = self.scrolledTextCreator(
                xpos=initCoords[0], ypos=initCoords[1], width=1000, height=200,
                root=fr, classname=f"message", isPlaced=True, bootstyle=SECONDARY
            )
            st.text.config(fg=BLACK, font=("SF Pro Medium", 16))
            st.text.insert(END, lastMessageContent)
            st.text.config(state=DISABLED)
        print(f"Coordinates after API call: {initCoords}")

    """
    # Example of an OpenAI ChatCompletion request with stream=True
    # https://platform.openai.com/docs/guides/chat

    # a ChatCompletion request
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': "What's 1+1? Answer in one word."}
        ],
        temperature=0,
        stream=True  # this time, we set stream=True
    )

    for chunk in response:
        print(chunk)
        {
        "choices": [
            {
            "delta": {
                "role": "assistant"
            },
            "finish_reason": null,
            "index": 0
            }
        ],
        "created": 1677825464,
        "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
        "model": "gpt-3.5-turbo-0301",
        "object": "chat.completion.chunk"
        }
        {
        "choices": [
            {
            "delta": {
                "content": "\n\n"
            },
            "finish_reason": null,
            "index": 0
            }
        ],
        "created": 1677825464,
        "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
        "model": "gpt-3.5-turbo-0301",
        "object": "chat.completion.chunk"
        }
        {
        "choices": [
            {
            "delta": {
                "content": "2"
            },
            "finish_reason": null,
            "index": 0
            }
        ],
        "created": 1677825464,
        "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
        "model": "gpt-3.5-turbo-0301",
        "object": "chat.completion.chunk"
        }
        {
        "choices": [
            {
            "delta": {},
            "finish_reason": "stop",
            "index": 0
            }
        ],
        "created": 1677825464,
        "id": "chatcmpl-6ptKyqKOGXZT6iQnqiXAH8adNLUzD",
        "model": "gpt-3.5-turbo-0301",
        "object": "chat.completion.chunk"
        }
    """

    def imagineWriteText(self, openAIresponse: openai.ChatCompletion.create, content: list, history: list):
        collected_chunks = []
        collected_messages = []
        for chunk in openAIresponse:
            collected_chunks.append(chunk)
            try:
                chunk_message = chunk["choices"][0]["delta"]["content"]
            except:
                chunk_message = chunk["choices"][0]["delta"]
            collected_messages.append(chunk_message)
            history.append({"role": "assistant", "content": chunk_message})
        fullrep = []
        for chunk_message in collected_messages:
            if type(chunk_message) == str:
                result = "".join(chunk_message).strip()
                result = result.replace("\n", "")
                fullrep.append(result)
                print(f"result: {result}")
        print(collected_messages)
        content.append(openAIresponse["choices"][0]["message"]["content"])

    def toggleScrollingDown(self):
        def scrollDown():
            if self.scrollingVar.get() == 1:
                self.mainScrolledFrame.yview("moveto", 1.0)
                self.mainScrolledFrame.after(100, scrollDown)
            else:
                return
        scrollDown()

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

