import wx # GUI toolkit for python
import wx.glcanvas as wxcanvas # to embed OpenGL rendering within wxPython window
import numpy as np
import math
from OpenGL import GL, GLU
# from OpenGL.GL import *
import glfw
import plyfile
from PIL import Image



class MyGLCanvas(wxcanvas.GLCanvas): 
    # responsible to setting up the OpenGL context， 
    # initializing OpenGL parameters, 
    # and rendering graphcis

    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window (typically the main frame).
    mesh_file: path to the .ply file to load the 3D model.
    image_file: path to the image file to load the 2D texture.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    """

    def __init__(self, parent, mesh_file, image_file): # TODO: !!!
        """Initialise canvas properties and useful variables."""

        # call the superclass constructor to initialise the canvas with specific attributes
        # that define the color depth and presence of a depth buffer
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])

        # Double buffering is a rendering technique that reduces flickering
        # which involves 2 buffers: one is displayed while the other is being rendered. When the rendering is done, the buffers are swapped.

        if not glfw.init():
            raise Exception("GLFW can't be initialized")
        
        
        self.init = False
        self.context = wxcanvas.GLContext(self) # create a new OpenGL rendering context associate with this canvas


        # self.mesh_alpha = 0.5
        self.img_alpha = 0.5
        self.img_size = 200.0

        # Load the 3D mesh and 2D texture
        self.mesh_vertices, self.mesh_faces, self.mesh_normals = self.load_ply(mesh_file)
        self.texture_id = self.load_texture(image_file)

        # Load the shader program
        self.shader_program = self.create_shader_program("shader_vert.glsl", "shader_frag.glsl")

        self.setup_buffers()

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas: painting, resizing, mouse interations
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)



    def load_ply(self, path_ply):
        """ Load mesh vertices and faces from a .ply file."""
        self.SetCurrent(self.context)
        plydata = plyfile.PlyData.read(path_ply)
        
        # Extract vertices
        vertices = np.array([(vertex['x'], vertex['y'], vertex['z']) for vertex in plydata['vertex'].data])
        centroid = np.mean(vertices, axis=0)
        print(f"Centroid of mesh: {centroid}")
        vertices -= centroid # center the mesh at the origin

        # Extract faces
        faces = np.array([face[0] for face in plydata['face'].data]) # vertex indices for each face
        
        # If normals are available
        if 'nx' in plydata['vertex'].data.dtype.names:
            normals = np.array([(vertex['nx'], vertex['ny'], vertex['nz']) for vertex in plydata['vertex'].data])


        print(f"Vertices: {vertices.shape}, Faces: {faces.shape}, Normals: {normals.shape}")
        return vertices, faces, normals


    def load_texture(self, path_img):
        """ Load a texture image from an image file and return its OpenGL texture ID."""
        try:
            self.SetCurrent(self.context)
            
            image = Image.open(path_img)
            image = image.transpose(Image.FLIP_TOP_BOTTOM) # OpenGL expects the image to be flipped in y-axis
            image_data = image.convert("RGBA").tobytes()

            texture_id = GL.glGenTextures(1)
            if not texture_id:
                raise ValueError("Failed to generate texture ID")
            # print(f"Generated texture ID: {texture_id}")

            
            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, image.width, image.height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_data)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            return texture_id
        
        except Exception as e:
            print(f"Error loading texture: {e}")
            return None

    
    # def set_meshalpha(self, alpha):
    #     """ Set the transparency of the mesh."""
    #     self.mesh_alpha = alpha

    def set_imgalpha(self, alpha):
        """ Set the transparency of the image."""
        self.img_alpha = alpha

    def set_imgsize(self, size):
        """ Set the size of the image."""
        self.img_size = size


        

    def create_shader_program(self, shader_vert_path, shader_frag_path):
        """ Compile shaders and link them into a shader program."""
        shader_vert = self.compile_shader(shader_vert_path, GL.GL_VERTEX_SHADER)
        shader_frag = self.compile_shader(shader_frag_path, GL.GL_FRAGMENT_SHADER)

        shader_program = GL.glCreateProgram()
        GL.glAttachShader(shader_program, shader_vert)
        GL.glAttachShader(shader_program, shader_frag)
        GL.glLinkProgram(shader_program)

        # query the linking status
        linkSuccess = GL.glGetProgramiv(shader_program, GL.GL_LINK_STATUS)
        if not linkSuccess:
            errorMessage = GL.glGetProgramInfoLog(shader_program)
            errorMessage = '\n' + errorMessage.decode('utf-8')
            GL.glDeleteProgram(shader_program)
            raise Exception(f"Error linking shader program: {errorMessage}")
        GL.glDeleteShader(shader_vert)
        GL.glDeleteShader(shader_frag)

        # Validate the shader program
        GL.glValidateProgram(shader_program)
        if GL.glGetProgramiv(shader_program, GL.GL_VALIDATE_STATUS) != GL.GL_TRUE:
            raise Exception(f"Error validating shader program")
        
        return shader_program


    def compile_shader(self, shader_path, shader_type):
        """ Compile a shader from a file."""
        with open(shader_path, 'r') as file:
            shader_src = file.read()

        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, shader_src)
        GL.glCompileShader(shader)

        # query the compilation status
        compileSuccess = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
        if not compileSuccess:
            errorMessage = GL.glGetShaderInfoLog(shader)
            errorMessage = '\n' + errorMessage.decode('utf-8')
            GL.glDeleteShader(shader)
            raise Exception(f"Error compiling shader: {errorMessage}")

        return shader


    def setup_buffers(self):
        """ Set up the vertex array object (VAO) and vertex buffer object (VBO) 
            which hold the vertex data, configure how data is interpreted by shaders,
            for rendering."""
        self.vao = GL.glGenVertexArrays(1) # generate and bind a vertex array object (VAO)
        GL.glBindVertexArray(self.vao)

        self.vbo = GL.glGenBuffers(1) # generate and bind a vertex buffer object (VBO) 
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        # Upload the vertex data self.mesh_vertices to the VBO (GPU)
        # GL_STATIC_DRAW: data will be uploaded (modified) once and drawn many times
        GL.glBufferData(GL.GL_ARRAY_BUFFER, self.mesh_vertices.nbytes, self.mesh_vertices, GL.GL_STATIC_DRAW)
        
        self.ebo = GL.glGenBuffers(1) # generate and bind an element buffer object (EBO)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, self.mesh_faces.nbytes, self.mesh_faces, GL.GL_STATIC_DRAW)

        # Position attribute
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 3 * np.dtype(np.float32).itemsize, None)
        GL.glEnableVertexAttribArray(0)

        # Normal attribute
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 3 * np.dtype(np.float32).itemsize, None)
        GL.glEnableVertexAttribArray(1)


        

        GL.glBindVertexArray(0) # unbind VAO
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0) # unbind VBO
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0) # unbind EBO





    def init_gl(self):
        """ Configure and initializes OpenGL settings 
        and prepares the rendering context with desired parameters 
        such as lighting, shading, and depth testing."""

        # Viewport configuration
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height) # (0,0) is the coordinates for bottom-left corner of the window

        # Projection matrix setup: switch to projection matrix mode 
        # and setup a perspective projection
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        # Modelview matrix setup
        # Rendering State Configuration
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH) # GL_SMOOTH for Gouraud shading, GL_FLAT for flat shading
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)

        # GL.glEnable(GL.GL_COLOR_MATERIAL)
        # GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST) # for proper occlusion handling
        # GL.glEnable(GL.GL_NORMALIZE)

        
        # GL.glEnable(GL.GL_LIGHTING) # enable lighting
        # GL.glEnable(GL.GL_LIGHT0)
        # GL.glEnable(GL.GL_LIGHT1)

        # light_pos = [50.0, 50.0, 50.0, 1.0]
        # GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, light_pos)
        # GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        # GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        # GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        # GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        # GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        # GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        # GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        # GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        # GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_SPECULAR, self.mat_specular)
        # GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_SHININESS, self.mat_shininess)
        # GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE,
        #                 self.mat_diffuse)
        # GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # # Enable texture mapping
        # GL.glEnable(GL.GL_TEXTURE_2D)
        # if self.texture_id:
        #     GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        # else:
        #     raise ValueError("Texture ID is invalid. Cannot bind texture.")

        # # Viewing transformation - set the viewpoint back from the scene
        # GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # # Modelling transformation - pan, zoom and rotate (initially set to identity)
        # GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        # GL.glMultMatrixf(self.scene_rotate)
        # GL.glScalef(self.zoom, self.zoom, self.zoom)







    def render(self):
        # Handle actual rendering of the scene. 
        # Clear the buffer and draw all objects onto the canvas.
        """Handle all drawing operations."""
        self.SetCurrent(self.context) # set the current OpenGL rendering context
        if not self.init: # call init_gl() to configure the OpenGL rendering context
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear the color and depth buffers to prepare for new frame rendering
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        

        GL.glUseProgram(self.shader_program)
        GL.glPointSize(10)                  # TODO: debug
        GL.glDrawArrays(GL.GL_POINTS, 0, 1) # TODO: debug
        

        # # Set uniforms
        # model = np.identity(4, dtype=np.float32)
        # view = np.identity(4, dtype=np.float32)
        # projection = np.identity(4, dtype=np.float32) # FIXME: orthographic vs perspective projection

        # model_loc = GL.glGetUniformLocation(self.shader_program, "model")
        # view_loc = GL.glGetUniformLocation(self.shader_program, "view")
        # proj_loc = GL.glGetUniformLocation(self.shader_program, "projection")
        # # light_pos_loc = GL.glGetUniformLocation(self.shader_program, "lightPos")
        # # view_pos_loc = GL.glGetUniformLocation(self.shader_program, "viewPos")
        # # light_color_loc = GL.glGetUniformLocation(self.shader_program, "lightColor")
        # # object_color_loc = GL.glGetUniformLocation(self.shader_program, "objectColor")
        # # alpha_loc = GL.glGetUniformLocation(self.shader_program, "alpha")


        # GL.glUniformMatrix4fv(model_loc, 1, GL.GL_FALSE, model)
        # GL.glUniformMatrix4fv(view_loc, 1, GL.GL_FALSE, view)
        # GL.glUniformMatrix4fv(proj_loc, 1, GL.GL_FALSE, projection)
        # # GL.glUniform3fv(light_pos_loc, 1, np.array([50.0, 50.0, 50.0], dtype=np.float32))
        # # GL.glUniform3fv(view_pos_loc, 1, np.array([0.0, 0.0, 100.0], dtype=np.float32))
        # # GL.glUniform3fv(light_color_loc, 1, np.array([1.0, 1.0, 1.0], dtype=np.float32))
        # # GL.glUniform3fv(object_color_loc, 1, np.array([1.0, 0.7, 0.5], dtype=np.float32))
        # # GL.glUniform1f(alpha_loc, self.img_alpha)

        # GL.glBindVertexArray(self.vao)
        # GL.glDrawElements(GL.GL_TRIANGLES, len(self.mesh_faces)*3, GL.GL_UNSIGNED_INT, None)
        # GL.glBindVertexArray(0)

        GL.glUseProgram(0)



        # # Draw the 3D mesh 
        # GL.glPushMatrix()  # Apply scaling to enlarge the mesh 
        # GL.glScalef(10, 10, 10)
        # GL.glColor4f(1.0, 0.7, 0.5, 1.0) # FIXME: change transparency into self.mesh_alpha
        # GL.glBegin(GL.GL_TRIANGLES)
        # for face in self.mesh_faces:
        #     for vertex_id in face:
        #         normal = self.mesh_normals[vertex_id]
        #         GL.glNormal3fv(normal)
        #         GL.glVertex3fv(self.mesh_vertices[vertex_id])
        # GL.glEnd()
        # GL.glPopMatrix()
        # # GL.glDepthMask(GL.GL_TRUE)


        # # First pass: Draw the 2D image as a textured plane with transparency
        # GL.glDisable(GL.GL_LIGHTING)
        # GL.glEnable(GL.GL_BLEND)
        # GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # # GL.glEnable(GL.GL_DEPTH_TEST)
        # # GL.glDepthMask(GL.GL_FALSE)
        # GL.glDisable(GL.GL_CULL_FACE)  # Disable face culling
        # GL.glEnable(GL.GL_TEXTURE_2D)
        # GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)
        # GL.glColor4f(1.0, 1.0, 1.0, self.img_alpha)  # set the color to white with transparency
        

        # # Draw the image as a textured plane, visible from both sides
        # for sign in [-1, 1]:
        #     GL.glBegin(GL.GL_QUADS)
        #     GL.glTexCoord2f(0.0, 0.0)
        #     GL.glVertex3f(-self.img_size, -self.img_size, sign * 0.0) 
        #     GL.glTexCoord2f(1.0, 0.0)
        #     GL.glVertex3f(self.img_size, -self.img_size, sign * 0.0)
        #     GL.glTexCoord2f(1.0, 1.0)
        #     GL.glVertex3f(self.img_size, self.img_size, sign * 0.0)
        #     GL.glTexCoord2f(0.0, 1.0)
        #     GL.glVertex3f(-self.img_size, self.img_size, sign * 0.0)
        #     GL.glEnd()

        
        # GL.glDisable(GL.GL_TEXTURE_2D)
        # GL.glEnable(GL.GL_LIGHTING)
        # # GL.glDepthMask(GL.GL_TRUE)
        # GL.glDisable(GL.GL_BLEND)


        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush() # force execution of OpenGL commands in finite time
        # all programs should call glFlush whenever they count on having all of their previously issued commands completed. 
        self.SwapBuffers() # swap the front and back buffers to display the rendered image


    def on_paint(self, event):
        # Handle the paint event triggered when the canvas needs to be redrawn
        # e.g. when the window is resized or uncovered
        """Handle the paint event."""
        self.SetCurrent(self.context) # set the current OpenGL rendering context
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render() # render the scene

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        size = self.GetClientSize() # Get the new size of the canvas

        if size.width == 0 or size.height == 0:
            return
        
        self.SetCurrent(self.context) # set the current OpenGL rendering context
        GL.glViewport(0,0, size.width, size.height) # Reconfigure the viewport

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000) # angle, aspect ratio, n, f


        # Modelview matrix setup
        # Rendering State Configuration
        GL.glMatrixMode(GL.GL_MODELVIEW)
        self.init = False # trigger reinitialisation of the OpenGL context

        self.Refresh() # triggers the on_paint() event to update display with new transformations, does not affext the OpenGL rendering context (initialization logic)
        event.Skip() # allows the event to be processed by other event handlers
        



    def on_mouse(self, event):
        """Handle mouse events for interactive manipulation of 3D scene, 
        including rotation, panning, and zooming."""
        self.SetCurrent(self.context)

        if event.ButtonDown(): # recode the current mouse position when a mouse button is pressed
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging(): 
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            # Calculate the change in mouse movement
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            # Depending on which mouse button is pressed, rotate, pan or zoom
            if event.LeftIsDown(): # rotate the scene about the x and y axes
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown(): # rotate the scene about the z axis
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown(): # pan the scene along the x and y axes
                self.pan_x += x
                self.pan_y -= y
            # Update the scene rotation matrix according to the mouse movement
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
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
    
    
    
    def render_text(self, text, x_pos, y_pos, z_pos): # TODO:!!!!
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        # Here we need to implement a text rendering routine without GLUT.
        # Since GLFW does not provide a direct method, you might need to use a
        # library like FreeType or a custom bitmap font renderer.
        # This is a placeholder where you would render text:
        # render_bitmap_text(font, text, x_pos, y_pos, z_pos)

        GL.glEnable(GL.GL_LIGHTING)


class Gui(wx.Frame):
    # Set up the main application window, menu and controls
    # Integrates 'MyGLCanvas' class and provides interative controls and like spin control, run button, text box
    # Handle GUI events like menu selections and button clicks
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    mesh_file, image_file: paths to the input files.

    

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, mesh_file, image_file):
        """Initialise widgets and layout."""
        

        # Call the superclass constructor to initialise the main window with the specified title and size
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu bar
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar) # FIXME: menu bar occluded!!

        # Create canvas for drawing signals
        self.canvas = MyGLCanvas(self, mesh_file, image_file) 
    
        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        # self.meshalpha_slider = wx.Slider(self, wx.ID_ANY, 50, 0, 100, style=wx.SL_HORIZONTAL)
        self.imgalpha_slider = wx.Slider(self, wx.ID_ANY, 50, 0, 100, style=wx.SL_HORIZONTAL)
        self.imgsize_slider = wx.Slider(self, wx.ID_ANY, 200, 50, 500, style=wx.SL_HORIZONTAL)
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        # self.meshalpha_slider.Bind(wx.EVT_SLIDER, self.on_meshalpha_slider)
        self.imgalpha_slider.Bind(wx.EVT_SLIDER, self.on_imgalpha_slider)
        self.imgsize_slider.Bind(wx.EVT_SLIDER, self.on_imgsize_slider)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for organising the layout of the widgets within the window
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        # side_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Mesh transparency"), 1, wx.TOP, 10)
        # side_sizer.Add(self.meshalpha_slider, 1, wx.ALL, 5)
        side_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Image transparency"), 1, wx.TOP, 10)
        side_sizer.Add(self.imgalpha_slider, 1, wx.ALL, 5)
        side_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Image size"), 1, wx.TOP, 10)
        side_sizer.Add(self.imgsize_slider, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
        # self.Layout()



    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Platform for AR registration for cochlear implant surgery",
                          "About ARCIS", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        print(f"Spin control value: {spin_value}") # TODO: tb completed
        self.canvas.render()

    # def on_meshalpha_slider(self, event):
    #     """Handle the event when the user changes the mesh transparency slider."""
    #     meshalpha_value = self.meshalpha_slider.GetValue()
    #     self.canvas.set_meshalpha(meshalpha_value / 100.0)
    #     self.canvas.render()
    #     # print(f"Mesh transparency: {meshalpha_value}")

    def on_imgalpha_slider(self, event):
        """Handle the event when the user changes the image transparency slider."""
        imgalpha_value = self.imgalpha_slider.GetValue()
        self.canvas.set_imgalpha(imgalpha_value / 100.0)
        self.canvas.render()
        # print(f"Image transparency: {imgalpha_value}")
    
    def on_imgsize_slider(self, event):
        """Handle the event when the user changes the image size slider."""
        imgsize_value = self.imgsize_slider.GetValue()
        self.canvas.set_imgsize(imgsize_value)
        self.canvas.render()
        # print(f"Image size: {imgsize_value}")

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        print("Run registration!") # TODO: tb completed
        self.canvas.render()

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        print(f"Text box value: {text_box_value}") # TODO: tb completed
        self.canvas.render()
