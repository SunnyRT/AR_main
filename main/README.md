# OpenGL examples with PyOpenGL and Pygame
The OpenGL examples are based on book *"Developing Graphics Frameworks with Python and OpenGL"* by Lee Stemkoski and Michael Pascale published by CRC Press in 2021. 


The environment was Python 3.8 with the following packages (without specifying their dependencies here):
```
numpy==1.22.4
pygame==2.1.2
PyOpenGL==3.1.6
PyOpenGL-accelerate==3.1.6
```


To execute the program window, type in the cmd:
``` 
python main/test-display.py
```
Note that it might be needed to change the path for desired .ply and image file 



User Interface:
- toggle between Perspective / Orthographic Projection:  SPACE
- (viewer) move forward / backward:                      W/S or MOUSEMIDDLE (scroll)
- (viewer) move left / right / up / down:                A/D/R/F or MOUSERIGHT (drag)                              
- (viewer) turn left / right / up / down:                Q/E/T/G or MOUSELEFT (drag)

- (orthographic) zoom in / out:                          UP/DOWN ARROW or MOUSEMIDDLE(scroll)


