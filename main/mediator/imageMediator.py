from mediator.mediator import Mediator

class ImageMediator(Mediator):
    def __init__(self, rig, microscope, 
                 imagePlaneFactory, 
                 contourMeshFactory, 
                 projectorMeshFactory):
        self.rig = rig
        self.microscope = microscope
        self.imagePlaneFactory = imagePlaneFactory
        self.contourMeshFactory = contourMeshFactory
        self.projectorMeshFactory = projectorMeshFactory
        
  

    def notify(self, sender, event, data=None):
        if event == "update near plane": # sent by microscope
            # print(f"ImageMediator: notified to update near plane by {sender}")
            self.handle_update_n(event, data)
        if event == "update far plane": # sent by microscope
            # print(f"ImageMediator: notified to update far plane by {sender}")
            self.handle_update_f(event, data)
        if event == "rig move along z": # sent by microscopeRIG!!! # FIXME: multiple mediators needed!!!!!
            # print(f"ImageMediator: notified to move rig along z by {sender}")
            self.handle_rig_movez(event, data)
        if event == "update projector delta": # sent by GUIframe
            print(f"ImageMediator: notified to update projector delta by {sender}")
            self.handle_update_delta(event, data)
            



    def handle_update_n(self, event, data):
        del_n = 10*data["shiftScroll"]
        # update near clipping plane in microscope and imagePlane
        self.imagePlaneFactory.update(del_n=del_n)
        self.projectorMeshFactory.contour =self.contourMeshFactory.update(del_n=del_n)
        self.projectorMeshFactory.update(del_n=del_n)
        # self.MatchMeshFactory.update() # FIXME:

    def handle_update_f(self, event, data):
        del_f = 10*data["ctrlScroll"]
        # update far clipping plane in microscope and imagePlane
        self.projectorMeshFactory.contour =self.contourMeshFactory.update(del_n=0)
        self.projectorMeshFactory.update(del_f=del_f)
        # self.MatchMeshFactory.update() # FIXME:


    def handle_rig_movez(self, event, data):
        altScroll = data["altScroll"]
        del_z = altScroll*10
        # update near and far clipping planes in microscope and imagePlane
        # self.microscope.update(del_n=-del_z)
        self.imagePlaneFactory.update(del_n=-del_z)
        self.projectorMeshFactory.contour = self.contourMeshFactory.update(del_n=-del_z)
        self.projectorMeshFactory.update(del_n=-del_z, del_f=-del_z)
        # self.MatchMeshFactory.update() # FIXME:
            

    def handle_update_delta(self, event, data):
        delta = data["delta"]
        # update delta in projectorMesh
        self.projectorMeshFactory.update(delta=delta)
        # self.MatchMeshFactory.update() # FIXME: