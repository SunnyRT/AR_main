import pygame
import sys
from core.input import Input


class Base(object):

    def __init__(self, screenSize=[512,512]):

        # initialize all pygame modules
        pygame.init()
        # indicate rendering details
        displayFlags = pygame.DOUBLEBUF | pygame.OPENGL # “|” is a bitwise OR operator
        
        
        # antialiasing
        # MSAA: multisample antialiasing
        pygame.display.gl_set_attribute(
            pygame.GL_MULTISAMPLEBUFFERS, 1 
        ) # enable multisampling: to allocate a single additional multipsample buffer per pixel
        pygame.display.gl_set_attribute(
            pygame.GL_MULTISAMPLESAMPLES, 4
        ) 
        # for each pixel, graphics hardware calculate and store 4 samples, 
        # these samples represent different positions within the pixel (subpixels),
        # which are averaged to determine the final color of the pixel

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

        # determine if main loop is active
        self.running = True
        # manage time-related data and operations
        self.clock = pygame.time.Clock()

        # manage user input
        self.input = Input()


    # implement by extending class
    def initialize(self):
        pass


    # implement by extending class
    def update(self):
        pass

    def run(self):
        """ contains all the phases of an interactive 
            graphics-based application """

        ## startup ##
        self.initialize()

        ## main loop ##
        while self.running:
            ## process input ##
            self.input.update()
            if self.input.quit:
                self.running = False

            ## update ##
            self.update()

            ## render ##
            # display image on the screen
            pygame.display.flip() # filp the back buffer to the front buffer (double buffering)

            # set the frame rate: pause the program to maintain 60 FPS
            self.clock.tick(60)
        
        ## shutdown ##
        pygame.quit()
        sys.exit()
