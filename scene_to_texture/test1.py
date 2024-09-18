import pygame
import pygame_gui
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Initialize Pygame
pygame.init()

# Create a window using Pygame
screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
glClearColor(0.0, 0.0, 0.0, 1.0)

# Set up Pygame GUI
manager = pygame_gui.UIManager((800, 600))

# Create GUI elements (buttons and labels)
button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 500), (100, 50)),
                                       text='Button 1',
                                       manager=manager)

button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((200, 500), (100, 50)),
                                       text='Button 2',
                                       manager=manager)

label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 450), (250, 30)),
                                    text='This is a label',
                                    manager=manager)

clock = pygame.time.Clock()

# Framebuffer size
width, height = 800, 600

def render_scene_to_texture(framebuffer, width, height):
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glViewport(0, 0, width, height)

    # Clear the framebuffer's color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Render the 3D scene (e.g., a simple rotating cube)
    glPushMatrix()
    glRotatef(pygame.time.get_ticks() * 0.01, 1, 1, 0)
    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    glVertex3f(-1, -1, -1)
    glVertex3f(1, -1, -1)
    glVertex3f(1, 1, -1)
    glVertex3f(-1, 1, -1)
    glEnd()
    glPopMatrix()

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

def render_texture_to_quad(texture_id, x, y, width, height):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(x, y)

    glTexCoord2f(1.0, 0.0)
    glVertex2f(x + width, y)

    glTexCoord2f(1.0, 1.0)
    glVertex2f(x + width, y + height)

    glTexCoord2f(0.0, 1.0)
    glVertex2f(x, y + height)
    glEnd()

    glDisable(GL_TEXTURE_2D)

# Create the framebuffer and texture for the 3D scene
framebuffer, framebuffer_texture = glGenFramebuffers(1), glGenTextures(1)

glBindTexture(GL_TEXTURE_2D, framebuffer_texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, framebuffer_texture, 0)

depthbuffer = glGenRenderbuffers(1)
glBindRenderbuffer(GL_RENDERBUFFER, depthbuffer)
glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, depthbuffer)

glBindFramebuffer(GL_FRAMEBUFFER, 0)

def render_gui_elements():
    time_delta = clock.tick(60) / 1000.0

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Handle GUI events
        manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == button1:
                    print("Button 1 clicked")
                elif event.ui_element == button2:
                    print("Button 2 clicked")

    # Update the GUI
    manager.update(time_delta)

    # This is the key: We draw GUI elements here after all OpenGL rendering is done
    glUseProgram(0)  # Disable any active shader programs to render the Pygame GUI
    glDisable(GL_DEPTH_TEST)  # Disable depth test for 2D GUI elements
    glDisable(GL_CULL_FACE)   # Disable face culling so all GUI is visible

    # Let Pygame handle the drawing of 2D GUI elements (overlaid on top of the OpenGL scene)
    manager.draw_ui(screen)
    

# Main loop
running = True
while running:
    # Render the 3D scene to the framebuffer
    # render_scene_to_texture(framebuffer, 800, 600)

    # # Clear the screen and render the 3D scene texture to a quad
    # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # render_texture_to_quad(framebuffer_texture, -1, -1, 2, 2)  # Full screen quad

    # Render 2D GUI elements (e.g., buttons)
    render_gui_elements()

    
    # Swap buffers to display the frame
    pygame.display.flip()
