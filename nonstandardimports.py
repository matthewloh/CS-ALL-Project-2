import jwt
import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Threading')
from System.Windows.Forms import Control
from System.Threading import Thread,ApartmentState,ThreadStart  
# ~~~~~ The Ability to Make a Colorkey in a Canvas / Widget Transparent Using Windows Only ~~~~~ #
# https://stackoverflow.com/questions/53021603/how-to-make-a-tkinter-canvas-background-transparent
import win32api
import win32con
import win32gui
from PIL import Image, ImageTk, ImageSequence, ImageDraw, ImageFont