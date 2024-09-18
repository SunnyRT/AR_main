import wx
import wx.glcanvas as glcanvas
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np

# Vertex and fragment shaders for modern OpenGL
vertex_shader = """
#version 330 core
layout(location = 0) in vec3 position;
void main()
{
    gl_Position = vec4(position, 1.0);
}
"""

fragment_shader = """
#version 330 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 0.0, 0.0, 1.0); // Red color
}
"""

class MyGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        attrib_list = [glcanvas.WX_GL_RGBA, glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_DEPTH_SIZE, 16, 0]
        super().__init__(parent, -1, attribList=attrib_list)

        self.context = glcanvas.GLContext(self)
        self.init = False

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        
    def init_gl(self):
        """Initialize modern OpenGL: Compile shaders, setup VBO and VAO."""
        self.shader = compileProgram(
            compileShader(vertex_shader, GL_VERTEX_SHADER),
            compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        )
        
        # Define vertices for a triangle
        self.vertices = np.array([
            [-0.5, -0.5, 0.0],
            [ 0.5, -0.5, 0.0],
            [ 0.0,  0.5, 0.0]
        ], dtype=np.float32)

        # Create a Vertex Array Object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Create a Vertex Buffer Object (VBO)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Specify the layout of the vertex data
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
    def on_paint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.init_gl()
            self.init = True
        
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use the shader program
        glUseProgram(self.shader)
        
        # Bind the VAO (the triangle)
        glBindVertexArray(self.vao)
        
        # Draw the triangle
        glDrawArrays(GL_TRIANGLES, 0, 3)
        
        # Swap buffers to display the rendered frame
        self.SwapBuffers()
        
    def on_size(self, event):
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)
        self.Refresh()

class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxPython Modern OpenGL Example", size=(800, 600))
        self.canvas = MyGLCanvas(self)

        # Create the MenuBar
        menubar = wx.MenuBar()

        # Create the File menu and its items
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "&Open")
        file_menu.Append(wx.ID_SAVE, "&Save")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "&Exit")

        # Create the Help menu and its items
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")

        # Add menus to the MenuBar
        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")

        # Attach the MenuBar to the Frame
        self.SetMenuBar(menubar)

        # Bind the menu items to events
        self.Bind(wx.EVT_MENU, self.on_menu)

        self.Show()

    def on_menu(self, event):
        """Event handler for menu items."""
        event_id = event.GetId()
        if event_id == wx.ID_EXIT:
            self.Close()
        elif event_id == wx.ID_ABOUT:
            wx.MessageBox("This is a wxPython Modern OpenGL Example", "About", wx.OK | wx.ICON_INFORMATION)
        elif event_id == wx.ID_OPEN:
            wx.MessageBox("Open menu clicked", "Open", wx.OK | wx.ICON_INFORMATION)
        elif event_id == wx.ID_SAVE:
            wx.MessageBox("Save menu clicked", "Save", wx.OK | wx.ICON_INFORMATION)

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.SetTopWindow(self.frame)
        return True

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()
