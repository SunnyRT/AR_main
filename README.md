# AR registration with PyOpenGL and Pygame
The work is based on book *"Developing Graphics Frameworks with Python and OpenGL"* by Lee Stemkoski and Michael Pascale published by CRC Press in 2021. 


The environment was Python 3.9.19 with the following packages:
```
conda create -n <env_name> python=3.9.19
conda install -c conda-forge wxpython
conda install pycodestyle pydocstyle pytest

conda install -c conda-forge pyopengl
conda install plyfile
pip install open3d
pip install glfw
```


To execute the program window, type in the cmd:
``` 
python main/test-xxx.py
```
Note that it might be needed to change the path for desired .ply and image file.
Some sample data files are available within the data_sample directory. 
The ```xxx.sw``` files contains the vertex coordinates for the traced contour.




User Interface:
- toggle between Perspective / Orthographic Projection:  SPACE / tool panel button “projection"
- (viewer) move forward / backward:                      W/S or MOUSESCROLL
- (viewer) move left / right / up / down:                A/D/R/F or MOUSERIGHT (drag)                              
- (viewer) turn left / right / up / down:                Q/E/T/G or MOUSELEFT (drag)
- (viewer) rotate about z:                               MOUSEMIDDLE (drag)

- (orthographic) zoom in / out:                          UP/DOWN ARROW or MOUSESCROLL


