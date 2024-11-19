from core_ext.object3d import Object3D
from math import pi

class MovementRig(Object3D):

    def __init__(self, unitsPerSecond=1, degreesPerSecond=60):
        
        # intialize base Object3D
        # controls movement, annd turn left/right
        super().__init__()

        # initialize attached Object3D
        # controls look up/down
        self.lookAttachment = Object3D()
        self.children = [self.lookAttachment]
        self.lookAttachment.parent = self

        self.projectorObject = None

        # control rate of movement
        self.unitsPerSecond = unitsPerSecond
        self.degreesPerSecond = degreesPerSecond

        # customize key mappings
        # Defaults: W, A, S, D, R, F (move), Q, E (turn), T, G (look)
        self.KEY_MOVE_FORWARDS = "w" # orthographic zoom in
        self.KEY_MOVE_BACKWARDS = "s" # orthographic zoom out
        self.KEY_MOVE_LEFT = "a"
        self.KEY_MOVE_RIGHT = "d"
        self.KEY_MOVE_UP = "r"
        self.KEY_MOVE_DOWN = "f"
        self.KEY_TURN_LEFT = "q"
        self.KEY_TURN_RIGHT = "e"
        self.KEY_LOOK_UP = "t"
        self.KEY_LOOK_DOWN = "g" 

    
    # adding and removing objects applies to the lookAttachment
    # override functions from Object3D class
    def add(self, child):
        self.lookAttachment.add(child)
    
    def remove(self, child):
        self.lookAttachment.remove(child)

    
    def update(self, inputObject, deltaTime=None):

        # TODO: track changes in camera parameters (microscopic camera1)
        self.isUpdated = False
        prevTransform = self.getWorldMatrix()

        if inputObject is None:
            print("MovementRig.update() error: inputObject is None")
            return  # Exit if inputObject is not passed correctly
        
        moveAmount = 0.1
        rotateAmount = pi / 180

        # Handle keyboard-based movement and rotation
        if inputObject.isKeyPressed(self.KEY_MOVE_FORWARDS):
            self.translate(0, 0, -moveAmount)
        if inputObject.isKeyPressed(self.KEY_MOVE_BACKWARDS):
            self.translate(0, 0, moveAmount)
        if inputObject.isKeyPressed(self.KEY_MOVE_LEFT):
            self.translate(-moveAmount, 0, 0)
        if inputObject.isKeyPressed(self.KEY_MOVE_RIGHT):
            self.translate(moveAmount, 0, 0)
        if inputObject.isKeyPressed(self.KEY_MOVE_UP):
            self.translate(0, moveAmount, 0)
        if inputObject.isKeyPressed(self.KEY_MOVE_DOWN):
            self.translate(0, -moveAmount, 0)

        if inputObject.isKeyPressed(self.KEY_TURN_RIGHT):
            self.rotateY(-rotateAmount)
        if inputObject.isKeyPressed(self.KEY_TURN_LEFT):
            self.rotateY(rotateAmount)

        if inputObject.isKeyPressed(self.KEY_LOOK_UP):
            # self.lookAttachment.rotateX(rotateAmount) # TODO:
            self.rotateX(rotateAmount)
        if inputObject.isKeyPressed(self.KEY_LOOK_DOWN):
            # self.lookAttachment.rotateX(-rotateAmount)
            self.rotateX(-rotateAmount)


        # # Handle mouse-based rotation when left mouse button is held down
        # rotate about global origin
        if inputObject.isMouseLeftDown():
            mouseDelta = inputObject.getMouseDelta()
            self.rotateY(mouseDelta[0] * rotateAmount, localCoord=False)
            self.rotateX(-mouseDelta[1] * rotateAmount, localCoord=False)
            # # reset rig up/down rotation to 0, lookattachment up/down rotation to target angle
            # pitch = self.getRotationMatrix()[0]
            # self.rotateX(-pitch, localCoord=True)
            # self.lookAttachment.rotateX(pitch, localCoord=True)




        # Handle mouse-based panning when right mouse button is held down
        if inputObject.isMouseRightDown():
            mouseDelta = inputObject.getMouseDelta()
            self.translate(-mouseDelta[0] * moveAmount, mouseDelta[1] * moveAmount, 0)

        if inputObject.isMouseMiddleDown():
            mouseDelta = inputObject.getMouseDelta()
            self.rotateZ(-(mouseDelta[0] + mouseDelta[1]) * rotateAmount)

        # Handle middle mouse button to move forward/backward (or zoom)
        mouseScroll = inputObject.getMouseScroll()
        if mouseScroll != 0:
            self.translate(0, 0, -mouseScroll * moveAmount)

        # super().update(inputObject, deltaTime) # propagate update to children
        currTransform = self.getWorldMatrix()
        if not (prevTransform == currTransform).all():
            self.isUpdated = True

    
        # super().update(inputObject, deltaTime) # propagate update to children
        



        
        