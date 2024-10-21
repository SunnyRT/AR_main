from main.core.InputCanvas import InputCanvas, InputFrame
import wx

# Check input with basic debugging
class TestCanvas(InputCanvas):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene_initialized = False

    def initialize(self):
        print("Initializing program...")
        self.scene_initialized = True

    def update(self):
        # # Update input
        # self.update_input()

        # Check if scene is initialized before rendering
        if not self.scene_initialized:
            self.initialize_scene()


        # Debug printing
        if len(self.keysDownList) > 0: 
            print("Keys down: ", self.keysDownList) 

        # if len(self.keysPressedList) > 0:
            # print("Keys pressed: ", self.keysPressedList)

        if len(self.keysUpList) > 0:
            print("Keys up: ", self.keysUpList)

        # if self.mouseDelta != (0, 0):
        #     print("Mouse delta: ", self.mouseDelta)

        if self.mouseScroll != 0:
            print("Mouse scroll: ", self.mouseScroll)

        # Typical usage example
        if self.isKeyDown("space"):
            print("The 'space' bar was just pressed down.") 
        
        if self.isKeyPressed("right"):
            print("The 'right' key is currently being pressed.")



class TestFrame(InputFrame):  # Extend the existing BaseFrame
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