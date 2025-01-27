import wx
from PIL import Image
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
        self.ID_RENDER = wx.NewIdRef()
        file_menu.Append(self.ID_RENDER, "&Render")
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

        # Create projection button
        self.projection_button = wx.Button(self.tool_panel, label="Projection")
        tool_sizer.Add(self.projection_button, 0, wx.ALL | wx.EXPAND, 5)  # Add spacing here
        self.Bind(wx.EVT_BUTTON, self.on_projection_click, self.projection_button)

        # Create register button
        self.register_button = wx.Button(self.tool_panel, label="Register")
        tool_sizer.Add(self.register_button, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self.on_register_click, self.register_button)


        """ Create registration itr slider"""
        self.n_itr = 20
        itr_sizer = wx.BoxSizer(wx.HORIZONTAL)
        itr_label = wx.StaticText(self.tool_panel, label="iteration:")
        itr_sizer.Add(itr_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2) 
        # Minimum value label
        min_label = wx.StaticText(self.tool_panel, label="1")
        itr_sizer.Add(min_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        # Slider itself
        self.itr_slider = wx.Slider(self.tool_panel, value=self.n_itr, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL) # precision: 1, actual range 1-100
        itr_sizer.Add(self.itr_slider, 0, wx.ALL | wx.EXPAND, 2)  

        # Maximum value label
        max_label = wx.StaticText(self.tool_panel, label="100")
        itr_sizer.Add(max_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        # Current value label
        self.itr_value_label = wx.StaticText(self.tool_panel, label=f"{self.itr_slider.GetValue():.0f}")
        itr_sizer.Add(self.itr_value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        tool_sizer.Add(itr_sizer, 0, wx.ALL | wx.EXPAND, 0)

        # Bind the slider event
        self.Bind(wx.EVT_SLIDER, self.on_itr_slider_change, self.itr_slider)
        """ End of slider creation """


        """ Create dmax slider"""
        dmax_sizer = wx.BoxSizer(wx.HORIZONTAL)
        dmax_label = wx.StaticText(self.tool_panel, label="dmax:")
        dmax_sizer.Add(dmax_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        # Minimum value label
        min_label = wx.StaticText(self.tool_panel, label="0")
        dmax_sizer.Add(min_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        # Slider itself
        try:
            self.dmax_slider = wx.Slider(self.tool_panel, value=self.canvas.registrator.d_max*10, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL) # precision: 0.1, actual range 0-10
        except:
            self.dmax_slider = wx.Slider(self.tool_panel, value=100, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL)
        dmax_sizer.Add(self.dmax_slider, 0, wx.ALL | wx.EXPAND, 2)  
        # Maximum value label
        max_label = wx.StaticText(self.tool_panel, label="10")
        dmax_sizer.Add(max_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        # Current value label
        self.dmax_value_label = wx.StaticText(self.tool_panel, label=f"{self.dmax_slider.GetValue() / 10:.1f}")
        dmax_sizer.Add(self.dmax_value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        tool_sizer.Add(dmax_sizer, 0, wx.ALL | wx.EXPAND, 0)

        # Bind the slider event
        self.Bind(wx.EVT_SLIDER, self.on_dmax_slider_change, self.dmax_slider)
        """ End of dmax slider creation """


        
        """ Create delta slider (coneMesh resolution along optical-axis)"""
        delta_sizer = wx.BoxSizer(wx.HORIZONTAL)
        delta_label = wx.StaticText(self.tool_panel, label="delta:")
        delta_sizer.Add(delta_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 2) 
        # Minimum value label
        min_label = wx.StaticText(self.tool_panel, label="0")
        delta_sizer.Add(min_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        # Slider itself
        try:
            self.delta_slider = wx.Slider(self.tool_panel, value=self.canvas.projector.delta*10, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL) # precision: 0.1, actual range 0-10
        except:
            self.delta_slider = wx.Slider(self.tool_panel, value=2, minValue=1, maxValue=100, style=wx.SL_HORIZONTAL)
        delta_sizer.Add(self.delta_slider, 0, wx.ALL | wx.EXPAND, 2)  
        # Maximum value label
        max_label = wx.StaticText(self.tool_panel, label="10")
        delta_sizer.Add(max_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
        # Current value label
        self.delta_value_label = wx.StaticText(self.tool_panel, label=f"{self.delta_slider.GetValue() / 10:.1f}")
        delta_sizer.Add(self.delta_value_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

        tool_sizer.Add(delta_sizer, 0, wx.ALL | wx.EXPAND, 0)

        # Bind the slider event
        self.Bind(wx.EVT_SLIDER, self.on_delta_slider_change, self.delta_slider)
        """ End of slider creation """

        # # Create a text box
        # self.textbox = wx.TextCtrl(self.tool_panel, style=wx.TE_PROCESS_ENTER)
        # tool_sizer.Add(self.textbox, 0, wx.ALL | wx.EXPAND, 10)  # Add spacing here
        # self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.textbox)

        tool_sizer.AddSpacer(10)

        """ Display Registration Parameters"""
        # Transformation matrix display(text)
        self.transform_matrix_text = wx.StaticText(
            self.tool_panel, 
            label="Transformation Matrix\n" + self.format_matrix(np.identity(4)),
            style=wx.ALIGN_LEFT
        )
        tool_sizer.Add(self.transform_matrix_text, 0, wx.ALL | wx.EXPAND, 0)


        def add_labeled_text(tool_panel, sizer, label_text, initial_value=""):
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(tool_panel, label=label_text)
            hbox.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)
            value_text = wx.StaticText(tool_panel, label=initial_value, style=wx.ALIGN_LEFT)
            hbox.Add(value_text, 1, wx.ALL | wx.EXPAND, 0)
            sizer.Add(hbox, 0, wx.ALL | wx.EXPAND, 0)
            return value_text
        
        # self.view_angle_text = add_labeled_text(self.tool_panel, tool_sizer, "View Angle:", "0.0")
        # self.match_count_text = add_labeled_text(self.tool_panel, tool_sizer, "Number of Matches:", "0")
        tool_sizer.Add(wx.StaticText(self.tool_panel, label="Registration Results:"), 0, wx.ALL | wx.EXPAND, 0)
        self.mean_error_text = add_labeled_text(self.tool_panel, tool_sizer, "Mean Error:", "0.0")
        self.mean_norm_measure_text = add_labeled_text(self.tool_panel, tool_sizer, "Mean Normal Measure:", "0.0")
        tool_sizer.Add(wx.StaticText(self.tool_panel, label="Validation Results:"), 0, wx.ALL | wx.EXPAND, 0)
        self.mean_error_val_text = add_labeled_text(self.tool_panel, tool_sizer, "Mean Error:", "0.0")
        self.mean_norm_measure_val_text = add_labeled_text(self.tool_panel, tool_sizer, "Mean Normal Measure:", "0.0")
        tool_sizer.AddSpacer(12)



        """ Transparency slider control for image2d, model3d and projector """
        def add_alpha_slider(tool_panel, sizer, label_text, default_value=50):


            # setup a horizontal sizer for the slider
            slider_sizer = wx.BoxSizer(wx.HORIZONTAL)
            label = wx.StaticText(tool_panel, label=label_text)
            slider_sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

            # Minimum value label
            min_label = wx.StaticText(tool_panel, label="0")
            slider_sizer.Add(min_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)

            # Slider itself
            slider = wx.Slider(tool_panel, value=default_value, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL)
            slider_sizer.Add(slider, 1, wx.ALL | wx.EXPAND, 2)

            # Maximum value label
            max_label = wx.StaticText(tool_panel, label="1")
            slider_sizer.Add(max_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 1)
            sizer.Add(slider_sizer, 0, wx.ALL | wx.EXPAND, 0)

            return slider
        
    
        self.model3d_slider = add_alpha_slider(self.tool_panel, tool_sizer, "Model 3D Alpha:", 100)
        self.Bind(wx.EVT_SLIDER, self.on_model3d_slider_change, self.model3d_slider)

        self.image2d_slider = add_alpha_slider(self.tool_panel, tool_sizer, "Image Plane Alpha:")
        self.Bind(wx.EVT_SLIDER, self.on_image2d_slider_change, self.image2d_slider)

        self.projector_slider = add_alpha_slider(self.tool_panel, tool_sizer, "Projector Alpha:")
        self.Bind(wx.EVT_SLIDER, self.on_projector_slider_change, self.projector_slider)


        """ Checkbox for visibility of contour and match mesh """
        visibility_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.contour_chkbx = wx.CheckBox(self.tool_panel, label="Show Contour")
        self.contour_chkbx.SetValue(True)
        visibility_sizer.Add(self.contour_chkbx, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.Bind(wx.EVT_CHECKBOX, self.on_contour_visible, self.contour_chkbx)

        self.match_chkbx = wx.CheckBox(self.tool_panel, label="Show Matches")
        self.match_chkbx.SetValue(True)
        visibility_sizer.Add(self.match_chkbx, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 3)
        self.Bind(wx.EVT_CHECKBOX, self.on_match_visible, self.match_chkbx)

        tool_sizer.Add(visibility_sizer, 0, wx.ALL | wx.EXPAND, 2)


        """ Radio button for ensemble visibility control """
        visible_ensemble_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pinna_rb = wx.RadioButton(self.tool_panel, label="Pinna", style=wx.RB_GROUP)
        self.incus_rb = wx.RadioButton(self.tool_panel, label="Incus")
        self.both_rb = wx.RadioButton(self.tool_panel, label="Both")
        visible_ensemble_sizer.Add(self.pinna_rb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        visible_ensemble_sizer.Add(self.incus_rb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        visible_ensemble_sizer.Add(self.both_rb, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.pinna_rb.Bind(wx.EVT_RADIOBUTTON, self.on_ensemble_visible)
        self.incus_rb.Bind(wx.EVT_RADIOBUTTON, self.on_ensemble_visible)
        self.both_rb.Bind(wx.EVT_RADIOBUTTON, self.on_ensemble_visible)

        tool_sizer.Add(visible_ensemble_sizer, 0, wx.ALL | wx.EXPAND, 2)


        """ Checkbox for visibility of individual objects in model3d """
        visibility_model3d_sizer = wx.BoxSizer(wx.VERTICAL)

        # List of components
        components = [
            "oticCapsule",
            "stapes",
            "sigmoidSinus",
            "incus",
            "malleus",
            "chordaTympani",
            "tensorTympani",
            "facialNerve",
            "pinna"
        ]

        # Dictionary to hold checkboxes for easy access
        self.component_chkbx = {}
        
        for component in components:
            # Create a checkbox for each component
            chkbx = wx.CheckBox(self.tool_panel, label=component)
            chkbx.SetValue(True)  # Set default value as visible
            visibility_model3d_sizer.Add(chkbx, 0, wx.ALL | wx.ALIGN_LEFT, 2)
            
            # Bind the checkbox to the generic event handler
            chkbx.Bind(wx.EVT_CHECKBOX, self.on_model3d_visible)
            
            # Store the checkbox in the dictionary
            self.component_chkbx[component] = chkbx
        
        tool_sizer.Add(visibility_model3d_sizer, 0, wx.ALL | wx.EXPAND, 2)
       



        # Create exit button
        self.exit_button = wx.Button(self.tool_panel, label="Exit")
        tool_sizer.Add(self.exit_button, 0, wx.ALL | wx.EXPAND, 10)
        self.Bind(wx.EVT_BUTTON, self.on_exit_click, self.exit_button)


        # Set sizer for the tool panel
        self.tool_panel.SetSizer(tool_sizer)

        
    
    def update_tool_panel(self, transform_matrix, distance, 
                          match_count, 
                          mean_error, mean_norm_measure, 
                          mean_error_val, mean_norm_measure_val):
        """ Update the text in the tool panel."""
        self.transform_matrix_text.SetLabel("Transformation Matrix:\n"+self.format_matrix(transform_matrix))
        # self.distance_text.SetLabel(f"Distance to Origin:\n {distance:.2f}")
        # self.view_angle_text.SetLabel(f"{view_angle:.2f}")
        # self.match_count_text.SetLabel(f"{match_count}")
        self.mean_error_text.SetLabel(f"{mean_error:.2f}")
        self.mean_norm_measure_text.SetLabel(f"{mean_norm_measure:.2f}")
        self.mean_error_val_text.SetLabel(f"{mean_error_val:.2f}")
        self.mean_norm_measure_val_text.SetLabel(f"{mean_norm_measure_val:.2f}")

    def format_matrix(self, matrix):
        """ Format the matrix as a string for display."""
        formatted_matrix = ""
        for row in matrix:
            formatted_matrix += " ".join(f"{val:.2f}" for val in row) + "\n"
        return formatted_matrix


    





    ############################ Event Handlers ############################
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
        elif event_id == self.ID_RENDER:
            self.on_render_ar()
        self.canvas.SetFocus()  # Set focus back to the canvas    

    def on_open_file(self): # FIXME: not implemented
        """ Open a file dialog to select a file to open."""
        wildcard = "JPEG files (*.jpg)|*.jpg|PNG files (*.png)|*.png|All files (*.*)|*.*"
        dialog = wx.FileDialog(self, "Open image file", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            # self.canvas.initialized = False
            print(f"Selected file: {path}, but unable to load.")
            
        dialog.Destroy() 
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_load_file(self):
        """ Load a registration text file, in the format of:
                Transformation Matrix: 
                xxxx
                xxxx
                xxxx
                xxxx

                [Object: x]
                Resolution: x
                Near plane (n): x
                Far plane (f): x
                Delta: x
        """
        
        dialog = wx.FileDialog(self, "Load registration result", 
                               wildcard="Text files (*.txt)|*.txt", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        
        if dialog.ShowModal() == wx.ID_OK:
            load_path = dialog.GetPath()
            # try:
            with open(load_path, "r") as file:
                matrix_lines = []
                reading_matrix = False
                obj_count = -1
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
                            reading_matrix = False
                            transform = np.array(matrix_lines)
                            self.canvas.init_registration = transform
                            # imgPlane_zpos = self.canvas.image2d.imagePlane.getWorldPosition()[2]
                            # coneMesh_len = self.canvas.f - self.canvas.n
                            # print(f"Old imagePlane position: {self.canvas.image2d.imagePlane.getWorldPosition()}")
                            # self.canvas.rig_ms.setWorldPosition([transform[0][3], transform[1][3], transform[2][3]])
                            # self.canvas.rig_ms.setWorldRotation(transform[0:3, 0:3])
                            

                            # # update self.canvas.n and self.canvas.f
                            # self.canvas.n = transform[2][3] - imgPlane_zpos
                            # self.canvas.f = self.canvas.n + coneMesh_len
                            # print(f"new near plane: {self.canvas.n}, new far plane: {self.canvas.f}")

                    # Parse additional parameters
                    elif line.startswith("[Object:"):
                        obj_count = int(line.split(":")[1].strip()[:-1])
                    elif line.startswith("Resolution:"):
                        self.canvas.res[obj_count] = float(line.split(":")[1].strip())
                    elif line.startswith("Near plane (n):"):
                        self.canvas.ns[obj_count] = float(line.split(":")[1].strip())
                    elif line.startswith("Far plane (f):"):
                        self.canvas.fs[obj_count] = float(line.split(":")[1].strip())
                    elif line.startswith("Delta:"):
                        self.canvas.deltas[obj_count] = float(line.split(":")[1].strip())
            # Reinitialize the scene with new parameters
            self.canvas.initialized = False
            wx.MessageBox(f"Registration result loaded from {load_path}", "Load Successful", wx.OK | wx.ICON_INFORMATION)
            
            print(f"New rig_ms position: {self.canvas.rig_ms.getWorldPosition()}")
            # except Exception as e:
            #     print(f"Failed to load file: {e}")
            #     wx.MessageBox(f"Failed to load file: {e}","Error", wx.OK | wx.ICON_ERROR)
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
                    matrix = self.canvas.rig_ms.getWorldMatrix()  # get world matrix of both microscopes == rig_ms
                    for row in matrix:
                        file.write(" ".join(f"{value:.2f}" for value in row) + "\n")
                    file.write("\n")
                    
                    # Write additional parameters
                    for i, projectorFac in enumerate(self.canvas.projectorFacs):
                        file.write(f"[Object: {i}]\n")
                        file.write(f"Resolution: {self.canvas.res[i]}\n")
                        file.write(f"Near plane (n): {projectorFac.n}\n")
                        file.write(f"Far plane (f): {projectorFac.f}\n")
                        file.write(f"Delta: {projectorFac.delta}\n")
                        file.write("\n")
                    # file.write(f"Resolution: {self.canvas.resolution}\n")
                    # file.write(f"Near plane (n): {self.canvas.n}\n")
                    # file.write(f"Far plane (f): {self.canvas.f}\n")
                    # file.write(f"Delta: {self.canvas.delta}\n")
                    
                    wx.MessageBox(f"Registration result saved to {save_path}", "Save Successful", wx.OK | wx.ICON_INFORMATION)
            except Exception as e:
                wx.MessageBox(f"Failed to save file: {e}", "Error", wx.OK | wx.ICON_ERROR)
        
        dialog.Destroy()
        self.canvas.SetFocus()  # Set focus back to the canvas

        
    def on_render_ar(self):
        """ Render the current scene and save the image to a file.
        """
        # Open a save file dialog
        wildcard = "PNG files (*.png)|*.png|JPEG files (*.jpg;*.jpeg)|*.jpg;*.jpeg"
        dialog = wx.FileDialog(self, "Save rendered AR view", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        
        if dialog.ShowModal() == wx.ID_OK:
            # Get the selected file path
            save_path = dialog.GetPath()
        
        try: 
            image = self.canvas.renderer.capture_vp(viewportSplit = "right")
        except Exception as e:
            wx.MessageBox(f"Failed to render AR view: {e}", "Error", wx.OK | wx.ICON_ERROR)
            dialog.Destroy()
            return
    
        ext = save_path.split(".")[-1]
        if ext == "jpg" or ext == "jpeg":
            image_type = wx.BITMAP_TYPE_JPEG
        elif ext == "png":
            image_type = wx.BITMAP_TYPE_PNG
        else:
            # default to PNG
            wx.MessageBox(f"Invalid file extension: {ext}. Defaulting to PNG", "Warning", wx.OK | wx.ICON_WARNING)
            image_type = wx.BITMAP_TYPE_PNG
            save_path += ".png"

        try:
            image.SaveFile(save_path, image_type)
            wx.MessageBox(f"Rendered AR view saved to {save_path}", "Save Successful", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"Failed to save file: {e}", "Error", wx.OK | wx.ICON_ERROR)
        
        dialog.Destroy()


    def on_projection_click(self, event):
        print("Toggle perspective / orthographic projection")
        self.canvas.state = (self.canvas.state + 1) % 2
        self.canvas.update()
        self.canvas.SetFocus()  # Set focus back to the canvas


    
    def on_register_click(self, event):
        if self.canvas.registrator is None:
            raise Exception("Registrator not initialized")
        for i in range(self.n_itr):
            self.canvas.registrator.register(n_iterations=1)
            self.canvas.validator.updateMatch()
            self.canvas.on_paint(event=None)
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_itr_slider_change(self, event):
        value = self.itr_slider.GetValue()
        self.itr_value_label.SetLabel(f"{value:.0f}")
        self.n_itr = int(value)
        self.canvas.SetFocus()
        
    def on_dmax_slider_change(self, event):
        value = self.dmax_slider.GetValue()/10
        self.dmax_value_label.SetLabel(f"{value:.1f}")
        viewport = self.canvas.viewport
        mediator = self.canvas.mediators[viewport]
        mediator.notify(self, "update dmax", data={"dmax": value})
        print(f"Maximum match pair distance dmax: {value}")
        self.canvas.SetFocus()  # Set focus back to the canvas

    def on_delta_slider_change(self, event):
        value = self.delta_slider.GetValue()/10
        self.delta_value_label.SetLabel(f"{value:.1f}")

        # FIXME: viewport = 0 or 1 separately!!!! BUG:!!!!! 
        print(f"GUI update: z-resolution = {value}")
        viewport = self.canvas.viewport
        mediator = self.canvas.mediators[viewport]
        mediator.notify(self, "update projector delta", data={"delta": value})
        
        self.canvas.SetFocus()  # Set focus back to the canvas

    # transparency slider event handlers
    def on_model3d_slider_change(self, event):
        value = self.model3d_slider.GetValue()/100
        self.canvas.model3d.setAlpha(value)
        # print(f"Model 3d alpha: {value}")
        self.canvas.SetFocus()


    def on_image2d_slider_change(self, event):
        value = self.image2d_slider.GetValue()/100
        for mediator in self.canvas.mediators:
            mediator.notify(self, "update alpha", data={"object":"image", "alpha": value})
        self.canvas.SetFocus()

    def on_projector_slider_change(self, event):
        value = self.projector_slider.GetValue()/100
        for mediator in self.canvas.mediators:
            mediator.notify(self, "update alpha", data={"object":"projector", "alpha": value})
        self.canvas.SetFocus()


    def on_contour_visible(self, event):
        visible = self.contour_chkbx.GetValue()
        viewport = self.canvas.viewport
        mediator = self.canvas.mediators[viewport]
        mediator.notify(self, "update visibility", data={"object":"contour", "is_visible": visible})
        self.canvas.SetFocus()

    def on_match_visible(self, event):
        visible = self.match_chkbx.GetValue()
        viewport = self.canvas.viewport
        mediator = self.canvas.mediators[viewport]
        mediator.notify(self, "update visibility", data={"object":"match", "is_visible": visible})
        self.canvas.SetFocus()

    def on_ensemble_visible(self, event):
        print(f"Ensemble visibility: pinna={self.pinna_rb.GetValue()}, incus={self.incus_rb.GetValue()}, both={self.both_rb.GetValue()}")
        pinna_visible = self.pinna_rb.GetValue() or self.both_rb.GetValue()
        incus_visible = self.incus_rb.GetValue() or self.both_rb.GetValue()
        mediators = self.canvas.mediators
        if (pinna_visible or incus_visible):
            mediators[0].notify(self, "update ensemble visibility", data={"is_visible": pinna_visible})
            mediators[1].notify(self, "update ensemble visibility", data={"is_visible": incus_visible})
        else:
            raise Exception("Invalid visibility selection")
        self.canvas.SetFocus()
    

    """ Control model3d object visibility """
    def on_model3d_visible(self, event):
        # Get the checkbox that triggered the event
        chkbx = event.GetEventObject()
        # Retrieve the label of the checkbox (component name)
        component = chkbx.GetLabel()
        # Get the current state of the checkbox
        is_checked = chkbx.GetValue()
        
        print(f"{component} visibility set to: {is_checked}")
        
        # Ensure that the model3d object and the attribute exist
        if hasattr(self.canvas.model3d, 'material'):
            material = self.canvas.model3d.material
            if hasattr(material, 'setComponentVisibility'):
                material.setComponentVisibility(component, is_checked)
                self.canvas.SetFocus()
            else:
                print(f"Warning: material has no method 'setComponentVisibility'")
        else:
            print(f"Warning: model3d has no attribute 'material'")
        self.canvas.Refresh()
            


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
