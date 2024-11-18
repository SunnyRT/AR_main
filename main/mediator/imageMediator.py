from mediator.mediator import Mediator

class ImageMediator(Mediator):
    def __init__(self, rig, microscope, 
                 imagePlaneFactory, 
                 contourMeshFactory, 
                 projectorMeshFactory):
        self.rig = rig
        self.microscope = microscope
        self.imagePlaneFactory = imagePlaneFactory
        self.contourMesh = contourMeshFactory
        self.projectorMesh = projectorMeshFactory

    def notify(self, sender, event, data=None):
        if event == "update near plane": # sent by microscope
            self.handle_update_n(event, data)
        if event == "microscope shift along z":
            self.handle_rig_zshift(event, data)
        


    def handle_update_n(self, event, data):
        del_n = 10*data["shiftScroll"]
        # update near clipping plane in microscope and imagePlane
        self.imagePlaneFactory.update(del_n=del_n)
        self.contourMeshFactory.update(del_n=del_n)
        self.projectorMeshFactory.update(del_n=del_n)
        self.MatchMeshFactory.update()

    # FIXME:xxxx
    def handleUpdateNearFar(self, event, data):
        self.imagePlane.update()
        self.contourMesh.update()
        self.projectorMesh.update()

    # FIXME:xxxx
    def handle_rig_zshift(self, event, data):
        altScroll = data["altScroll"]
        # update near and far clipping planes in microscope and imagePlane
        self.microscope.updateNear(-altScroll*10) # subtract altScroll*10 from near
        self.imagePlane.updateNearFar(-altScroll*10, -altScroll*10)
            



    def recreateObject(self, objectName):
        if objectName == "imagePlane":
            self.imagePlaneFactory.update()
        elif objectName == "contourMesh":
            self.contourMeshFactory.update()
        elif objectName == "projectorMesh":
            self.projectorMeshFactory.update()
        else:
            print("Object not found")
