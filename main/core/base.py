import wx
import wx.glcanvas as glcanvas
import sys
from OpenGL.GL import glViewport
from core.input import Input


class BaseCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, screenSize=[800, 600]):
        attrib_list = [
            glcanvas.WX_GL_RGBA,
            glcanvas.WX_GL_DOUBLEBUFFER,
            glcanvas.WX_GL_DEPTH_SIZE, 16, 0
        ]
        
        # Create GLCanvas with OpenGL context
        super().__init__(parent, -1, attribList=attrib_list)

        self.context = glcanvas.GLContext(self)
        self.running = True
        self.init = False

        # Event bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_TIMER, self.on_timer)

        # Timer for update loop (60 FPS)
        self.timer = wx.Timer(self)
        self.timer.Start(16)  # ~60 FPS

        # Manage input
        self.input = Input()  

    def initialize(self):
        """Override in subclass."""
        pass

    def update(self):
        """Override in subclass."""
        pass

    def on_paint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.initialize()
            self.init = True

        # Run the update method
        self.update()

        # Swap buffers to display the rendered image
        self.SwapBuffers()

    def on_size(self, event):
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)

    def on_timer(self, event):
        # Trigger paint event to continuously update the scene
        self.Refresh()



class BaseFrame(wx.Frame):
    def __init__(self, title="Graphics Window"):
        super().__init__(None, title=title, size=(800, 600))
        
        # Initialize input handler
        self.input = Input()
        
        # Bind key and mouse events
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_mouse_up)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_mouse_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_scroll)

        # Timer for continuous updates
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer.Start(16)  # Roughly 60 FPS

        # Show the window
        self.Show()


    def on_timer(self, event):
        self.input.update()
        self.update()

    def on_key_down(self, event):
        self.input.on_key_down(event)

    def on_key_up(self, event):
        self.input.on_key_up(event)

    def on_mouse_down(self, event):
        self.input.on_mouse_down(event)

    def on_mouse_up(self, event):
        self.input.on_mouse_up(event)

    def on_mouse_scroll(self, event):
        self.input.on_mouse_scroll(event)

    def update(self):
        """ This should be overridden in your child class """
        pass


class BaseApp(wx.App):
    def OnInit(self):
        self.frame = wx.Frame(None, title="Graphics Window", size=(800, 600))
        self.canvas = BaseCanvas(self.frame)
        self.frame.Show()
        return True