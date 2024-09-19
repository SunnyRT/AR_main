from core.base import BaseCanvas, BaseFrame
import wx

# Check input with basic debugging
class TestCanvas(BaseCanvas):
    def __init__(self, parent):
        super().__init__(parent)


    def initialize(self):
        print("Initializing program...")
    

    def update(self):
        # Debug printing
        if len(self.input.keysDownList) > 0: 
            print("Keys down: ", self.input.keysDownList) # FIXME:???

        if len(self.input.keysPressedList) > 0:
            print("Keys pressed: ", self.input.keysPressedList)

        if len(self.input.keysUpList) > 0:
            print("Keys up: ", self.input.keysUpList)

        if self.input.mouseDelta != (0, 0):
            print("Mouse delta: ", self.input.mouseDelta)

        if self.input.mouseScroll != 0:
            print("Mouse scroll: ", self.input.mouseScroll)

        # Typical usage example
        if self.input.isKeyDown("space"):
            print("The 'space' bar was just pressed down.") # FIXME:???
        
        if self.input.isKeyPressed("right"):
            print("The 'right' key is currently being pressed.")


# Instantiate this class and run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = BaseFrame()
    test = TestCanvas(frame)
    app.MainLoop()
