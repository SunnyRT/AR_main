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
        self.ID_LOAD = wx.NewIdRef()
        file_menu.Append(self.ID_LOAD, "&Load")
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



        """ Create dmax slider"""
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
        """ End of dmax slider creation """


        """ Create delta slider (conMesh resolution along optical-axis)"""
        slider_sizer = wx.BoxSizer(wx.VERTICAL)
        delta_label = wx.StaticText(self.tool_panel, label="delta:")
        slider_sizer.Add(delta_label, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5) 
        slider_with_labels_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Minimum value label
        min_label = wx.StaticText(self.tool_panel, label="0")
        slider_with_labels_sizer.Add(min_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Slider itself
        try:
            self.delta_slider = wx.Slider(self.tool_panel, value=self.canvas.projector.delta, minValue=0, maxValue=10, style=wx.SL_HORIZONTAL)
        except:
            self.delta_slider = wx.Slider(self.tool_panel, value=2, minValue=0, maxValue=10, style=wx.SL_HORIZONTAL)
        slider_with_labels_sizer.Add(self.delta_slider, 0, wx.ALL | wx.EXPAND, 10)  # Add spacing here
        
        # Maximum value label
        max_label = wx.StaticText(self.tool_panel, label="10")
        slider_with_labels_sizer.Add(max_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # Add the slider with labels sizer to the main slider sizer
        slider_sizer.Add(slider_with_labels_sizer, 0, wx.ALL | wx.EXPAND, 5)
        # Add the slider_sizer to the main tool panel sizer
        tool_sizer.Add(slider_sizer, 0, wx.ALL | wx.EXPAND, 10)

        # Bind the slider event
        self.Bind(wx.EVT_SLIDER, self.on_delta_slider_change, self.delta_slider)
        """ End of slider creation """

        # # Create a text box
        # self.textbox = wx.TextCtrl(self.tool_panel, style=wx.TE_PROCESS_ENTER)
        # tool_sizer.Add(self.textbox, 0, wx.ALL | wx.EXPAND, 10)  # Add spacing here
        # self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.textbox)

        # tool_sizer.AddSpacer(10)

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

        # self.distance_text = wx.StaticText(
        #     self.tool_panel,
        #     label="Distance to Origin: 0.0",
        #     style=wx.ALIGN_LEFT
        # )
        # tool_sizer.Add(self.distance_text, 0, wx.ALL | wx.EXPAND, 10)

        # tool_sizer.AddSpacer(10)

        self.view_angle_text = wx.StaticText(
            self.tool_panel,
            label="View Angle: 0.0",
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.view_angle_text, 0, wx.ALL | wx.EXPAND, 10)

        self.match_count_text = wx.StaticText(
            self.tool_panel,
            label="Number of Matches: 0",
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.match_count_text, 0, wx.ALL | wx.EXPAND, 10)

        self.mean_error_text = wx.StaticText(
            self.tool_panel,
            label="Mean Error: 0.0",
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.mean_error_text, 0, wx.ALL | wx.EXPAND, 10)

        self.mean_norm_meausre_text = wx.StaticText(
            self.tool_panel,
            label="Mean Normal Similarity Measure: 0.0",
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.mean_norm_meausre_text, 0, wx.ALL | wx.EXPAND, 10)

        # Set sizer for the tool panel
        self.tool_panel.SetSizer(tool_sizer)


    def update_tool_panel(self, transform_matrix, distance, view_angle, match_count, mean_error, mean_norm_measure):
        """ Update the text in the tool panel."""
        self.transform_matrix_text.SetLabel("Transformation Matrix:\n"+self.format_matrix(transform_matrix))
        # self.distance_text.SetLabel(f"Distance to Origin:\n {distance:.2f}")
        self.view_angle_text.SetLabel(f"View Angle:\n {view_angle:.2f}")
        self.match_count_text.SetLabel(f"Number of Matches:\n {match_count}")
        self.mean_error_text.SetLabel(f"Mean Error:\n {mean_error:.2f}")
        self.mean_norm_meausre_text.SetLabel(f"Mean Normal Similarity Measure:\n {mean_norm_measure:.2f}")

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
        elif event_id == self.ID_LOAD:
            self.on_load_file()
        elif event_id == wx.ID_SAVE:
            self.on_save_file()
        self.canvas.SetFocus()  # Set focus back to the canvas    

    def on_open_file(self): # FIXME: open directory which contains a corresponding pair of (image file + contour.sw)
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

    def on_load_file(self):
        """ Load a registration text file, in the format of:
                Transformation Matrix: xxx
                Resolution:
                Near plane (n):
                Far plane (f):
                Delta:
        """
        
        dialog = wx.FileDialog(self, "Load registration result", 
                               wildcard="Text files (*.txt)|*.txt", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_OK:
            load_path = dialog.GetPath()
            try:
                with open(load_path, "r") as file:
                    matrix_lines = []
                    reading_matrix = False
                    for line in file:
                        line = line.strip()
                        if not line:
                            continue
                        if "Transformation Matrix" in line:
                            reading_matrix = True
                            continue
                        if reading_matrix:
                            # Read the transformation matrix values
                            if len(matrix_lines) < 4:  # Assuming a 4x4 matrix
                                matrix_row = [float(value) for value in line.split()]
                                matrix_lines.append(matrix_row)
                            if len(matrix_lines) == 4:
                                self.canvas.init_registration = np.array(matrix_lines)
                                self.canvas.camera1_z = self.canvas.init_registration[2][3]
                                reading_matrix = False

                        # Parse additional parameters
                        elif line.startswith("Resolution:"):
                            self.canvas.resolution = float(line.split(":")[1].strip())
                        elif line.startswith("Near plane (n):"):
                            self.canvas.n = float(line.split(":")[1].strip())
                        elif line.startswith("Far plane (f):"):
                            self.canvas.f = float(line.split(":")[1].strip())
                        elif line.startswith("Delta:"):
                            self.canvas.delta = float(line.split(":")[1].strip())
                wx.MessageBox(f"Registration result loaded from {load_path}", "Load Successful", wx.OK | wx.ICON_INFORMATION)
                self.canvas.initialized = False
            except Exception as e:
                wx.MessageBox(f"Failed to load file: {e}","Error", wx.OK | wx.ICON_ERROR)
            
        dialog.Destroy() 
        self.canvas.SetFocus()  # Set focus back to the canvas
    
    def on_save_file(self):
        """ Save current registration result in a text file:
            - Transformation matrix of camera in world coordinates
            - Resolution
            - Near and far plane distances (n and f)
            - Delta parameter
        """
        # Open a save file dialog
        dialog = wx.FileDialog(self, "Save registration result", wildcard="Text files (*.txt)|*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_OK:
            # Get the selected file path
            save_path = dialog.GetPath()
            try:
                with open(save_path, "w") as file:
                    # Write the transformation matrix
                    file.write("Transformation Matrix:\n")
                    matrix = self.canvas.rig1.getWorldMatrix()  # get world matrix of camera1 == rig1
                    for row in matrix:
                        file.write(" ".join(f"{value:.2f}" for value in row) + "\n")
                    file.write("\n")
                    
                    # Write additional parameters
                    file.write(f"Resolution: {self.canvas.resolution}\n")
                    file.write(f"Near plane (n): {self.canvas.n}\n")
                    file.write(f"Far plane (f): {self.canvas.f}\n")
                    file.write(f"Delta: {self.canvas.delta}\n")
                    
                    wx.MessageBox(f"Registration result saved to {save_path}", "Save Successful", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Failed to save file: {e}", "Error", wx.OK | wx.ICON_ERROR)
        
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
        print(f"Maximum match pair distance dmax: {value}")
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_delta_slider_change(self, event):
        value = self.delta_slider.GetValue()
        self.canvas.projector.delta = value
        self.canvas.projector._updateConeMesh()
        self.canvas.registrator.updateMesh1(mesh1=self.canvas.projector.coneMesh)
        print(f"Projector coneMesh z-resolution: {value}")
        self.canvas.SetFocus()  # Set focus back to the canvas

    # def on_text_enter(self, event):
    #     text = self.textbox.GetValue()
    #     print(f"Text entered: {text}")
    #     self.canvas.SetFocus()  # Set focus back to the canvas

    def on_exit_click(self, event):
        self.Close()

# Instantiate the wxPython app and run it
if __name__ == "__main__":
    app = wx.App(False)
    frame = GUIFrame(None, title="App with Tool Panel", size=(1024, 768))  # Window size increased
    app.MainLoop()
