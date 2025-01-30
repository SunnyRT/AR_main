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
        # 1. Handle alt mouse scroll -> move rig along z
        altMouseScroll = inputObject.getAltMouseScroll()
        if altMouseScroll != 0:
            self.translate(0, 0, -altMouseScroll*10)
            for mediator in self.mediators:
                mediator.notify(self, "rig move along z", data={"altScroll": altMouseScroll})





        # 2. track changes in camera parameters (microscopic camera1)
        prevTransform = self.getWorldMatrix()

        # selective update propagation to child objects (microscope)
        # no child update propagation, only inherited movement updates
        super().update(inputObject, deltaTime) 

        # if rig has moved, notify mediators
        currTransform = self.getWorldMatrix()
        if not (prevTransform == currTransform).all():
            # choose to notify only 1 single mediatorReg
            # eventually reaching the same registrator and the matchMeshFactory
            self.mediators[0].notify(self, "microscope rig moved", data={"prevTransform": prevTransform, "currTransform": currTransform}) 
            # notify only 1 single mediatorVal
            # eventually reaching the same validator and the matchMeshFactory
            try:
                self.mediators[2].notify(self, "microscope rig moved", data={"prevTransform": prevTransform, "currTransform": currTransform}) 
            except:
                pass
            
    def addMediator(self, mediator):
        self.mediators.append(mediator)
    
    def removeMediator(self, mediator):
        self.mediators.pop(mediator)

        
        