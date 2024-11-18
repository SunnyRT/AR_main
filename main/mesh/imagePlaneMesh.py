from mesh.mesh import Mesh
from OpenGL.GL import *

class ImagePlaneMesh(Mesh):

    def __init__(self, geometry, material, mediator=None):
        super().__init__(geometry, material, mediator)

        
    # def update(self, inputObject, deltaTime=None):
    #     # Handle shift mouse scroll -> set near clipping plane n
    #     shiftMouseScroll = inputObject.getShiftMouseScroll()
    #     if shiftMouseScroll != 0:
    #         if self.mediator:
    #             self.mediator.notify(self, "update near plane", data={"shiftScroll": shiftMouseScroll})
    
    def updateNearFar(self, del_n, del_f):
        pass

    
