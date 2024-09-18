import pygame
from OpenGL.GL import *
import pygame_gui
from pygame.locals import *

# Initialize Pygame and OpenGL
pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
gui_manager = pygame_gui.UIManager((800, 600))

# Framebuffer for off-screen 3D rendering
fbo = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, fbo)

# Create a texture to render the 3D scene into
fbo_texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, fbo_texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fbo_texture, 0)

# Check if framebuffer is complete
if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    raise RuntimeError("Framebuffer is not complete!")

# Unbind the framebuffer
glBindFramebuffer(GL_FRAMEBUFFER, 0)

# Function to render the 3D scene to the FBO
def render_scene_to_fbo():
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glViewport(0, 0, 800, 600)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Render the 3D scene here (OpenGL code for 3D rendering)
    # Example: rendering a red triangle
    glBegin(GL_TRIANGLES)
    glColor3f(1.0, 0.0, 0.0)
    glVertex2f(-0.5, -0.5)
    glVertex2f(0.5, -0.5)
    glVertex2f(0.0, 0.5)
    glEnd()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

# Function to render the texture (3D scene) to a 2D Pygame surface
def render_fbo_texture_to_screen():
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, fbo_texture)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(-1.0, -1.0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(1.0, -1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(1.0, 1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(-1.0, 1.0)
    glEnd()

    glDisable(GL_TEXTURE_2D)

# Main loop
running = True
clock = pygame.time.Clock()

# Create a simple button using pygame_gui
button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                      text="Click me!",
                                      manager=gui_manager)

while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        gui_manager.process_events(event)

    # Render the 3D scene to the FBO
    render_scene_to_fbo()

    # Clear the screen for 2D rendering
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Render the 3D scene (as a texture) to the screen
    render_fbo_texture_to_screen()

    # Switch to Pygame's rendering for the GUI
    glFlush()  # Ensure all OpenGL rendering is done

    # This is important: render GUI elements after OpenGL
    gui_manager.update(time_delta)
    gui_manager.draw_ui(screen)

    # Swap buffers to display everything
    pygame.display.flip()

pygame.quit()
