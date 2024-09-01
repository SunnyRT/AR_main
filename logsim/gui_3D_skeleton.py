"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""

import wx
import wx.glcanvas as wxcanvas
import numpy as np
import math
from OpenGL import GL, GLU, GLUT
from names import Names
from devices import Devices
from network import Network
from monitors import Monitors


class MyGLCanvas(wxcanvas.GLCanvas):
    def __init__(self, parent, devices, monitors):
        super().__init__(
            parent,
            -1,
            attribList=[
                wxcanvas.WX_GL_RGBA,
                wxcanvas.WX_GL_DOUBLEBUFFER,
                wxcanvas.WX_GL_DEPTH_SIZE,
                16,
                0,
            ],
        )
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Store devices and monitors for later use
        self.devices = devices
        self.monitors = monitors
        self.signal_data = {}

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, "f")

        # Initialise variables for zooming
        self.zoom = 1
        self.min_zoom = 0.8  # Set minimum zoom level

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(
            GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE, self.mat_diffuse
        )
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        # Set the clear color to white
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        GL.glTranslatef(0.0, 0.0, -self.depth_offset)
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self, signal_data=None, text=""):
        self.SetCurrent(self.context)
        if not self.init:
            self.init_gl()
            self.init = True

        if signal_data is not None:
            self.signal_data = signal_data

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw the signal traces
        self.draw_signal_traces()

        # Draw the monitor labels
        self.draw_monitor_labels()

        GL.glColor3f(0.0, 0.0, 0.0)  # Text is black
        self.render_text(text, 0, 0, 210)

        GL.glFlush()
        self.SwapBuffers()

    def draw_signal_traces(self):
        """Draw the signal traces in 3D."""
        y_base = 300
        y_offset = 100
        z_base = 0  # Keep z_base fixed for all signal traces

        half_width = 10
        half_depth = 5
        cuboid_height = 26

        for (device_id, output_id), signals in self.signal_data.items():
            # Draw x-axis and y-axis for the signal trace
            self.draw_axes(y_base, z_base, len(signals))

            x = -250  # Start position for the signal trace
            for signal in signals:
                if signal == 1:  # High signal level
                    height = cuboid_height
                elif signal == 0:  # Low signal level
                    height = 1
                else:
                    height = (
                        cuboid_height / 2
                    )  # Intermediate value for undefined signals

                GL.glColor3f(1.0, 0.7, 0.5)  # signal trace is beige
                self.draw_cuboid(
                    x, y_base, z_base, half_width, half_depth, height
                )
                x += 20
            y_base -= y_offset  # Move to the next trace

    def draw_axes(self, y_base, z_base, num_cycles):
        """Draw the x-axis and y-axis for the signal traces."""
        # Draw y-axis labels (0 and 1)
        self.render_text("0", -270, y_base, z_base)  # Position of 0 label
        self.render_text("1", -270, y_base + 25, z_base)  # Position of 1 label

        # Draw x-axis and cycle numbers
        GL.glColor3f(0.5, 0.5, 0.5)  # Grey color for the axis
        GL.glBegin(GL.GL_LINES)
        GL.glVertex3f(-260, y_base - 5, z_base)  # Start of x-axis
        x_end = -260 + 20 * num_cycles
        GL.glVertex3f(
            x_end, y_base - 5, z_base
        )  # End of x-axis, dynamic based on signal length
        GL.glEnd()

        # Draw cycle numbers along the x-axis
        x = -260
        for cycle in range(num_cycles + 1):
            self.render_text(
                str(cycle), x, y_base - 15, z_base
            )  # Adjust y position as needed
            x += 20

    def draw_monitor_labels(self):
        """Draw labels for the monitors."""
        y_base = 300
        y_offset = 100

        for device_id, output_id in self.signal_data.keys():
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            GL.glColor3f(0.0, 0.0, 0.0)
            self.render_text(monitor_name, -320, y_base, 10)
            y_base -= y_offset

    def get_y_coordinate(self, signal):
        """Convert signal level to y-coordinate."""
        if signal == 1:  # High signal level
            return 10
        elif signal == 0:  # Low signal level
            return 0
        return 5  # Intermediate value for undefined signals

    def draw_cuboid(self, x_pos, y_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        # Bottom face
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos + half_depth)
        # Top face
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos + half_depth)
        # Left face
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos + half_depth)
        # Right face
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos + half_depth)
        # Front face
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos - half_depth)
        # Back face
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event):
        self.SetCurrent(self.context)
        if not self.init:
            self.init_gl()
            self.init = True
        self.render()

    def on_size(self, event):
        self.init = False

    def on_mouse(self, event):
        self.SetCurrent(self.context)
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= 1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())
            )
            if self.zoom < self.min_zoom:
                self.zoom = self.min_zoom
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = f"Negative mouse wheel rotation. Zoom is now: {self.zoom}"
        if event.GetWheelRotation() > 0:
            self.zoom /= 1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())
            )
            if self.zoom < self.min_zoom:
                self.zoom = self.min_zoom
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = f"Positive mouse wheel rotation. Zoom is now: {self.zoom}"

        self.Refresh()

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == "\n":
                y_pos -= 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def update_devices(self, devices):
        """Update the devices and names used by the canvas."""
        self.devices = devices


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """

    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.text_box = wx.TextCtrl(
            self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER
        )

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(
                "Logic Simulator\nCreated by Mojisola Agboola\n2017",
                "About Logsim",
                wx.ICON_INFORMATION | wx.OK,
            )

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.canvas.render()

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        self.canvas.render()

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        self.canvas.render()
