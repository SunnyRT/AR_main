import wx
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *

class MyGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1)
        self.context = glcanvas.GLContext(self)
        self.init = False
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
    
    def InitGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        self.init = True

    def OnSize(self, event):
        self.SetCurrent(self.context)
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)
        self.OnDraw()

    def OnPaint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
        self.OnDraw()

    def OnDraw(self):
        size = self.GetClientSize()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # First Viewport (Left Side)
        glViewport(0, 0, size.width // 2, size.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (size.width // 2) / size.height, 1, 100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 1, 0)  # Camera for first viewport
        self.DrawScene()

        # Second Viewport (Right Side)
        glViewport(size.width // 2, 0, size.width // 2, size.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (size.width // 2) / size.height, 1, 100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 5, 5, 0, 0, 0, 0, 1, 0)  # Camera for second viewport
        self.DrawScene()

        self.SwapBuffers()

    def DrawScene(self):
        # Draw a simple box (cube) at the origin
        glBegin(GL_QUADS)

        # Front face (z = 1.0)
        glColor3f(1.0, 0.0, 0.0)  # Red
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)

        # Back face (z = -1.0)
        glColor3f(0.0, 1.0, 0.0)  # Green
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)

        # Left face (x = -1.0)
        glColor3f(0.0, 0.0, 1.0)  # Blue
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)

        # Right face (x = 1.0)
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)

        glEnd()

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 600))
        self.canvas = MyGLCanvas(self)
        self.Show()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "OpenGL Multiple Viewports Example")
        self.SetTopWindow(frame)
        return True

app = MyApp()
app.MainLoop()
