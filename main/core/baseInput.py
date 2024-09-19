
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

    def update_input(self):
        self.keysDownList = []
        self.keysUpList = []
        self.mouseDelta = (0, 0)
        self.mouseScroll = 0

        # Calculate mouse delta (movement)
        newMousePos = wx.GetMousePosition()
        self.mouseDelta = (newMousePos[0] - self.mousePos[0], newMousePos[1] - self.mousePos[1])
        self.mousePos = newMousePos

    def on_key_down(self, event):
        keyCode = event.GetKeyCode()
        keyName = self.get_key_name(keyCode)
        if keyName not in self.keysPressedList:
            self.keysDownList.append(keyName)
            self.keysPressedList.append(keyName)
    
    

