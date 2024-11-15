
import wx
from core.base import BaseCanvas, BaseFrame

class InputCanvas(BaseCanvas):
    def __init__(self, parent, screenSize=[800,600]):
        super().__init__(parent, screenSize)
        

        # Input management
        self.keysDownList = []
        self.keysPressedList = []
        self.keysUpList = []
        self.mouseLeftDown = False
        self.mouseMiddleDown = False
        self.mouseRightDown = False
        self.mousePos = wx.GetMousePosition()
        self.mouseDelta = (0, 0)
        self.mouseScroll = 0
        self.shiftMouseScroll = 0
        self.ctrlMouseScroll = 0
        self.altMouseScroll = 0

        # Bind additional input events
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_mouse_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_scroll)


        # initialize two variables (near and far clipping planes)
        self.n = None
        self.f = None

    def update_input(self):

        self.keysDownList = []
        self.keysUpList = []
        self.mouseDelta = (0, 0)
        self.mouseScroll = 0
        self.shiftMouseScroll = 0
        self.ctrlMouseScroll = 0
        self.altMouseScroll = 0

        # Calculate mouse delta (movement)
        newMousePos = wx.GetMousePosition()
        self.mouseDelta = (newMousePos[0] - self.mousePos[0], newMousePos[1] - self.mousePos[1])
        self.mousePos = newMousePos


    def on_timer(self, event):
        self.update_input()
        event.Skip()  # Allow the event to propagate
        self.Refresh()  # Force a paint event

    def on_key_down(self, event):
        keyCode = event.GetKeyCode()
        keyName = self.get_key_name(keyCode)
        if keyName not in self.keysPressedList:
            self.keysDownList.append(keyName)
            self.keysPressedList.append(keyName)
            self.Refresh()
    
    def on_key_up(self, event):
        keyCode = event.GetKeyCode()
        keyName = self.get_key_name(keyCode)
        if keyName in self.keysPressedList:
            self.keysUpList.append(keyName)
            self.keysPressedList.remove(keyName)
            self.Refresh()

    def on_mouse_down(self, event):
        if event.LeftIsDown():
            self.mouseLeftDown = True
        if event.MiddleIsDown():
            self.mouseMiddleDown = True
        if event.RightIsDown():
            self.mouseRightDown = True

    def on_mouse_up(self, event):
        if not event.LeftIsDown():
            self.mouseLeftDown = False
        if not event.MiddleIsDown():
            self.mouseMiddleDown = False
        if not event.RightIsDown():
            self.mouseRightDown = False

    def on_mouse_scroll(self, event):
        scroll = event.GetWheelRotation()
        scroll_dir = 1 if scroll > 0 else -1

        if event.ShiftDown():
            self.shiftMouseScroll = scroll_dir
        elif event.ControlDown():
            self.ctrlMouseScroll = scroll_dir
        elif event.AltDown():
            self.altMouseScroll = scroll_dir
        else:
            self.mouseScroll = scroll_dir  
        self.Refresh()  # Force a paint event

    # Function to check key states
    def isKeyDown(self, keyName):
        return keyName in self.keysDownList

    def isKeyPressed(self, keyName):
        return keyName in self.keysPressedList

    def isKeyUp(self, keyName):
        return keyName in self.keysUpList

    # Functions to check mouse states
    def isMouseLeftDown(self):
        return self.mouseLeftDown

    def isMouseMiddleDown(self):
        return self.mouseMiddleDown

    def isMouseRightDown(self):
        return self.mouseRightDown

    def getMousePos(self):
        return self.mousePos

    def getMouseDelta(self):
        return self.mouseDelta

    def getMouseScroll(self):
        return self.mouseScroll
    
    def getShiftMouseScroll(self):
        return self.shiftMouseScroll

    def getCtrlMouseScroll(self):
        return self.ctrlMouseScroll
    
    def getAltMouseScroll(self):
        return self.altMouseScroll

    def get_key_name(self, keyCode):
        """ Translate the wx key code into a string representation """
        keyMap = {
            wx.WXK_SPACE: "space",
            wx.WXK_UP: "up",
            wx.WXK_DOWN: "down",
            wx.WXK_LEFT: "left",
            wx.WXK_RIGHT: "right",
            ord('W'): "w",
            ord('A'): "a",
            ord('S'): "s",
            ord('D'): "d",
            ord('Q'): "q",
            ord('E'): "e",
            ord('R'): "r",
            ord('F'): "f",
            ord('T'): "t",
            ord('G'): "g",
            ord('I'): "i",
        }
        return keyMap.get(keyCode, f"key_{keyCode}")
    


class InputFrame(BaseFrame):
    def __init__(self, title="Graphics Window"):
        super().__init__(None, title=title, size=(800, 600))
        
        # TODO: Set up the canvas (to be implemented in subclass)
        self.canvas = InputCanvas(self)

        # Show the window
        self.Show()