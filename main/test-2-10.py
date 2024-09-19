from core.base import BaseCanvas, BaseFrame
import wx

# Check input with basic debugging
class TestCanvas(BaseCanvas):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene_initialized = False

    def initialize(self):
        print("Initializing program...")
        self.scene_initialized = True

    def update(self):
        # Check if scene is initialized before rendering
        if not self.scene_initialized:
            self.initialize_scene()

        self.input.update()

        # Debug printing
        if len(self.input.keysDownList) > 0: 
            print("Keys down: ", self.input.keysDownList) # FIXME:???

        # if len(self.input.keysPressedList) > 0:
        #     print("Keys pressed: ", self.input.keysPressedList)

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



class TestFrame(BaseFrame):  # Extend the existing BaseFrame
    def __init__(self, parent, title, size):
        # Call the wx.Frame constructor with title and size
        wx.Frame.__init__(self, parent, title=title, size=size)

        # Initialize the TestCanvas as the main canvas
        self.canvas = TestCanvas(self)
        self.Show()

  # Instantiate the wxPython app and run it
class TestApp(wx.App):
    def OnInit(self):
        self.frame = TestFrame(None, title="Movement Rig Test", size=(800, 600))  # Pass size and title here
        self.SetTopWindow(self.frame)
        return True  

if __name__ == "__main__":
    app = TestApp(False)
    app.MainLoop()