from mesh.mesh import Mesh

class MeshFactory(object):
    def __init__(self, mediator=None):
        self.mediator = mediator # TODO: may not be necessary
        self.mesh = None
        pass

    def setMediator(self, mediator):
        self.mediator = mediator

    def createMesh(self, geometry=None, material=None):
        pass # TODO: override this method
        if geometry is not None and material is not None:
            return Mesh(geometry, material)
        else:
            return None
    
    def setAlpha(self, alpha):
        self.mesh.setAlpha(alpha)

    def setVisibility(self, visible):
        self.mesh.visible = visible
    
    def update(self):
        # find parent node, remove mesh from parent node
        parent = self.mesh.parent
        descendents = self.mesh.children
        # print(f"oldMesh parent: {parent}, to remove: {self.mesh} among children: {parent.children}")
        for child in parent.children:
            if child.geometry.vertexCount == self.mesh.geometry.vertexCount:
                parent.remove(child)
                del child
                break # Assume only one mesh with the same vertex count to be removed

        # create new mesh
        self.mesh = self.createMesh()
        if len(descendents) > 0:
            for child in descendents:
                self.mesh.add(child)
        parent.add(self.mesh)
        return self.mesh
