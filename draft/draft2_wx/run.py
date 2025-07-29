import wx

from core.openGLCanvas import OpenGLCanvas


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.canvas = OpenGLCanvas(self)

        self.SetTitle("3D Model and 2D Image Display")
        self.Show(True)


if __name__ == "__main__":
    app = wx.App()
    frame = MainWindow(None, title = "3D Model and 2D Image Display", size=(800,600))
    app.MainLoop()