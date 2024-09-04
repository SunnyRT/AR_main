import pygame   

class Input(object):

    def __init__(self):
        # has the user quit the application?
        self.quit = False

        # lists to store key states
            # down, up: discrete events; lasts for one iteration
            # pressed: continuous event; between down and up events
        self.keysDownList = []
        self.keysPressedList = []
        self.keysUpList = []

        # variables to store mouse state
        self.mouseLeftDown = False
        self.mouseMiddleDown = False
        self.mouseRightDown = False
        self.mousePos = pygame.mouse.get_pos()
        self.mouseDelta = (0,0)
        self.mouseScroll = 0




    def update(self):

        # reset discrete key states
        self.keysDownList = []
        self.keysUpList = []
        self.mouseDelta = (0,0)
        self.mouseScroll = 0

        newMousePos = pygame.mouse.get_pos()
        self.mouseDelta = (newMousePos[0] - self.mousePos[0], newMousePos[1] - self.mousePos[1])
        self.mousePos = newMousePos

        # iterate over all user input events (e.g. keyboard, mouse)
        # that have occurred since the last time events were checked
        for event in pygame.event.get():

        # quit event occurs by clicking the close button
        # if event.type == pygame.QUIT:
            if event.type == pygame.QUIT:
                self.quit = True

            # check for keydown and keyup events
                # get name of key from event
                # and append / remove from list
            if event.type == pygame.KEYDOWN:
                keyName = pygame.key.name(event.key)
                self.keysDownList.append(keyName)
                self.keysPressedList.append(keyName)

            if event.type == pygame.KEYUP:
                keyName = pygame.key.name(event.key)
                self.keysUpList.append(keyName)
                self.keysPressedList.remove(keyName)

            # check for mouse button down events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left
                    self.mouseLeftDown = True
                if event.button == 2: # middle
                    self.mouseMiddleDown = True
                if event.button == 3: # right
                    self.mouseRightDown = True
                if event.button == 4: # scroll up
                    self.mouseScroll = 1
                if event.button == 5: # scroll down
                    self.mouseScroll = -1

            # check for mouse button up events
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # left
                    self.mouseLeftDown = False
                if event.button == 2: # middle
                    self.mouseMiddleDown = False
                if event.button == 3: # right
                    self.mouseRightDown = False



    
    # functions to check key states
    def isKeyDown(self, keyName):
        return keyName in self.keysDownList
    def isKeyPressed(self, keyName):
        return keyName in self.keysPressedList
    def isKeyUp(self, keyName):
        return keyName in self.keysUpList
    

    # functions to check mouse states
    def isMouseLeftDown(self):
        return self.mouseLeftDown
    def isMouseMiddleDown(self):
        return self.mouseMiddleDown
    def isMouseRightDown(self):
        return self.mouseRightDown
    def getMousePos(self):
        return self.mousePos
    def getMouseDelta(self):
        return self.mouseDelta
    def getMouseScroll(self):
        return self.mouseScroll

        