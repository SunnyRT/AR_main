import pygame
import sys


class Base(object):

    def __init__(self, screenSize=[512,512]):

        # initialize all pygame modules
        pygame.init()
        # indicate rendering details
        displayFlags = pygame.DOUBLEBUF | pygame.OPENGL
        # initialize buffers to perform antialiasing
        pygame.display.gl_set_attribute(
            pygame.GL_MULTISAMPLEBUFFERS, 1 
        ) # 1 buffer
        pygame.display.gl_set_attribute(
            pygame.GL_MULTISAMPLESAMPLES, 4
        ) # 4x antialiasing

        # use a core OpegnGL profile for cross-platform compatibility
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, 
            pygame.GL_CONTEXT_PROFILE_CORE
        )
        
        # create and display the window
        self.screen = pygame.display.set_mode(
            screenSize, displayFlags
        )

        # set the text that appears in the title bar of the window
        pygame.display.set_caption("Graphics Window")
