from mediator.mediator import Mediator

class ImageMediator(Mediator):
    def __init__(self, rig, microscope, 
                 imagePlaneFactory, 
                 contourMeshFactory, 
                 projectorMeshFactory, idx=0):
        self.rig = rig
        self.microscope = microscope
        self.imagePlaneFactory = imagePlaneFactory
        self.contourMeshFactory = contourMeshFactory
        self.projectorMeshFactory = projectorMeshFactory
        self.idx = idx

        # since registrator and matchMeshFactory are shared between multiple mediators
        # only update once for some events (to prevent duplicate updates)
        self.matchMeshFactory = None
        self.registrator = None
        
    def setMatchMeshFactory(self, matchMeshFactory):
        self.matchMeshFactory = matchMeshFactory

    def setRegistrator(self, registrator):
        self.registrator = registrator    

    def notify(self, sender, event, data=None):
        """ updates from keyboard/mouse events """
        if event == "update near plane": # sent by microscope
            # print(f"ImageMediator: notified to update near plane by {sender}")
            self.handle_update_n(event, data)
        if event == "update far plane": # sent by microscope
            # print(f"ImageMediator: notified to update far plane by {sender}")
            self.handle_update_f(event, data)
        if event == "rig move along z": # sent by microscope rig!!! # multiple mediators needed!!!!!
            # print(f"ImageMediator: notified to move rig along z by {sender}")
            self.handle_rig_movez(event, data)
        if event == "microscope rig moved": # sent by microscope rig
            # print(f"ImageMediator: notified to move rig by {sender}")
            self.handle_msrig_move(event, data)

        """ updates from GUIframe """   
        if event == "update projector delta": # sent by GUIframe
            # print(f"ImageMediator: notified to update projector delta by {sender}")
            self.handle_update_delta(event, data)
        if event == "update dmax":
            self.handle_update_dmax(event, data)
        if event == "update alpha":
            self.handle_update_alpha(event, data)
        if event == "update visibility":
            self.handle_update_visibility(event, data)    
            
            



    def handle_update_n(self, event, data):
        del_n = 10*data["shiftScroll"]
        # update near clipping plane in microscope and imagePlane
        self.imagePlaneFactory.update(del_n=del_n)
        self.projectorMeshFactory.contour = self.contourMeshFactory.update(del_n=del_n)
        projector = self.projectorMeshFactory.update(del_n=del_n)
        
        self.registrator.updateMesh1(mesh1=projector, idx=self.idx)
        self.matchMeshFactory.update(self.registrator.closestPairsPerRay)

    def handle_update_f(self, event, data):
        del_f = 10*data["ctrlScroll"]
        # update far clipping plane in microscope and imagePlane
        self.projectorMeshFactory.contour = self.contourMeshFactory.update(del_n=0)
        projector = self.projectorMeshFactory.update(del_f=del_f)
        
        self.registrator.updateMesh1(mesh1=projector, idx=self.idx)
        self.matchMeshFactory.update(self.registrator.closestPairsPerRay)


    def handle_rig_movez(self, event, data):
        altScroll = data["altScroll"]
        del_z = altScroll*10
        # update near and far clipping planes in microscope and imagePlane
        # self.microscope.update(del_n=-del_z)
        self.imagePlaneFactory.update(del_n=-del_z)
        self.projectorMeshFactory.contour = self.contourMeshFactory.update(del_n=-del_z)
        projector = self.projectorMeshFactory.update(del_n=-del_z, del_f=-del_z)
        
        self.registrator.updateMesh1(mesh1=projector, idx=self.idx)
        self.matchMeshFactory.update(self.registrator.closestPairsPerRay)
         
    def handle_msrig_move(self, event, data):
        # only need to update registrator and matchMeshFactory
        # print(f"ImageMediator: notified to move rig by {data['prevTransform']} to {data['currTransform']}")
        self.registrator.updateMatch()
        self.matchMeshFactory.update(self.registrator.closestPairsPerRay)



    def handle_update_delta(self, event, data):
        delta = data["delta"]
        # update delta in projectorMesh
        # print(f"ImageMediator: notified to update projector delta to {delta}")
        projector = self.projectorMeshFactory.update(delta=delta)
        
        self.registrator.updateMesh1(mesh1=projector, idx=self.idx)
        self.matchMeshFactory.update(self.registrator.closestPairsPerRay)
    
    def handle_update_dmax(self, event, data):
        dmax = data["dmax"]
        self.registrator.d_max = dmax
        self.registrator.updateMatch()
        self.matchMeshFactory.update(self.registrator.closestPairsPerRay)
    
    def handle_update_alpha(self, event, data):
        alpha = data["alpha"]
        if data["object"] == "image":
            self.imagePlaneFactory.setAlpha(alpha)
        elif data["object"] == "projector":
            self.projectorMeshFactory.setAlpha(alpha)
    
    def handle_update_visibility(self, event, data):
        visible = data["is_visible"]
        if data["object"] == "contour":
            self.contourMeshFactory.setVisibility(visible)
        elif data["object"] == "match":
            self.matchMeshFactory.setVisibility(visible)