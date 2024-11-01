import wx
import numpy as np
from core.InputCanvas import InputFrame, InputCanvas

from core_ext.texture import Texture
from material.textureMaterial import TextureMaterial


class GUIFrame(InputFrame):
    def __init__(self, parent, title, size):
        wx.Frame.__init__(self, parent, title=title, size=size)
        
        # # TODO: to be overried
        # self.canvas = InputCanvas(self)
        
        # self.create_menu_bar()
        # self.create_tool_panel()

        # # Use a box sizer to hold both the canvas and the tool panel
        # self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.sizer.Add(self.canvas, 1, wx.EXPAND)  # The OpenGL canvas fills most of the window
        # self.sizer.Add(self.tool_panel, 0, wx.EXPAND)  # Tool panel on the right side

        # # Set the sizer for the frame
        # self.SetSizer(self.sizer)
        # self.Show()     



    def create_menu_bar(self):
        menubar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_OPEN, "&Open")
        file_menu.Append(wx.ID_SAVE, "&Save")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit")

        # Help menu
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")

        # Append menus to the menu bar
        menubar.Append(file_menu, "&File")
        menubar.Append(help_menu, "&Help")

        # Bind menu events
        self.Bind(wx.EVT_MENU, self.on_menu)
        
        # Set the menu bar for the frame
        self.SetMenuBar(menubar)

    def create_tool_panel(self):
        """Creates the vertical tool panel on the right side of the window."""
        self.tool_panel = wx.Panel(self)
        tool_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a button
        self.projection_button = wx.Button(self.tool_panel, label="Projection")
        tool_sizer.Add(self.projection_button, 0, wx.ALL | wx.EXPAND, 10)  # Add spacing here
        self.Bind(wx.EVT_BUTTON, self.on_projection_click, self.projection_button)

        # Create a button
        self.register_button = wx.Button(self.tool_panel, label="Register")
        tool_sizer.Add(self.register_button, 0, wx.ALL | wx.EXPAND, 10)
        self.Bind(wx.EVT_BUTTON, self.on_register_click, self.register_button)



        """ Create a slider"""
        slider_sizer = wx.BoxSizer(wx.VERTICAL)
        dmax_label = wx.StaticText(self.tool_panel, label="d_max:")
        slider_sizer.Add(dmax_label, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5) 
        slider_with_labels_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Minimum value label
        min_label = wx.StaticText(self.tool_panel, label="0")
        slider_with_labels_sizer.Add(min_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Slider itself
        try:
            self.dmax_slider = wx.Slider(self.tool_panel, value=self.canvas.registrator.d_max, minValue=0, maxValue=20, style=wx.SL_HORIZONTAL)
        except:
            self.dmax_slider = wx.Slider(self.tool_panel, value=10, minValue=0, maxValue=20, style=wx.SL_HORIZONTAL)
        slider_with_labels_sizer.Add(self.dmax_slider, 0, wx.ALL | wx.EXPAND, 10)  # Add spacing here
        
        # Maximum value label
        max_label = wx.StaticText(self.tool_panel, label="20")
        slider_with_labels_sizer.Add(max_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Add the slider with labels sizer to the main slider sizer
        slider_sizer.Add(slider_with_labels_sizer, 0, wx.ALL | wx.EXPAND, 5)
        # Add the slider_sizer to the main tool panel sizer
        tool_sizer.Add(slider_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Bind the slider event
        self.Bind(wx.EVT_SLIDER, self.on_dmax_slider_change, self.dmax_slider)
        """ End of slider creation """



        # Create a text box
        self.textbox = wx.TextCtrl(self.tool_panel, style=wx.TE_PROCESS_ENTER)
        tool_sizer.Add(self.textbox, 0, wx.ALL | wx.EXPAND, 10)  # Add spacing here
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.textbox)

        tool_sizer.AddSpacer(10)

        # Create another button
        self.exit_button = wx.Button(self.tool_panel, label="Exit")
        tool_sizer.Add(self.exit_button, 0, wx.ALL | wx.EXPAND, 10)
        self.Bind(wx.EVT_BUTTON, self.on_exit_click, self.exit_button)

        tool_sizer.AddSpacer(10)

        """ Display Registration Parameters"""
        # Transformation matrix display(text)
        self.transform_matrix_text = wx.StaticText(
            self.tool_panel, 
            label="Transformation Matrix\n" + self.format_matrix(np.identity(4)),
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.transform_matrix_text, 0, wx.ALL | wx.EXPAND, 10)

        self.distance_text = wx.StaticText(
            self.tool_panel,
            label="Distance to Origin: 0.0",
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.distance_text, 0, wx.ALL | wx.EXPAND, 10)

        tool_sizer.AddSpacer(10)

        self.view_angle_text = wx.StaticText(
            self.tool_panel,
            label="View Angle: 0.0",
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.view_angle_text, 0, wx.ALL | wx.EXPAND, 10)

        # Set sizer for the tool panel
        self.tool_panel.SetSizer(tool_sizer)


    def update_tool_panel(self, transform_matrix, distance, view_angle):
        self.transform_matrix_text.SetLabel("Transformation Matrix:\n"+self.format_matrix(transform_matrix))
        self.distance_text.SetLabel(f"Distance to Origin:\n {distance:.2f}")
        self.view_angle_text.SetLabel(f"View Angle:\n {view_angle:.2f}")

    def format_matrix(self, matrix):
        """ Format the matrix as a string for display."""
        formatted_matrix = ""
        for row in matrix:
            formatted_matrix += " ".join(f"{val:.2f}" for val in row) + "\n"
        return formatted_matrix





    def on_menu(self, event):
        event_id = event.GetId()
        if event_id == wx.ID_EXIT:
            self.Close()
        elif event_id == wx.ID_ABOUT:
            wx.MessageBox("wxPython OpenGL Example with Menu Bar", "About", wx.OK | wx.ICON_INFORMATION)
        elif event_id == wx.ID_OPEN:
            self.on_open_file()
        self.canvas.SetFocus()  # Set focus back to the canvas    

    def on_open_file(self):
        """ Open a file dialog to select a file to open."""
        wildcard = "JPEG files (*.jpg)|*.jpg|PNG files (*.png)|*.png|All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Open image file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_OK:
            image2d_path = dialog.GetPath()
            self.canvas.image2d_path = image2d_path
            self.canvas.initialized = False
            print(f"Selected file: {image2d_path}")
            
        dialog.Destroy()
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_projection_click(self, event):
        print("Toggle perspective / orthographic projection")
        self.canvas.cameraIdx = (self.canvas.cameraIdx + 1) % 2
        self.canvas.update()
        self.canvas.SetFocus()  # Set focus back to the canvas


    # FIXME: to be done!!!!
    def on_register_click(self, event):
        if self.canvas.registrator is None:
            raise Exception("Registrator not initialized")
        self.canvas.registrator.register(n_iterations=1)
        self.canvas.update() #TODO: is this necessary????
        self.canvas.SetFocus()  # Set focus back to the canvas

        

    def on_dmax_slider_change(self, event):
        value = self.dmax_slider.GetValue()
        self.canvas.registrator.d_max = value
        self.canvas.registrator.updateMatch()
        print(f"Slider value changed to: {value}")
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_text_enter(self, event):
        text = self.textbox.GetValue()
        print(f"Text entered: {text}")
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_exit_click(self, event):
        self.Close()

# Instantiate the wxPython app and run it
if __name__ == "__main__":
    app = wx.App(False)
    frame = GUIFrame(None, title="App with Tool Panel", size=(1024, 768))  # Window size increased
    app.MainLoop()
