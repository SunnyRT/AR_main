import wx

class Input(object):

    def __init__(self):
        # Has the user quit the application?
        self.quit = False

        # Lists to store key states
        self.keysDownList = [] # FIXME: this does not seem to be working well????
        self.keysPressedList = []
        self.keysUpList = []

        # Variables to store mouse state
        self.mouseLeftDown = False
        self.mouseMiddleDown = False
        self.mouseRightDown = False
        self.mousePos = wx.GetMousePosition()
        self.mouseDelta = (0, 0)
        self.mouseScroll = 0

    def update(self):
        """Reset discrete key and mouse states"""
        self.keysDownList = []
        self.keysUpList = []
        self.mouseDelta = (0, 0)
        self.mouseScroll = 0

        # Calculate mouse delta (movement)
        newMousePos = wx.GetMousePosition()
        self.mouseDelta = (newMousePos[0] - self.mousePos[0], newMousePos[1] - self.mousePos[1])
        self.mousePos = newMousePos

    # Handle key down event
    def on_key_down(self, event):
        keyCode = event.GetKeyCode()
        keyName = self.get_key_name(keyCode)
        if keyName not in self.keysPressedList:
            self.keysDownList.append(keyName)
            self.keysPressedList.append(keyName)

    # Handle key up event
    def on_key_up(self, event):
        keyCode = event.GetKeyCode()
        keyName = self.get_key_name(keyCode)
        if keyName in self.keysPressedList:
            self.keysUpList.append(keyName)
            self.keysPressedList.remove(keyName)

    # Handle mouse down event
    def on_mouse_down(self, event):
        if event.LeftIsDown():
            self.mouseLeftDown = True
        if event.MiddleIsDown():
            self.mouseMiddleDown = True
        if event.RightIsDown():
            self.mouseRightDown = True

    # Handle mouse up event
    def on_mouse_up(self, event):
        if not event.LeftIsDown():
            self.mouseLeftDown = False
        if not event.MiddleIsDown():
            self.mouseMiddleDown = False
        if not event.RightIsDown():
            self.mouseRightDown = False

    # Handle mouse scroll event
    def on_mouse_scroll(self, event):
        scroll = event.GetWheelRotation()
        if scroll > 0:
            self.mouseScroll = 1  # Scroll up
        elif scroll < 0:
            self.mouseScroll = -1  # Scroll down

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

    # A simple helper to map key codes to human-readable key names
    def get_key_name(self, keyCode):
        key_map = {
            wx.WXK_SPACE: "space",
            wx.WXK_RIGHT: "right",
            wx.WXK_LEFT: "left",
            wx.WXK_UP: "up",
            wx.WXK_DOWN: "down",
            # Add more key mappings here as needed
        }
        return key_map.get(keyCode, f"key_{keyCode}")  # Return raw keyCode if not mapped
