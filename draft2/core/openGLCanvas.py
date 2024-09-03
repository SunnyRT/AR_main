import wx
import wx.glcanvas as wxcanvas
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from core.openGLUtils import *
from core.mesh import Mesh
import math
import numpy as np



class OpenGLCanvas(wxcanvas.GLCanvas):
    def __init__(self, parent):
        attribs = [wxcanvas.WX_GL_RGBA, 
                   wxcanvas.WX_GL_DOUBLEBUFFER, 
                   wxcanvas.WX_GL_DEPTH_SIZE, 16, 0]
        super().__init__(parent, -1, attribList=attribs)

        
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.SetCurrent(self.context)


        self.mesh = Mesh("D:\\sunny\\Codes\\IIB_project\\data\\summer\\fitted_otic_capsule.ply")


        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.scene_rotate = np.identity(4, 'f')
        self.zoom = 1.0
        self.depth_offset = 1000.0

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)



    def on_paint(self, event):
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.init_gl()
            self.init = True
        self.render()
        # self.SwapBuffers()

    def on_size(self, event):
        size = self.GetClientSize()
        if size.width == 0 or size.height == 0:
            return
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, size.width / size.height, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        event.Skip()


    def on_mouse(self, event):
        """Handle mouse events for interactive manipulation of 3D scene, 
        including rotation, panning, and zooming."""
        self.SetCurrent(self.context)

        if event.ButtonDown(): # recode the current mouse position when a mouse button is pressed
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging(): 
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            # Calculate the change in mouse movement
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            # Depending on which mouse button is pressed, rotate, pan or zoom
            if event.LeftIsDown(): # rotate the scene about the x and y axes
                glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown(): # rotate the scene about the z axis
                glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown(): # pan the scene along the x and y axes
                self.pan_x += x
                self.pan_y -= y
            # Update the scene rotation matrix according to the mouse movement
            glMultMatrixf(self.scene_rotate)
            glGetFloatv(GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            # to trigger redraw of the scene (require reinitialisation of the OpenGL context)
            # for fundamental changes (e.g. window resize, etc)
            self.init = False 

        # Adjust the zoom level based on the mouse wheel rotation
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False 

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False 

        self.Refresh()  # triggers the on_paint() event to update display with new transformations, does not affext the OpenGL rendering context (initialization logic)
    
    
    def init_gl(self):

        size = self.GetClientSize()
        self.SetCurrent(self.context)

        glViewport(0, 0, size.width, size.height)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, size.width/size.height, 10, 1000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)  # Use default depth function
        glClearDepth(1.0)  # Clear depth to maximum value
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Clear the screen to black
        # OpenGLUtils.printSystemInfo()
        self.mesh.initialize()


    def render(self):
        self.SetCurrent(self.context) # set the current OpenGL rendering context
        if not self.init: # call init_gl() to configure the OpenGL rendering context
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()


        # Apply camera transformations (pan, zoom, rotate)
        glTranslatef(self.pan_x, self.pan_y, -self.zoom * 10.0)  # Pan and Zoom
        glMultMatrixf(self.scene_rotate)  # Apply rotation matrix
        glScalef(self.zoom, self.zoom, self.zoom)  # Apply zoom factor


        
        self.mesh.render()

        glFlush()
        self.SwapBuffers()