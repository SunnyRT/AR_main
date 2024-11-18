from mesh.mesh import Mesh

class MeshFactory(object):
    def __init__(self, mediator=None):
        self.mediator = mediator # TODO: may not be necessary
        pass

    def setMediator(self, mediator):
        self.mediator = mediator

    def createMesh(self, geometry=None, material=None):
        pass # TODO: override this method
        if geometry is not None and material is not None:
            return Mesh(geometry, material)
        else:
            return None
    

    
    def update(self, mesh):
        # find parent node, remove mesh from parent node
        parent = mesh.parent
        parent.remove(mesh)
        del mesh

        # create new mesh
        mesh = self.createMesh()
        parent.add(mesh)
        return mesh 
