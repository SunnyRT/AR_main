from extras.movementRig import MovementRig
from math import pi

class MicroscopeRig(MovementRig):

    def __init__(self, unitsPerSecond=1, degreesPerSecond=60, mediators=None):
        
        # intialize base Object3D
        # controls movement, annd turn left/right
        super().__init__(unitsPerSecond, degreesPerSecond)

        # Allow multiple mediators to be attached to the rig
        if mediators is None:
            self.mediators = []
        elif isinstance(mediators, list):
            self.mediators = mediators
        else:
            self.mediators = [mediators]


    def update(self, inputObject, deltaTime=None):
        # Handle alt mouse scroll -> move rig along z
        altMouseScroll = inputObject.getAltMouseScroll()
        if altMouseScroll != 0:
            self.translate(0, 0, -altMouseScroll*10)
            for mediator in self.mediators:
                mediator.notify(self, "rig move along z", data={"altScroll": altMouseScroll})

        # FIXME: selective update propagation to child objects (microscope)
        super().update(inputObject, deltaTime) # no child update propagation, only inherited movement updates
    

    def addMediator(self, mediator):
        self.mediators.append(mediator)
    
    def removeMediator(self, mediator):
        self.mediators.pop(mediator)

        
        