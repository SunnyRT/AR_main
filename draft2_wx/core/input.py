import pygame   

class Input(object):

    def __init__(self):
        # has the user quit the application?
        self.quit = False

    def update(self):
        # iterate over all user input events (e.g. keyboard, mouse)
        # that have occurred since the last time events were checked
        for event in pygame.event.get():

        # quit event occurs by clicking the close button
        # if event.type == pygame.QUIT:
            if event.type == pygame.QUIT:
                self.quit = True

        